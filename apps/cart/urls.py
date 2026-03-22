from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name='view'),
    path('add/', views.add_to_cart, name='add'),
    path('item/<uuid:item_id>/update/', views.update_cart_item, name='update_item'),
    path('item/<uuid:item_id>/remove/', views.remove_cart_item, name='remove_item'),
    path('item/<uuid:item_id>/attributes/', views.update_item_attributes, name='update_attributes'),
    path('sidebar/', views.cart_sidebar, name='sidebar'),
    path('count/', views.cart_count, name='count'),
    path('price/', views.get_product_price, name='get_price'),
    path('coupon/', views.apply_coupon, name='apply_coupon'),
    path('clear/', views.clear_cart, name='clear'),
]
