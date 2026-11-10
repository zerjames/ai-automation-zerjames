"""
Module AI Text-to-SQL untuk Nasabah Perbankan.
Menerjemahkan bahasa natural Indonesia menjadi query SQL SELECT yang valid dan aman.
Mendukung pencarian entitas spesifik:
- Nama Nasabah (contoh: 'Cari nasabah Rendy', 'atas nama Budi', 'bernama Siti')
- NIK (16 digit KTP)
- Nomor Rekening (contoh: 'rekening 123-45-678901')
- CIF (Customer Information File ID, contoh: 'CIF10130601')
- Filter Segmentasi, Cabang, Saldo, Status KYC, dan Risiko.
"""

import re
import os

SCHEMA_DESCRIPTION = """
Tabel: nasabah
Kolom:
- cif (TEXT, ID unik nasabah)
- no_rekening (TEXT, nomor rekening)
- nama_nasabah (TEXT, nama lengkap nasabah)
- nik (TEXT, 16 digit NIK)
- no_telepon (TEXT)
- email (TEXT)
- alamat (TEXT)
- cabang_pembuka (TEXT, contoh: 'KC Jakarta Sudirman', 'KC Bandung Asia Afrika', 'KC Surabaya Darmo', dll)
- produk_rekening (TEXT, contoh: 'Tabungan Utama IDR', 'Tabungan Bisnis IDR', 'Giro Perorangan', 'Deposito Berjangka', 'Tabungan Valas USD')
- segmentasi (TEXT, contoh: 'Reguler', 'Gold', 'Prioritas / High Net Worth')
- saldo_terakhir (REAL, nominal rupiah)
- status_kyc (TEXT, contoh: 'Verified', 'Pending Review', 'Expired')
- tanggal_buka_rekening (TEXT, format 'YYYY-MM-DD')
- skor_risiko (TEXT, contoh: 'Rendah', 'Menengah', 'Tinggi')
"""

def parse_nominal(text: str) -> float:
    """Mendeteksi nominal angka dari teks seperti '100 juta', '1 milyar', '50jt', '500.000.000'."""
    text = text.lower().replace(",", ".").replace("rp", "").strip()
    
    # Cek kata milyar / m
    milyar_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:milyar|miliar|m\b)', text)
    if milyar_match:
        return float(milyar_match.group(1)) * 1_000_000_000

    # Cek kata juta / jt
    juta_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:juta|jt\b)', text)
    if juta_match:
        return float(juta_match.group(1)) * 1_000_000

    # Cek format angka biasa misal 50000000 atau 50.000.000
    cleaned = re.sub(r'[^\d]', '', text)
    if cleaned:
        return float(cleaned)
    return 0.0

def extract_identity_entities(prompt: str):
    """
    Mengekstrak entitas identitas spesifik: NIK, CIF, No. Rekening, atau Nama Nasabah.
    """
    p_raw = prompt.strip()
    
    # 1. NIK (16 digit angka)
    nik_m = re.search(r'\b\d{16}\b', p_raw)
    if nik_m:
        return "nik", nik_m.group(0)

    # 2. CIF (Format: CIF + digit angka)
    cif_m = re.search(r'\b(CIF\d{6,10})\b', p_raw, re.IGNORECASE)
    if cif_m:
        return "cif", cif_m.group(1).upper()

    # 3. Nomor Rekening (Format: 3 digit - 2/4 digit - 3/6 digit)
    rek_m = re.search(r'\b\d{3}[-\s]?(?:\d{2}|\*{2,4})[-\s]?\d{3,6}\b', p_raw)
    if rek_m:
        return "no_rekening", rek_m.group(0).replace(" ", "")

    # 4. Nama Nasabah Eksplisit (pola: bernama <NAMA>, atas nama <NAMA>, a/n <NAMA>, nama <NAMA>)
    m_name1 = re.search(
        r'(?:bernama|atas nama|a/n|nama)\s+([a-zA-Z\s\.\,\'\`]+?)(?=\s+(?:di|yang|dengan|saldo|cabang|dan|status|rekening|prioritas|gold|reguler)|$)',
        p_raw,
        re.IGNORECASE
    )
    if m_name1:
        val = m_name1.group(1).strip()
        reserved = ['nasabah', 'rekening', 'prioritas', 'gold', 'reguler', 'bank']
        if len(val) > 1 and val.lower() not in reserved:
            return "nama_nasabah", val

    # 5. Pola Pencarian Nama Langsung ('cari nasabah <NAMA>', 'cari <NAMA>', 'tampilkan data nasabah <NAMA>')
    m_name2 = re.search(
        r'(?:cari nasabah|data nasabah|tampilkan nasabah|profil nasabah|cari)\s+([a-zA-Z\s\.\,\'\`]+?)(?=\s+(?:di|yang|dengan|saldo|cabang|dan|status|rekening|prioritas|gold|reguler)|$)',
        p_raw,
        re.IGNORECASE
    )
    if m_name2:
        val = m_name2.group(1).strip()
        reserved = ['nasabah', 'semua', 'top', 'prioritas', 'gold', 'reguler', 'verified', 'pending', 'expired', 'cabang', 'data']
        words = val.lower().split()
        if len(val) > 1 and not any(w in reserved for w in words):
            return "nama_nasabah", val

    return None, None

