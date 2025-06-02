from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [    # Home and product views
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('barang-lokal/', views.local_products, name='local_products'),
    path('barang-asing/', views.foreign_products, name='foreign_products'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    
    # Cart and checkout
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    
    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('order/<str:order_number>/', views.order_detail, name='order_detail'),
    path('order/<str:order_number>/cancel/', views.cancel_order, name='cancel_order'),
    path('order/<str:order_number>/complete/', views.complete_order, name='complete_order'),
    
    # Search
    path('search/', views.search_products, name='search_products'),
    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    # Search API endpoints
    path('api/search-suggestions/', views.api_search_suggestions, name='api_search_suggestions'),
    path('api/search-products/', views.api_search_products, name='api_search_products'),

    # Buy Now functionality
    path('add-to-cart-and-checkout/<int:product_id>/', views.add_to_cart_and_checkout, name='add_to_cart_and_checkout'),

    # Cart API for AJAX updates
    path('get-cart-totals/', views.get_cart_totals, name='get_cart_totals'),
    path('get-guest-cart-totals/', views.get_guest_cart_totals, name='get_guest_cart_totals'),
]
