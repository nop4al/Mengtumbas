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

## Instalasi Lokal

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

4. Buat file .env di root project (lihat .env.example untuk contoh)

5. Jalankan migrasi database
```bash
python manage.py migrate
```

6. Buat superuser
```bash
python manage.py createsuperuser
```

7. Jalankan server development
```bash
python manage.py runserver
```

## Deployment ke Render

### Opsi 1: Deployment Menggunakan render.yaml

1. Pastikan repository project ada di GitHub

2. Kunjungi [Render Dashboard](https://dashboard.render.com/)

3. Klik "New" dan pilih "Blueprint"

4. Hubungkan dengan GitHub repository Anda

5. Render akan otomatis mendeteksi file `render.yaml` dan membuat layanan sesuai konfigurasi

6. Klik "Apply" untuk memulai deployment

### Opsi 2: Deployment Manual

1. Kunjungi [Render Dashboard](https://dashboard.render.com/)

2. Klik "New" dan pilih "Web Service"

3. Hubungkan dengan GitHub repository Anda

4. Isi konfigurasi berikut:
   - **Name**: mengtumbas (atau nama yang diinginkan)
   - **Runtime**: Python
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn mengtumbas_store.wsgi:application --bind 0.0.0.0:$PORT`

5. Tambahkan Environment Variable berikut:
   - `DATABASE_URL`: Akan otomatis diberikan jika menggunakan PostgreSQL dari Render
   - `SECRET_KEY`: Generate nilai rahasia (misal: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
   - `DJANGO_DEBUG`: `False`
   - `DJANGO_ALLOWED_HOSTS`: `your-app-name.onrender.com,localhost,127.0.0.1`
   - `PORT`: `10000`

6. Klik "Create Web Service"

## Setelah Deployment

1. Jalankan migrasi database:
```bash
python manage.py migrate
```

2. Buat superuser baru:
```bash
python manage.py createsuperuser
```

3. (Opsional) Load data sampel:
```bash
python manage.py loaddata store/fixtures/sample_data.json
```

## Pertanyaan dan Bantuan

Untuk pertanyaan lebih lanjut, silahkan buka issue di GitHub atau hubungi kontributor project.