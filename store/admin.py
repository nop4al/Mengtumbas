from django.contrib import admin
from .models import Category, Product, Customer, Cart, CartItem, Order, OrderItem, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'origin_type', 'parent', 'get_slug', 'get_product_count', 'is_active', 'get_created_at']
    list_filter = ['origin_type', 'is_active', 'parent', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['origin_type', 'is_active']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')

    def get_name(self, obj):
        return obj.get_full_name()
    get_name.short_description = 'Nama Kategori'
    
    def get_slug(self, obj):
        return obj.slug
    get_slug.short_description = 'Slug'
    
    def get_is_active(self, obj):
        return obj.is_active
    get_is_active.short_description = 'Aktif'
    get_is_active.boolean = True
    
    def get_created_at(self, obj):
        return obj.created_at.strftime('%d %b %Y')
    get_created_at.short_description = 'Dibuat Pada'
    
    def get_product_count(self, obj):
        return obj.get_product_count()
    get_product_count.short_description = 'Jumlah Produk'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_category', 'price', 'stock', 'featured', 'is_active', 'get_created_at']
    list_filter = ['category', 'featured', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock', 'featured', 'is_active']
    
    def get_category(self, obj):
        return obj.category
    get_category.short_description = 'Kategori'
    
    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Dibuat Pada'

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['get_user', 'get_phone', 'get_address']
    search_fields = ['user__username', 'user__email', 'phone', 'address']
    
    def get_queryset(self, request):
        # Override to only include users who have a customer profile
        return super().get_queryset(request).select_related('user')
    
    def get_user(self, obj):
        return obj.user
    get_user.short_description = 'Pengguna'
    
    def get_phone(self, obj):
        return obj.phone
    get_phone.short_description = 'Nomor Telepon'
    
    def get_address(self, obj):
        return obj.address
    get_address.short_description = 'Alamat'

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['get_customer', 'get_total_items', 'get_total_price', 'get_created_at']
    list_filter = ['created_at']
    inlines = [CartItemInline]
    
    def get_customer(self, obj):
        return obj.customer
    get_customer.short_description = 'Pelanggan'
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Total Item'
    
    def get_total_price(self, obj):
        return f"Rp {obj.get_total_price():,.2f}"
    get_total_price.short_description = 'Total Harga'
    
    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Dibuat Pada'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'status', 'total_amount', 'created_at')
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'customer__user__username']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    def order_number(self, obj):
        return obj.order_number
    order_number.short_description = 'Nomor Pesanan'
    
    def customer(self, obj):
        return obj.customer
    customer.short_description = 'Pelanggan'
    
    def status(self, obj):
        return obj.status
    status.short_description = 'Status'
    
    def total_amount(self, obj):
        return f"Rp {obj.total_amount:,.2f}"
    total_amount.short_description = 'Total'
    
    def created_at(self, obj):
        return obj.created_at
    created_at.short_description = 'Dibuat Pada'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['get_product', 'get_customer', 'get_rating', 'get_created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['comment']
    
    def get_product(self, obj):
        return obj.product
    get_product.short_description = 'Produk'
    
    def get_customer(self, obj):
        return obj.customer
    get_customer.short_description = 'Pelanggan'
    
    def get_rating(self, obj):
        return obj.rating
    get_rating.short_description = 'Penilaian'
    
    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Dibuat Pada'
