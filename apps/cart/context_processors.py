from .models import Cart


def cart_context(request):
    """Context processor for cart"""
    cart = None
    cart_count = 0
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.filter(user=request.user).first()
        except Cart.DoesNotExist:
            pass
    else:
        session_key = request.session.session_key
        if session_key:
            try:
                cart = Cart.objects.filter(session_key=session_key).first()
            except Cart.DoesNotExist:
                pass
    
    if cart:
        cart_count = cart.total_items
    
    return {
        'cart': cart,
        'cart_count': cart_count,
    }
