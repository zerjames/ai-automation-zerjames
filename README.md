# 🏦 Bank AI Customer Data Automation System (Python + SQL + Excel)

Sistem otomasi penarikan data nasabah berbasis **Python, SQL Database, dan Excel** yang dirancang sesuai standar kepatuhan perbankan (OJK, BI, & UU Pelindungan Data Pribadi / PDP).

---

## 💡 Konsep: Menjawab Pertanyaan Wawancara Bank (Web vs Prompt)

Ketika pihak bank menyebutkan **SQL**, arsitektur idealnya adalah **Web Dashboard Hybrid**:
1. **Bagi Tim Operasional & Backoffice:** Butuh antarmuka **Web** dengan filter pasti (Dropdown Cabang, Tanggal, Segmentasi).
2. **Bagi Manajer / Eksekutif / Analis:** Diberikan **AI Prompt Assistant (Text-to-SQL)** agar bisa mengetik instruksi bahasa sehari-hari tanpa harus bisa bahasa SQL:
   > *"Tarik nasabah prioritas di KC Sudirman dengan saldo di atas 1 milyar"*
   > ➔ AI mengubahnya menjadi query SQL: `SELECT * FROM nasabah WHERE segmentasi LIKE '%Prioritas%' AND saldo_terakhir >= 1000000000`
   > ➔ Otomatis di-export ke template **Excel resmi perbankan** (.xlsx).

---

## 🚀 Fitur Unggulan

1. **AI Text-to-SQL Engine:**
   - Menerjemahkan bahasa Indonesia natural ke query SQL `SELECT` yang valid dan aman.
   - Dilengkapi *query guardrails*: memblokir perintah destruktif (`DROP`, `DELETE`, `UPDATE`, `INSERT`).
2. **Kepatuhan Data Masking (UU PDP):**
   - Sensor otomatis pada kolom sensitif (NIK: `3201********1234`, No. Rekening: `123-****-789`, No. HP: `0812****5678`).
   - Dapat di-toggle on/off sesuai wewenang role pengguna.
3. **Standar Pelaporan Excel Korporat (OpenPyXL):**
   - Header biru perbankan (Corporate Navy `#0F2942`).
   - Kartu ringkasan KPI (Total Nasabah, Total DPK, Nasabah Prioritas).
   - Format nominal rupiah standar (`Rp #,##0`).
   - Status KYC berwarna (*Verified*, *Pending*, *Expired*).
   - Formula penjumlahan otomatis (`=SUM(...)`).
4. **Dua Mode Antarmuka:**
   - **Mode 1:** AI Prompt Assistant.
   - **Mode 2:** Form Filter Manual Standar.

---

## 📂 Struktur Proyek

```
c:\xampp\htdocs\ai_automation\
│
├── bank_automation/
│   ├── ai_engine.py       # Text-to-SQL parser bahasa Indonesia
│   ├── database.py        # SQLite / SQL Connection & Safe Query Execution
│   ├── data_generator.py  # Generator data realistis nasabah Indonesia (Faker)
│   ├── excel_exporter.py  # Openpyxl Formatter (Styling, KPI Cards, Auto-width)
│   └── validator.py       # Validasi NIK & algoritma Data Masking PDP
│
├── data/
│   └── bank_nasabah.db    # Database SQL (otomatis terbuat & terisi saat jalan)
│
├── output/
│   └── *.xlsx             # File laporan Excel hasil generate
│
├── app.py                 # Web Dashboard Interaktif (Streamlit)
├── cli.py                 # Script terminal / batch (untuk cron/scheduler)
└── README.md
```

---

## 🖥️ Cara Menjalankan

### 1. Menjalankan Web Dashboard (Rekomendasi untuk Demo):
Buka terminal / PowerShell di folder ini, lalu jalankan:
```bash
streamlit run app.py
```
Aplikasi akan otomatis terbuka di browser Anda di: `http://localhost:8501`.

### 2. Menjalankan via Terminal / Batch (CLI):
```bash
python cli.py --prompt "Tampilkan nasabah prioritas dengan saldo di atas 500 juta"
```
Hasil file Excel akan langsung tersimpan di folder `output/`.

---

## 🛡️ Nilai Tambah untuk Interview / Portofolio:
- **Paham Ekosistem Data Bank:** Tahu bahwa data tersimpan di RDBMS (SQL) dan harus diakses dengan permission *Read-Only*.
- **Paham Regulasi PDP:** Tahu bahwa data NIK dan No. Rekening tidak boleh sembarangan di-export tanpa masking.
- **Nilai Bisnis Tinggi:** Mengurangi beban tim IT/Database Administrator dari permintaan tarikan data manual harian.

