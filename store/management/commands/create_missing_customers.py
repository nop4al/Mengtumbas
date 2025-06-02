from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Customer


class Command(BaseCommand):
    help = 'Create Customer objects for Users that don\'t have them'

    def handle(self, *args, **kwargs):
        users_without_customers = User.objects.filter(customer__isnull=True)
        count = users_without_customers.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No users without customers found.'))
            return
            
        self.stdout.write(f'Found {count} users without customer profiles.')
        
        for user in users_without_customers:
            Customer.objects.create(user=user)
            self.stdout.write(f'Created customer for user: {user.username}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} customer profiles.'))
