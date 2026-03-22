from django.contrib import admin
from unfold.admin import ModelAdmin
from import_export.admin import ImportExportModelAdmin
from .models import Cart, CartItem
from .resources import CartResource, CartItemResource


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['product', 'variant', 'quantity', 'unit_price', 'total_price']


@admin.register(Cart)
class CartAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = CartResource
    list_display = ['id', 'user', 'session_key', 'total_items', 'total', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'session_key']
    readonly_fields = ['created_at', 'updated_at', 'total_items', 'subtotal', 'delivery_fee', 'total']
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = CartItemResource
    list_display = ['cart', 'product', 'variant', 'quantity', 'unit_price', 'total_price']
    list_filter = ['product', 'variant']
