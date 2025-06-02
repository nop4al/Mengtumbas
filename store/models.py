from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from abc import ABC, abstractmethod
from decimal import Decimal

# Abstract Base Class - Implementasi Abstraction
class BaseModel(models.Model):
    """
    Abstract base class yang mengimplementasikan konsep Abstraction
    Menyediakan field common untuk semua model
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
    
    @abstractmethod
    def get_display_name(self):
        """Abstract method yang harus diimplementasikan oleh subclass"""
        pass

# Category Model - Implementasi Encapsulation dan Inheritance
class Category(BaseModel):
    """
    Model Category yang inherit dari BaseModel
    Mengimplementasikan Encapsulation dengan private attributes
    Mendukung kategorisasi Barang Lokal dan Barang Asing
    """
    ORIGIN_CHOICES = [
        ('local', 'Barang Lokal'),
        ('foreign', 'Barang Asing'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    origin_type = models.CharField(
        max_length=10, 
        choices=ORIGIN_CHOICES, 
        default='local',
        help_text="Pilih apakah kategori ini untuk barang lokal atau asing"
    )
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='subcategories',
        help_text="Kategori induk (opsional untuk subkategori)"
    )
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['origin_type', 'name']
        unique_together = ['name', 'origin_type', 'parent']
    
    def __str__(self):
        if self.parent:
            return f"{self.get_origin_type_display()} - {self.parent.name} > {self.name}"
        return f"{self.get_origin_type_display()} - {self.name}"
    
    def get_display_name(self):
        """Implementation of abstract method"""
        return self.name
    
    def get_absolute_url(self):
        return reverse('store:category_detail', kwargs={'slug': self.slug})
    
    def get_full_name(self):
        """Method untuk mendapatkan nama lengkap dengan hierarki"""
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    # Encapsulation - Method untuk mengakses data yang di-encapsulate
    def get_product_count(self):
        """Method untuk mendapatkan jumlah produk dalam kategori"""
        return self.products.filter(is_active=True).count()
    
    def get_all_products_count(self):
        """Method untuk mendapatkan jumlah semua produk termasuk subkategori"""
        count = self.get_product_count()
        for subcategory in self.subcategories.all():
            count += subcategory.get_all_products_count()
        return count
    
    def is_main_category(self):
        """Check apakah ini kategori utama (tidak punya parent)"""
        return self.parent is None
    
    def get_main_category(self):
        """Dapatkan kategori utama dari kategori ini"""
        if self.parent:
            return self.parent.get_main_category()
        return self

# Product Model - Implementasi Multiple Inheritance concepts
class Product(BaseModel):
    """
    Model Product dengan implementasi OOP principles
    """
    # Konstanta untuk biaya tambahan produk asing
    IMPORT_TAX_RATE = Decimal('0.10')  # 10% pajak impor
    CUSTOMS_FEE = Decimal('50000')  # Rp 50.000 biaya bea cukai
    HANDLING_FEE = Decimal('25000')  # Rp 25.000 biaya penanganan
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    slug = models.SlugField(unique=True)
    featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_display_name(self):
        """Implementation of abstract method"""
        return f"{self.name} - {self.category.name}"
    
    def get_absolute_url(self):
        return reverse('store:product_detail', kwargs={'slug': self.slug})
    
    # Method overloading simulation - different behaviors based on parameters
    def get_price(self, quantity=1, discount_percent=0):
        """
        Method yang mensimulasikan overloading
        Dapat dipanggil dengan parameter berbeda
        """
        base_price = self.price * quantity
        if discount_percent > 0:
            discount = base_price * Decimal(discount_percent / 100)
            return base_price - discount
        return base_price
    
    def is_in_stock(self):
        """Encapsulation - method untuk cek stock"""
        return self.stock > 0
    
    def reduce_stock(self, quantity):
        """Method untuk mengurangi stock"""
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False
    
    def get_final_price(self):
        """Menghitung harga akhir termasuk pajak dan biaya tambahan untuk produk asing"""
        base_price = self.price
        if self.category and self.category.origin_type == 'foreign':
            # Menambahkan pajak impor
            import_tax = base_price * self.IMPORT_TAX_RATE
            # Total harga termasuk semua biaya
            final_price = base_price + import_tax + self.CUSTOMS_FEE + self.HANDLING_FEE
            return final_price
        return base_price

    def get_tax_details(self):
        """Mendapatkan rincian biaya tambahan untuk produk asing"""
        if self.category and self.category.origin_type == 'foreign':
            import_tax = self.price * self.IMPORT_TAX_RATE
            return {
                'base_price': self.price,
                'import_tax': import_tax,
                'customs_fee': self.CUSTOMS_FEE,
                'handling_fee': self.HANDLING_FEE,
                'total_additional': import_tax + self.CUSTOMS_FEE + self.HANDLING_FEE,
                'final_price': self.get_final_price()
            }
        return None

# Customer Model - Inheritance dari User
class Customer(models.Model):
    """
    Model Customer yang extend Django User model
    Implementasi Inheritance dan Encapsulation
    Supports both registered and guest users
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    email = models.EmailField(blank=True)  # For guest users
    first_name = models.CharField(max_length=30, blank=True)  # For guest users  
    last_name = models.CharField(max_length=30, blank=True)  # For guest users
    
    def __str__(self):
        if self.user:
            return self.user.username
        return f"Guest Customer ({self.email or 'No Email'})"
    
    def get_full_name(self):
        """Method untuk mendapatkan nama lengkap"""
        return f"{self.user.first_name} {self.user.last_name}"
    
    def get_display_name(self):
        """Method untuk display name"""
        full_name = self.get_full_name().strip()
        return full_name if full_name else self.user.username

