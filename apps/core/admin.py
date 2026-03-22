from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import action, display
from .models import User, SiteSetting, Page, HeroSection, FeaturedCard, Testimonial


def environment_callback(request):
    from django.conf import settings
    if settings.DEBUG:
        return ["Development", "warning"]
    return ["Production", "success"]


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ['email', 'full_name', 'phone_number', 'is_verified', 'is_staff', 'created_at']
    list_filter = ['is_verified', 'is_staff', 'is_active', 'newsletter_subscribed']
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('email', 'username', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'phone_number')
        }),
        ('Preferences', {
            'fields': ('newsletter_subscribed', 'receive_promotions')
        }),
        ('Status', {
            'fields': ('is_verified', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('tab',),
        }),
    )


@admin.register(SiteSetting)
class SiteSettingAdmin(ModelAdmin):
    list_display = ['site_name', 'email', 'phone_primary']
    fieldsets = (
        ('Site Information', {
            'fields': ('site_name', 'site_description', 'site_logo', 'favicon')
        }),
        ('Contact Information', {
            'fields': ('phone_primary', 'phone_secondary', 'email', 'address', 'whatsapp_number')
        }),
        ('Business Hours', {
            'fields': ('monday_friday', 'saturday', 'sunday')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'instagram_url', 'threads_url', 'twitter_url', 'tiktok_url')
        }),
        ('Delivery Settings', {
            'fields': ('free_delivery_threshold', 'delivery_fee')
        }),
        ('SEO Settings', {
            'fields': ('meta_description', 'meta_keywords', 'google_analytics_id')
        }),
    )

    def has_add_permission(self, request):
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Page)
class PageAdmin(ModelAdmin):
    list_display = ['title', 'slug', 'is_published', 'show_in_footer', 'order']
    list_filter = ['is_published', 'show_in_footer']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ['title']}
    list_editable = ['order', 'is_published', 'show_in_footer']


@admin.register(HeroSection)
class HeroSectionAdmin(ModelAdmin):
    list_display = ['title', 'background_type', 'is_active', 'order', 'preview']
    list_filter = ['background_type', 'is_active']
    list_editable = ['order', 'is_active']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'subtitle', 'description')
        }),
        ('Background', {
            'fields': ('background_type', 'background_image', 'background_video', 
                      'gradient_start', 'gradient_end', 'slider_images', 'slider_interval')
        }),
        ('Animation', {
            'fields': ('title_animation', 'content_animation', 'animation_delay')
        }),
        ('Call to Action', {
            'fields': ('cta_text', 'cta_link', 'cta_style', 
                      'secondary_cta_text', 'secondary_cta_link')
        }),
        ('Overlay', {
            'fields': ('show_overlay', 'overlay_opacity')
        }),
        ('Status', {
            'fields': ('is_active', 'order')
        }),
    )
    
    @display(description='Preview')
    def preview(self, obj):
        if obj.background_image:
            return format_html(
                '<img src="{}" width="100" height="50" style="object-fit: cover; border-radius: 4px;" />',
                obj.background_image.url
            )
        return '-'


@admin.register(FeaturedCard)
class FeaturedCardAdmin(ModelAdmin):
    list_display = ['title', 'icon', 'animation_type', 'is_active', 'show_on_homepage', 'order']
    list_filter = ['animation_type', 'is_active', 'show_on_homepage']
    list_editable = ['order', 'is_active', 'show_on_homepage']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'subtitle', 'description')
        }),
        ('Visual', {
            'fields': ('image', 'icon', 'link')
        }),
        ('Animation & Styling', {
            'fields': ('animation_type', 'background_color', 'text_color', 'border_color')
        }),
        ('Status', {
            'fields': ('is_active', 'show_on_homepage', 'order')
        }),
    )


@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin):
    list_display = ['customer_name', 'rating', 'occasion', 'is_verified', 'is_featured', 'created_at']
    list_filter = ['rating', 'is_verified', 'is_featured', 'is_active']
    search_fields = ['customer_name', 'comment']
    list_editable = ['is_verified', 'is_featured']
