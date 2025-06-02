from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Min, Max
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
from decimal import Decimal

from .models import Product, Category, Cart, CartItem, Order, OrderItem, Customer, Review, Wishlist
from .forms import ReviewForm
from .utils import ensure_customer_exists

def home(request):
    """
    Homepage view dengan featured products
    Implementasi Polymorphism dalam display berbagai tipe produk
    """
    featured_products = Product.objects.filter(featured=True, is_active=True)[:8]
    
    # Kategori dengan hierarki (main categories saja untuk navigasi utama)
    local_categories = Category.objects.filter(
        is_active=True, 
        origin_type='local',
        parent__isnull=True  # Hanya kategori utama
    )
    foreign_categories = Category.objects.filter(
        is_active=True, 
        origin_type='foreign',
        parent__isnull=True  # Hanya kategori utama
    )
    
    latest_products = Product.objects.filter(is_active=True)[:8]
    
    # Get wishlist products if user is authenticated
    wishlist_products = []
    if request.user.is_authenticated:
        customer = ensure_customer_exists(request.user)
        try:
            wishlist = Wishlist.objects.get(customer=customer)
            wishlist_products = [p.id for p in wishlist.products.all()]
        except Wishlist.DoesNotExist:
            pass
    
    context = {
        'featured_products': featured_products,
        'local_categories': local_categories,
        'foreign_categories': foreign_categories,
        'latest_products': latest_products,
        'wishlist_products': wishlist_products,
    }
    return render(request, 'store/home.html', context)

def product_list(request):
    """
    Product list view dengan filter dan pagination
    Demonstrasi Encapsulation dalam akses data
    """
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_by = request.GET.get('sort', 'name')
    
    products = Product.objects.filter(is_active=True)
    
    # Apply filters
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    selected_category = None
    if category_id:
        try:
            selected_category = Category.objects.get(id=category_id)
            # Include products from subcategories
            category_ids = [selected_category.id]
            category_ids.extend(selected_category.subcategories.values_list('id', flat=True))
            products = products.filter(category_id__in=category_ids)
        except (Category.DoesNotExist, ValueError):
            pass
        
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
    
    # Apply sorting
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
    
    # Get categories for filter sidebar - only get parent categories
    categories = Category.objects.filter(is_active=True)
    
    # Get min and max price for filter
    price_range = Product.objects.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.get_page(page)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)
    
    # Get wishlist products if user is authenticated
    wishlist_products = []
    if request.user.is_authenticated:
        customer = ensure_customer_exists(request.user)
        try:
            wishlist = Wishlist.objects.get(customer=customer)
            wishlist_products = [p.id for p in wishlist.products.all()]
        except Wishlist.DoesNotExist:
            pass
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'category_id': category_id,
        'selected_category': selected_category,
        'min_price': min_price or price_range['min_price'],
        'max_price': max_price or price_range['max_price'],
        'sort_by': sort_by,
        'price_range': price_range,
        'wishlist_products': wishlist_products,
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
    in_wishlist = False
    if request.user.is_authenticated:
        try:
            user_review = reviews.get(customer__user=request.user)
        except Review.DoesNotExist:
            pass
            
        # Check if product is in user's wishlist
        customer = ensure_customer_exists(request.user)
        try:
            wishlist = Wishlist.objects.get(customer=customer)
            in_wishlist = wishlist.has_product(product)
        except Wishlist.DoesNotExist:
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
                review.customer = ensure_customer_exists(request.user)
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
        'categories': Category.objects.filter(is_active=True),
        'form': form,
        'in_wishlist': in_wishlist,
    }
    return render(request, 'store/product_detail.html', context)

def cart_view(request):
    """
    Shopping cart view
    Implementasi Aggregation pattern with guest support
    """
    cart = None
    if request.user.is_authenticated:
        customer = ensure_customer_exists(request.user)
        cart = Cart.objects.filter(customer=customer).first()
        if not cart:
            cart = Cart.objects.create(customer=customer)
    else:
        if 'guest_cart' not in request.session:
            request.session['guest_cart'] = {'items': [], 'total_items': 0, 'subtotal': 0}
        cart = request.session['guest_cart']
        
    context = {
        'cart': cart,
        'is_guest': not request.user.is_authenticated,
    }
    return render(request, 'store/cart.html', context)

