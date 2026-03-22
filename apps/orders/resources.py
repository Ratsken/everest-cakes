from import_export import resources
from .models import Order


class OrderResource(resources.ModelResource):
    class Meta:
        model = Order
        fields = ('id', 'order_number', 'customer_name', 'customer_email', 'customer_phone',
                  'delivery_address', 'delivery_city', 'delivery_date', 'subtotal', 
                  'delivery_fee', 'total', 'payment_method', 'payment_status', 'status',
                  'created_at', 'updated_at')
        export_order = fields
