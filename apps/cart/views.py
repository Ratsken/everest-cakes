from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from decimal import Decimal
import json

from .models import Cart, CartItem
from apps.products.models import Product, ProductVariant, ProductAttributeOption, ProductAddon


def get_or_create_cart(request):
    """Get or create cart for current user/session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            defaults={'session_key': request.session.session_key}
        )
        # Merge session cart if exists
        session_key = request.session.session_key
        if session_key and not created:
            session_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
            if session_cart:
                for item in session_cart.items.all():
                    cart_item, created = CartItem.objects.get_or_create(
                        cart=cart,
                        product=item.product,
                        variant=item.variant,
                        defaults={
                            'quantity': item.quantity,
                            'base_price': item.base_price,
                            'selected_attributes': item.selected_attributes,
                            'selected_addons': item.selected_addons,
                            'attributes_price': item.attributes_price,
                            'addons_price': item.addons_price,
                            'unit_price': item.unit_price,
                            'custom_message': item.custom_message,
                            'special_instructions': item.special_instructions,
                        }
                    )
                    if not created:
                        cart_item.quantity += item.quantity
                        cart_item.save()
                session_cart.delete()
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(
            session_key=request.session.session_key,
            user=None
        )
    return cart


@require_POST
def add_to_cart(request):
    """Add item to cart with attributes and addons (HTMX endpoint)"""
    product_id = request.POST.get('product_id')
    variant_id = request.POST.get('variant_id')
    quantity = int(request.POST.get('quantity', 1))
    custom_message = request.POST.get('custom_message', '')
    special_instructions = request.POST.get('special_instructions', '')
    
    # Get selected attributes
    selected_attributes = {}
    for key, value in request.POST.items():
        if key.startswith('attr_'):
            attr_id = key.replace('attr_', '')
            selected_attributes[attr_id] = value
    
    # Get selected addons
    selected_addons = []
    for key, value in request.POST.items():
        if key.startswith('addon_') and value:
            addon_id = key.replace('addon_', '')
            addon_qty = int(request.POST.get(f'addon_qty_{addon_id}', 1))
            selected_addons.append({
                'addon_id': addon_id,
                'quantity': addon_qty
            })
    
    product = get_object_or_404(Product, id=product_id, is_available=True)
    variant = None
    
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id)
    
    cart = get_or_create_cart(request)
    
    # Create cart item
    cart_item = CartItem(
        cart=cart,
        product=product,
        variant=variant,
        quantity=quantity,
        selected_attributes=selected_attributes,
        selected_addons=selected_addons,
        custom_message=custom_message,
        special_instructions=special_instructions,
    )
    
    # Calculate price
    cart_item.calculate_price()
    
    # Check if same item exists (same product, variant, attributes, addons)
    existing_item = None
    for item in cart.items.all():
        if (item.product == product and 
            item.variant == variant and
            item.selected_attributes == selected_attributes and
            item.selected_addons == selected_addons):
            existing_item = item
            break
    
    if existing_item:
        existing_item.quantity += quantity
        existing_item.save()
    else:
        cart_item.save()
    
    if request.htmx:
        return render(request, 'cart/partials/cart_sidebar.html', {'cart': cart, 'added': True})
    
    return JsonResponse({
        'success': True,
        'cart_count': cart.total_items,
        'message': f'{product.name} added to cart'
    })


@require_POST
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        cart_item.delete()
    else:
        cart_item.quantity = min(quantity, cart_item.product.max_order_quantity)
        cart_item.save()
    
    cart = cart_item.cart
    
    if request.htmx:
        return render(request, 'cart/partials/cart_sidebar.html', {'cart': cart})
    
    return JsonResponse({
        'success': True,
        'cart_count': cart.total_items if cart else 0
    })


@require_POST
def remove_cart_item(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = cart_item.cart
    cart_item.delete()
    
    if request.htmx:
        return render(request, 'cart/partials/cart_sidebar.html', {'cart': cart})
    
    return JsonResponse({
        'success': True,
        'cart_count': cart.total_items if cart else 0
    })


@require_GET
def cart_sidebar(request):
    """Get cart sidebar content (HTMX)"""
    cart = get_or_create_cart(request)
    return render(request, 'cart/partials/cart_sidebar.html', {'cart': cart})


@require_GET
def cart_count(request):
    """Get cart item count (for badge)"""
    cart = get_or_create_cart(request)
    return JsonResponse({'count': cart.total_items})


def cart_view(request):
    """Full cart page"""
    cart = get_or_create_cart(request)
    return render(request, 'cart/cart.html', {'cart': cart})


@require_POST
def update_item_attributes(request, item_id):
    """Update cart item attributes/addons"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    # Get selected attributes
    selected_attributes = {}
    for key, value in request.POST.items():
        if key.startswith('attr_'):
            attr_id = key.replace('attr_', '')
            selected_attributes[attr_id] = value
    
    # Get selected addons
    selected_addons = []
    for key, value in request.POST.items():
        if key.startswith('addon_') and value:
            addon_id = key.replace('addon_', '')
            addon_qty = int(request.POST.get(f'addon_qty_{addon_id}', 1))
            selected_addons.append({
                'addon_id': addon_id,
                'quantity': addon_qty
            })
    
    cart_item.selected_attributes = selected_attributes
    cart_item.selected_addons = selected_addons
    cart_item.custom_message = request.POST.get('custom_message', '')
    cart_item.special_instructions = request.POST.get('special_instructions', '')
    cart_item.calculate_price()
    
    cart = cart_item.cart
    
    if request.htmx:
        return render(request, 'cart/partials/cart_sidebar.html', {'cart': cart})
    
    return JsonResponse({
        'success': True,
        'new_price': str(cart_item.unit_price)
    })


