from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.urls import reverse
import uuid


class User(AbstractUser):
    """Custom User Model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?254[0-9]{9}$', message='Enter a valid Kenyan phone number')],
        blank=True
    )
    is_verified = models.BooleanField(default=False)
    
    # Preferences
    newsletter_subscribed = models.BooleanField(default=True)
    receive_promotions = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
        ]
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username


class SiteSetting(models.Model):
    """Site-wide settings"""
    site_name = models.CharField(max_length=100, default='Everest Cakes')
    site_description = models.TextField(blank=True, default='Bespoke, artisanal cakes for every occasion in Thika.')
    site_logo = models.ImageField(upload_to='settings/', blank=True)
    favicon = models.ImageField(upload_to='settings/', blank=True)
    
    # Contact Info
    phone_primary = models.CharField(max_length=15, default='+254700000000')
    phone_secondary = models.CharField(max_length=15, blank=True)
    email = models.EmailField(default='hello@everestcakes.co.ke')
    address = models.TextField(default='Thika, Kenya')
    whatsapp_number = models.CharField(max_length=15, default='+254700000000')
    
    # Business Hours
    monday_friday = models.CharField(max_length=50, default='8:00 AM - 7:00 PM')
    saturday = models.CharField(max_length=50, default='8:00 AM - 7:00 PM')
    sunday = models.CharField(max_length=50, default='10:00 AM - 4:00 PM')
    
    # Social Links
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)
    
    # Delivery Settings
    free_delivery_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=5000)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=300)
    
    # SEO
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=500, blank=True)
    google_analytics_id = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return self.site_name
    
    @classmethod
    def get_settings(cls):
        settings, _ = cls.objects.get_or_create(pk=1)
        return settings


class Page(models.Model):
    """CMS Pages"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=200, blank=True)
    is_published = models.BooleanField(default=True)
    show_in_footer = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('core:page', args=[self.slug])


class HeroSection(models.Model):
    """Animated Hero Sections - controlled from admin"""
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    
    # Background Options
    BACKGROUND_TYPE_CHOICES = [
        ('image', 'Background Image'),
        ('video', 'Background Video'),
        ('gradient', 'Gradient'),
        ('slider', 'Image Slider'),
    ]
    background_type = models.CharField(max_length=20, choices=BACKGROUND_TYPE_CHOICES, default='image')
    background_image = models.ImageField(upload_to='hero/', blank=True)
    background_video = models.FileField(upload_to='hero/', blank=True)
    gradient_start = models.CharField(max_length=20, default='#1A1A1A')
    gradient_end = models.CharField(max_length=20, default='#2D2D2D')
    
    # Slider Images (JSON array of image URLs)
    slider_images = models.JSONField(default=list, blank=True)
    slider_interval = models.IntegerField(default=5000, help_text='Slider interval in milliseconds')
    
    # Animation Settings
    ANIMATION_TYPE_CHOICES = [
        ('fade', 'Fade In'),
        ('slide', 'Slide Up'),
        ('zoom', 'Zoom In'),
        ('typewriter', 'Typewriter'),
        ('none', 'No Animation'),
    ]
    title_animation = models.CharField(max_length=20, choices=ANIMATION_TYPE_CHOICES, default='fade')
    content_animation = models.CharField(max_length=20, choices=ANIMATION_TYPE_CHOICES, default='slide')
    animation_delay = models.IntegerField(default=200, help_text='Animation delay in milliseconds')
    
    # Call to Action
    cta_text = models.CharField(max_length=100, blank=True)
    cta_link = models.CharField(max_length=200, blank=True)
    cta_style = models.CharField(max_length=50, default='bg-gold text-charcoal hover:bg-gold/90')
    secondary_cta_text = models.CharField(max_length=100, blank=True)
    secondary_cta_link = models.CharField(max_length=200, blank=True)
    
    # Overlay
    show_overlay = models.BooleanField(default=True)
    overlay_opacity = models.IntegerField(default=40, help_text='Overlay opacity percentage (0-100)')
    
    # Status
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Hero Section'
        verbose_name_plural = 'Hero Sections'
    
    def __str__(self):
        return self.title


class FeaturedCard(models.Model):
    """Animated Featured Cards - controlled from admin"""
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    
    # Card Image/Icon
    image = models.ImageField(upload_to='cards/', blank=True)
    icon = models.CharField(max_length=100, blank=True, help_text='Lucide icon name (e.g., cake, star, gift)')
    
    # Link
    link = models.CharField(max_length=200, blank=True)
    
    # Animation
    ANIMATION_CHOICES = [
        ('hover-lift', 'Lift on Hover'),
        ('hover-scale', 'Scale on Hover'),
        ('hover-glow', 'Glow on Hover'),
        ('pulse', 'Pulsing'),
        ('float', 'Floating'),
        ('none', 'No Animation'),
    ]
    animation_type = models.CharField(max_length=20, choices=ANIMATION_CHOICES, default='hover-lift')
    
    # Styling
    background_color = models.CharField(max_length=30, default='#FFFFFF')
    text_color = models.CharField(max_length=30, default='#1A1A1A')
    border_color = models.CharField(max_length=30, default='#E5E7EB')
    
    # Status
    is_active = models.BooleanField(default=True)
    show_on_homepage = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Featured Card'
        verbose_name_plural = 'Featured Cards'
    
    def __str__(self):
        return self.title


class Testimonial(models.Model):
    """Customer Testimonials"""
    customer_name = models.CharField(max_length=200)
    customer_photo = models.ImageField(upload_to='testimonials/', blank=True)
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    occasion = models.CharField(max_length=100, blank=True, help_text='e.g., Wedding, Birthday')
    location = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer_name} - {self.rating} stars"
