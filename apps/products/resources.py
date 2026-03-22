from import_export import resources
from .models import (
    Product,
    Category,
    ProductVariant,
    ProductReview,
    ProductAttribute,
    ProductAttributeOption,
    ProductAttributeMapping,
    ProductAddon,
)


class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'category__name', 'base_price', 'sale_price', 
                  'stock_quantity', 'is_available', 'is_featured', 'is_bestseller',
                  'weight', 'serving_size', 'created_at', 'updated_at')
        export_order = fields


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'is_active', 'order')
        export_order = fields


class ProductAttributeResource(resources.ModelResource):
    class Meta:
        model = ProductAttribute
        fields = ('id', 'name', 'slug', 'description', 'is_required', 'order')
        export_order = fields


class ProductAttributeOptionResource(resources.ModelResource):
    class Meta:
        model = ProductAttributeOption
        fields = ('id', 'attribute__name', 'name', 'price_adjustment', 'is_available', 'order')
        export_order = fields


class ProductAddonResource(resources.ModelResource):
    class Meta:
        model = ProductAddon
        fields = ('id', 'name', 'slug', 'description', 'price', 'is_free', 'max_quantity', 'is_available', 'order')
        export_order = fields


class ProductVariantResource(resources.ModelResource):
    class Meta:
        model = ProductVariant
        fields = ('id', 'product__name', 'name', 'weight', 'price_adjustment', 'stock_quantity', 'is_default', 'order')
        export_order = fields


class ProductReviewResource(resources.ModelResource):
    class Meta:
        model = ProductReview
        fields = ('id', 'product__name', 'user__email', 'guest_name', 'rating', 'title', 'is_approved', 'is_verified_purchase', 'created_at')
        export_order = fields


class ProductAttributeMappingResource(resources.ModelResource):
    class Meta:
        model = ProductAttributeMapping
        fields = ('id', 'product__name', 'attribute__name', 'default_option__name', 'is_required', 'order')
        export_order = fields
