# Generated by Django 5.2.1 on 2025-06-01 05:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_wishlist'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='customer',
            name='first_name',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='customer',
            name='last_name',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='order',
            name='is_guest_order',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='customer',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
