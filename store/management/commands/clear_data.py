from django.core.management.base import BaseCommand
from store.models import Category, Product, Cart, CartItem, Order, OrderItem, Review

class Command(BaseCommand):
    help = 'Clears all store data while preserving users and admin configuration'

    def handle(self, *args, **kwargs):
        # Clear reviews first because they reference products
        self.stdout.write('Deleting reviews...')
        Review.objects.all().delete()

        # Clear carts and cart items
        self.stdout.write('Deleting cart items and carts...')
        CartItem.objects.all().delete()
        Cart.objects.all().delete()

        # Clear orders and order items
        self.stdout.write('Deleting order items and orders...')
        OrderItem.objects.all().delete()
        Order.objects.all().delete()

        # Clear products and categories
        self.stdout.write('Deleting products...')
        Product.objects.all().delete()
        self.stdout.write('Deleting categories...')
        Category.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Successfully cleared all store data!'))
