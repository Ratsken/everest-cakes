from django.db import models
from django.conf import settings
import uuid


class Cart(models.Model):
    """Shopping Cart Model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['session_key']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"Cart {self.id}"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())
    
    @property
    def delivery_fee(self):
        from apps.core.models import SiteSetting
        setting = SiteSetting.get_settings()
        if setting and self.subtotal >= setting.free_delivery_threshold:
            return 0
        return setting.delivery_fee if setting else 300
    
    @property
    def total(self):
        return self.subtotal + self.delivery_fee


class CartItem(models.Model):
    """Cart Item Model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    variant = models.ForeignKey('products.ProductVariant', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    
    # Base price (before attributes/addons)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Selected Attributes (JSON: {"attribute_id": "option_id", ...})
    selected_attributes = models.JSONField(default=dict, blank=True)
    
    # Selected Addons (JSON: [{"addon_id": "id", "quantity": 1}, ...])
    selected_addons = models.JSONField(default=list, blank=True)
    
    # Attributes price adjustment
    attributes_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Addons total price
    addons_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Final unit price (includes everything)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Customization
    custom_message = models.TextField(blank=True, help_text='Custom cake message')
    special_instructions = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['cart', 'product', 'variant']
    
    @property
    def total_price(self):
        return self.unit_price * self.quantity
    
    @property
    def product_name(self):
        return self.product.name
    
    @property
    def variant_name(self):
        return self.variant.name if self.variant else None
    
    @property
    def selected_attributes_display(self):
        """Return human-readable selected attributes"""
        from apps.products.models import ProductAttribute, ProductAttributeOption
        display = []
        for attr_id, opt_id in self.selected_attributes.items():
            try:
                attr = ProductAttribute.objects.get(id=attr_id)
                opt = ProductAttributeOption.objects.get(id=opt_id)
                display.append(f"{attr.name}: {opt.name}")
            except:
                pass
        return display
    
    @property
    def selected_addons_display(self):
        """Return human-readable selected addons"""
        from apps.products.models import ProductAddon
        display = []
        for addon_item in self.selected_addons:
            try:
                addon = ProductAddon.objects.get(id=addon_item.get('addon_id'))
                qty = addon_item.get('quantity', 1)
                display.append(f"{addon.name} (x{qty})")
            except:
                pass
        return display
    
    def calculate_price(self):
        """Calculate total price including variant, attributes, and addons"""
        from apps.products.models import ProductAttributeOption, ProductAddon
        from decimal import Decimal
        
        # Start with product base price or sale price
        price = self.product.current_price
        
        # Add variant price adjustment
        if self.variant:
            price += self.variant.price_adjustment
        
        self.base_price = price
        
        # Calculate attributes price adjustment
        attr_price = Decimal('0')
        for opt_id in self.selected_attributes.values():
            try:
                opt = ProductAttributeOption.objects.get(id=opt_id)
                attr_price += opt.price_adjustment
            except:
                pass
        self.attributes_price = attr_price
        
        # Calculate addons price
        addon_price = Decimal('0')
        for addon_item in self.selected_addons:
            try:
                addon = ProductAddon.objects.get(id=addon_item.get('addon_id'))
                qty = addon_item.get('quantity', 1)
                addon_price += addon.price * qty
            except:
                pass
        self.addons_price = addon_price
        
        # Final unit price
        self.unit_price = self.base_price + self.attributes_price + self.addons_price
        self.save()
        
        return self.unit_price
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
