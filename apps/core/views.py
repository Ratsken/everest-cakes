from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Q, Min

from .models import Page, HeroSection, FeaturedCard, Testimonial
from apps.products.models import Product, Category


class HomeView(TemplateView):
    """Homepage view"""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Hero sections (animated, controlled from admin)
        context['hero_sections'] = HeroSection.objects.filter(is_active=True).order_by('order')
        context['primary_hero'] = context['hero_sections'].first()
        
        # Featured cards (animated, controlled from admin)
        context['featured_cards'] = FeaturedCard.objects.filter(
            is_active=True, 
            show_on_homepage=True
        ).order_by('order')
        
        # Featured products
        context['featured_products'] = Product.objects.filter(
            is_featured=True, 
            is_available=True
        )[:8]
        
        # Best sellers
        context['bestsellers'] = Product.objects.filter(
            is_bestseller=True, 
            is_available=True
        )[:4]
        
        # Categories — annotated with cheapest available product price
        context['categories'] = (
            Category.objects.filter(is_active=True)
            .annotate(min_price=Min('products__base_price'))
            .order_by('order')
        )

        # Primary hero's linked category min-price for the floating badge
        primary_hero = context.get('primary_hero')
        if primary_hero and primary_hero.linked_category_id:
            linked_cat = (
                Category.objects.filter(pk=primary_hero.linked_category_id)
                .annotate(min_price=Min('products__base_price'))
                .first()
            )
            context['hero_category'] = linked_cat
        else:
            context['hero_category'] = None
        
        # Testimonials
        context['testimonials'] = Testimonial.objects.filter(
            is_active=True, 
            is_featured=True
        )[:6]
        
        return context


@method_decorator(cache_page(60 * 15), name='dispatch')
class PageView(DetailView):
    """CMS Page view"""
    model = Page
    template_name = 'core/page.html'
    slug_url_kwarg = 'slug'
    context_object_name = 'page'
    
    def get_queryset(self):
        return Page.objects.filter(is_published=True)


class SearchView(ListView):
    """Search results view"""
    model = Product
    template_name = 'core/search.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        queryset = Product.objects.filter(is_available=True)
        
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(short_description__icontains=query) |
                Q(category__name__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct()
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['total_results'] = self.get_queryset().count()
        return context


@require_GET
def search_suggestions(request):
    """HTMX search suggestions endpoint"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    products = Product.objects.filter(
        is_available=True,
        name__icontains=query
    )[:5]
    
    categories = Category.objects.filter(
        is_active=True,
        name__icontains=query
    )[:3]
    
    suggestions = []
    for product in products:
        suggestions.append({
            'type': 'product',
            'name': product.name,
            'url': product.get_absolute_url(),
            'image': product.featured_image.url if product.featured_image else None,
            'price': str(product.current_price)
        })
    
    for category in categories:
        suggestions.append({
            'type': 'category',
            'name': category.name,
            'url': category.get_absolute_url(),
        })
    
    return JsonResponse({'suggestions': suggestions})


def about(request):
    """About page"""
    page = Page.objects.filter(slug='about', is_published=True).first()
    testimonials = Testimonial.objects.filter(is_active=True)[:6]
    return render(request, 'core/about.html', {'page': page, 'testimonials': testimonials})


def contact(request):
    """Contact page"""
    return render(request, 'core/contact.html')


def privacy_policy(request):
    """Privacy policy page"""
    page = get_object_or_404(Page, slug='privacy-policy', is_published=True)
    return render(request, 'core/page.html', {'page': page})


def terms_of_service(request):
    """Terms of service page"""
    page = get_object_or_404(Page, slug='terms-of-service', is_published=True)
    return render(request, 'core/page.html', {'page': page})
