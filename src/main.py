import os
import sys

from scrapers.grabfood import GrabFoodScraper
from utils.exporter import save_to_excel

def get_locations(filepath="data/lokasi_jambi.txt"):
    if not os.path.exists("data"):
        os.makedirs("data")
        
    if not os.path.exists(filepath):
        # Buat default jika tidak ada
        default_content = """Bagan Pete | -1.635000,103.560000
Jelutung | -1.611111,103.600000
Telanaipura | -1.590000,103.580000
Kotabaru | -1.625000,103.590000
Jambi Selatan | -1.629342,103.630018
Jambi Timur | -1.583162,103.626884"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(default_content)
            
    locations = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if "|" in line:
                name, latlng = line.split("|")
                locations.append({
                    "name": name.strip(),
                    "latlng": latlng.strip()
                })
    return locations

def main():
    print("\n" + "="*60)
    print(" GRABFOOD SCRAPER (cURL Interceptor & Multi-Location)")
    print("="*60)
    
    curl_file = "grab_curl.txt"
    if not os.path.exists(curl_file):
        print(f"File '{curl_file}' TIDAK DITEMUKAN!")
        print("Membuat file kosong 'grab_curl.txt'...")
        with open(curl_file, "w", encoding="utf-8") as f:
            f.write("")
            
        print("\nINSTRUKSI PENTING:")
        print("1. Buka Google Chrome biasa, buka food.grab.com.")
        print("2. Cari lokasi kotamu sampai daftar restoran muncul.")
        print("3. Tekan F12 -> tab Network.")
        print("4. Scroll halaman GrabFood ke bawah agar request 'search' muncul.")
        print("5. Klik kanan pada request 'search' -> Copy -> Copy as cURL (bash).")
        print("6. Paste hasilnya ke dalam file 'grab_curl.txt'.")
        print("7. Jalankan ulang script ini!")
        sys.exit(0)

    scraper = GrabFoodScraper(curl_file=curl_file) 
    
    # 1. Muat Lokasi
    print("Memuat daftar lokasi dan mengecek ketersediaan data di GrabFood...")
    locations = get_locations()
    if not locations:
        print("File data/lokasi_jambi.txt kosong. Silakan isi terlebih dahulu.")
        sys.exit(0)
        
    # 2. PING setiap lokasi untuk mendapatkan Total Count
    for i, loc in enumerate(locations):
        print(f"Mengecek {loc['name']}...", end="\r")
        total = scraper.check_total_restaurants(loc['latlng'])
        loc['total'] = total
        
    print("Pengecekan selesai!                                  \n")
    
    # 3. Tampilkan Menu
    print("="*50)
    print(" PILIH LOKASI KELURAHAN / KECAMATAN")
    print("="*50)
    for i, loc in enumerate(locations):
        print(f"[{i+1}] {loc['name'].ljust(20)} (Ada {loc['total']} Restoran)")
    print(f"[{len(locations)+1}] Ambil Semua Lokasi Sekaligus!")
    print("[0] Batal & Keluar")
    print("="*50)
    
    pilihan_str = input("Masukkan nomor pilihan (bisa koma, misal: 1,3) [0]: ")
    if not pilihan_str or pilihan_str.strip() == "0":
        print("Dibatalkan.")
        sys.exit(0)
        
    selected_locs = []
    if str(len(locations)+1) in pilihan_str.split(","):
        selected_locs = locations
    else:
        for idx in pilihan_str.split(","):
            try:
                i = int(idx.strip()) - 1
                if 0 <= i < len(locations):
                    selected_locs.append(locations[i])
            except ValueError:
                pass
                
    if not selected_locs:
        print("Pilihan tidak valid.")
        sys.exit(0)

    try:
        print("\n--- PENGATURAN KECEPATAN SCRAPING ---")
        print("Makin cepat = makin rawan error 429. Makin lambat = makin aman.")
        delay_input = input("Masukkan jeda waktu per detik untuk setiap restoran (Misal: 3 atau 5) [Default: 3]: ")
        delay_seconds = float(delay_input) if delay_input.strip() else 3.0
    except ValueError:
        print("Input tidak valid, menggunakan default 3 detik.")
        delay_seconds = 3.0
    except KeyboardInterrupt:
        print("\nDibatalkan oleh pengguna.")
        sys.exit(0)

    # 4. Scraping Loop
    all_data = []
    for loc in selected_locs:
        if loc['total'] == 0:
            print(f"\nMelewati {loc['name']} karena tidak ada restoran (atau curl kadaluarsa).")
            continue
            
        print(f"\n==================================================")
        print(f" MENARIK DATA: {loc['name'].upper()}")
        print(f"==================================================")
        
        data = scraper.scrape_by_curl(latlng_str=loc['latlng'], location_name=loc['name'], max_results=500, delay_seconds=delay_seconds)
        all_data.extend(data)
        
    if all_data:
        file_path = save_to_excel(all_data, platform_name="GrabFood_Multi")
        print(f"\nProses selesai secara keseluruhan! Total {len(all_data)} restoran ditarik.")
        print(f"Cek file hasil di: {file_path}")
    else:
        print("\nTidak ada data yang berhasil diambil secara keseluruhan.")

if __name__ == "__main__":
    main()
