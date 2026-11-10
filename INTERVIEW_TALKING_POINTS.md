# 🎯 Panduan Jawaban Wawancara (Interview Talking Points)
### Topik: Otomasi AI Ekstraksi Data Nasabah (SQL + Python + Excel)

Dokumen ini disiapkan untuk membantu Anda menjawab pertanyaan pewawancara teknis (*Lead Engineer*, *Enterprise Architect*, maupun *Head of Digital Banking/IT*).

---

## 1. Pertanyaan Kunci: "Kenapa Memilih Model Web Dashboard + AI Prompt daripada Chatbot Saja?"

**Jawaban Bernilai Tinggi:**
> *"Di lingkungan perbankan, pengguna memiliki level literasi teknologi yang berbeda-beda. Staf backoffice dan audit harian lebih menyukai **form filter pasti (dropdown)** karena anti-salah (*zero risk of hallucination*). Namun untuk analis bisnis atau pimpinan cabang, mereka membutuhkan kecepatan eksplorasi data secara *ad-hoc* tanpa harus antre meminta bantuan tim IT/DBA.*
>
> *Oleh karena itu, arsitektur terbaik adalah **Web Internal dengan model Hybrid**: di dalamnya tersedia form filter baku untuk operasional rutin, sekaligus dilengkapi **AI Text-to-SQL Engine** agar pengguna bisa mengetik instruksi bahasa Indonesia dan otomatis mendapatkan berkas Excel berstandar perbankan."*

---

## 2. Pertanyaan Keamanan: "Bagaimana Mencegah SQL Injection atau AI Mengeksekusi Query Berbahaya?"

**Jawaban Bernilai Tinggi:**
> *"Keamanan diatur dalam 3 lapis proteksi (*Defense in Depth*):*
> 1. **Database Role Level:** Koneksi aplikasi ke database core banking menggunakan kredensial akun dengan hak akses **Read-Only (SELECT Only)**.
> 2. **Application Level Guardrails:** Sebelum query dijalankan, sistem melakukan validasi sintaks. Query hanya diproses jika dimulai dengan klausa `SELECT`. Perintah DDL/DML seperti `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, dan `TRUNCATE` akan langsung ditolak sistem (*exception handling*).
> 3. **Query Safety Limit:** Setiap query yang dihasilkan AI otomatis dipasangi klausul batas aman (`LIMIT 100` atau `LIMIT 500`) untuk mencegah beban kerja memori (*memory exhaustion / denial of service*) pada server database perbankan."*

---

## 3. Pertanyaan Regulasi: "Bagaimana Kepatuhan terhadap UU Perlindungan Data Pribadi (UU PDP) dan OJK?"

**Jawaban Bernilai Tinggi:**
> *"Kami menerapkan modul **Data Masking Engine**:*
> - *Nomor Induk Kependudukan (NIK) disensor: `3201********1234`.*
> - *Nomor Rekening disensor: `123-****-789`.*
> - *Nomor Telepon disensor: `0812****5678`.*
> - *Fitur ini memiliki toggle otorisasi: staf operasional standar hanya dapat melihat dan mengunduh data termasking, sedangkan data lengkap hanya dapat diakses dengan persetujuan audit (*maker-checker principle*).*
> - *Pada berkas Excel yang di-export, kami menyertakan sheet khusus **Audit Trail & Compliance** yang mencatat stempel waktu penarikan, query yang dijalankan, dan nilai hash SHA-256 sebagai bukti integritas data bagi auditor OJK/BI."*

---

## 4. Pertanyaan Teknis: "Mengapa Menggunakan OpenPyXL daripada Pandas `to_excel()` Biasa?"

**Jawaban Bernilai Tinggi:**
> *"Pandas `to_excel()` hanya melakukan *raw data dump* (tabel polos tanpa format). Laporan perbankan resmi memerlukan:*
> 1. *Format mata uang Rupiah (`#,##0`) yang benar agar bisa langsung dijumlahkan oleh pengguna.*
> 2. *Struktur **Multi-Sheet Workbook** (Ringkasan Eksekutif, Detail Nasabah, dan Log Audit).*
> 3. *Styling korporat, kartu metrik KPI, warna status KYC (*Verified/Pending/Expired*), dan *freeze panes* agar header tetap terbaca saat tabel di-scroll.*
> 4. *OpenPyXL memungkinkan manipulasi *cell-by-cell*, penyisipan formula Excel asli (`=SUM(...)`), dan penyesuaian lebar kolom otomatis (*auto-fit width*)."*

---

## 5. Pertanyaan Integrasi: "Bagaimana Jika Sistem Core Banking Lain Ingin Memakai Fitur Ini?"

**Jawaban Bernilai Tinggi:**
> *"Sistem ini dirancang modular dan telah dilengkapi service **REST API (`api_server.py`)** berbasis Flask/FastAPI.*
> *Portal internal bank yang dibangun menggunakan PHP/Laravel, Java Spring, atau React dapat melakukan pemanggilan API:*
> - `POST /api/query`: Mengirim prompt dan menerima data JSON nasabah teranalisis.
> - `GET/POST /api/export-excel`: Menghasilkan berkas Excel terformat secara langsung sebagai respons unduhan berkas."*

