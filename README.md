# Portofolio Pribadi (UIkit & Flask)

![Tangkapan Layar Utama Proyek](https://res.cloudinary.com/dzsqaauqn/image/upload/v1754044714/Screenshot_2025-08-01_173704_dp1n45.jpg)

Proyek ini adalah aplikasi portofolio pribadi yang dibangun menggunakan kerangka kerja Python Flask. Proyek ini dirancang untuk menampilkan proyek-proyek Anda secara dinamis dari database MongoDB, dengan antarmuka yang bersih dan responsif berkat framework UIkit CSS.

## Fitur Utama

* **Tampilan Proyek Dinamis**: Mengelola dan menampilkan proyek-proyek dari database MongoDB.
* **Antarmuka Admin**: Halaman login yang aman untuk menambah, mengedit, dan menghapus proyek.
* **Penyimpanan Gambar Cloud**: Menggunakan Cloudinary untuk mengunggah dan mengelola gambar proyek secara efisien.
* **Formulir Kontak**: Formulir kontak yang berfungsi penuh dengan notifikasi email (menggunakan Flask-Mail).
* **Desain Responsif**: Antarmuka yang dioptimalkan untuk perangkat desktop, tablet, dan mobile, dibangun dengan UIkit CSS.
* **SEO-Friendly**: Termasuk `sitemap.xml` dan `robots.txt` yang dibuat secara dinamis, serta tag SEO (Open Graph) untuk setiap halaman proyek.
* **Penanganan Kesalahan**: Halaman kesalahan kustom untuk `404 Not Found` dan `500 Internal Server Error`.

## Teknologi

* **Backend**: Python, Flask
* **Database**: MongoDB (dengan `pymongo`)
* **Frontend**: HTML5, CSS3, JavaScript
* **Framework CSS**: [UIkit](https://getuikit.com/)
* **Manajemen Gambar**: [Cloudinary](https://cloudinary.com/)
* **Email**: [Flask-Mail](https://pythonhosted.org/Flask-Mail/)
* **Login**: [Flask-Login](https://flask-login.readthedocs.io/en/latest/)

## Instalasi dan Setup Lokal

Ikuti langkah-langkah di bawah ini untuk menjalankan proyek di lingkungan lokal Anda.

### Prasyarat

* Python 3.8+
* `pip` (pengelola paket Python)
* Akun MongoDB Atlas atau instance lokal.
* Akun Cloudinary.

### Langkah-langkah

1.  **Clone repositori:**
    ```bash
    git clone [https://github.com/](https://github.com/)[username]/portofolio-uikit-css.git
    cd portofolio-uikit-css
    ```

2.  **Buat virtual environment dan aktifkan:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Untuk Linux/macOS
    # venv\Scripts\activate  # Untuk Windows
    ```

3.  **Instal dependensi:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Konfigurasi Variabel Lingkungan:**
    Buat file `.env` di direktori root proyek dan isi dengan kredensial Anda.
    ```env
    MONGO_URI='mongodb+srv://[username]:[password]@clustername.mongodb.net/UIkit_CSS_db'
    CLOUDINARY_CLOUD_NAME='[nama_cloud_anda]'
    CLOUDINARY_API_KEY='[kunci_api]'
    CLOUDINARY_API_SECRET='[rahasia_api]'
    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USERNAME='[email_anda]@gmail.com'
    MAIL_PASSWORD='[kata_sandi_aplikasi_gmail_anda]'
    SECRET_KEY='[kunci_rahasia_acak_yang_kuat]'
    ```

5.  **Buat Pengguna Admin:**
    tambahkan kode ini di app.py
    ```python
    @app.cli.command('create-admin')
    def create_admin():
        username = input("Enter admin username: ")
        password = input("Enter admin password: ")
        hashed_password = generate_password_hash(password)
        
        if users_collection.find_one({'username': username}):
            print("Admin user already exists.")
        else:
            users_collection.insert_one({'username': username, 'password': hashed_password})
            print(f"Admin user '{username}' created successfully.")
    ```
    Gunakan perintah CLI khusus untuk membuat pengguna admin pertama.
    ```bash
    flask create-admin
    ```
    Ikuti petunjuk di terminal untuk memasukkan nama pengguna dan kata sandi.

6.  **Jalankan Aplikasi:**
    ```bash
    flask run
    ```
    Aplikasi akan berjalan di `http://127.0.0.1:5000`.

## Deployment

Proyek ini telah dikonfigurasi untuk deployment ke Vercel. Pastikan Anda memiliki akun Vercel dan file konfigurasi berikut ada di repositori Anda:

* `vercel.json`
* `api/index.py`

Untuk deployment, cukup impor repositori Anda di Vercel dan tambahkan semua variabel lingkungan yang tercantum di atas melalui dashboard Vercel.