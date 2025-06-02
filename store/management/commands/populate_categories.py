from django.core.management.base import BaseCommand
from django.utils.text import slugify
from store.models import Category


class Command(BaseCommand):
    help = 'Populate database with sample categories for local and foreign products'

    def create_unique_slug(self, name, origin_type, parent=None):
        """Generate a unique slug for the category"""
        base_slug = slugify(name)
        slug = f"{origin_type}-{base_slug}"
        if parent:
            slug = f"{parent.slug}-{base_slug}"
        
        # Check if slug exists and make it unique
        counter = 1
        original_slug = slug
        while Category.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1
        return slug

    def handle(self, *args, **options):
        self.stdout.write('Populating categories...')
        
        # Local Products (Barang Lokal) Categories
        local_categories = {
            'Makanan & Minuman Lokal': [
                'Makanan Tradisional',
                'Minuman Tradisional',
                'Camilan Lokal',
                'Rempah-rempah',
                'Kopi & Teh Lokal'
            ],
            'Pakaian & Fashion Lokal': [
                'Batik',
                'Tenun',
                'Pakaian Adat',
                'Sepatu Lokal',
                'Aksesoris Tradisional'
            ],
            'Kerajinan Tangan': [
                'Keramik & Gerabah',
                'Ukiran Kayu',
                'Anyaman',
                'Perhiasan Tradisional',
                'Seni Lukis'
            ],
            'Produk Pertanian': [
                'Beras Lokal',
                'Sayuran Organik',
                'Buah-buahan Lokal',
                'Hasil Kebun',
                'Produk Olahan Pertanian'
            ],
            'Perawatan & Kecantikan Lokal': [
                'Jamu Tradisional',
                'Kosmetik Herbal',
                'Sabun Natural',
                'Minyak Tradisional',
                'Perawatan Kulit Alami'
            ]
        }
        
        # Foreign Products (Barang Asing) Categories
        foreign_categories = {
            'Elektronik': [
                'Smartphone',
                'Laptop & Komputer',
                'Audio & Video',
                'Gaming',
                'Aksesoris Elektronik'
            ],
            'Fashion Import': [
                'Pakaian Branded',
                'Sepatu Import',
                'Tas & Dompet',
                'Jam Tangan',
                'Kacamata'
            ],
            'Makanan & Minuman Import': [
                'Makanan Beku',
                'Snack Import',
                'Minuman Import',
                'Makanan Kaleng',
                'Permen & Coklat'
            ],
            'Produk Kecantikan Import': [
                'Skincare Korea',
                'Makeup Import',
                'Parfum',
                'Perawatan Rambut',
                'Suplemen Kecantikan'
            ],
            'Peralatan Rumah Tangga': [
                'Peralatan Masak',
                'Peralatan Kebersihan',
                'Dekorasi Rumah',
                'Furniture',
                'Peralatan Elektronik Rumah'
            ],
            'Olahraga & Rekreasi': [
                'Peralatan Fitness',
                'Sepatu Olahraga',
                'Pakaian Olahraga',
                'Outdoor Gear',
                'Mainan & Hobi'
            ]
        }
        
        # Create local categories
        self.stdout.write('Creating local categories...')
        for main_cat_name, subcats in local_categories.items():
            # Create or get main category
            main_cat, created = Category.objects.get_or_create(
                name=main_cat_name,
                origin_type='local',
                defaults={'description': f'Kategori utama untuk {main_cat_name}'}
            )
            if created:
                self.stdout.write(f'  Created main category: {main_cat_name}')
            
            # Create subcategories
            for subcat_name in subcats:
                subcat, created = Category.objects.get_or_create(
                    name=subcat_name,
                    origin_type='local',
                    parent=main_cat,
                    defaults={'description': f'Subkategori {subcat_name} dalam {main_cat_name}'}
                )
                if created:
                    self.stdout.write(f'    Created subcategory: {subcat_name}')
        
        # Create foreign categories
        self.stdout.write('Creating foreign categories...')
        for main_cat_name, subcats in foreign_categories.items():
            # Create or get main category
            main_cat, created = Category.objects.get_or_create(
                name=main_cat_name,
                origin_type='foreign',
                defaults={'description': f'Kategori utama untuk {main_cat_name}'}
            )
            if created:
                self.stdout.write(f'  Created main category: {main_cat_name}')
            
            # Create subcategories
            for subcat_name in subcats:
                subcat, created = Category.objects.get_or_create(
                    name=subcat_name,
                    origin_type='foreign',
                    parent=main_cat,
                    defaults={'description': f'Subkategori {subcat_name} dalam {main_cat_name}'}
                )
                if created:
                    self.stdout.write(f'    Created subcategory: {subcat_name}')
        
        # Update existing category if needed
        existing_cat = Category.objects.filter(name='Kebutuhan Sehari-Hari').first()
        if existing_cat and not existing_cat.origin_type:
            existing_cat.origin_type = 'local'
            existing_cat.save()
            self.stdout.write('Updated existing category: Kebutuhan Sehari-Hari')
        
        # Display summary
        local_count = Category.objects.filter(origin_type='local').count()
        foreign_count = Category.objects.filter(origin_type='foreign').count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCategories populated successfully!\n'
                f'Local categories: {local_count}\n'
                f'Foreign categories: {foreign_count}\n'
                f'Total categories: {local_count + foreign_count}'
            )
        )
