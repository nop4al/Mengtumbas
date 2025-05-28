from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

from store.forms import CustomUserCreationForm, CustomAuthenticationForm, CustomerProfileForm, UserProfileForm

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
    customer = request.user.customer
    
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        customer_form = CustomerProfileForm(request.POST, instance=customer)
        
        if user_form.is_valid() and customer_form.is_valid():
            user_form.save()
            customer_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        user_form = UserProfileForm(instance=request.user)
        customer_form = CustomerProfileForm(instance=customer)
    
    # Get user's recent orders
    recent_orders = customer.order_set.all()[:5]
    
    context = {
        'user_form': user_form,
        'customer_form': customer_form,
        'recent_orders': recent_orders,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def order_history(request):
    """
    User's complete order history
    """
    orders = request.user.customer.order_set.all().order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/order_history.html', context)