@require_POST
def add_to_cart(request, product_id):
    """
    Add product to cart via AJAX
    Supports both authenticated users and guests
    Implementasi Composition pattern
    """
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Handle both form data and JSON data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
        else:
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

        if request.user.is_authenticated:
            # Handle logged in user cart
            customer = ensure_customer_exists(request.user)
            cart, created = Cart.objects.get_or_create(customer=customer)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
                
            cart_count = cart.get_total_items()
        else:
            # Handle guest cart in session
            if 'guest_cart' not in request.session:
                request.session['guest_cart'] = {'items': [], 'total_items': 0, 'subtotal': 0}
            
            guest_cart = request.session['guest_cart']
            found = False
            
            # Update quantity if product exists
            for item in guest_cart['items']:
                if item['product_id'] == product_id:
                    item['quantity'] += quantity
                    found = True
                    break
            
            # Add new item if not found
            if not found:
                guest_cart['items'].append({
                    'product_id': product_id,
                    'product_name': product.name,
                    'quantity': quantity,
                    'price': str(product.price),
                    'image_url': product.image.url if product.image else None,
                    'slug': product.slug
                })
            
            # Update cart totals
            guest_cart['total_items'] = sum(item['quantity'] for item in guest_cart['items'])
            guest_cart['subtotal'] = sum(float(item['price']) * item['quantity'] for item in guest_cart['items'])
            request.session.modified = True
            cart_count = guest_cart['total_items']

        return JsonResponse({
            'success': True,
            'message': 'Produk berhasil ditambahkan ke keranjang',
            'cart_count': cart_count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

def checkout(request):
    """
    Checkout process with guest support and validation
    Implementasi State Pattern dalam order processing
    """
    if request.user.is_authenticated:
        customer = ensure_customer_exists(request.user)
        cart = get_object_or_404(Cart, customer=customer)
        if not cart.items.exists():
            messages.warning(request, 'Keranjang Anda kosong.')
            return redirect('store:cart')
            
        # Calculate shipping cost and import fees for foreign products
        shipping_cost = Decimal('0')
        foreign_items_count = 0
        import_fees = Decimal('0')
        
        for item in cart.items.all():
            if item.product.category.origin_type == 'foreign':
                foreign_items_count += 1
                # Calculate import fees
                tax_details = item.product.get_tax_details()
                if tax_details:
                    import_fees += tax_details['total_additional'] * item.quantity
        
        if foreign_items_count > 0:
            shipping_cost = Decimal('150000') * foreign_items_count
    else:
        guest_cart = request.session.get('guest_cart', {'items': []})
        if not guest_cart['items']:
            messages.warning(request, 'Keranjang Anda kosong.')
            return redirect('store:cart')
        cart = guest_cart
        
        # Calculate shipping cost for foreign products in guest cart
        shipping_cost = Decimal('0')
        foreign_items_count = 0
        import_fees = Decimal('0')
        for item in guest_cart['items']:
            try:
                product = Product.objects.get(id=item['product_id'])
                if product.category.origin_type == 'foreign':
                    foreign_items_count += 1
                    # Calculate import fees
                    tax_details = product.get_tax_details()
                    if tax_details:
                        import_fees += tax_details['total_additional'] * item['quantity']
            except (Product.DoesNotExist, KeyError):
                pass
                
        if foreign_items_count > 0:
            shipping_cost = Decimal('150000') * foreign_items_count
    
    if request.method == 'POST':
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'shipping_address']
        if not request.user.is_authenticated:
            for field in required_fields:
                if not request.POST.get(field):
                    messages.error(request, f'Mohon isi {field.replace("_", " ").title()}')
                    return redirect('store:checkout')
        
        # Validate email format for guest users  
        if not request.user.is_authenticated:
            email = request.POST.get('email')
            if not email or '@' not in email:
                messages.error(request, 'Mohon masukkan alamat email yang valid')
                return redirect('store:checkout')
            
        # Shipping address validation
        shipping_address = request.POST.get('shipping_address')
        if not shipping_address or len(shipping_address.strip()) < 10:
            messages.error(request, 'Mohon masukkan alamat pengiriman lengkap')
            return redirect('store:checkout')

        # Check stock availability one more time
        if request.user.is_authenticated:
            for item in cart.items.all():
                if item.quantity > item.product.stock:
                    messages.error(request, f'Stok {item.product.name} tidak mencukupi')
                    return redirect('store:cart')
        else:
            for item in cart['items']:
                product = get_object_or_404(Product, id=item['product_id'])
                if item['quantity'] > product.stock:
                    messages.error(request, f'Stok {product.name} tidak mencukupi')
                    return redirect('store:cart')
                    
        # Check payment method restrictions for orders above 10,000,000
        payment_method = request.POST.get('payment_method', 'cod')
        
        # Calculate total amount
        if request.user.is_authenticated:
            total_amount = cart.get_subtotal()
            if foreign_items_count > 0:
                total_amount += import_fees + shipping_cost
        else:
            total_amount = Decimal(cart.get('subtotal', 0))
            if foreign_items_count > 0:
                total_amount += import_fees + shipping_cost
                
        # Add admin fee if applicable
        if payment_method in ['virtual_account', 'ewallet', 'qris']:
            admin_fee = Decimal(total_amount) * Decimal('0.005')
            total_amount += admin_fee
            
        # Restrict payment methods for orders above 10,000,000
        if total_amount > Decimal('10000000') and payment_method in ['cod', 'ewallet', 'qris']:
            messages.error(request, 'Untuk pembelian di atas Rp 10.000.000, metode pembayaran yang tersedia hanya Virtual Account.')
            return redirect('store:checkout')
            
        # Restrict COD payment for orders above 1,000,000
        if payment_method == 'cod' and total_amount > Decimal('1000000'):
            messages.error(request, 'Pembayaran COD hanya tersedia untuk pesanan di bawah Rp 1.000.000.')
            return redirect('store:checkout')

        try:
            # For guest users, create guest customer
            if not request.user.is_authenticated:
                guest_customer = Customer.objects.create(
                    user=None,
                    email=request.POST['email'],
                    first_name=request.POST['first_name'],
                    last_name=request.POST['last_name'],
                    address=request.POST.get('shipping_address')
                )
                customer = guest_customer
                guest_cart = request.session['guest_cart']
            else:
                customer = ensure_customer_exists(request.user)
            
            # Create order with shipping costs and import fees
            order = Order.objects.create(
                customer=customer,
                order_number=f'ORD-{uuid.uuid4().hex[:10].upper()}',
                total_amount=total_amount,
                shipping_address=shipping_address,
                notes=request.POST.get('notes', ''),
                is_guest_order=not request.user.is_authenticated,
                payment_method=request.POST.get('payment_method', 'cod'),
                payment_channel=request.POST.get('payment_channel', '')
            )
            
            # Calculate and add admin fee if applicable
            if payment_method in ['virtual_account', 'ewallet', 'qris']:
                # 0.5% admin fee
                admin_fee = Decimal(total_amount) * Decimal('0.005')
                order.admin_fee = admin_fee
                order.total_amount += admin_fee
                order.save()
            
            # Create order items and reduce stock
            if request.user.is_authenticated:
                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price,
                    )
                    cart_item.product.reduce_stock(cart_item.quantity)
                cart.clear_cart()
            else:
                for item in guest_cart['items']:
                    product = get_object_or_404(Product, id=item['product_id'])
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item['quantity'], 
                        price=float(item['price']),
                    )
                    product.reduce_stock(item['quantity'])
                request.session['guest_cart'] = {'items': [], 'total_items': 0, 'subtotal': 0}
                request.session.modified = True
            
            messages.success(request, f'Pesanan {order.order_number} berhasil dibuat!')
            return redirect('store:order_detail', order_number=order.order_number)
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
            return redirect('store:checkout')
    
    context = {
        'cart': cart,
        'shipping_cost': shipping_cost,
        'import_fees': import_fees,
        'foreign_items_count': foreign_items_count,
        'has_foreign_products': foreign_items_count > 0,
    }
    return render(request, 'store/checkout.html', context)

