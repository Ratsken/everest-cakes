from import_export import resources
from .models import User, SiteSetting, Page, HeroSection, FeaturedCard, Testimonial


class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'phone_number',
            'is_verified', 'newsletter_subscribed', 'receive_promotions',
            'is_active', 'is_staff', 'created_at', 'updated_at'
        )
        export_order = fields


class SiteSettingResource(resources.ModelResource):
    class Meta:
        model = SiteSetting
        fields = (
            'id', 'site_name', 'site_description', 'phone_primary', 'phone_secondary',
            'email', 'address', 'whatsapp_number', 'facebook_url', 'instagram_url',
            'threads_url', 'twitter_url', 'tiktok_url', 'free_delivery_threshold',
            'delivery_fee', 'created_at', 'updated_at'
        )
        export_order = fields


class PageResource(resources.ModelResource):
    class Meta:
        model = Page
        fields = (
            'id', 'title', 'slug', 'meta_description', 'meta_keywords',
            'is_published', 'show_in_footer', 'order', 'created_at', 'updated_at'
        )
        export_order = fields


class HeroSectionResource(resources.ModelResource):
    class Meta:
        model = HeroSection
        fields = (
            'id', 'title', 'subtitle', 'description', 'linked_category__name',
            'background_type', 'gradient_start', 'gradient_end', 'slider_interval',
            'title_animation', 'content_animation', 'animation_delay', 'cta_text',
            'cta_link', 'secondary_cta_text', 'secondary_cta_link', 'show_overlay',
            'overlay_opacity', 'is_active', 'order', 'created_at', 'updated_at'
        )
        export_order = fields


class FeaturedCardResource(resources.ModelResource):
    class Meta:
        model = FeaturedCard
        fields = (
            'id', 'title', 'subtitle', 'description', 'icon', 'link',
            'animation_type', 'background_color', 'text_color', 'border_color',
            'is_active', 'show_on_homepage', 'order', 'created_at', 'updated_at'
        )
        export_order = fields


class TestimonialResource(resources.ModelResource):
    class Meta:
        model = Testimonial
        fields = (
            'id', 'customer_name', 'rating', 'comment', 'occasion', 'location',
            'is_verified', 'is_featured', 'is_active', 'created_at'
        )
        export_order = fields
