from import_export import resources
from .models import Product, Category


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
