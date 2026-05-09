import os
import sys
import json
import shlex
import logging
import requests
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.utils.exporter import save_to_excel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GrabFoodScraper:
    def __init__(self, curl_file="grab_curl.txt"):
        self.curl_file = curl_file
        
    def parse_curl_shlex(self, curl_cmd):
        # Membersihkan string jika ada line breaks
        curl_cmd = curl_cmd.replace('\\\n', ' ').strip()
        tokens = shlex.split(curl_cmd)
        
        headers = {}
        data = None
        url = ""
        
        for i, token in enumerate(tokens):
            if token.startswith("http"):
                url = token
            elif token == "-H" or token == "--header":
                header_str = tokens[i+1]
                if ':' in header_str:
                    key, val = header_str.split(':', 1)
                    headers[key.strip()] = val.strip()
            elif token == "-b" or token == "--cookie":
                cookie_str = tokens[i+1]
                if 'cookie' in headers:
                    headers['cookie'] += f"; {cookie_str}"
                else:
                    headers['cookie'] = cookie_str
            elif token == "--data-raw" or token == "--data" or token == "-d":
                data_str = tokens[i+1]
                try:
                    data = json.loads(data_str)
                except Exception as e:
                    logging.warning(f"Gagal parse JSON body dari cURL: {e}")
                    data = data_str
                    
        return url, headers, data

    def check_total_restaurants(self, latlng_str):
        if not os.path.exists(self.curl_file):
            return 0
            
        with open(self.curl_file, "r", encoding="utf-8") as f:
            curl_cmd = f.read().strip()
            
        url, headers, payload = self.parse_curl_shlex(curl_cmd)
        
        if 'accept-encoding' in headers:
            del headers['accept-encoding']
            
        payload["latlng"] = latlng_str
        payload["offset"] = 0
        payload["pageSize"] = 1
        
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("searchResult", {}).get("totalCount", 0)
        except Exception:
            pass
        return 0

    def check_total_restaurants(self, latlng_str):
        if not os.path.exists(self.curl_file):
            return 0
            
        with open(self.curl_file, "r", encoding="utf-8") as f:
            curl_cmd = f.read().strip()
            
        url, headers, payload = self.parse_curl_shlex(curl_cmd)
        
        if 'accept-encoding' in headers:
            del headers['accept-encoding']
            
        payload["latlng"] = latlng_str
        payload["offset"] = 0
        payload["pageSize"] = 1
        
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("searchResult", {}).get("totalCount", 0)
        except Exception:
            pass
        return 0

    def scrape_by_curl(self, latlng_str=None, location_name="Jambi", max_results=500, delay_seconds=5.0):
        if not os.path.exists(self.curl_file):
            logging.error(f"File {self.curl_file} tidak ditemukan!")
            return []
            
        with open(self.curl_file, "r", encoding="utf-8") as f:
            curl_cmd = f.read().strip()
            
        if not curl_cmd.startswith("curl"):
            logging.error(f"Isi file {self.curl_file} tidak valid. Harus dimulai dengan 'curl'.")
            return []
            
        logging.info("Membedah perintah cURL...")
        url, headers, payload = self.parse_curl_shlex(curl_cmd)
        
        if not url or not payload or not isinstance(payload, dict):
            logging.error("Gagal mengekstrak URL atau JSON Body dari cURL. Pastikan yang dicopy adalah cURL (bash) dari request 'search'.")
            return []
            
        logging.info(f"Berhasil mengekstrak Headers ({len(headers)} item) dan payload pencarian.")
        
        # Override header yang mungkin bikin error karena decompress
        if 'accept-encoding' in headers:
            del headers['accept-encoding']
            
        # Override latlng jika diberikan
        if latlng_str:
            payload["latlng"] = latlng_str
            
        results = []
        offset = 0
        page_size = payload.get("pageSize", 32)
        
        logging.info("Memulai ekstraksi data via API GrabFood...")
        session = requests.Session()
        
        while True:
            logging.info(f"Mengambil data (Offset: {offset})...")
            
            # Update payload offset
            payload["offset"] = offset
            
            try:
                response = session.post(url, headers=headers, json=payload, timeout=15)
                
                if response.status_code != 200:
                    logging.error(f"API Error {response.status_code}: {response.text}")
                    break
                    
                data = response.json()
                
                search_result = data.get("searchResult", {})
                merchants = search_result.get("searchMerchants", [])
                
                if not merchants:
                    logging.info("Tidak ada restoran lagi yang dikembalikan oleh API.")
                    break
                    
                logging.info(f"Berhasil menarik {len(merchants)} restoran di batch ini.")
                
                for m in merchants:
                    name = m.get("address", {}).get("name", "-")
                    rating = m.get("rating", "-")
                    
                    latlng_obj = m.get("latlng", {})
                    lat = latlng_obj.get("latitude", "-")
                    lng = latlng_obj.get("longitude", "-")
                    
                    # Ekstrak kategori
                    cuisines = m.get("merchantBrief", {}).get("cuisine", [])
                    kategori = ", ".join(cuisines) if cuisines else "-"
                    
                    link = f"https://food.grab.com/id/en/restaurant/{m.get('id', '')}"
                    
                    results.append({
                        "Platform": "GrabFood",
                        "Lokasi/Kelurahan": location_name,
                        "Nama Usaha": name,
                        "Kategori": kategori,
                        "Rating": rating,
                        "Latitude": lat,
                        "Longitude": lng,
                        "Alamat Lengkap": "-", # Tidak ada di response search
                        "Link URL": link
                    })
                    
                # Increment offset
                offset += len(merchants)
                
                if len(results) >= max_results:
                    logging.info(f"Mencapai target batas maksimal {max_results} restoran.")
                    break
                    
            except Exception as e:
                logging.error(f"Request failed: {e}")
                break

        # ==========================================
        # FASE 2: DEEP SCRAPING UNTUK ALAMAT LENGKAP
        # ==========================================
        logging.info("="*50)
        logging.info(f"Fase 1 Selesai. Ditemukan {len(results)} restoran.")
        logging.info("Memulai FASE 2: Deep Scraping untuk mengambil Alamat Lengkap...")
        logging.info("Proses ini akan membuka data setiap restoran satu per satu (bisa memakan waktu beberapa menit).")
        logging.info("="*50)
        
        # Ekstrak base API URL dari URL pencarian (misal portal.grab.com/foodweb/guest/v2)
        api_base = url.split('/search')[0]
        
        for i, res in enumerate(results):
            try:
                merchant_id = res["Link URL"].split("/")[-1]
                detail_url = f"{api_base}/merchants/{merchant_id}"
                
                max_retries = 3
                for attempt in range(max_retries):
                    resp = session.get(detail_url, headers=headers, timeout=10)
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        merchant_data = data.get("merchant", {})
                        address_obj = merchant_data.get("address", {})
                        
                        full_address = address_obj.get("combined_address") or address_obj.get("street") or "-"
                        res["Alamat Lengkap"] = full_address
                        break # Sukses, keluar dari loop retry
                        
                    elif resp.status_code == 429:
                        wait_time = 5 * (attempt + 1)
                        logging.warning(f"Terkena Limit 429 (Too Many Requests). Istirahat {wait_time} detik...")
                        time.sleep(wait_time)
                        if attempt == max_retries - 1:
                            res["Alamat Lengkap"] = "Gagal (429 Limit)"
                            
                    else:
                        res["Alamat Lengkap"] = f"Gagal (Status: {resp.status_code})"
                        break
                
                # Kasih jeda sesuai input user untuk mencegah blokir
                time.sleep(delay_seconds)
                
                # Log progres
                if (i + 1) % 20 == 0 or i == 0 or i == len(results) - 1:
                    logging.info(f"Progress Deep Scraping: [{i+1}/{len(results)}] -> {res['Nama Usaha']}")
                    
            except Exception as e:
                res["Alamat Lengkap"] = "Error Timeout/Jaringan"
                logging.debug(f"Gagal scrape alamat untuk {res['Nama Usaha']}: {e}")

        logging.info(f"Selesai! Total {len(results)} restoran berhasil diekstrak beserta alamat lengkapnya.")
        return results

if __name__ == "__main__":
    scraper = GrabFoodScraper()
    data = scraper.scrape_by_curl(max_results=500)
    if data:
        file_path = save_to_excel(data, platform_name="GrabFood")
        print(f"\nProses selesai. Cek file hasil di: {file_path}")
    else:
        print("\nTidak ada data yang berhasil diambil.")
