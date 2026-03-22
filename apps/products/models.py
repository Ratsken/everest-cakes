from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from taggit.managers import TaggableManager
import uuid


class Category(models.Model):
    """Product Category"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Lucide icon name")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:category', args=[self.slug])
    
    @property
    def product_count(self):
        return self.products.filter(is_available=True).count()


class ProductAttribute(models.Model):
    """Product Attributes like Flavor, Frosting, Shape, etc."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text="e.g., 'Flavor', 'Frosting Type', 'Shape'")
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_required = models.BooleanField(default=True, help_text="Customer must select an option")
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Product Attribute'
        verbose_name_plural = 'Product Attributes'
    
    def __str__(self):
        return self.name


class ProductAttributeOption(models.Model):
    """Options for each attribute"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=100, help_text="e.g., 'Chocolate', 'Vanilla', 'Red Velvet'")
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Additional cost for this option")
    is_available = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        if self.price_adjustment > 0:
            return f"{self.name} (+KSh {self.price_adjustment})"
        return self.name


class ProductAttributeMapping(models.Model):
    """Maps attributes to specific products"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='attribute_mappings')
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE)
    available_options = models.ManyToManyField(ProductAttributeOption, blank=True, help_text="Leave empty for all options")
    default_option = models.ForeignKey(ProductAttributeOption, on_delete=models.SET_NULL, null=True, blank=True, related_name='default_for')
    is_required = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        unique_together = ['product', 'attribute']
        verbose_name = 'Product Attribute Mapping'
    
    def __str__(self):
        return f"{self.product.name} - {self.attribute.name}"
    
    def get_options(self):
        if self.available_options.exists():
            return self.available_options.filter(is_available=True)
        return self.attribute.options.filter(is_available=True)


class ProductAddon(models.Model):
    """Product Addons - Extra items like candles, message cards, decorations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text="e.g., 'Birthday Candles', 'Message Card', 'Gift Box'")
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="0 for free addons")
    is_free = models.BooleanField(default=False, help_text="Mark as free addon")
    image = models.ImageField(upload_to='addons/', blank=True)
    max_quantity = models.IntegerField(default=5, help_text="Maximum quantity per order")
    is_available = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Product Addon'
        verbose_name_plural = 'Product Addons'
    
    def __str__(self):
        if self.is_free or self.price == 0:
            return f"{self.name} (Free)"
        return f"{self.name} (KSh {self.price})"
    
    @property
    def display_price(self):
        if self.is_free or self.price == 0:
            return "Free"
        return f"KSh {self.price}"


class Product(models.Model):
    """Product Model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    
    # Category & Tags
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    tags = TaggableManager(blank=True)
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Images
    featured_image = models.ImageField(upload_to='products/')
    image_2 = models.ImageField(upload_to='products/', blank=True)
    image_3 = models.ImageField(upload_to='products/', blank=True)
    image_4 = models.ImageField(upload_to='products/', blank=True)
    
    # Stock & Availability
    stock_quantity = models.IntegerField(default=0)
    min_order_quantity = models.IntegerField(default=1)
    max_order_quantity = models.IntegerField(default=10)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    
    # Dimensions
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    serving_size = models.CharField(max_length=50, blank=True, help_text="e.g., 'Serves 10-12'")
    
    # Attributes & Addons
    attributes = models.ManyToManyField(ProductAttribute, through=ProductAttributeMapping, blank=True)
    addons = models.ManyToManyField(ProductAddon, blank=True, help_text="Available addons for this product")
    enable_custom_message = models.BooleanField(default=True, help_text="Allow custom message on cake")
    max_message_length = models.IntegerField(default=50, help_text="Maximum characters for cake message")
    
    # Lead Time
    min_lead_time = models.IntegerField(default=24, help_text="Minimum hours before delivery")
    max_lead_time = models.IntegerField(default=72, help_text="Maximum hours for advance order")
    
    # Ratings
    average_rating = models.FloatField(default=0)
    review_count = models.IntegerField(default=0)
    
    # Social Sharing
    og_title = models.CharField(max_length=200, blank=True)
    og_description = models.TextField(blank=True)
    og_image = models.ImageField(upload_to='products/social/', blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['is_featured', 'is_available']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:detail', args=[self.slug])
    
    @property
    def current_price(self):
        return self.sale_price if self.sale_price else self.base_price
    
    @property
    def discount_percentage(self):
        if self.sale_price and self.base_price:
            return int((1 - self.sale_price / self.base_price) * 100)
        return 0
    
    @property
    def stock_status(self):
        if self.stock_quantity <= 0:
            return 'out_of_stock'
        elif self.stock_quantity <= 10:
            return 'low_stock'
        return 'in_stock'
    
    @property
    def all_images(self):
        images = []
        if self.featured_image:
            images.append(self.featured_image.url)
        if self.image_2:
            images.append(self.image_2.url)
        if self.image_3:
            images.append(self.image_3.url)
        if self.image_4:
            images.append(self.image_4.url)
        return images
    
    def get_attributes(self):
        """Get all attributes with their options for this product"""
        return self.attribute_mappings.select_related('attribute').prefetch_related('available_options')
    
    def get_addons(self):
        """Get available addons for this product"""
        return self.addons.filter(is_available=True).order_by('order')
    
    def update_rating(self):
        reviews = self.reviews.all()
        if reviews:
            self.average_rating = sum(r.rating for r in reviews) / len(reviews)
            self.review_count = len(reviews)
        else:
            self.average_rating = 0
            self.review_count = 0
        self.save(update_fields=['average_rating', 'review_count'])


class ProductVariant(models.Model):
    """Product Variants (Size, Weight, etc.)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100, help_text="e.g., 'Small', 'Medium', 'Large'")
    weight = models.CharField(max_length=50, blank=True, help_text="e.g., '1kg', '2kg'")
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Price adjustment from base price")
    stock_quantity = models.IntegerField(default=0)
    is_default = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'price_adjustment']
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"
    
    @property
    def final_price(self):
        return self.product.base_price + self.price_adjustment


class ProductReview(models.Model):
    """Customer Reviews"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('core.User', on_delete=models.CASCADE, null=True, blank=True)
    guest_name = models.CharField(max_length=200, blank=True)
    guest_email = models.EmailField(blank=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.rating} stars"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.update_rating()
    
    def delete(self, *args, **kwargs):
        product = self.product
        super().delete(*args, **kwargs)
        product.update_rating()