@login_required
def order_list(request):
    """
    User's order history with status filtering
    """
    customer = ensure_customer_exists(request.user)
    orders = Order.objects.filter(customer=customer).order_by('-created_at')
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status and status != 'all':
        orders = orders.filter(status=status)
    
    context = {
        'orders': orders,
        'status': status,
    }
    return render(request, 'store/order_list.html', context)

@login_required
def order_detail(request, order_number):
    """
    Order detail view
    Demonstrasi Polymorphism dalam order status handling
    """
    customer = ensure_customer_exists(request.user)
    order = get_object_or_404(Order, order_number=order_number, customer=customer)
    
    context = {
        'order': order,
    }
    return render(request, 'store/order_detail.html', context)

@require_POST
def update_cart_item(request, item_id):
    """
    Update cart item quantity
    """
    # Handle guest cart update
    if not request.user.is_authenticated:
        try:
            product_id = int(item_id)
            product = get_object_or_404(Product, id=product_id)
            
            if 'guest_cart' not in request.session:
                request.session['guest_cart'] = {'items': [], 'total_items': 0, 'subtotal': 0}
            
            guest_cart = request.session['guest_cart']
            
            # Check if we're receiving JSON data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                quantity = data.get('quantity')
                
                if quantity is not None:
                    if quantity > 0:
                        # Check stock availability
                        if quantity <= product.stock:
                            # Find and update the item
                            for item in guest_cart['items']:
                                if item['product_id'] == product_id:
                                    item['quantity'] = quantity
                                    item['total_price'] = float(item['price']) * quantity
                                    break
                            
                            # Update cart totals
                            guest_cart['total_items'] = sum(item['quantity'] for item in guest_cart['items'])
                            guest_cart['subtotal'] = sum(float(item['price']) * item['quantity'] for item in guest_cart['items'])
                            request.session.modified = True
                            
                            return JsonResponse({
                                'success': True,
                                'cart_total_items': guest_cart['total_items'],
                                'cart_total_price': guest_cart['subtotal'],
                                'item_quantity': quantity,
                            })
                        else:
                            return JsonResponse({
                                'success': False,
                                'message': 'Stok tidak mencukupi'
                            })
                    elif quantity == 0:
                        # Remove the item
                        guest_cart['items'] = [item for item in guest_cart['items'] if item['product_id'] != product_id]
                        
                        # Update cart totals
                        guest_cart['total_items'] = sum(item['quantity'] for item in guest_cart['items'])
                        guest_cart['subtotal'] = sum(float(item['price']) * item['quantity'] for item in guest_cart['items'])
                        request.session.modified = True
                        
                        return JsonResponse({
                            'success': True,
                            'message': 'Item berhasil dihapus'
                        })
            else:
                # Handle form POST actions
                action = request.POST.get('action')
                
                # Find the item
                item_found = False
                for item in guest_cart['items']:
                    if item['product_id'] == product_id:
                        item_found = True
                        current_quantity = item['quantity']
                        
                        if action == 'increase':
                            if current_quantity < product.stock:
                                item['quantity'] += 1
                                item['total_price'] = float(item['price']) * item['quantity']
                                messages.success(request, 'Jumlah item berhasil ditambah')
                            else:
                                messages.error(request, 'Stok tidak mencukupi')
                        elif action == 'decrease':
                            if current_quantity > 1:
                                item['quantity'] -= 1
                                item['total_price'] = float(item['price']) * item['quantity']
                                messages.success(request, 'Jumlah item berhasil dikurangi')
                            else:
                                # Remove the item when quantity is 1 and user clicks decrease
                                guest_cart['items'] = [i for i in guest_cart['items'] if i['product_id'] != product_id]
                                messages.success(request, 'Item berhasil dihapus dari keranjang')
                        break
                
                if item_found:
                    # Update cart totals
                    guest_cart['total_items'] = sum(item['quantity'] for item in guest_cart['items'])
                    guest_cart['subtotal'] = sum(float(item['price']) * item['quantity'] for item in guest_cart['items'])
                    request.session.modified = True
                
                return redirect('store:cart')
            
            return JsonResponse({
                'success': False,
                'message': 'Invalid request'
            })
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
            return redirect('store:cart')
    
    # Handle authenticated user cart update
    try:
        customer = ensure_customer_exists(request.user)
        cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=customer)
        
        # Check if we're receiving JSON data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            quantity = data.get('quantity')
            
            if quantity and quantity > 0:
                # Check stock availability
                if quantity <= cart_item.product.stock:
                    cart_item.quantity = quantity
                    cart_item.save()
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Stok tidak mencukupi'
                    })
            elif quantity == 0:
                cart_item.delete()
        else:
            # Handle form POST actions
            action = request.POST.get('action')
            
            if action == 'increase':
                if cart_item.quantity < cart_item.product.stock:
                    cart_item.quantity += 1
                    cart_item.save()
                    messages.success(request, 'Jumlah item berhasil ditambah')
                else:
                    messages.error(request, 'Stok tidak mencukupi')
            elif action == 'decrease':
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                    messages.success(request, 'Jumlah item berhasil dikurangi')
                else:
                    # Remove the item when quantity is 1 and user clicks decrease
                    cart_item.delete()
                    messages.success(request, 'Item berhasil dihapus dari keranjang')
            elif action == 'remove':
                cart_item.delete()
                messages.success(request, 'Item berhasil dihapus dari keranjang')
            
            return redirect('store:cart')
        
        cart = cart_item.cart if cart_item.id else customer.cart_set.first()
        
        return JsonResponse({
            'success': True,
            'cart_total_items': cart.get_total_items() if cart else 0,
            'cart_total_price': float(cart.get_total()) if cart else 0,
            'item_total': float(cart_item.get_total_price()) if cart_item.id else 0,
            'item_price': float(cart_item.product.price),
            'item_quantity': cart_item.quantity if cart_item.id else 0,
        })
        
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('store:cart')

