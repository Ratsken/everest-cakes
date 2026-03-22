from import_export import resources
from .models import Order, OrderTracking, PaymentTransaction, OrderAttachment, Enquiry


class OrderResource(resources.ModelResource):
    class Meta:
        model = Order
        fields = ('id', 'order_number', 'customer_name', 'customer_email', 'customer_phone',
                  'delivery_address', 'delivery_city', 'delivery_date', 'subtotal', 
                  'delivery_fee', 'total', 'payment_method', 'payment_status', 'status',
                  'created_at', 'updated_at')
        export_order = fields


class OrderTrackingResource(resources.ModelResource):
    class Meta:
        model = OrderTracking
        fields = ('id', 'order__order_number', 'status', 'description', 'location', 'created_at')
        export_order = fields


class PaymentTransactionResource(resources.ModelResource):
    class Meta:
        model = PaymentTransaction
        fields = ('id', 'order__order_number', 'provider', 'transaction_id', 'amount', 'status', 'created_at')
        export_order = fields


class OrderAttachmentResource(resources.ModelResource):
    class Meta:
        model = OrderAttachment
        fields = ('id', 'order__order_number', 'attachment_type', 'description', 'created_at')
        export_order = fields


class EnquiryResource(resources.ModelResource):
    class Meta:
        model = Enquiry
        fields = ('id', 'name', 'email', 'phone', 'subject', 'product__name', 'status', 'email_sent', 'whatsapp_sent', 'created_at', 'updated_at')
        export_order = fields
