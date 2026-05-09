import pandas as pd
import os
from datetime import datetime
import logging

def save_to_excel(data, platform_name, output_dir="data/processed/"):
    """
    Menyimpan data scraping ke dalam format Excel (.xlsx).
    """
    if not data:
        logging.warning("Tidak ada data untuk disimpan ke Excel.")
        return None

    # Pastikan direktori ada
    os.makedirs(output_dir, exist_ok=True)

    # Buat nama file dengan timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{platform_name}_results_{timestamp}.xlsx"
    filepath = os.path.join(output_dir, filename)

    try:
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False, engine='openpyxl')
        logging.info(f"Data berhasil disimpan ke: {filepath}")
        return filepath
    except Exception as e:
        logging.error(f"Gagal menyimpan data ke Excel: {e}")
        return None