@require_POST
def remove_from_cart(request, item_id):
    """
    Remove item from cart
    """
    # Handle guest cart removal
    if not request.user.is_authenticated:
        try:
            product_id = int(item_id)
            
            if 'guest_cart' in request.session:
                guest_cart = request.session['guest_cart']
                
                # Remove the item
                guest_cart['items'] = [item for item in guest_cart['items'] if item['product_id'] != product_id]
                
                # Update cart totals
                guest_cart['total_items'] = sum(item['quantity'] for item in guest_cart['items'])
                guest_cart['subtotal'] = sum(float(item['price']) * item['quantity'] for item in guest_cart['items'])
                request.session.modified = True
                
                if request.content_type == 'application/json':
                    return JsonResponse({
                        'success': True,
                        'message': 'Item berhasil dihapus'
                    })
            
            return redirect('store:cart')
            
        except Exception as e:
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                })
            messages.error(request, f'Gagal menghapus item: {str(e)}')
            return redirect('store:cart')
    
    # Handle authenticated user cart removal
    try:
        customer = ensure_customer_exists(request.user)
        cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=customer)
        cart = cart_item.cart
        cart_item.delete()
        
        messages.success(request, 'Item berhasil dihapus dari keranjang')
        return redirect('store:cart')
        
    except Exception as e:
        messages.error(request, f'Gagal menghapus item: {str(e)}')
        return redirect('store:cart')

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
    
    # Get wishlist products for authenticated users
    wishlist_products = []
    if request.user.is_authenticated:
        customer = ensure_customer_exists(request.user)
        try:
            wishlist = Wishlist.objects.get(customer=customer)
            wishlist_products = list(wishlist.products.values_list('id', flat=True))
        except Wishlist.DoesNotExist:
            pass
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'current_sort': sort_by,
        'wishlist_products': wishlist_products,
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

