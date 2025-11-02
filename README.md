# 👙 VPants - Sistem Pembukuan & Stok Otomatis

![VPants Logo](assets/logo.webp)

Sistem pembukuan dan manajemen stok otomatis untuk bisnis **celana dalam wanita**, dibangun dengan Streamlit dan Python.

## 🚀 Fitur Utama

### 💰 Manajemen Keuangan
- **Pencatatan Transaksi**: Penjualan retail & pack, pembelian, pengeluaran, penarikan
- **Saldo Otomatis**: Update real-time setelah setiap transaksi
- **Profit Calculation**: Hitung profit harian/bulanan otomatis
- **Biaya Admin**: Otomatis termasuk biaya penarikan (Rp 3,000)

### 📦 Manajemen Stok
- **Stok Bahan Mentah**: Kain waterproof, polar, spandex, diadora, karet elastis, benang
- **Stok Barang Jadi**: Celana dalam wanita, celana pembalut, premium - per ukuran (S, M, L, XL, XXL)
- **Update Otomatis**: Stok berkurang saat penjualan, bertambah saat produksi
- **Alert Stok Menipis**: Notifikasi ketika stok hampir habis

### 🏭 Sistem Produksi
- **Tracking Produksi**: Bahan digunakan, ongkos jahit, biaya total
- **Multi Produk**: Support celana dalam biasa, celana pembalut, premium
- **Pack Sales**: Support penjualan pack 3, 5, 10 pcs dengan harga khusus

### 📊 Laporan & Analytics
- **Laporan Harian**: Ringkasan transaksi dan profit harian
- **Laporan Bulanan**: Analisis performa bulanan
- **Riwayat Transaksi**: Filter dan export data ke CSV
- **Dashboard Real-time**: Monitoring kesehatan bisnis

## 🛠️ Teknologi

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: SQLite
- **Architecture**: Modular (MVC Pattern)

## 📦 Struktur Project

```

vpants/
├──app.py                 # Main Streamlit application
├──config/               # Configuration files
│├── database.py       # Database configuration
│└── brand_config.py   # Brand identity
├──models/               # Data models
│├── product.py        # Product model
│├── transaction.py    # Transaction model
│└── stock.py          # Stock model
├──services/             # Business logic
│├── finance_service.py
│├── stock_service.py
│├── stock_management_service.py
│├── initial_setup_service.py
│├── report_service.py
│├── production_service.py
│└── sales_service.py
├──utils/                # Helper functions
│└── helpers.py
├──assets/               # Static files
│└── logo.webp
├──data/                 # Database (ignored in git)
├──requirements.txt
└──README.md

```

## 🚀 Instalasi & Menjalankan

1. **Clone repository**:
```bash
git clone https://github.com/XdibsAI/Vpants-.git
cd Vpants-
```

1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Jalankan aplikasi:

```bash
python -m streamlit run app.py
```

1. Buka browser: http://localhost:8501

⚙️ Setup Awal

1. Buka menu ⚙️ Setup Awal
2. Set Saldo Awal bisnis
3. Setup Produk Default (opsional - sudah include produk celana dalam)
4. Input Stok Awal di menu Input Stock Awal

🎯 Produk yang Didukung

· 👙 Celana Dalam VPants: Rp 75,000 (S, M, L), Rp 80,000 (XL, XXL)
· 🩲 Celana Pembalut VPants: Rp 85,000 (semua size)
· 💎 Celana Dalam Premium: Rp 95,000 (S, M, L)
· 📦 Pack Sales: 3pcs (Rp 200K), 5pcs (Rp 300K), 10pcs (Rp 550K)

📋 Requirements

```bash
streamlit==1.28.0
pandas==2.0.3
plotly==5.15.0
Pillow==10.0.1
```

👥 Kontribusi

1. Fork project ini
2. Buat feature branch (git checkout -b feature/AmazingFeature)
3. Commit changes (git commit -m 'Add some AmazingFeature')
4. Push ke branch (git push origin feature/AmazingFeature)
5. Buat Pull Request

📞 Kontak

· CP: 085157149669
· Brand: SMART WOMEN
· Produk: Celana Dalam Wanita

📄 License

Distributed under the MIT License. See LICENSE for more information.

---

Dibangun dengan ❤️ untuk bisnis celana dalam wanita modern
