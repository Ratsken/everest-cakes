from django.utils import timezone
from datetime import timedelta


def clean_expired_carts():
    """Remove expired carts older than 30 days"""
    from .models import Cart
    
    cutoff = timezone.now() - timedelta(days=30)
    expired_carts = Cart.objects.filter(
        updated_at__lt=cutoff,
        user__isnull=True
    )
    count = expired_carts.count()
    expired_carts.delete()
    
    return f"Deleted {count} expired carts"
