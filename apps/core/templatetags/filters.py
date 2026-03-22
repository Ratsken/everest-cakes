import math
from django import template

register = template.Library()


@register.filter
def floor(value):
    """
    Returns the floor of a number.
    Usage: {{ value|floor }}
    """
    try:
        return math.floor(float(value))
    except (ValueError, TypeError):
        return 0
