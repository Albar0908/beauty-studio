# ◈ Beauty Studio — Serum Market Intelligence

Dashboard Streamlit light premium untuk analisis serum wajah Shopee dari notebook `Data_Analysis_Beauty_Product (1).ipynb` milik pengguna. Gaya putih/teal meneruskan Retail Studio, dengan aksen coral dan lilac serta enam tab analisis. Tidak membutuhkan API key, database, akun layanan berbayar, atau eksekusi notebook.

## Jalankan di Mac + VS Code

1. Ekstrak **seluruh ZIP**. Buka folder `beauty-studio` lewat VS Code → File → Open Folder.
2. Pastikan Python 3.11 atau 3.12 tersedia (`python3 --version`). Jika belum, instal dari https://www.python.org/downloads/macos/ .
3. Terminal → New Terminal, jalankan satu per satu:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

4. Buka http://localhost:8501 . Hentikan dengan Ctrl+C.

Untuk dibuka kembali, jalankan `source .venv/bin/activate` lalu perintah Streamlit terakhir. Jika port dipakai Retail Studio, gunakan `python -m streamlit run app.py --server.port 8502`.

Internet diperlukan hanya untuk instalasi. CSV sudah disertakan dan tidak diunduh saat aplikasi dijalankan. Font daring bersifat opsional dan memakai font fallback bila offline. Jangan menjalankan `app.py` memakai tombol Run Python biasa; jalankan melalui `python -m streamlit run app.py`.

Jika `ModuleNotFoundError`: periksa `.venv` aktif dan instal requirements dengan interpreter yang sama. Pada VS Code pilih Python: Select Interpreter → `.venv`.

## Enam tab

| Tab | Isi |
| --- | --- |
| Ringkasan | KPI, Top brand, komposisi kontribusi, produk unggulan, aktivitas 0 vs >0 unit |
| Brand landscape | Scatter unit × omzet, perbandingan ranking, Pareto kumulatif, tabel dan ekspor |
| Product explorer | Ranking produk, tabel judul + brand, sumber listing dan ekspor |
| Seller & lokasi | Ranking seller/lokasi seller, heatmap brand × lokasi, ekspor |
| Eksplorasi | Kata kunci judul, distribusi unit, benchmark, hipotesis riset, audit rasio omzet/unit |
| Data & metodologi | Audit lintas sheet, URL konflik, definisi, batas data, SHA-256, tabel terfilter dan ekspor |

Filter global: brand, lokasi seller, seller, pencarian literal nama/brand, hanya baris terjual, dan minimum unit per baris. Multiselect kosong = semua. Top N mengubah panjang peringkat, bukan menyaring data. Ukuran ranking dapat diubah dari unit ke omzet; definisi empat KPI utama tetap sama. Audit sumber di tab terakhir selalu memakai data penuh dan diberi label terpisah.

## Data & temuan yang penting

Sumber notebook memakai dua CSV dari repository `Faiqazmi/Dataset_latihan`:

