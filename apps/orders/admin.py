from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import action, display
from import_export.admin import ImportExportModelAdmin
from .models import Order, OrderTracking, PaymentTransaction, OrderAttachment, Enquiry
from .resources import OrderResource


class OrderAttachmentInline(admin.TabularInline):
    model = OrderAttachment
    extra = 0
    readonly_fields = ['attachment_type', 'file', 'description', 'created_at']
    can_delete = True


class OrderTrackingInline(admin.TabularInline):
    model = OrderTracking
    extra = 0
    fields = ['status', 'description', 'location', 'created_at']
    readonly_fields = ['created_at']


class PaymentTransactionInline(admin.TabularInline):
    model = PaymentTransaction
    extra = 0
    readonly_fields = ['provider', 'transaction_id', 'amount', 'status', 'created_at']
    can_delete = False


@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = OrderResource
    list_display = ['order_number', 'customer_name', 'customer_phone', 'total', 
                    'payment_method', 'payment_status_badge', 'status_badge', 
                    'delivery_date', 'email_sent', 'whatsapp_sent', 'created_at']
    list_filter = ['status', 'payment_status', 'payment_method', 'created_at', 'delivery_date',
                   'email_sent', 'whatsapp_sent']
    search_fields = ['order_number', 'customer_name', 'customer_phone', 'customer_email']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'paid_at', 'item_count',
                       'email_sent', 'whatsapp_sent']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'status', 'created_at', 'updated_at')
        }),
        ('Customer Information', {
            'fields': ('user', 'customer_name', 'customer_email', 'customer_phone')
        }),
        ('Delivery Information', {
            'fields': ('delivery_address', 'delivery_city', 'delivery_date', 
                      'delivery_time_slot', 'delivery_instructions')
        }),
        ('Gift Options', {
            'fields': ('is_gift', 'recipient_name', 'recipient_phone', 'gift_message'),
            'classes': ('collapse',),
        }),
        ('Order Items', {
            'fields': ('items', 'item_count'),
        }),
        ('Pricing', {
            'fields': ('subtotal', 'delivery_fee', 'discount', 'total')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_status', 'payment_reference', 'paid_at')
        }),
        ('Customer Notes', {
            'fields': ('notes',)
        }),
        ('Internal Notes', {
            'fields': ('internal_notes',)
        }),
        ('Notifications', {
            'fields': ('email_sent', 'whatsapp_sent'),
            'classes': ('collapse',),
        }),
    )
    
    inlines = [OrderTrackingInline, PaymentTransactionInline, OrderAttachmentInline]
    
    @display(description='Payment')
    def payment_status_badge(self, obj):
        colors = {
            'pending': 'bg-yellow-100 text-yellow-800',
            'processing': 'bg-blue-100 text-blue-800',
            'completed': 'bg-green-100 text-green-800',
            'failed': 'bg-red-100 text-red-800',
        }
        return format_html(
            '<span class="{} px-2 py-1 rounded text-xs font-medium">{}</span>',
            colors.get(obj.payment_status, 'bg-gray-100 text-gray-800'),
            obj.get_payment_status_display()
        )
    
    @display(description='Status')
    def status_badge(self, obj):
        colors = {
            'pending': 'bg-gray-100 text-gray-800',
            'confirmed': 'bg-blue-100 text-blue-800',
            'processing': 'bg-indigo-100 text-indigo-800',
            'ready': 'bg-purple-100 text-purple-800',
            'out_for_delivery': 'bg-orange-100 text-orange-800',
            'delivered': 'bg-green-100 text-green-800',
            'cancelled': 'bg-red-100 text-red-800',
        }
        return format_html(
            '<span class="{} px-2 py-1 rounded text-xs font-medium">{}</span>',
            colors.get(obj.status, 'bg-gray-100 text-gray-800'),
            obj.get_status_display()
        )
    
    @action(description="Mark as Confirmed", url_path="mark-confirmed")
    def mark_confirmed(self, request, queryset):
        count = queryset.update(status='confirmed')
        self.message_user(request, f"{count} orders marked as confirmed.")
    
    @action(description="Mark as Delivered", url_path="mark-delivered")
    def mark_delivered(self, request, queryset):
        from django.utils import timezone
        count = 0
        for order in queryset:
            order.status = 'delivered'
            if order.payment_method in ['cash', 'cod']:
                order.payment_status = 'completed'
                order.paid_at = timezone.now()
            order.save()
            count += 1
        self.message_user(request, f"{count} orders marked as delivered.")
    
    @action(description="Resend Notifications", url_path="resend-notifications")
    def resend_notifications(self, request, queryset):
        from .tasks import send_order_notifications
        count = 0
        for order in queryset:
            send_order_notifications.delay(str(order.id))
            count += 1
        self.message_user(request, f"Notifications queued for {count} orders.")
    
    @action(description="Export Orders CSV", url_path="export-orders")
    def export_orders(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Order Number', 'Customer', 'Phone', 'Email', 'Total', 'Payment Method', 
                        'Payment Status', 'Order Status', 'Delivery Date', 'Created At'])
        
        for order in queryset:
            writer.writerow([
                order.order_number,
                order.customer_name,
                order.customer_phone,
                order.customer_email,
                order.total,
                order.get_payment_method_display(),
                order.get_payment_status_display(),
                order.get_status_display(),
                order.delivery_date,
                order.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response


@admin.register(OrderAttachment)
class OrderAttachmentAdmin(ModelAdmin):
    list_display = ['order', 'attachment_type', 'description', 'created_at']
    list_filter = ['attachment_type', 'created_at']
    search_fields = ['order__order_number']


@admin.register(OrderTracking)
class OrderTrackingAdmin(ModelAdmin):
    list_display = ['order', 'status', 'description', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number']


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(ModelAdmin):
    list_display = ['order', 'provider', 'transaction_id', 'amount', 'status', 'created_at']
    list_filter = ['provider', 'status', 'created_at']
    search_fields = ['order__order_number', 'transaction_id']


@admin.register(Enquiry)
class EnquiryAdmin(ModelAdmin):
    list_display = ['name', 'email', 'phone', 'subject', 'product', 'status', 
                    'email_sent', 'whatsapp_sent', 'created_at']
    list_filter = ['status', 'email_sent', 'whatsapp_sent', 'created_at']
    search_fields = ['name', 'email', 'phone', 'subject', 'message']
    list_editable = ['status']
    readonly_fields = ['name', 'email', 'phone', 'subject', 'message', 'product', 
                       'image', 'email_sent', 'whatsapp_sent', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Enquiry Details', {
            'fields': ('name', 'email', 'phone', 'subject', 'message', 'product', 'image')
        }),
        ('Status', {
            'fields': ('status', 'notes')
        }),
        ('Notifications', {
            'fields': ('email_sent', 'whatsapp_sent', 'created_at', 'updated_at')
        }),
    )
    
    @action(description="Mark as Resolved", url_path="mark-resolved")
    def mark_resolved(self, request, queryset):
        count = queryset.update(status='resolved')
        self.message_user(request, f"{count} enquiries marked as resolved.")
    
    @action(description="Resend Notifications", url_path="resend-enquiry-notifications")
    def resend_notifications(self, request, queryset):
        from .tasks import send_enquiry_notifications
        count = 0
        for enquiry in queryset.filter(status='new'):
            send_enquiry_notifications.delay(str(enquiry.id))
            count += 1
        self.message_user(request, f"Notifications queued for {count} enquiries.")
