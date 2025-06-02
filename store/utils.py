from django.contrib.auth.models import User
from .models import Customer

def ensure_customer_exists(user):
    """
    Helper function to ensure a Customer profile exists for a User
    Returns the Customer instance
    """
    if not user or not user.is_authenticated:
        return None
        
    try:
        customer = user.customer
    except Customer.DoesNotExist:
        customer = Customer.objects.create(user=user)
        
    return customer
