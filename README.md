# GrabFood Deep Scraper 🍔

Alat otomatis (berbasis Python) untuk melakukan ekstraksi data *scraping* skala besar dari platform **GrabFood**. Mengambil informasi restoran, kategori, rating, titik koordinat, dan menyedot **Alamat Lengkap** restoran.

## 🔥 Fitur Utama
* **Universal cURL Interceptor:** Sistem 100% *Anti-Bot* yang memanfaatkan *Cookie* dan token otentikasi (JWT) asli milikmu. Memungkinkan skrip untuk berkeliling Indonesia tanpa perlu membuka *browser*!
* **Multi-Location Pinging:** Mampu mendeteksi dan menghitung total restoran di berbagai kelurahan/kecamatan yang kamu tentukan sebelum proses pengambilan data dimulai.
* **Deep Scraping:** Fitur cerdas untuk membuka "pintu belakang" API setiap restoran guna mengambil **Alamat Lengkap** (nama jalan, patokan, dll) yang biasanya disembunyikan oleh GrabFood di halaman pencarian awal.
* **Smart Rate Limiter:** Sistem rem otomatis (*Auto-Retry* & *Custom Delay*) untuk melewati perlindungan WAF dan batas *Too Many Requests (429)* dari server Grab.
* **Ekspor Excel Otomatis:** Semua data digabungkan, disortir, dan diekspor ke dalam format `.xlsx` yang siap pakai.

## 🛠 Persyaratan Sistem
- OS: Windows / macOS / Linux
- Python 3.9 atau lebih baru

## 🚀 Instalasi

1. **Clone repository ini**
   ```bash
   git clone https://github.com/username-anda/scrap-e-commerce.git
   cd scrap-e-commerce
   ```

2. **Buat Virtual Environment (Sangat Disarankan)**
   ```bash
   python -m venv .venv
   # Di Windows:
   .\.venv\Scripts\activate
   # Di macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Cara Penggunaan (Tutorial cURL & Cookies)

GrabFood menerapkan perlindungan *anti-bot* yang sangat ketat. Oleh karena itu, *script* ini bekerja dengan cara "meminjam" sesi (*Cookies*) dari *browser* aslimu. 

**Langkah 1: Mendapatkan Sesi cURL (Cookie)**
1. Buka Google Chrome biasa di komputermu, masuk ke `food.grab.com`.
2. Lakukan pencarian lokasi secara acak (misal: "Jambi") sampai daftar restoran muncul di layarmu.
3. Tekan tombol **F12** di keyboard untuk membuka *Developer Tools*, lalu masuk ke tab **Network**.
4. Di *web* GrabFood, *scroll* halamannya sedikit ke bawah agar Chrome mengirimkan permintaan data baru ke *server*.
5. Di daftar *Network*, cari dan temukan *request* bernama `search`.
6. Klik kanan pada `search` tersebut -> pilih **Copy** -> pilih **Copy as cURL (bash)**.

**Langkah 2: Menjalankan Skrip**
1. Buat file baru bernama `grab_curl.txt` di folder utama (root) proyek ini.
2. *Paste* (tempelkan) hasil *copy* cURL tadi ke dalam file `grab_curl.txt`, lalu *Save*.
3. Buka terminalmu dan jalankan:
   ```bash
   python src/main.py
   ```
4. Jika berhasil, program akan otomatis membaca daftar lokasi dari file `data/lokasi_jambi.txt` dan memunculkan menu pilihan ganda kelurahan mana yang ingin disedot datanya!

*(Tips: Kamu bisa mengedit file `data/lokasi_jambi.txt` untuk menambah nama kecamatan atau kota lain beserta titik Latitude & Longitudenya)*

## 📂 Struktur Folder
```text
📦 scrap-e-commerce
 ┣ 📂 data
 ┃ ┣ 📂 processed/       # Hasil output .xlsx
 ┃ ┗ 📜 lokasi_jambi.txt # Database lokasi & koordinat (Bisa diedit!)
 ┣ 📂 src
 ┃ ┣ 📂 scrapers/        # Logika scraping (grabfood.py)
 ┃ ┣ 📂 utils/           # Utilitas (exporter.py)
 ┃ ┗ 📜 main.py          # Entry point utama & Menu CLI
 ┣ 📜 .gitignore         # Perlindungan data sensitif
 ┣ 📜 requirements.txt
 ┗ 📜 README.md
```

## ⚠️ Peringatan Keamanan & Privasi (SANGAT PENTING!)
* File `grab_curl.txt` berisi **Cookie, Session ID, dan Token JWT pribadi** milik akun komputermu!
* **JANGAN PERNAH** membagikan isi file `grab_curl.txt` kepada siapa pun atau mengunggahnya ke repositori publik (GitHub/GitLab). Jika ada yang mendapatkan file tersebut, mereka bisa meniru sesimu.
* Repositori ini telah dilengkapi dengan aturan `.gitignore` yang ketat. File bernama `grab_curl.txt` sudah otomatis ditolak oleh Git sehingga **mustahil** terunggah (ter-push) ke GitHub, menjaga privasimu tetap 100% aman.

## ⚖️ Disclaimer
Proyek ini dibuat **sepenuhnya untuk tujuan riset dan pembelajaran (edukasi)**. Penyalahgunaan skrip ini untuk melakukan ekstraksi data yang merugikan atau melanggar *Terms of Service* (ToS) platform terkait berada sepenuhnya di luar tanggung jawab pengembang.
