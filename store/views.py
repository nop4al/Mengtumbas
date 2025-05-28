from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import uuid

from .models import Product, Category, Cart, CartItem, Order, OrderItem, Customer, Review
from .forms import ReviewForm

def home(request):
    """
    Homepage view dengan featured products
    Implementasi Polymorphism dalam display berbagai tipe produk
    """
    featured_products = Product.objects.filter(featured=True, is_active=True)[:8]
    categories = Category.objects.filter(is_active=True)[:6]
    latest_products = Product.objects.filter(is_active=True)[:8]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'latest_products': latest_products,
    }
    return render(request, 'store/home.html', context)

def product_list(request):
    """
    Product listing dengan filtering dan pagination
    """
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Category filtering
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Price sorting
    sort_by = request.GET.get('sort')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('name')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'current_category': category_slug,
        'current_sort': sort_by,
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, slug):
    """
    Product detail view dengan reviews
    Demonstrasi Encapsulation dalam akses product data
    """
    product = get_object_or_404(Product, slug=slug, is_active=True)
    reviews = product.reviews.filter(is_active=True)
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product.id)[:4]
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    # Check if user already reviewed this product
    user_review = None
    if request.user.is_authenticated:
        try:
            user_review = reviews.get(customer__user=request.user)
        except Review.DoesNotExist:
            pass
      # Handle review form submission
    if request.method == 'POST' and request.user.is_authenticated:
        if user_review:
            messages.warning(request, 'Anda sudah memberikan ulasan untuk produk ini.')
        else:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.product = product
                review.customer = request.user.customer
                review.save()
                messages.success(request, 'Ulasan Anda telah berhasil dikirim!')
                return redirect('store:product_detail', slug=slug)
    else:
        form = ReviewForm()
    
    context = {
        'product': product,
        'reviews': reviews,
        'related_products': related_products,
        'avg_rating': avg_rating,
        'user_review': user_review,
        'form': form,
    }
    return render(request, 'store/product_detail.html', context)

@login_required
def cart_view(request):
    """
    Shopping cart view
    Implementasi Aggregation pattern
    """
    cart, created = Cart.objects.get_or_create(customer=request.user.customer)
    
    context = {
        'cart': cart,
    }
    return render(request, 'store/cart.html', context)

@login_required
@require_POST
def add_to_cart(request, product_id):
    """
    Add product to cart via AJAX
    Implementasi Composition pattern
    """
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart, created = Cart.objects.get_or_create(customer=request.user.customer)
        
        quantity = int(request.POST.get('quantity', 1))
        
        if not product.is_in_stock():
            return JsonResponse({
                'success': False,
                'message': 'Produk sedang habis stok'
            })
        
        if product.stock < quantity:
            return JsonResponse({
                'success': False,
                'message': f'Hanya tersedia {product.stock} item'
            })
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Produk berhasil ditambahkan ke keranjang',
            'cart_total_items': cart.get_total_items(),
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
def checkout(request):
    """
    Checkout process
    Implementasi State Pattern dalam order processing
    """
    cart = get_object_or_404(Cart, customer=request.user.customer)
    
    if not cart.items.exists():
        messages.warning(request, 'Keranjang Anda kosong.')
        return redirect('store:cart')
    
    if request.method == 'POST':
        # Create order
        order = Order.objects.create(
            customer=request.user.customer,
            order_number=f'ORD-{uuid.uuid4().hex[:10].upper()}',
            total_amount=cart.get_total_price(),
            shipping_address=request.POST.get('shipping_address'),
            notes=request.POST.get('notes', ''),
        )
        
        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
            )
            # Reduce stock
            cart_item.product.reduce_stock(cart_item.quantity)
        
        # Clear cart
        cart.clear_cart()
        
        messages.success(request, f'Pesanan {order.order_number} berhasil dibuat!')
        return redirect('store:order_detail', order_number=order.order_number)
    
    context = {
        'cart': cart,
    }
    return render(request, 'store/checkout.html', context)

@login_required
def order_list(request):
    """
    User's order history
    """
    orders = Order.objects.filter(customer=request.user.customer).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'store/order_list.html', context)

@login_required
def order_detail(request, order_number):
    """
    Order detail view
    Demonstrasi Polymorphism dalam order status handling
    """
    order = get_object_or_404(Order, order_number=order_number, customer=request.user.customer)
    
    context = {
        'order': order,
    }
    return render(request, 'store/order_detail.html', context)

@login_required
@require_POST
def update_cart_item(request, item_id):
    """
    Update cart item quantity
    """
    try:
        cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user.customer)
        action = request.POST.get('action')
        
        if action == 'increase':
            if cart_item.product.stock > cart_item.quantity:
                cart_item.increase_quantity()
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Stok tidak mencukupi'
                })
        elif action == 'decrease':
            cart_item.decrease_quantity()
        elif action == 'remove':
            cart_item.delete()
        
        cart = cart_item.cart if cart_item.id else request.user.customer.cart_set.first()
        
        return JsonResponse({
            'success': True,
            'cart_total_items': cart.get_total_items() if cart else 0,
            'cart_total_price': float(cart.get_total_price()) if cart else 0,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

def category_detail(request, slug):
    """
    Category detail view dengan products
    """
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = category.products.filter(is_active=True)
    
    # Sorting
    sort_by = request.GET.get('sort')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('name')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'current_sort': sort_by,
    }
    return render(request, 'store/category_detail.html', context)

def search_products(request):
    """
    Search products view dengan filtering
    Implementasi Polymorphism dalam search berbagai kriteria
    """
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_by = request.GET.get('sort', 'name')
    
    products = Product.objects.filter(is_active=True)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    # Sorting dengan Polymorphism
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'rating':
        products = products.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    else:
        products = products.order_by('name')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'categories': categories,
        'selected_category': category_id,
        'min_price': min_price,
        'max_price': max_price,
        'current_sort': sort_by,
    }
    return render(request, 'store/search_results.html', context)
