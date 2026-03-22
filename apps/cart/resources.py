from import_export import resources
from .models import Cart, CartItem


class CartResource(resources.ModelResource):
    class Meta:
        model = Cart
        fields = ('id', 'user__email', 'session_key', 'created_at', 'updated_at')
        export_order = fields


class CartItemResource(resources.ModelResource):
    class Meta:
        model = CartItem
        fields = (
            'id', 'cart__id', 'product__name', 'variant__name', 'quantity',
            'base_price', 'attributes_price', 'addons_price', 'unit_price',
            'custom_message', 'special_instructions', 'created_at', 'updated_at'
        )
        export_order = fields
