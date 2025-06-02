# Mengtumbas - Aplikasi E-Commerce

Final Project Pemrograman Berbasis Objek
Teknik Informatika - Universitas Negeri Surabaya

## Deskripsi
Mengtumbas adalah aplikasi e-commerce yang dibangun menggunakan Django Framework. Aplikasi ini memungkinkan pengguna untuk membeli produk secara online dengan mudah dan aman.

## Fitur

- Autentikasi pengguna (login, register, logout)
- Manajemen produk dan kategori
- Keranjang belanja
- Sistem pemesanan
- Review produk
- Dashboard admin
- Responsive design

## Instalasi

1. Clone repository ini
```bash
git clone https://github.com/username/mengtumbas.git
cd mengtumbas
```

2. Buat virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Jalankan migrasi database
```bash
python manage.py migrate
```

5. Buat superuser
```bash
python manage.py createsuperuser
```

6. Jalankan server development
```bash
python manage.py runserver
```