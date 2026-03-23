from .models import Cart


def cart_context(request):
    """Context processor for cart"""
    cart = None
    cart_count = 0
    cart_items = []
    cart_total = 0
    
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).order_by('-updated_at').first()
    else:
        session_key = request.session.session_key
        if session_key:
            cart = Cart.objects.filter(session_key=session_key, user__isnull=True).order_by('-updated_at').first()
    
    if cart:
        cart_count = cart.total_items
        cart_items = cart.items.select_related('product', 'variant').all()
        cart_total = cart.subtotal
    
    return {
        'cart': cart,
        'cart_count': cart_count,
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
