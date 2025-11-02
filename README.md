# 👖 VPants - Sistem Pembukuan & Stok Otomatis

![VPants Logo](assets/logo.webp)

Sistem pembukuan dan manajemen stok otomatis untuk bisnis pakaian, dibangun dengan Streamlit dan Python.

## 🚀 Fitur Utama

### 💰 Manajemen Keuangan
- **Pencatatan Transaksi**: Penjualan, pembelian, pengeluaran, penarikan
- **Saldo Otomatis**: Update real-time setelah setiap transaksi
- **Profit Calculation**: Hitung profit harian/bulanan otomatis
- **Biaya Admin**: Otomatis termasuk biaya penarikan (Rp 3,000)

### 📦 Manajemen Stok
- **Stok Bahan Mentah**: Waterproof, Polar, Spandex, Diadora
- **Stok Barang Jadi**: Tracking per ukuran (S, M, L, XL, XXL)
- **Update Otomatis**: Stok berkurang saat penjualan, bertambah saat produksi
- **Alert Stok Menipis**: Notifikasi ketika stok hampir habis

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
│└── report_service.py
├──utils/                # Helper functions
│└── helpers.py
├──assets/               # Static files
│└── logo.webp
└──data/                 # Database (ignored in git)

```

## 🚀 Instalasi & Menjalankan

1. **Clone repository**:
```bash
git clone https://github.com/username/vpants.git
cd vpants
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
3. Setup Produk Default (opsional)
4. Input Stok Awal di menu ⚡ Input Stock Awal

📋 Requirements

Lihat requirements.txt untuk daftar dependencies.

👥 Kontribusi

1. Fork project ini
2. Buat feature branch (git checkout -b feature/AmazingFeature)
3. Commit changes (git commit -m 'Add some AmazingFeature')
4. Push ke branch (git push origin feature/AmazingFeature)
5. Buat Pull Request

📞 Kontak

· CP: 085157149669
· Brand: SMART WOMEN

📄 License

Distributed under the MIT License. See LICENSE for more information.

---

Dibangun dengan ❤️ untuk bisnis pakaian modern