@login_required
def wishlist_view(request):
    """
    View for displaying the user's wishlist
    """
    customer = ensure_customer_exists(request.user)
    wishlist, created = Wishlist.objects.get_or_create(customer=customer)
    
    context = {
        'wishlist': wishlist,
    }
    return render(request, 'store/wishlist.html', context)

@login_required
@require_POST
def add_to_wishlist(request, product_id):
    """
    Add a product to the user's wishlist
    """
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        customer = ensure_customer_exists(request.user)
        wishlist, created = Wishlist.objects.get_or_create(customer=customer)
        
        if wishlist.has_product(product):
            return JsonResponse({
                'success': True,
                'message': 'Produk sudah ada di wishlist',
                'wishlist_count': wishlist.get_product_count(),
            })
        
        wishlist.add_product(product)
        
        return JsonResponse({
            'success': True,
            'message': 'Produk berhasil ditambahkan ke wishlist',
            'wishlist_count': wishlist.get_product_count(),
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    """
    Remove a product from the user's wishlist
    """
    try:
        product = get_object_or_404(Product, id=product_id)
        customer = ensure_customer_exists(request.user)
        wishlist, created = Wishlist.objects.get_or_create(customer=customer)
        
        if not wishlist.has_product(product):
            return JsonResponse({
                'success': True,
                'message': 'Produk tidak ada di wishlist',
                'wishlist_count': wishlist.get_product_count(),
            })
        
        wishlist.remove_product(product)
        
        return JsonResponse({
            'success': True,
            'message': 'Produk berhasil dihapus dari wishlist',
            'wishlist_count': wishlist.get_product_count(),
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

def api_search_suggestions(request):
    """
    API endpoint untuk mendapatkan saran pencarian produk
    """
    query = request.GET.get('q', '').strip()
    suggestions = []
    
    if len(query) >= 2:
        # Get product name suggestions
        product_suggestions = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(category__name__icontains=query)
        ).values_list('name', flat=True)[:5]
        
        # Get category suggestions
        category_suggestions = Category.objects.filter(
            name__icontains=query
        ).values_list('name', flat=True)[:3]
        
        suggestions = list(product_suggestions) + list(category_suggestions)
        suggestions = list(set(suggestions))[:5]  # Remove duplicates and limit to 5
    
    return JsonResponse({'suggestions': suggestions})

def api_search_products(request):
    """
    API endpoint untuk pencarian produk secara dinamis
    """
    # Reuse search_products logic for filtering
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_by = request.GET.get('sort', 'name')
    page = request.GET.get('page', '1')
    
    products = Product.objects.filter(is_active=True)
    
    # Apply filters
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
    
    # Apply sorting
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
    try:
        page_obj = paginator.get_page(page)
    except:
        page_obj = paginator.get_page(1)
    
    # Render only the products grid portion
    html = render(request, 'store/partials/product_grid.html', {
        'page_obj': page_obj
    }).content.decode('utf-8')
    
    return JsonResponse({
        'html': html,
        'page': page,
        'hasNext': page_obj.has_next(),
        'hasPrev': page_obj.has_previous(),
        'total': paginator.count,
    })

@login_required
@require_POST 
def cancel_order(request, order_number):
    """
    Cancel an order if it's in pending or confirmed state
    """
    try:
        customer = ensure_customer_exists(request.user)
        order = get_object_or_404(Order, order_number=order_number, customer=customer)
        
        if order.cancel_order():
            messages.success(request, 'Pesanan berhasil dibatalkan.')
            
            # Return items to stock
            for item in order.items.all():
                item.product.stock += item.quantity
                item.product.save()
        else:
            messages.error(request, 'Pesanan tidak dapat dibatalkan pada status ini.')
            
        return redirect('store:order_detail', order_number=order_number)
        
    except Order.DoesNotExist:
        messages.error(request, 'Pesanan tidak ditemukan.')
        return redirect('store:order_list')

@login_required
@require_POST
def complete_order(request, order_number):
    """
    Mark order as complete/delivered
    Only shipped orders can be marked as delivered
    """
    try:
        customer = ensure_customer_exists(request.user)
        order = get_object_or_404(Order, order_number=order_number, customer=customer)

        if order.status == 'shipped':
            order._deliver_order()
            messages.success(request, 'Pesanan telah diterima. Terima kasih telah berbelanja!')
        else:
            messages.error(request, 'Pesanan belum dikirim, tidak dapat ditandai selesai.')
        
        return redirect('store:order_detail', order_number=order_number)

    except Order.DoesNotExist:
        messages.error(request, 'Pesanan tidak ditemukan.')
        return redirect('store:order_list')

@require_POST
def add_to_cart_and_checkout(request, product_id):
    """View to add a product to the cart and proceed to checkout."""
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        quantity = int(request.POST.get('quantity', 1))

        if not product.is_in_stock():
            messages.error(request, 'Produk sedang habis stok!')
            return redirect('store:product_detail', slug=product.slug)

        if product.stock < quantity:
            messages.error(request, f'Hanya tersedia {product.stock} item')
            return redirect('store:product_detail', slug=product.slug)

        # Handle guest users
        if not request.user.is_authenticated:
            messages.error(request, 'Silakan login terlebih dahulu untuk melanjutkan checkout!')
            return redirect('accounts:login')

        # Get or create the cart for the current user
        customer = ensure_customer_exists(request.user)
        cart, created = Cart.objects.get_or_create(customer=customer)        # Add the product to the cart with specified quantity
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            # Check if total quantity exceeds stock
            if cart_item.quantity > product.stock:
                cart_item.quantity = product.stock
            cart_item.save()
        
        messages.success(request, f'{product.name} berhasil ditambahkan ke keranjang!')
        return redirect('store:checkout')

    except Exception as e:
        messages.error(request, 'Terjadi kesalahan saat menambahkan produk ke keranjang!')
        return redirect('store:product_detail', slug=product.slug)

@login_required
def get_cart_totals(request):
    """
    Get cart totals for AJAX updates
    """
    try:
        customer = ensure_customer_exists(request.user)
        cart = customer.cart_set.first()
        
        if cart:
            return JsonResponse({
                'success': True,
                'subtotal': float(cart.get_subtotal()),
                'shipping': float(cart.get_shipping_cost() or 0),
                'discount': float(cart.get_discount_amount() or 0),
                'total': float(cart.get_total()),
                'item_count': cart.get_total_items()
            })
        else:
            return JsonResponse({
                'success': True,
                'subtotal': 0,
                'shipping': 0,
                'discount': 0,
                'total': 0,
                'item_count': 0
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

def get_guest_cart_totals(request):
    """
    Get guest cart totals for AJAX updates
    """
    try:
        cart = request.session.get('guest_cart', {'items': [], 'total_items': 0, 'subtotal': 0})
        items_count = sum(item['quantity'] for item in cart.get('items', []))
        
        # Calculate subtotal by converting string prices to float
        subtotal = 0
        for item in cart.get('items', []):
            price = item.get('price', 0)
            quantity = item.get('quantity', 0)
            # Convert to float if it's a string
            if isinstance(price, str):
                price = float(price)
            subtotal += price * quantity
        
        return JsonResponse({
            'success': True,
            'subtotal': subtotal,
            'shipping': 0,  # Assume no shipping for simplicity
            'discount': 0,  # Assume no discount for simplicity
            'total': subtotal,
            'item_count': items_count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

def local_products(request):
    """
    View khusus untuk menampilkan barang lokal
    """
    products = Product.objects.filter(is_active=True, category__origin_type='local')
    categories = Category.objects.filter(is_active=True, origin_type='local', parent__isnull=True)
    
    # Category filtering
    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug, origin_type='local')
        # Include products from subcategories
        category_ids = [selected_category.id]
        category_ids.extend(selected_category.subcategories.values_list('id', flat=True))
        products = products.filter(category__id__in=category_ids)
    
    # Price sorting
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('name')
    
    # Get wishlist products for authenticated users
    wishlist_products = []
    if request.user.is_authenticated:
        customer = ensure_customer_exists(request.user)
        try:
            wishlist = Wishlist.objects.get(customer=customer)
            wishlist_products = list(wishlist.products.values_list('id', flat=True))
        except Wishlist.DoesNotExist:
            pass
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_slug,
        'current_sort': sort_by,
        'selected_category': selected_category,
        'page_title': 'Barang Lokal',
        'origin_type': 'local',
        'wishlist_products': wishlist_products,
    }
    return render(request, 'store/origin_products.html', context)

def foreign_products(request):
    """
    View khusus untuk menampilkan barang asing dengan informasi biaya tambahan
    """
    products = Product.objects.filter(is_active=True, category__origin_type='foreign')
    categories = Category.objects.filter(is_active=True, origin_type='foreign', parent__isnull=True)
    
    # Category filtering
    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug, origin_type='foreign')
        category_ids = [selected_category.id]
        category_ids.extend(selected_category.subcategories.values_list('id', flat=True))
        products = products.filter(category__id__in=category_ids)
    
    # Get wishlist products for authenticated users
    wishlist_products = []
    if request.user.is_authenticated:
        customer = ensure_customer_exists(request.user)
        try:
            wishlist = Wishlist.objects.get(customer=customer)
            wishlist_products = list(wishlist.products.values_list('id', flat=True))
        except Wishlist.DoesNotExist:
            pass
    
    # Price sorting - menggunakan harga final termasuk biaya tambahan
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_low':
        products = sorted(products, key=lambda p: p.get_final_price())
    elif sort_by == 'price_high':
        products = sorted(products, key=lambda p: p.get_final_price(), reverse=True)
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('name')
    
    # Menambahkan informasi biaya tambahan untuk setiap produk
    products_with_fees = []
    for product in products:
        tax_details = product.get_tax_details()
        products_with_fees.append({
            'product': product,
            'tax_details': tax_details
        })
    
    # Pagination
    paginator = Paginator(products_with_fees, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Informasi umum tentang biaya tambahan
    import_info = {
        'tax_rate': f"{Product.IMPORT_TAX_RATE * 100}%",
        'customs_fee': Product.CUSTOMS_FEE,
        'handling_fee': Product.HANDLING_FEE
    }
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_slug,
        'current_sort': sort_by,
        'selected_category': selected_category,
        'page_title': 'Barang Asing',
        'origin_type': 'foreign',
        'import_info': import_info,
        'wishlist_products': wishlist_products,
    }
    return render(request, 'store/origin_products.html', context)
