"""Rebuild metadata from included raw files. Does not execute the notebook."""
from pathlib import Path
import hashlib
import json
import pandas as pd
from analytics import clean_data,audit_sheets

ROOT=Path(__file__).parent
SOURCES=[f'https://raw.githubusercontent.com/Faiqazmi/Dataset_latihan/main/Serum%20Wajah%20_1-31%20August%20-%20Sheet{i}.csv' for i in (1,2)]

def prepare():
    a,b=[pd.read_csv(ROOT/f'data/source_sheet{i}.csv') for i in (1,2)]
    clean_data(b)  # Validate schema without changing the included source files.
    meta=audit_sheets(a,b)
    meta.update(period='1–31 Agustus; tahun tidak tercantum dalam notebook/sumber CSV',
        analytical_source='Sheet2, mengikuti notebook pengguna',source_urls=SOURCES,
        downloaded_at='2026-10-15',
        sha256={f'source_sheet{i}.csv':hashlib.sha256((ROOT/f'data/source_sheet{i}.csv').read_bytes()).hexdigest() for i in (1,2)},
        transformation='Trim kolom teks, title-case lokasi, cast kuantitas bulat; semua baris dan angka Sheet2 dipertahankan.',
        license='Lisensi redistribusi tidak tercantum pada notebook; periksa izin pemilik sebelum publikasi ulang.')
    (ROOT/'data/metadata.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False))
    print(json.dumps(meta,indent=2,ensure_ascii=False))

if __name__=='__main__':
    prepare()