- [Sheet1](https://raw.githubusercontent.com/Faiqazmi/Dataset_latihan/main/Serum%20Wajah%20_1-31%20August%20-%20Sheet1.csv)
- [Sheet2](https://raw.githubusercontent.com/Faiqazmi/Dataset_latihan/main/Serum%20Wajah%20_1-31%20August%20-%20Sheet2.csv)

Salinan diambil 15 Oktober 2026. Pengambilan ini tidak berarti periode penjualannya tahun 2026. Nama sumber menyebut **1–31 Agustus**, tanpa tahun atau tanggal per baris. Tidak ada data harian, customer, pesanan, biaya, atau iklan. Dashboard tidak membuat timeline, growth, conversion rate atau profit.

**Basis analisis mengikuti Sheet2**, sesuai keputusan pada notebook. Notebook tidak dieksekusi; CSV diambil dari URL yang tercantum, lalu semua agregasi dihitung ulang. Seluruh 3.692 baris dipertahankan tanpa sampling, tanpa menyatukan dua sheet, tanpa koreksi spekulatif. Transformasi hanya trim teks, title-case lokasi, dan kuantitas menjadi integer setelah validasi.

### Rekonsiliasi dasar Sheet2

| Pemeriksaan | Hasil |
| --- | ---: |
| Baris | 3.692 |
| URL listing unik | 3.690 |
| Unit total | 623.125 |
| Omzet tercatat total | Rp90.804.526.236 |
| Brand teramati | 533 |
| Seller teramati | 451 |
| Lokasi seller | 44 |
| Baris 0 unit | 983 |
| Sel kosong | 0 |
| Duplikat persis | 0 |

### Masalah sumber yang tidak disembunyikan

1. **Semua Seller Type berisi Official Store.** Tidak dapat membandingkan dengan non-official atau membuktikan official store lebih unggul. Label sumber tidak memverifikasi status toko saat ini.
2. **Sheet1 dan Sheet2 tidak identik per URL.** Pada 3.690 URL bersama, menggunakan kemunculan pertama per URL, 2.329 URL berbeda kuantitas dan 2.700 berbeda omzet. Sheet1 tidak dipakai untuk mengganti angka Sheet2. Ini audit konsistensi, bukan penentuan sheet mana yang benar.
3. **Dua URL memiliki brand/angka berbeda di Sheet2.** Judul produk Dear Me Beauty juga dilabel Avoskin pada dua baris lain dengan angka berbeda. Empat baris tersebut dipertahankan mengikuti notebook dan ditampilkan pada tab audit. Total mungkin terdampak konflik tersebut; tidak mengklaim telah deduplikasi/koreksi.
4. Ada rasio omzet/unit yang ekstrem. Karena rasio bukan harga jual listing dan sumber tidak konsisten, dashboard tidak memberikan rekomendasi harga berdasarkan angka tersebut.
5. Cakupan pengumpulan tidak diketahui. Pangsa yang ditampilkan hanya dalam dataset atau filter aktif, bukan keseluruhan Shopee.

Verifikasi ke sumber awal diperlukan sebelum keputusan komersial. Ringkasan angka menggambarkan isi Sheet2, bukan jaminan validitas bisnisnya.

## Definisi

- Unit = Σ Sales Quantity, bukan jumlah pesanan.
- Omzet tercatat = Σ Sales Revenue; bukan profit/net revenue yang sudah diverifikasi.
- Listing = URL unik. Jumlah baris ditampilkan terpisah.
- Produk = kelompok judul + brand; tidak mengklaim SKU sudah disatukan lintas seller.
- Pangsa = ukuran entitas / total ukuran pada filter aktif. Top 3/10 dihitung pada ukuran ranking yang dipilih.
- Pareto = kontribusi kumulatif brand dibagi seluruh brand pada filter, bukan hanya Top N.
- Lokasi = lokasi seller, bukan lokasi customer atau distribusi permintaan pembeli.
- Keyword = regex judul produk. Kategori tumpang tindih; bukan verifikasi kandungan, keamanan, atau efektivitas.
- Revenue per Unit = omzet tercatat dibagi unit untuk baris positif; kosong untuk 0 unit. Hanya audit eksploratif, bukan harga produk.

## Struktur proyek

```text
beauty-studio/
  app.py
  analytics.py
  prepare_data.py
  test_dashboard.py
  requirements.txt
  requirements-tested.txt
  README.md
  TESTING.md
  .gitignore
  .streamlit/config.toml
  data/source_sheet1.csv
  data/source_sheet2.csv
  data/metadata.json
```

`prepare_data.py` memvalidasi salinan CSV dan membangun ulang metadata/SHA-256 secara lokal. Tidak perlu dijalankan untuk membuka dashboard:

```bash
python prepare_data.py
python -m unittest -v
```

`requirements-tested.txt` menyimpan versi persis pengujian. Gunakan file itu sebagai pengganti requirements.txt bila ingin versi top-level sama. Pengujian dijalankan pada Linux, bukan Mac asli; bukan lockfile semua dependensi transitif.

## Upload dengan Git

`.gitignore` sudah disertakan untuk mengecualikan environment, cache, secrets, dan .DS_Store. Folder data dan config tema ikut di-track.

**Periksa izin redistribusi dataset sebelum membuat repository publik.** Lisensi data tidak tercantum pada notebook; URL publik tidak otomatis berarti izin publikasi ulang. Gunakan repository private sementara bila izin belum jelas. Jangan mengunggah credential atau data perusahaan.

Untuk repository GitHub baru yang kosong, tanpa README/commit awal di GitHub:

```bash
git init
git add .
git status
git commit -m "Add Beauty Studio Streamlit dashboard"
git branch -M main
git remote add origin https://github.com/USERNAME/beauty-studio-dashboard.git
git push -u origin main
```

Ganti USERNAME dan buat repository terlebih dahulu. Jika identitas Git belum disetel, jalankan `git config user.name "Nama Kamu"` dan `git config user.email "Email GitHub kamu"`, lalu ulangi commit. Ikuti autentikasi GitHub melalui browser/credential manager; jangan taruh token di kode, remote URL yang dibagikan, atau chat.

Jika repository sudah berisi proyek lain atau histori remote, jangan force-push. Upload kode ini tidak otomatis menayangkan dashboard sebagai aplikasi. Tidak ada deployment publik yang dilakukan.

## Mengubah tampilan / data

Nama brand dan teks ada di app.py. Warna widget di `.streamlit/config.toml`; warna chart/CSS di app.py. Saat mengubah dataset, perbarui metadata, batas periode, audit, nilai ekspektasi tes, dan narasi. Jangan sekadar mengganti CSV tanpa memeriksa semantiknya.

Notebook asli tidak diubah. Paket ini adalah proyek baru terpisah dari Retail Studio sebelumnya.
