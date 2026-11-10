"""
Module untuk menghasilkan data sampel nasabah perbankan Indonesia yang realistis.
Dapat digunakan untuk pengujian atau simulasi penarikan data core banking.
"""

import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('id_ID')

CABANG_LIST = [
    "KC Jakarta Sudirman",
    "KC Jakarta Thamrin",
    "KC Surabaya Darmo",
    "KC Bandung Asia Afrika",
    "KC Medan Balai Kota",
    "KC Semarang Pemuda",
    "KC Yogyakarta Malioboro",
    "KC Makassar Ratulangi",
    "KC Denpasar Gajah Mada"
]

JENIS_TABUNGAN = [
    "Tabungan Utama IDR",
    "Tabungan Bisnis IDR",
    "Tabungan Valas USD",
    "Giro Perorangan",
    "Deposito Berjangka"
]

STATUS_KYC = ["Verified", "Verified", "Verified", "Pending Review", "Expired"]

def generate_nik():
    # 16 digit NIK realistis Indonesia: [6 digit wilayah][6 digit tgl lahir][4 digit urut]
    provinsi = random.choice(["31", "32", "33", "35", "51", "12", "73"])
    kota = str(random.randint(1, 99)).zfill(2)
    kecamatan = str(random.randint(1, 99)).zfill(2)
    tgl = str(random.randint(1, 28)).zfill(2)
    bln = str(random.randint(1, 12)).zfill(2)
    thn = str(random.randint(70, 99)).zfill(2)
    urut = str(random.randint(1, 9999)).zfill(4)
    return f"{provinsi}{kota}{kecamatan}{tgl}{bln}{thn}{urut}"

def generate_no_rekening():
    # 10-12 digit format rekening
    return f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(100000, 999999)}"

def generate_cif():
    # Customer Information File ID
    return f"CIF{random.randint(10000000, 99999999)}"

def generate_dummy_customers(count=100):
    """Menghasilkan list dictionary nasabah dengan format perbankan."""
    customers = []
    
    for _ in range(count):
        gender = random.choice(["M", "F"])
        nama = fake.name_male() if gender == "M" else fake.name_female()
        
        # Saldo bervariasi dari tabungan mikro sampai nasabah prioritas
        tier = random.choices(["Reguler", "Gold", "Prioritas / High Net Worth"], weights=[70, 20, 10])[0]
        if tier == "Reguler":
            saldo = round(random.uniform(500_000, 49_999_999), -3)
        elif tier == "Gold":
            saldo = round(random.uniform(50_000_000, 499_999_999), -3)
        else:
            saldo = round(random.uniform(500_000_000, 8_500_000_000), -3)

        tanggal_buka = fake.date_between(start_date='-5y', end_date='today')
        nik = generate_nik()
        no_hp = "08" + str(random.choice([12, 13, 21, 52, 57, 81])) + str(random.randint(1000000, 9999999))
        
        customers.append({
            "cif": generate_cif(),
            "no_rekening": generate_no_rekening(),
            "nama_nasabah": nama,
            "nik": nik,
            "no_telepon": no_hp,
            "email": fake.email(),
            "alamat": fake.street_address() + ", " + fake.city(),
            "cabang_pembuka": random.choice(CABANG_LIST),
            "produk_rekening": random.choice(JENIS_TABUNGAN),
            "segmentasi": tier,
            "saldo_terakhir": saldo,
            "status_kyc": random.choice(STATUS_KYC),
            "tanggal_buka_rekening": tanggal_buka.strftime("%Y-%m-%d"),
            "skor_risiko": random.choices(["Rendah", "Menengah", "Tinggi"], weights=[75, 20, 5])[0]
        })
        
    return customers

