from django.contrib import admin
from django.utils.html import format_html, conditional_escape
from django.utils.safestring import mark_safe
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import action, display
from import_export.admin import ImportExportModelAdmin
from .models import Order, OrderTracking, PaymentTransaction, OrderAttachment, Enquiry
from .resources import (
    OrderResource,
    OrderTrackingResource,
    PaymentTransactionResource,
    OrderAttachmentResource,
    EnquiryResource,
)


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
                       'email_sent', 'whatsapp_sent', 'items_display']
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
            'fields': ('items_display', 'item_count'),
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

    @display(description='Order Items')
    def items_display(self, obj):
        items = obj.items or []
        if not items:
            return mark_safe('<p style="color:#999;">No items recorded.</p>')

        rows = []
        for idx, item in enumerate(items):
            name = conditional_escape(item.get('name', '\u2014'))
            variant = conditional_escape(item.get('variant_name', '') or '')
            qty = int(item.get('quantity', 1))
            base_price = conditional_escape(str(item.get('base_price', '0.00')))
            unit_price = conditional_escape(str(item.get('unit_price', '0.00')))
            total_price = conditional_escape(str(item.get('total_price', item.get('total', '0.00'))))
            custom_message = conditional_escape(item.get('custom_message', '') or '')
            special_instructions = conditional_escape(item.get('special_instructions', '') or '')

            # Attributes
            attr_parts = []
            for attr in item.get('attributes', []):
                attr_name = conditional_escape(attr.get('attribute', attr.get('name', '')))
                opt = conditional_escape(attr.get('option', ''))
                adj = attr.get('price_adjustment', '0.00')
                try:
                    adj_val = float(adj or 0)
                except (ValueError, TypeError):
                    adj_val = 0
                adj_str = mark_safe(f' <span style="color:#888;font-size:11px;">(+KSh {conditional_escape(str(adj))})</span>') if adj_val > 0 else ''
                attr_parts.append(mark_safe(f'<li style="margin:2px 0;"><strong>{attr_name}:</strong> {opt}{adj_str}</li>'))
            attr_html = mark_safe(''.join(str(p) for p in attr_parts))

            # Addons
            addon_parts = []
            for addon in item.get('addons', []):
                addon_name = conditional_escape(addon.get('name', ''))
                addon_price = addon.get('price', '0.00')
                try:
                    addon_price_val = float(addon_price or 0)
                except (ValueError, TypeError):
                    addon_price_val = 0
                addon_qty = int(addon.get('quantity', 1))
                addon_total = conditional_escape(str(addon.get('total', '0.00')))
                price_str = mark_safe(f'KSh {conditional_escape(str(addon_price))}') if addon_price_val > 0 else mark_safe('Free')
                addon_parts.append(mark_safe(
                    f'<li style="margin:2px 0;">{addon_name} &times;{addon_qty} \u2014 {price_str}'
                    f' <span style="color:#888;font-size:11px;">(KSh {addon_total})</span></li>'
                ))
            addon_html = mark_safe(''.join(str(p) for p in addon_parts))

            variant_str = mark_safe(f'<span style="color:#666;margin-left:8px;font-size:12px;">{variant}</span>') if variant else ''
            msg_str = mark_safe(f'<p style="margin:4px 0;color:#555;"><em>Message: {custom_message}</em></p>') if custom_message else ''
            instr_str = mark_safe(f'<p style="margin:4px 0;color:#555;"><em>Note: {special_instructions}</em></p>') if special_instructions else ''
            attr_block = mark_safe(f'<ul style="margin:8px 0 4px 0;padding-left:18px;font-size:13px;">{attr_html}</ul>') if attr_html else ''
            addon_block = mark_safe(
                f'<div style="margin-top:6px;"><span style="font-size:12px;font-weight:600;color:#555;">Add-ons:</span>'
                f'<ul style="margin:2px 0;padding-left:18px;font-size:13px;">{addon_html}</ul></div>'
            ) if addon_html else ''

            rows.append(mark_safe(
                f'<div style="border:1px solid #e0e0e0;border-radius:8px;padding:14px;margin-bottom:12px;background:#fafafa;">'
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">'
                f'<div><span style="font-size:15px;font-weight:600;color:#1a1a1a;">{name}</span>{variant_str}'
                f'<span style="display:inline-block;margin-left:10px;background:#f0f0f0;border-radius:4px;padding:1px 8px;font-size:12px;color:#555;">Qty: {qty}</span></div>'
                f'<div style="text-align:right;">'
                f'<div style="font-size:12px;color:#888;">Base: KSh {base_price} &nbsp;|&nbsp; Unit: KSh {unit_price}</div>'
                f'<div style="font-size:14px;font-weight:700;color:#1a5e1a;">Line Total: KSh {total_price}</div>'
                f'</div></div>'
                f'{attr_block}{addon_block}{msg_str}{instr_str}'
                f'</div>'
            ))

        return mark_safe('<div style="max-width:700px;">' + ''.join(str(r) for r in rows) + '</div>')
    
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
            try:
                send_order_notifications(str(order.id))
            except Exception:
                import logging
                logging.getLogger(__name__).exception("Failed to send notifications for order %s", order.id)
            count += 1
        self.message_user(request, f"Notifications triggered for {count} orders.")
    
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
class OrderAttachmentAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = OrderAttachmentResource
    list_display = ['order', 'attachment_type', 'description', 'created_at']
    list_filter = ['attachment_type', 'created_at']
    search_fields = ['order__order_number']


@admin.register(OrderTracking)
class OrderTrackingAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = OrderTrackingResource
    list_display = ['order', 'status', 'description', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number']


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = PaymentTransactionResource
    list_display = ['order', 'provider', 'transaction_id', 'amount', 'status', 'created_at']
    list_filter = ['provider', 'status', 'created_at']
    search_fields = ['order__order_number', 'transaction_id']


@admin.register(Enquiry)
class EnquiryAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = EnquiryResource
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
            try:
                send_enquiry_notifications(str(enquiry.id))
            except Exception:
                import logging
                logging.getLogger(__name__).exception("Failed to send enquiry notifications for %s", enquiry.id)
            count += 1
        self.message_user(request, f"Notifications triggered for {count} enquiries.")
