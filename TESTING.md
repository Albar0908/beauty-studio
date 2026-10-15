# Hasil pengujian

Tanggal: 15 Oktober 2026. Environment: Linux / Python 3.12, Streamlit 1.66.0, Pandas 2.2.3, Plotly 6.9.0.

`python -m unittest -v`: **12 tes lulus**.

1. Total sumber: 3.692 baris, 623.125 unit, Rp90.804.526.236, 3.690 URL unik.
2. Tidak ada penghapusan diam-diam: 983 baris 0 unit, 2 baris ekstra ber-URL konflik, label Official Store dipertahankan.
3. Top brand konsisten dengan notebook: Scarlett, 124.437 unit.
4. Total grup brand, seller, lokasi, serta produk direkonsiliasi terhadap total sumber.
5. Kombinasi filter brand, lokasi, minimum unit dan penjualan positif.
6. Pencarian literal termasuk karakter regex dan hasil kosong.
7. Kata kunci multi-label.
8. Pembagian nol dan rasio unit nol.
9. Validasi kolom wajib, angka negatif dan unit pecahan.
10. Audit lintas sheet: 3.690 URL bersama, 2.329 beda kuantitas, 2.700 beda omzet; kemunculan pertama per URL hanya untuk audit.
11. Streamlit AppTest: default 6 tab; ubah ukuran ranking ke omzet, brand, toggle penjualan positif, minimum unit, pencarian kosong/tidak cocok/karakter literal tanpa exception.
12. Streamlit AppTest: brand yang seluruh barisnya 0 unit tetap tampil tanpa crash atau insight kepemimpinan palsu.

Smoke check tambahan: tree Streamlit default memuat 12 elemen chart, 8 dataframe, 5 tombol unduh dan 0 exception. Pemeriksaan compile seluruh file Python lulus.

## Batas pengujian

Belum diperiksa rendering visual/pixel-perfect lewat browser, instalasi pada Mac asli, interaksi unduh di browser, atau deployment Streamlit Cloud. Browser pengujian tidak tersedia karena pembatasan lingkungan. AppTest memeriksa eksekusi dan interaksi widget, bukan tampilan akhir Chrome/Safari. Proyek tidak mengklaim telah diuji end-to-end browser.

Tes konsistensi angka tidak membuktikan akurasi data sumber. Dataset mempunyai perbedaan antar-sheet, URL konflik, dan cakupan pengumpulan tidak diketahui. Lihat halaman Data & metodologi dan README.
