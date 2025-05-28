from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Signals untuk auto-create Customer ketika User dibuat
@receiver(post_save, sender=User)
def create_customer(sender, instance, created, **kwargs):
    """
    Signal untuk membuat Customer otomatis ketika User dibuat
    Implementasi dari Observer Pattern
    """
    if created:
        from store.models import Customer
        Customer.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_customer(sender, instance, **kwargs):
    """
    Signal untuk save Customer ketika User di-save
    """
    try:
        instance.customer.save()
    except:
        # Jika Customer belum ada, buat yang baru
        from store.models import Customer
        Customer.objects.create(user=instance)
