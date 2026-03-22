from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='list'),
    path('filter/', views.product_filter, name='filter'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='detail'),
    path('<slug:slug>/review/', views.submit_review, name='submit_review'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
]
