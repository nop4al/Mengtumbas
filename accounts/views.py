from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

from store.forms import CustomUserCreationForm, CustomAuthenticationForm, CustomerProfileForm, UserProfileForm, ReviewForm
from store.utils import ensure_customer_exists
from store.models import Review, OrderItem, Wishlist

class CustomLoginView(LoginView):
    """
    Custom login view dengan styling
    Implementasi Inheritance dari Django's LoginView
    """
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('store:home')

class CustomLogoutView(LogoutView):
    """
    Custom logout view
    """
    next_page = reverse_lazy('store:home')
    http_method_names = ['get', 'post']  # Mengizinkan method GET dan POST

def register(request):
    """
    User registration view
    Implementasi Constructor pattern dalam user creation
    """
    if request.user.is_authenticated:
        return redirect('store:home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Akun berhasil dibuat untuk {username}!')
            
            # Auto login after registration
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            if user:
                login(request, user)
                return redirect('store:home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    """
    User profile view
    Demonstrasi Encapsulation dalam profile management
    """
    try:
        customer = ensure_customer_exists(request.user)
        if not customer:
            messages.error(request, "Tidak dapat menemukan profil pelanggan Anda. Silakan hubungi administrator.")
            return redirect('store:home')
        
        # Get user's orders with proper error handling
        try:
            orders = customer.order_set.all().order_by('-created_at')[:10]
            orders_count = customer.order_set.count()
        except Exception:
            orders = []
            orders_count = 0
        
        # Get user's reviews count with proper error handling
        try:
            reviews = Review.objects.filter(customer=customer).order_by('-created_at')
            reviews_count = reviews.count()
        except Exception:
            reviews = []
            reviews_count = 0
        
        # Get user's wishlist count with proper error handling
        try:
            wishlist, created = Wishlist.objects.get_or_create(customer=customer)
            wishlist_count = wishlist.products.count()
            wishlist_products = wishlist.products.all()
        except Exception as e:
            print(f"Error getting wishlist: {str(e)}")
            wishlist_count = 0
            wishlist_products = []
        
        # Get current cart if exists
        try:
            cart = customer.cart_set.first()
            cart_count = cart.get_total_items() if cart else 0
        except Exception:
            cart_count = 0
        
        context = {
            'customer': customer,
            'user': request.user,
            'orders': orders,
            'orders_count': orders_count,
            'reviews': reviews,
            'reviews_count': reviews_count,
            'wishlist_count': wishlist_count,
            'wishlist_products': wishlist_products,
            'cart_count': cart_count,
        }
        return render(request, 'accounts/profile.html', context)
    except Exception as e:
        messages.error(request, f"Terjadi kesalahan saat memuat profil: {str(e)}")
        return redirect('store:home')

@login_required
def profile_edit(request):
    """
    Profile editing view
    """
    customer = ensure_customer_exists(request.user)
    
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        customer_form = CustomerProfileForm(request.POST, instance=customer)
        
        if user_form.is_valid() and customer_form.is_valid():
            user_form.save()
            customer_form.save()
            messages.success(request, 'Profil Anda telah berhasil diperbarui!')
            return redirect('accounts:profile')
    else:
        user_form = UserProfileForm(instance=request.user)
        customer_form = CustomerProfileForm(instance=customer)
    
    context = {
        'user_form': user_form,
        'customer_form': customer_form,
    }
    return render(request, 'accounts/profile_edit.html', context)

@login_required
def order_history(request):
    """
    User's complete order history
    """
    customer = ensure_customer_exists(request.user)
    orders = customer.order_set.all().order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/order_history.html', context)

@login_required
def edit_review(request, review_id):
    """
    Edit a review
    """
    customer = ensure_customer_exists(request.user)
    
    try:
        review = Review.objects.get(id=review_id, customer=customer)
    except Review.DoesNotExist:
        messages.error(request, "Ulasan tidak ditemukan atau Anda tidak memiliki izin untuk mengeditnya.")
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Ulasan berhasil diperbarui!")
            return redirect('accounts:profile')
    else:
        form = ReviewForm(instance=review)
    
    context = {
        'form': form,
        'review': review,
    }
    return render(request, 'accounts/edit_review.html', context)

@login_required
def add_review(request, order_item_id):
    """
    Add a new review for a purchased product
    """
    customer = ensure_customer_exists(request.user)
    
    # Get the order item
    try:
        order_item = OrderItem.objects.get(id=order_item_id)
        # Check if this order item belongs to the customer's order
        if order_item.order.customer != customer:
            messages.error(request, "Anda tidak memiliki izin untuk memberikan ulasan pada produk ini.")
            return redirect('accounts:profile')
        
        # Check if the order is delivered
        if order_item.order.status != 'delivered':
            messages.error(request, "Anda hanya dapat memberikan ulasan untuk pesanan yang telah selesai.")
            return redirect('accounts:profile')
        
        # Check if review already exists
        existing_review = Review.objects.filter(customer=customer, product=order_item.product).first()
        
        if request.method == 'POST':
            form = ReviewForm(request.POST, instance=existing_review)
            if form.is_valid():
                review = form.save(commit=False)
                review.customer = customer
                review.product = order_item.product
                review.save()
                messages.success(request, "Ulasan berhasil disimpan!")
                return redirect('accounts:profile')
        else:
            form = ReviewForm(instance=existing_review)
        
        context = {
            'form': form,
            'order_item': order_item,
            'existing_review': existing_review,
        }
        return render(request, 'accounts/add_review.html', context)
        
    except OrderItem.DoesNotExist:
        messages.error(request, "Produk tidak ditemukan.")
        return redirect('accounts:profile')
