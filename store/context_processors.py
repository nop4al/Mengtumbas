from .models import Cart, Category, Wishlist

def cart_context(request):
    """
    Context processor untuk menampilkan cart info dan kategori di semua template
    Implementasi Observer pattern untuk cart updates dengan guest support
    """
    cart_items_count = 0
    wishlist_count = 0
    
    if request.user.is_authenticated:
        try:
            # First, make sure the user has a customer profile
            from .models import Customer
            customer, created = Customer.objects.get_or_create(user=request.user)
            
            # Now safely get the cart
            cart = Cart.objects.get(customer=customer)
            cart_items_count = cart.get_total_items()
            
            # Get wishlist count
            try:
                wishlist, created = Wishlist.objects.get_or_create(customer=customer)
                wishlist_count = wishlist.products.count()
            except Exception:
                wishlist_count = 0
        except Cart.DoesNotExist:
            cart_items_count = 0
    else:
        # Handle guest cart
        guest_cart = request.session.get('guest_cart', {})
        cart_items_count = guest_cart.get('total_items', 0)
    
    # Tambahkan kategori untuk navigasi
    categories = Category.objects.filter(
        is_active=True,
        parent__isnull=True  # Hanya kategori utama
    ).order_by('origin_type', 'name')
    
    return {
        'cart_items_count': cart_items_count,
        'cart_count': cart_items_count,
        'wishlist_count': wishlist_count,
        'categories': categories
    }
