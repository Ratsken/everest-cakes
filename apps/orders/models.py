from django.db import models
from django.db import transaction
from django.db.models import F
from django.conf import settings
from django.utils import timezone
import uuid
import random
import string


def generate_order_number():
    """Generate unique order number"""
    prefix = 'EC'
    timestamp = timezone.now().strftime('%y%m%d')
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}-{timestamp}-{random_chars}"


def order_attachment_upload_path(instance, filename):
    """Generate upload path for order attachments"""
    return f'orders/{instance.order.order_number}/{filename}'


class Order(models.Model):
    """Order Model"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('ready', 'Ready for Delivery'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash on Delivery'),
        ('cod', 'Cash on Delivery'),
        ('mpesa', 'M-Pesa'),
        ('card', 'Card Payment'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    # Order Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=20, unique=True, default=generate_order_number)
    
    # Customer Info
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    
    # Delivery Info
    delivery_address = models.TextField()
    delivery_city = models.CharField(max_length=100)
    delivery_date = models.DateField()
    delivery_time_slot = models.CharField(max_length=50, blank=True)
    delivery_instructions = models.TextField(blank=True)
    
    # Recipient Info (if different from customer)
    recipient_name = models.CharField(max_length=200, blank=True)
    recipient_phone = models.CharField(max_length=15, blank=True)
    gift_message = models.TextField(blank=True)
    is_gift = models.BooleanField(default=False)
    
    # Order Items (stored as JSON for flexibility)
    # Each item includes: product_id, name, variant_id, variant_name, quantity, 
    # base_price, attributes (list), addons (list), attributes_price, addons_price,
    # unit_price, total_price, custom_message, special_instructions
    items = models.JSONField(default=list)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_reference = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, help_text='Customer notes')
    internal_notes = models.TextField(blank=True, help_text='Admin only notes')
    
    # Notification Status
    email_sent = models.BooleanField(default=False)
    whatsapp_sent = models.BooleanField(default=False)
    stock_deducted = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['status']),
            models.Index(fields=['customer_phone']),
            models.Index(fields=['delivery_date']),
        ]
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    @property
    def item_count(self):
        return sum(item.get('quantity', 0) for item in self.items)
    
    @property
    def items_summary(self):
        """Generate a text summary of items for notifications"""
        summary = []
        for item in self.items:
            text = f"• {item.get('quantity', 1)}x {item.get('name', 'Product')}"
            if item.get('variant_name'):
                text += f" ({item['variant_name']})"
            text += f" - KSh {item.get('total_price', 0)}"
            
            # Add attributes
            attrs = item.get('attributes', [])
            if attrs:
                attr_text = ", ".join([f"{a['attribute']}: {a['option']}" for a in attrs])
                text += f"\n  [{attr_text}]"
            
            # Add addons
            addons = item.get('addons', [])
            if addons:
                addon_text = ", ".join([f"{a['name']} (x{a['quantity']})" for a in addons])
                text += f"\n  [+{addon_text}]"
            
            # Add custom message
            if item.get('custom_message'):
                text += f"\n  Message: \"{item['custom_message']}\""
            
            summary.append(text)
        return "\n".join(summary)
    
    def mark_paid(self, reference=''):
        self.payment_status = 'completed'
        self.payment_reference = reference
        self.paid_at = timezone.now()
        self.save()
    
    def confirm(self):
        self.status = 'confirmed'
        self.save()

    def deduct_stock_once(self):
        """Deduct stock for order items exactly once."""
        if self.stock_deducted:
            return

        from apps.products.models import Product, ProductVariant

        with transaction.atomic():
            locked_order = Order.objects.select_for_update().get(pk=self.pk)
            if locked_order.stock_deducted:
                return

            touched_product_ids = set()

            for item in locked_order.items:
                quantity = int(item.get('quantity') or 0)
                if quantity <= 0:
                    continue

                product_id = item.get('product_id')
                variant_id = item.get('variant_id')

                if product_id:
                    Product.objects.filter(id=product_id).update(stock_quantity=F('stock_quantity') - quantity)
                    Product.objects.filter(id=product_id, stock_quantity__lt=0).update(stock_quantity=0)
                    touched_product_ids.add(product_id)

                if variant_id:
                    ProductVariant.objects.filter(id=variant_id).update(stock_quantity=F('stock_quantity') - quantity)
                    ProductVariant.objects.filter(id=variant_id, stock_quantity__lt=0).update(stock_quantity=0)

            for product_id in touched_product_ids:
                product = Product.objects.filter(id=product_id).first()
                if product and product.stock_quantity <= 0 and product.is_available:
                    product.is_available = False
                    product.save(update_fields=['is_available'])

            locked_order.stock_deducted = True
            locked_order.save(update_fields=['stock_deducted'])
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('orders:detail', args=[self.order_number])


class OrderAttachment(models.Model):
    """Order Attachments - Images and Videos"""
    ATTACHMENT_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='attachments')
    attachment_type = models.CharField(max_length=10, choices=ATTACHMENT_TYPE_CHOICES, default='image')
    file = models.FileField(upload_to=order_attachment_upload_path)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.attachment_type}"


class OrderTracking(models.Model):
    """Order Status Tracking"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking')
    status = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.status}"


class PaymentTransaction(models.Model):
    """Payment Transaction Log"""
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('timeout', 'Timeout'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')
    provider = models.CharField(max_length=20)  # mpesa, card, etc.
    transaction_id = models.CharField(max_length=100, blank=True)
    checkout_request_id = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    response_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.provider} - {self.status}"


class Enquiry(models.Model):
    """Customer Enquiries/Contact Form Submissions"""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('spam', 'Spam'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # For product-specific enquiries
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Attachments
    image = models.ImageField(upload_to='enquiries/', blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    notes = models.TextField(blank=True, help_text='Admin notes')
    
    # Notifications
    email_sent = models.BooleanField(default=False)
    whatsapp_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Enquiry'
        verbose_name_plural = 'Enquiries'
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
