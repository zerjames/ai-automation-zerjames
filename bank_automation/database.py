"""
Module Database SQL untuk Nasabah Bank.
Menggunakan SQLite lokal (tanpa perlu setting server rumit) dan kompatibel dengan MySQL.
"""

import sqlite3
import os
from .data_generator import generate_dummy_customers

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "bank_nasabah.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database(populate_dummy_count=500):
    """Inisialisasi tabel nasabah dan isi data awal jika kosong."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nasabah (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cif TEXT UNIQUE,
        no_rekening TEXT UNIQUE,
        nama_nasabah TEXT,
        nik TEXT,
        no_telepon TEXT,
        email TEXT,
        alamat TEXT,
        cabang_pembuka TEXT,
        produk_rekening TEXT,
        segmentasi TEXT,
        saldo_terakhir REAL,
        status_kyc TEXT,
        tanggal_buka_rekening TEXT,
        skor_risiko TEXT
    )
    """)
    
    # Cek apakah sudah ada data
    cursor.execute("SELECT COUNT(*) FROM nasabah")
    count = cursor.fetchone()[0]
    
    if count == 0 and populate_dummy_count > 0:
        customers = generate_dummy_customers(populate_dummy_count)
        cursor.executemany("""
        INSERT INTO nasabah (
            cif, no_rekening, nama_nasabah, nik, no_telepon, email, alamat,
            cabang_pembuka, produk_rekening, segmentasi, saldo_terakhir,
            status_kyc, tanggal_buka_rekening, skor_risiko
        ) VALUES (
            :cif, :no_rekening, :nama_nasabah, :nik, :no_telepon, :email, :alamat,
            :cabang_pembuka, :produk_rekening, :segmentasi, :saldo_terakhir,
            :status_kyc, :tanggal_buka_rekening, :skor_risiko
        )
        """, customers)
        conn.commit()
    
    conn.close()
    return DB_PATH

def execute_safe_query(query: str, params: tuple = ()):
    """
    Menjalankan query SQL dengan perlindungan keamanan (Hanya memperbolehkan SELECT).
    Mencegah query destruktif (DROP, DELETE, UPDATE, INSERT) dari AI prompt.
    """
    clean_query = query.strip()
    first_word = clean_query.split()[0].upper() if clean_query else ""
    
    if first_word != "SELECT":
        raise ValueError("Demi keamanan perbankan, hanya perintah pencarian (SELECT) yang diizinkan.")
        
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "ATTACH", "DETACH"]
    upper_query = clean_query.upper()
    for word in forbidden:
        # Cek jika ada keyword berbahaya sebagai kata terpisah
        if f" {word} " in f" {upper_query} ":
            raise ValueError(f"Perintah '{word}' diblokir demi keamanan data nasabah.")
            
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    results = [dict(row) for row in rows]
    conn.close()
    return results

