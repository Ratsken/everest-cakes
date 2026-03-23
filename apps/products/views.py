from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Q
from django.core.paginator import Paginator
from decimal import Decimal, InvalidOperation
import json

from .models import Product, Category, ProductReview


class ProductListView(ListView):
    """Product listing with filtering"""
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_paginate_by(self, queryset):
        category_slug = self.request.GET.get('category')
        if category_slug in (None, '', 'all'):
            return None
        return self.paginate_by
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True).select_related('category')
        
        # Category filter
        category_slug = self.request.GET.get('category')
        if category_slug and category_slug != 'all':
            queryset = queryset.filter(category__slug=category_slug)
        
        # Price range filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        # Parse prices safely and ignore invalid values
        try:
            min_price_val = Decimal(min_price) if min_price not in (None, '') else None
        except (InvalidOperation, TypeError):
            min_price_val = None
        try:
            max_price_val = Decimal(max_price) if max_price not in (None, '') else None
        except (InvalidOperation, TypeError):
            max_price_val = None

        # If both provided and min > max, swap them
        if min_price_val is not None and max_price_val is not None and min_price_val > max_price_val:
            min_price_val, max_price_val = max_price_val, min_price_val

        if min_price_val is not None:
            queryset = queryset.filter(base_price__gte=min_price_val)
        if max_price_val is not None:
            queryset = queryset.filter(base_price__lte=max_price_val)
        
        # Features filter
        if self.request.GET.get('featured'):
            queryset = queryset.filter(is_featured=True)
        if self.request.GET.get('bestseller'):
            queryset = queryset.filter(is_bestseller=True)
        if self.request.GET.get('new'):
            queryset = queryset.filter(is_new=True)
        
        # Sort
        sort = self.request.GET.get('sort', '-created_at')
        if sort in ['name', '-name', 'base_price', '-base_price', '-created_at', '-average_rating']:
            queryset = queryset.order_by(sort)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True).order_by('order')
        current_category_slug = self.request.GET.get('category')
        context['current_category'] = current_category_slug
        if current_category_slug:
            context['category'] = Category.objects.filter(slug=current_category_slug, is_active=True).first()
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        return context


class ProductDetailView(DetailView):
    """Product detail view with social sharing metadata"""
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Product.objects.filter(is_available=True).select_related('category').prefetch_related('variants', 'reviews')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        
        # Related products
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_available=True
        ).exclude(id=product.id)[:4]
        
        # Reviews
        context['reviews'] = product.reviews.filter(is_approved=True)[:10]
        
        # Social sharing metadata
        context['og_title'] = product.og_title or product.name
        context['og_description'] = product.og_description or product.short_description or product.description[:160]
        context['og_image'] = product.og_image.url if product.og_image else (product.featured_image.url if product.featured_image else None)
        
        # Default variant
        context['default_variant'] = product.variants.filter(is_default=True).first() or product.variants.first()
        
        return context


class CategoryView(ListView):
    """Category page with products"""
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'], is_active=True)
        return Product.objects.filter(category=self.category, is_available=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.filter(is_active=True).order_by('order')
        context['current_category'] = self.category.slug
        context['current_sort'] = '-created_at'
        context['min_price'] = ''
        context['max_price'] = ''
        return context


@require_POST
def submit_review(request, slug):
    """Submit a product review"""
    product = get_object_or_404(Product, slug=slug)
    
    rating = int(request.POST.get('rating', 5))
    title = request.POST.get('title', '')
    comment = request.POST.get('comment', '')
    
    if request.user.is_authenticated:
        review, created = ProductReview.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={
                'rating': rating,
                'title': title,
                'comment': comment,
                'is_verified_purchase': True,  # Check if user has ordered this product
            }
        )
    else:
        guest_name = request.POST.get('name')
        guest_email = request.POST.get('email')
        ProductReview.objects.create(
            product=product,
            guest_name=guest_name,
            guest_email=guest_email,
            rating=rating,
            title=title,
            comment=comment
        )
    
    if request.htmx:
        reviews = product.reviews.filter(is_approved=True)
        return render(request, 'products/partials/reviews.html', {'reviews': reviews, 'product': product})
    
    return redirect(product.get_absolute_url())


@require_GET
def product_filter(request):
    """HTMX product filter endpoint"""
    queryset = Product.objects.filter(is_available=True).select_related('category')
    
    category_slug = request.GET.get('category')
    if category_slug and category_slug != 'all':
        queryset = queryset.filter(category__slug=category_slug)
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    try:
        min_price_val = Decimal(min_price) if min_price not in (None, '') else None
    except (InvalidOperation, TypeError):
        min_price_val = None
    try:
        max_price_val = Decimal(max_price) if max_price not in (None, '') else None
    except (InvalidOperation, TypeError):
        max_price_val = None

    if min_price_val is not None and max_price_val is not None and min_price_val > max_price_val:
        min_price_val, max_price_val = max_price_val, min_price_val

    if min_price_val is not None:
        queryset = queryset.filter(base_price__gte=min_price_val)
    if max_price_val is not None:
        queryset = queryset.filter(base_price__lte=max_price_val)
    
    if request.GET.get('featured'):
        queryset = queryset.filter(is_featured=True)
    if request.GET.get('bestseller'):
        queryset = queryset.filter(is_bestseller=True)
    if request.GET.get('new'):
        queryset = queryset.filter(is_new=True)
    
    sort = request.GET.get('sort', '-created_at')
    if sort in ['name', '-name', 'base_price', '-base_price', '-created_at', '-average_rating']:
        queryset = queryset.order_by(sort)
    
    if category_slug in (None, '', 'all'):
        products = queryset
    else:
        paginator = Paginator(queryset, 12)
        page = request.GET.get('page', 1)
        products = paginator.get_page(page)
    
    return render(request, 'products/partials/product_grid.html', {'products': products})