def natural_language_to_sql(prompt: str) -> str:
    """
    Mengonversi prompt berbahasa Indonesia menjadi query SQL SELECT yang valid dan aman.
    """
    p = prompt.strip().lower()
    conditions = []
    order_by = ""
    limit_clause = ""

    # =========================================================================
    # 0. DETEKSI IDENTITAS & NAMA SPESIFIK
    # =========================================================================
    ent_type, ent_val = extract_identity_entities(prompt)
    if ent_type == "nama_nasabah":
        # Sanitasi single quote untuk keamanan SQL
        safe_val = ent_val.replace("'", "''")
        conditions.append(f"nama_nasabah LIKE '%{safe_val}%'")
    elif ent_type == "nik":
        conditions.append(f"nik LIKE '%{ent_val}%'")
    elif ent_type == "cif":
        conditions.append(f"cif = '{ent_val}'")
    elif ent_type == "no_rekening":
        # Jika ada asterisk sensor, ganti jadi wildcard %
        rek_wildcard = ent_val.replace("*", "%")
        conditions.append(f"no_rekening LIKE '%{rek_wildcard}%'")

    # =========================================================================
    # 1. DETEKSI SEGMENTASI
    # =========================================================================
    if "prioritas" in p:
        conditions.append("segmentasi LIKE '%Prioritas%'")
    elif "gold" in p:
        conditions.append("segmentasi = 'Gold'")
    elif "reguler" in p:
        conditions.append("segmentasi = 'Reguler'")

    # =========================================================================
    # 2. DETEKSI STATUS KYC
    # =========================================================================
    if "pending" in p or "belum verified" in p:
        conditions.append("status_kyc = 'Pending Review'")
    elif "expired" in p or "kadaluarsa" in p:
        conditions.append("status_kyc = 'Expired'")
    elif "verified" in p or "terverifikasi" in p:
        conditions.append("status_kyc = 'Verified'")

    # =========================================================================
    # 3. DETEKSI SKOR RISIKO
    # =========================================================================
    if "risiko tinggi" in p or "high risk" in p:
        conditions.append("skor_risiko = 'Tinggi'")
    elif "risiko rendah" in p or "low risk" in p:
        conditions.append("skor_risiko = 'Rendah'")
    elif "risiko menengah" in p or "medium risk" in p:
        conditions.append("skor_risiko = 'Menengah'")

    # =========================================================================
    # 4. DETEKSI KOTA / CABANG
    # =========================================================================
    kota_keywords = {
        "sudirman": "KC Jakarta Sudirman",
        "thamrin": "KC Jakarta Thamrin",
        "jakarta": "Jakarta",
        "surabaya": "Surabaya",
        "bandung": "Bandung",
        "medan": "Medan",
        "semarang": "Semarang",
        "yogyakarta": "Yogyakarta",
        "jogja": "Yogyakarta",
        "makassar": "Makassar",
        "denpasar": "Denpasar",
        "bali": "Denpasar"
    }
    for kw, val in kota_keywords.items():
        if kw in p:
            conditions.append(f"cabang_pembuka LIKE '%{val}%'")
            break

    # =========================================================================
    # 5. DETEKSI PRODUK REKENING
    # =========================================================================
    if "giro" in p:
        conditions.append("produk_rekening LIKE '%Giro%'")
    elif "deposito" in p:
        conditions.append("produk_rekening LIKE '%Deposito%'")
    elif "valas" in p or "usd" in p:
        conditions.append("produk_rekening LIKE '%Valas%'")

    # =========================================================================
    # 6. DETEKSI SALDO
    # =========================================================================
    saldo_match_above = re.search(r'(?:saldo|tabungan|simpanan)?\s*(?:di atas|lebih dari|>|minimal|paling sedikit)\s*([0-9\.\,\s]+(?:juta|jt|milyar|miliar|m)?)', p)
    saldo_match_below = re.search(r'(?:saldo|tabungan|simpanan)?\s*(?:di bawah|kurang dari|<|maksimal|paling banyak)\s*([0-9\.\,\s]+(?:juta|jt|milyar|miliar|m)?)', p)
    
    if saldo_match_above:
        val = parse_nominal(saldo_match_above.group(1))
        if val > 0:
            conditions.append(f"saldo_terakhir >= {val}")
    elif saldo_match_below:
        val = parse_nominal(saldo_match_below.group(1))
        if val > 0:
            conditions.append(f"saldo_terakhir <= {val}")

    # =========================================================================
    # 7. DETEKSI URUTAN (ORDER BY)
    # =========================================================================
    if "terbesar" in p or "tertinggi" in p or "paling banyak" in p:
        order_by = " ORDER BY saldo_terakhir DESC"
    elif "terkecil" in p or "terendah" in p or "paling sedikit" in p:
        order_by = " ORDER BY saldo_terakhir ASC"
    elif "terbaru" in p:
        order_by = " ORDER BY tanggal_buka_rekening DESC"

    # =========================================================================
    # 8. DETEKSI LIMIT / JUMLAH CATATAN
    # =========================================================================
    limit_match = re.search(r'(?:top|sebanyak|ambil|tampilkan)?\s*(\d+)\s*(?:nasabah|orang|data|catatan)?', p)
    if limit_match and int(limit_match.group(1)) <= 500:
        limit_clause = f" LIMIT {limit_match.group(1)}"

    # =========================================================================
    # 9. SUSUN QUERY SQL AKHIR
    # =========================================================================
    query = "SELECT * FROM nasabah"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    if order_by:
        query += order_by
    if limit_clause:
        query += limit_clause
    else:
        # Jika pencarian nama atau identitas spesifik, default limit 50, selain itu 100
        query += " LIMIT 50" if ent_type else " LIMIT 100"

    return query
