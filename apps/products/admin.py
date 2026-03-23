from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import action, display
from import_export.admin import ImportExportModelAdmin
from .models import (
    Product, Category, ProductVariant, ProductReview,
    ProductAttribute, ProductAttributeOption, ProductAttributeMapping, ProductAddon
)
from .resources import (
    ProductResource,
    CategoryResource,
    ProductVariantResource,
    ProductReviewResource,
    ProductAttributeResource,
    ProductAttributeOptionResource,
    ProductAttributeMappingResource,
    ProductAddonResource,
)


class ProductVariantInline(TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['name', 'weight', 'price_adjustment', 'stock_quantity', 'is_default', 'order']


class ProductReviewInline(TabularInline):
    model = ProductReview
    extra = 0
    fields = ['user', 'guest_name', 'rating', 'title', 'comment', 'is_approved']
    readonly_fields = ['user', 'guest_name', 'rating', 'title', 'comment']
    can_delete = True


class ProductAttributeMappingInline(TabularInline):
    model = ProductAttributeMapping
    extra = 1
    fields = ['attribute', 'is_required', 'default_option', 'order']
    autocomplete_fields = ['attribute', 'default_option']


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = CategoryResource
    list_display = ['name', 'slug', 'product_count_display', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ['name']}
    list_editable = ['order', 'is_active']
    
    @display(description='Products')
    def product_count_display(self, obj):
        count = obj.products.count()
        return format_html(
            '<a href="/admin/products/product/?category__id__exact={}" class="text-primary-600">{}</a>',
            obj.id, count
        )


class ProductAttributeOptionInline(TabularInline):
    model = ProductAttributeOption
    extra = 2
    fields = ['name', 'price_adjustment', 'is_available', 'order']


@admin.register(ProductAttribute)
class ProductAttributeAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = ProductAttributeResource
    list_display = ['name', 'slug', 'is_required', 'option_count', 'order']
    list_editable = ['order', 'is_required']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ['name']}
    inlines = [ProductAttributeOptionInline]
    
    @display(description='Options')
    def option_count(self, obj):
        return obj.options.count()


@admin.register(ProductAttributeOption)
class ProductAttributeOptionAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = ProductAttributeOptionResource
    list_display = ['name', 'attribute', 'price_adjustment', 'is_available', 'order']
    list_filter = ['attribute', 'is_available']
    list_editable = ['price_adjustment', 'is_available', 'order']
    search_fields = ['name', 'attribute__name']


@admin.register(ProductAddon)
class ProductAddonAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = ProductAddonResource
    list_display = ['name', 'slug', 'price', 'is_free', 'is_available', 'order']
    list_filter = ['is_free', 'is_available']
    list_editable = ['price', 'is_free', 'is_available', 'order']
    prepopulated_fields = {'slug': ['name']}
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = ProductResource
    list_display = [
        'thumbnail', 'name', 'category', 'current_price_display', 
        'stock_status_badge', 'is_featured', 'is_bestseller', 'is_available'
    ]
    list_filter = ['category', 'is_featured', 'is_available', 'is_bestseller', 'is_new']
    search_fields = ['name', 'description', 'short_description']
    prepopulated_fields = {'slug': ['name']}
    list_editable = ['is_featured', 'is_bestseller', 'is_available']
    readonly_fields = ['average_rating', 'review_count', 'created_at', 'updated_at']
    filter_horizontal = ['addons']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'short_description', 'description')
        }),
        ('Pricing', {
            'fields': ('base_price', 'sale_price', 'cost_price'),
            'classes': ('tab',),
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'min_order_quantity', 'max_order_quantity', 'is_available'),
            'classes': ('tab',),
        }),
        ('Images', {
            'fields': ('featured_image', 'image_2', 'image_3', 'image_4'),
            'classes': ('tab',),
        }),
        ('Product Details', {
            'fields': ('weight', 'serving_size', 'min_lead_time', 'max_lead_time'),
            'classes': ('tab',),
        }),
        ('Attributes & Addons', {
            'fields': ('addons', 'enable_custom_message', 'max_message_length'),
            'classes': ('tab',),
        }),
        ('Social Sharing', {
            'fields': ('og_title', 'og_description', 'og_image'),
            'classes': ('tab',),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('tab',),
        }),
        ('Status Flags', {
            'fields': ('is_featured', 'is_bestseller', 'is_new', 'average_rating', 'review_count'),
            'classes': ('tab',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('tab',),
        }),
    )
    
    inlines = [ProductVariantInline, ProductAttributeMappingInline, ProductReviewInline]
    
    @display(description='Image')
    def thumbnail(self, obj):
        if obj.featured_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 8px; object-fit: cover;" />',
                obj.featured_image.url
            )
        return '-'
    
    @display(description='Price')
    def current_price_display(self, obj):
        if obj.sale_price:
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">KSh {}</span> <span style="color: #D4AF37; font-weight: bold;">KSh {}</span>',
                obj.base_price, obj.sale_price
            )
        return f"KSh {obj.base_price}"
    
    @display(description='Stock')
    def stock_status_badge(self, obj):
        status = obj.stock_status
        if status == 'out_of_stock':
            return mark_safe('<span class="bg-red-100 text-red-800 px-2 py-1 rounded text-xs font-medium">Out of Stock</span>')
        elif status == 'low_stock':
            return format_html('<span class="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-xs font-medium">Low ({})</span>', obj.stock_quantity)
        return format_html('<span class="bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-medium">In Stock ({})</span>', obj.stock_quantity)
    
    @action(description="Mark as featured", url_path="mark-featured")
    def mark_featured(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f"{count} products marked as featured.")
    
    @action(description="Mark as bestseller", url_path="mark-bestseller")
    def mark_bestseller(self, request, queryset):
        count = queryset.update(is_bestseller=True)
        self.message_user(request, f"{count} products marked as bestseller.")
    
    @action(description="Mark as new", url_path="mark-new")
    def mark_new(self, request, queryset):
        count = queryset.update(is_new=True)
        self.message_user(request, f"{count} products marked as new.")


@admin.register(ProductVariant)
class ProductVariantAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = ProductVariantResource
    list_display = ['product', 'name', 'weight', 'price_adjustment', 'stock_quantity', 'is_default']
    list_filter = ['product', 'is_default']
    search_fields = ['product__name', 'name']


@admin.register(ProductReview)
class ProductReviewAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = ProductReviewResource
    list_display = ['product', 'user_display', 'rating', 'title', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'is_verified_purchase']
    search_fields = ['product__name', 'user__email', 'guest_name', 'comment']
    list_editable = ['is_approved']
    
    @display(description='User')
    def user_display(self, obj):
        return obj.user.email if obj.user else obj.guest_name
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'user')


@admin.register(ProductAttributeMapping)
class ProductAttributeMappingAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = ProductAttributeMappingResource
    list_display = ['product', 'attribute', 'is_required', 'default_option']
    list_filter = ['attribute', 'is_required']
    search_fields = ['product__name', 'attribute__name']
    autocomplete_fields = ['product', 'attribute', 'default_option']
