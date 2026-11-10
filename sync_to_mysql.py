"""
Skrip Migrasi / Sinkronisasi Data dari SQLite ke MySQL XAMPP (phpMyAdmin).
Menyalin seluruh data nasabah dari SQLite ke database 'bank_nasabah' di MySQL XAMPP.
"""

import sqlite3
import pymysql
import os
import sys

SQLITE_PATH = os.path.join(os.path.dirname(__file__), "data", "bank_nasabah.db")

MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DB = "bank_nasabah"

def main():
    print("=" * 65)
    print("SINKRONISASI DATA NASABAH KE MYSQL XAMPP (phpMyAdmin)")
    print("=" * 65)

    # 1. Cek SQLite
    if not os.path.exists(SQLITE_PATH):
        print(f"[ERROR] Berkas SQLite tidak ditemukan di {SQLITE_PATH}")
        print("Jalankan 'python -m bank_automation.database' terlebih dahulu.")
        sys.exit(1)

    # 2. Cek Koneksi MySQL XAMPP
    print(f"[*] Menghubungi MySQL XAMPP di {MYSQL_HOST}:{MYSQL_PORT}...")
    try:
        conn_root = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            connect_timeout=3
        )
        print("[+] MySQL XAMPP terhubung!")
    except Exception as e:
        print("\n[GAGAL] Tidak dapat terhubung ke MySQL XAMPP!")
        print("Penyebab: Service MySQL di XAMPP Control Panel belum di-START.")
        print("Solusi:")
        print("1. Buka XAMPP Control Panel.")
        print("2. Klik tombol 'Start' pada modul MySQL.")
        print("3. Jalankan kembali file ini: python sync_to_mysql.py\n")
        sys.exit(1)

    # 3. Buat Database bank_nasabah di phpMyAdmin
    with conn_root.cursor() as cur:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"[+] Database `{MYSQL_DB}` siap di phpMyAdmin.")
    conn_root.close()

    # 4. Hubungkan ke Database bank_nasabah
    conn_mysql = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        charset="utf8mb4"
    )

    with conn_mysql.cursor() as cur:
        # Buat tabel nasabah
        cur.execute("""
        CREATE TABLE IF NOT EXISTS `nasabah` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `cif` VARCHAR(30) UNIQUE,
            `no_rekening` VARCHAR(30) UNIQUE,
            `nama_nasabah` VARCHAR(100),
            `nik` VARCHAR(20),
            `no_telepon` VARCHAR(25),
            `email` VARCHAR(100),
            `alamat` TEXT,
            `cabang_pembuka` VARCHAR(100),
            `produk_rekening` VARCHAR(50),
            `segmentasi` VARCHAR(50),
            `saldo_terakhir` DOUBLE,
            `status_kyc` VARCHAR(30),
            `tanggal_buka_rekening` DATE,
            `skor_risiko` VARCHAR(30),
            INDEX `idx_cabang` (`cabang_pembuka`),
            INDEX `idx_segmentasi` (`segmentasi`),
            INDEX `idx_saldo` (`saldo_terakhir`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Bersihkan tabel lama agar tidak duplikat
        cur.execute("TRUNCATE TABLE `nasabah`")
        print("[+] Tabel `nasabah` di MySQL siap menerima data.")

    # 5. Baca data dari SQLite
    print("[*] Membaca data nasabah dari SQLite...")
    conn_sqlite = sqlite3.connect(SQLITE_PATH)
    conn_sqlite.row_factory = sqlite3.Row
    sqlite_rows = conn_sqlite.execute("SELECT * FROM nasabah").fetchall()
    conn_sqlite.close()

    records = [dict(r) for r in sqlite_rows]
    print(f"[+] Ditemukan {len(records)} data nasabah di SQLite.")

    # 6. Masukkan ke MySQL
    sql_insert = """
    INSERT INTO `nasabah` (
        `cif`, `no_rekening`, `nama_nasabah`, `nik`, `no_telepon`, `email`, `alamat`,
        `cabang_pembuka`, `produk_rekening`, `segmentasi`, `saldo_terakhir`,
        `status_kyc`, `tanggal_buka_rekening`, `skor_risiko`
    ) VALUES (
        %(cif)s, %(no_rekening)s, %(nama_nasabah)s, %(nik)s, %(no_telepon)s, %(email)s, %(alamat)s,
        %(cabang_pembuka)s, %(produk_rekening)s, %(segmentasi)s, %(saldo_terakhir)s,
        %(status_kyc)s, %(tanggal_buka_rekening)s, %(skor_risiko)s
    )
    """

    with conn_mysql.cursor() as cur:
        cur.executemany(sql_insert, records)
        conn_mysql.commit()

    conn_mysql.close()

    print("\n" + "=" * 65)
    print(f"[SUKSES] Berhasil memasukkan {len(records)} data nasabah ke MySQL XAMPP!")
    print(f" -> Database : {MYSQL_DB}")
    print(f" -> Tabel    : nasabah")
    print(f" -> Cek di   : http://localhost/phpmyadmin")
    print("=" * 65)

if __name__ == "__main__":
    main()