# Cart Model - Implementasi Aggregation
class Cart(BaseModel):
    """
    Model Cart yang mengimplementasikan relationship aggregation
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Cart for {self.customer.user.username}"
    
    def get_display_name(self):
        return f"Cart - {self.customer.get_display_name()}"
    
    def get_total_items(self):
        """Method untuk mendapatkan total items di cart"""
        return sum(item.quantity for item in self.items.all())
    
    def get_total(self):
        """Method untuk mendapatkan total akhir"""
        return self.get_subtotal() + self.get_shipping_cost() - self.get_discount_amount()
    
    def get_subtotal(self):
        """Method untuk mendapatkan subtotal (sebelum shipping dan diskon)"""
        return sum(item.get_total_price() for item in self.items.all())
    
    def get_shipping_cost(self):
        """Method untuk mendapatkan biaya pengiriman"""
        return Decimal('0')  # Gratis ongkir untuk sementara
    
    def get_discount_amount(self):
        """Method untuk mendapatkan jumlah diskon"""
        return Decimal('0')  # Belum ada diskon untuk sementara
    
    def get_total_price(self):
        """Method untuk mendapatkan total harga (alias untuk get_total untuk kompatibilitas)"""
        return self.get_total()
    
    def clear_cart(self):
        """Method untuk mengosongkan cart"""
        self.items.all().delete()

# CartItem Model - Composition relationship
class CartItem(models.Model):
    """
    Model CartItem yang mengimplementasikan composition
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('cart', 'product')
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def get_total_price(self):
        """Method untuk mendapatkan total harga item"""
        # For foreign products, we use the base price without taxes for the subtotal
        # The taxes will be added separately in the checkout
        return self.product.price * self.quantity
    
    def increase_quantity(self, amount=1):
        """Method untuk menambah quantity"""
        self.quantity += amount
        self.save()
    
    def decrease_quantity(self, amount=1):
        """Method untuk mengurangi quantity"""
        if self.quantity > amount:
            self.quantity -= amount
            self.save()
        else:
            self.delete()

# Order Model - Implementasi State Pattern dan Polymorphism
class Order(BaseModel):
    """
    Model Order dengan implementasi State pattern
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    notes = models.TextField(blank=True)
    is_guest_order = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=20, default='cod', blank=True)
    payment_channel = models.CharField(max_length=20, blank=True)
    admin_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    def get_display_name(self):
        return f"Order {self.order_number} - {self.customer.get_display_name()}"
    
    def get_absolute_url(self):
        return reverse('store:order_detail', kwargs={'order_number': self.order_number})
    
    # Polymorphism - different behaviors based on status
    def process_order(self):
        """Method polymorphic berdasarkan status"""
        if self.status == 'pending':
            return self._confirm_order()
        elif self.status == 'confirmed':
            return self._start_processing()
        elif self.status == 'processing':
            return self._ship_order()
        elif self.status == 'shipped':
            return self._deliver_order()
        return False
    
    def _confirm_order(self):
        """Private method untuk confirm order"""
        self.status = 'confirmed'
        self.save()
        return True
    
    def _start_processing(self):
        """Private method untuk start processing"""
        self.status = 'processing'
        self.save()
        return True
    
    def _ship_order(self):
        """Private method untuk ship order"""
        self.status = 'shipped'
        self.save()
        return True
    
    def _deliver_order(self):
        """Private method untuk deliver order"""
        self.status = 'delivered'
        self.save()
        return True
    
    def cancel_order(self):
        """Method untuk cancel order"""
        if self.status in ['pending', 'confirmed']:
            self.status = 'cancelled'
            self.save()
            return True
        return False

# OrderItem Model
class OrderItem(models.Model):
    """
    Model OrderItem untuk menyimpan detail item dalam order
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Harga saat order dibuat
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def get_total_price(self):
        """Method untuk mendapatkan total harga item"""
        return self.price * self.quantity

# Review Model - Additional feature untuk customer feedback
class Review(BaseModel):
    """
    Model Review untuk customer feedback
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('product', 'customer')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.customer.user.username} for {self.product.name}"
    
    def get_display_name(self):
        return f"Review - {self.product.name} ({self.rating} stars)"

# Wishlist Model - Implementasi untuk fitur wishlist
class Wishlist(BaseModel):
    """
    Model Wishlist untuk menyimpan produk yang disukai customer
    """
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField(Product, related_name='wishlists')
    
    def __str__(self):
        return f"Wishlist for {self.customer.user.username}"
    
    def get_display_name(self):
        return f"Wishlist - {self.customer.get_display_name()}"
    
    def add_product(self, product):
        """Add product to wishlist"""
        self.products.add(product)
        
    def remove_product(self, product):
        """Remove product from wishlist"""
        self.products.remove(product)
        
    def has_product(self, product):
        """Check if product is in wishlist"""
        return self.products.filter(id=product.id).exists()
    
    def get_product_count(self):
        """Get number of products in wishlist"""
        return self.products.count()
