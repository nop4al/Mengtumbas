from django import template
from django.utils import timezone
import pytz
from django.conf import settings
import os
from decimal import Decimal

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    return float(value) * float(arg)

@register.filter(name='to_wib')
def to_wib(dt):
    """Convert datetime to WIB timezone"""
    if not dt:
        return ''
    wib = pytz.timezone('Asia/Jakarta')
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(wib)

@register.filter(name='split')
def split(value, arg):
    """Split a string by the given delimiter"""
    return value.split(arg)

@register.filter(name='int')
def int_filter(value):
    """Convert a string to an integer"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

@register.filter(name='image_exists')
def image_exists(image_path):
    """Check if an image file exists"""
    if not image_path:
        return False
    
    # If it's already a URL, assume it exists
    if image_path.startswith('http'):
        return True
        
    # Remove the media URL prefix if present
    if image_path.startswith(settings.MEDIA_URL):
        image_path = image_path[len(settings.MEDIA_URL):]
        
    # Check if the file exists in the media root
    full_path = os.path.join(settings.MEDIA_ROOT, image_path)
    return os.path.exists(full_path)

@register.filter(name='shipping_cost')
def shipping_cost(count, rate=150000):
    """Calculate shipping cost based on item count and rate"""
    try:
        count = int(count)
        rate = Decimal(rate)
        return count * rate
    except (ValueError, TypeError):
        return Decimal('0')

@register.filter(name='count_foreign_items')
def count_foreign_items(cart_items):
    """Count the number of foreign items in the cart"""
    count = 0
    for item in cart_items:
        if hasattr(item, 'product') and hasattr(item.product, 'category') and item.product.category.origin_type == 'foreign':
            count += 1
    return count
