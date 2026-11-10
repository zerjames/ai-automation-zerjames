"""
Module Database SQL untuk Nasabah Bank.
Mendukung Dual-Engine:
1. SQLite (Default zero-config di data/bank_nasabah.db)
2. MySQL XAMPP / MariaDB (phpMyAdmin localhost:3306)

Dilengkapi Auto-Detect: Jika MySQL XAMPP aktif, otomatis terhubung ke MySQL.
Jika MySQL XAMPP sedang tidak aktif, otomatis fallback ke SQLite.
"""

import os
import sqlite3
import pymysql
import pymysql.cursors
from .data_generator import generate_dummy_customers

# Mode Database: 'auto', 'mysql', atau 'sqlite'
DB_ENGINE_MODE = os.getenv("DB_ENGINE", "auto")

DB_SQLITE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "bank_nasabah.db")

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "bank_nasabah"),
    "charset": "utf8mb4",
    "connect_timeout": 2
}

def test_mysql_connection():
    """Memeriksa apakah MySQL XAMPP sedang aktif dan database tersedia."""
    try:
        conn = pymysql.connect(
            host=MYSQL_CONFIG["host"],
            port=MYSQL_CONFIG["port"],
            user=MYSQL_CONFIG["user"],
            password=MYSQL_CONFIG["password"],
            database=MYSQL_CONFIG["database"],
            connect_timeout=1
        )
        conn.close()
        return True
    except Exception:
        return False

def get_active_db_info():
    """Mengembalikan informasi database yang sedang aktif (MySQL atau SQLite)."""
    if DB_ENGINE_MODE == "mysql" or (DB_ENGINE_MODE == "auto" and test_mysql_connection()):
        return {
            "type": "MySQL",
            "name": f"MySQL XAMPP (phpMyAdmin)",
            "target": f"{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']} / {MYSQL_CONFIG['database']}"
        }
    else:
        return {
            "type": "SQLite",
            "name": "SQLite Standalone",
            "target": "data/bank_nasabah.db"
        }

def get_connection():
    """Membuka koneksi database sesuai engine yang aktif."""
    info = get_active_db_info()
    
    if info["type"] == "MySQL":
        conn = pymysql.connect(
            host=MYSQL_CONFIG["host"],
            port=MYSQL_CONFIG["port"],
            user=MYSQL_CONFIG["user"],
            password=MYSQL_CONFIG["password"],
            database=MYSQL_CONFIG["database"],
            charset=MYSQL_CONFIG["charset"],
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    else:
        os.makedirs(os.path.dirname(DB_SQLITE_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def init_database(populate_dummy_count=500):
    """Inisialisasi tabel nasabah dan isi data awal jika kosong."""
    info = get_active_db_info()
    
    if info["type"] == "MySQL":
        init_mysql_database(populate_dummy_count)
        return "MySQL"
    else:
        init_sqlite_database(populate_dummy_count)
        return DB_SQLITE_PATH

def init_sqlite_database(populate_dummy_count=500):
    """Inisialisasi khusus SQLite."""
    os.makedirs(os.path.dirname(DB_SQLITE_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_SQLITE_PATH)
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

def init_mysql_database(populate_dummy_count=500):
    """Inisialisasi database dan tabel di MySQL XAMPP."""
    # 1. Pastikan database ada
    root_conn = pymysql.connect(
        host=MYSQL_CONFIG["host"],
        port=MYSQL_CONFIG["port"],
        user=MYSQL_CONFIG["user"],
        password=MYSQL_CONFIG["password"]
    )
    with root_conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_CONFIG['database']}` CHARACTER SET utf8mb4")
    root_conn.close()

    # 2. Buat tabel nasabah
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS nasabah (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cif VARCHAR(30) UNIQUE,
            no_rekening VARCHAR(30) UNIQUE,
            nama_nasabah VARCHAR(100),
            nik VARCHAR(20),
            no_telepon VARCHAR(25),
            email VARCHAR(100),
            alamat TEXT,
            cabang_pembuka VARCHAR(100),
            produk_rekening VARCHAR(50),
            segmentasi VARCHAR(50),
            saldo_terakhir DOUBLE,
            status_kyc VARCHAR(30),
            tanggal_buka_rekening DATE,
            skor_risiko VARCHAR(30),
            INDEX idx_cabang (cabang_pembuka),
            INDEX idx_segmentasi (segmentasi),
            INDEX idx_saldo (saldo_terakhir)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        cur.execute("SELECT COUNT(*) as cnt FROM nasabah")
        res = cur.fetchone()
        count = res["cnt"] if isinstance(res, dict) else res[0]
        
        if count == 0 and populate_dummy_count > 0:
            customers = generate_dummy_customers(populate_dummy_count)
            sql = """
            INSERT INTO nasabah (
                cif, no_rekening, nama_nasabah, nik, no_telepon, email, alamat,
                cabang_pembuka, produk_rekening, segmentasi, saldo_terakhir,
                status_kyc, tanggal_buka_rekening, skor_risiko
            ) VALUES (
                %(cif)s, %(no_rekening)s, %(nama_nasabah)s, %(nik)s, %(no_telepon)s, %(email)s, %(alamat)s,
                %(cabang_pembuka)s, %(produk_rekening)s, %(segmentasi)s, %(saldo_terakhir)s,
                %(status_kyc)s, %(tanggal_buka_rekening)s, %(skor_risiko)s
            )
            """
            cur.executemany(sql, customers)
            conn.commit()
            
    conn.close()

def execute_safe_query(query: str, params: tuple = ()):
    """
    Menjalankan query SQL dengan perlindungan keamanan (Hanya memperbolehkan SELECT).
    Mendukung SQLite dan MySQL secara transparan.
    """
    clean_query = query.strip()
    first_word = clean_query.split()[0].upper() if clean_query else ""
    
    if first_word != "SELECT":
        raise ValueError("Demi keamanan perbankan, hanya perintah pencarian (SELECT) yang diizinkan.")
        
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "ATTACH", "DETACH"]
    upper_query = clean_query.upper()
    for word in forbidden:
        if f" {word} " in f" {upper_query} ":
            raise ValueError(f"Perintah '{word}' diblokir demi keamanan data nasabah.")
            
    conn = get_connection()
    info = get_active_db_info()
    
    if info["type"] == "MySQL":
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
        conn.close()
        return list(results)
    else:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        conn.close()
        return results