@require_POST
def apply_coupon(request):
    """Apply coupon code"""
    code = request.POST.get('coupon_code', '').strip().upper()
    cart = get_or_create_cart(request)
    
    from apps.core.models import SiteSetting
    settings = SiteSetting.get_settings()
    promo_codes = settings.promo_codes if hasattr(settings, 'promo_codes') else {}
    
    if code in promo_codes:
        discount = promo_codes[code]
        request.session['coupon_code'] = code
        request.session['coupon_discount'] = discount
        messages.success(request, f'Coupon applied! {discount}% discount')
    else:
        messages.error(request, 'Invalid coupon code')
    
    if request.htmx:
        return render(request, 'cart/partials/cart_summary.html', {'cart': cart})
    
    return redirect('cart:view')


def clear_cart(request):
    """Clear all items from cart"""
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    messages.success(request, 'Cart cleared')
    
    if request.htmx:
        return render(request, 'cart/partials/cart_sidebar.html', {'cart': cart})
    
    return redirect('cart:view')


@require_GET
def get_product_price(request):
    """Calculate product price with attributes and addons (AJAX)"""
    product_id = request.GET.get('product_id')
    variant_id = request.GET.get('variant_id')
    
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    
    # Base price
    price = product.current_price
    
    # Variant adjustment
    if variant_id:
        try:
            variant = ProductVariant.objects.get(id=variant_id)
            price += variant.price_adjustment
        except ProductVariant.DoesNotExist:
            pass
    
    # Attribute adjustments
    for key, value in request.GET.items():
        if key.startswith('attr_'):
            try:
                option = ProductAttributeOption.objects.get(id=value)
                price += option.price_adjustment
            except ProductAttributeOption.DoesNotExist:
                pass
    
    # Addon prices
    addons_total = Decimal('0')
    addons_display = []
    for key, value in request.GET.items():
        if key.startswith('addon_') and value:
            addon_id = key.replace('addon_', '')
            qty = int(request.GET.get(f'addon_qty_{addon_id}', 1))
            try:
                addon = ProductAddon.objects.get(id=addon_id)
                addons_total += addon.price * qty
                addons_display.append({
                    'name': addon.name,
                    'quantity': qty,
                    'price': str(addon.price),
                    'total': str(addon.price * qty)
                })
            except ProductAddon.DoesNotExist:
                pass
    
    total_price = price + addons_total
    
    return JsonResponse({
        'base_price': str(price),
        'addons_total': str(addons_total),
        'total_price': str(total_price),
        'addons': addons_display
    })
