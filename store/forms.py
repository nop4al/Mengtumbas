from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from store.models import Customer, Review

class CustomUserCreationForm(UserCreationForm):
    """
    Custom registration form dengan additional fields
    Implementasi dari Form Inheritance
    """
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(max_length=30, required=True, label="Nama Depan")
    last_name = forms.CharField(max_length=30, required=True, label="Nama Belakang")
    
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
        labels = {
            'username': 'Nama Pengguna',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Styling dengan Tailwind classes dan placeholder bahasa Indonesia
        field_attrs = {
            'username': {'placeholder': 'Masukkan nama pengguna'},
            'first_name': {'placeholder': 'Masukkan nama depan'},
            'last_name': {'placeholder': 'Masukkan nama belakang'},
            'email': {'placeholder': 'contoh@email.com'},
            'password1': {'placeholder': 'Masukkan kata sandi'},
            'password2': {'placeholder': 'Konfirmasi kata sandi'},
        }
        
        # Update field labels
        self.fields['password1'].label = 'Kata Sandi'
        self.fields['password2'].label = 'Konfirmasi Kata Sandi'
        
        for field_name, field in self.fields.items():
            attrs = {
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent'
            }
            if field_name in field_attrs:
                attrs.update(field_attrs[field_name])
            field.widget.attrs.update(attrs)
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom login form dengan styling
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update field labels
        self.fields['username'].label = 'Nama Pengguna'
        self.fields['password'].label = 'Kata Sandi'
        
        # Update placeholders dan styling
        field_attrs = {
            'username': {'placeholder': 'Masukkan nama pengguna'},
            'password': {'placeholder': 'Masukkan kata sandi'},
        }
        
        for field_name, field in self.fields.items():
            attrs = {
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent'
            }
            if field_name in field_attrs:
                attrs.update(field_attrs[field_name])
            field.widget.attrs.update(attrs)

class CustomerProfileForm(forms.ModelForm):
    """
    Form untuk update customer profile
    """
    class Meta:
        model = Customer
        fields = ['phone', 'address', 'date_of_birth']
        labels = {
            'phone': 'Nomor Telepon',
            'address': 'Alamat',
            'date_of_birth': 'Tanggal Lahir',
        }
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Masukkan alamat lengkap'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update placeholders
        self.fields['phone'].widget.attrs['placeholder'] = 'Contoh: 08123456789'
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent'
            })

class UserProfileForm(forms.ModelForm):
    """
    Form untuk update user profile
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nama Depan',
            'last_name': 'Nama Belakang',
            'email': 'Email',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update placeholders
        field_attrs = {
            'first_name': {'placeholder': 'Masukkan nama depan'},
            'last_name': {'placeholder': 'Masukkan nama belakang'},
            'email': {'placeholder': 'contoh@email.com'},
        }
        
        for field_name, field in self.fields.items():
            attrs = {
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent'
            }
            if field_name in field_attrs:
                attrs.update(field_attrs[field_name])
            field.widget.attrs.update(attrs)

class ReviewForm(forms.ModelForm):
    """
    Form untuk customer review
    """
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        labels = {
            'rating': 'Rating',
            'comment': 'Komentar',
        }
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Bintang') for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Bagikan pengalaman Anda dengan produk ini...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent'
        })
        self.fields['comment'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent'
        })
