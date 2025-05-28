from .models import Cart

def cart_context(request):
    """
    Context processor untuk menampilkan cart info di semua template
    Implementasi Observer pattern untuk cart updates
    """
    cart_items_count = 0
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(customer=request.user.customer)
            cart_items_count = cart.get_total_items()
        except Cart.DoesNotExist:
            cart_items_count = 0
    
    return {
        'cart_items_count': cart_items_count,
    }
