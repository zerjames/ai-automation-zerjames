"""
Module Otomasi Terjadwal (Scheduled Automation Runner).
Dapat dijalankan secara mandiri atau didaftarkan ke Windows Task Scheduler
untuk mengekstraksi data nasabah dan mengenerate laporan Excel setiap hari/minggu secara otomatis.
"""

import os
import time
import argparse
from datetime import datetime
from bank_automation.database import init_database, execute_safe_query
from bank_automation.ai_engine import natural_language_to_sql
from bank_automation.validator import apply_masking_to_record
from bank_automation.excel_exporter import export_customers_to_excel

OUTPUT_BASE_DIR = os.path.join(os.path.dirname(__file__), "output", "scheduled_reports")

TASKS_PRESET = [
    {
        "id": "DAILY_PRIORITY_REPORT",
        "title": "LAPORAN HARIAN NASABAH PRIORITAS (DPK > 1 MILYAR)",
        "prompt": "Tampilkan nasabah prioritas dengan saldo di atas 1 milyar",
        "mask_data": True
    },
    {
        "id": "DAILY_AML_KYC_AUDIT",
        "title": "AUDIT HARIAN NASABAH DENGAN STATUS KYC PENDING ATAU EXPIRED",
        "prompt": "Cari nasabah yang status KYC nya pending atau expired",
        "mask_data": True
    },
    {
        "id": "DAILY_TOP_PORTFOLIO",
        "title": "REKAPITULASI TOP 50 NASABAH SALDO TERBESAR",
        "prompt": "Tampilkan 50 nasabah dengan saldo terbesar",
        "mask_data": True
    }
]

def run_scheduled_job(task):
    """Mengeksekusi satu tugas otomasi penarikan data dan penyimpanan berkas Excel."""
    task_id = task["id"]
    title = task["title"]
    prompt = task["prompt"]
    mask_data = task["mask_data"]

    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_dir = os.path.join(OUTPUT_BASE_DIR, datetime.now().strftime("%Y-%m-%d"))
    os.makedirs(target_dir, exist_ok=True)
    
    file_name = f"{task_id}_{date_str}.xlsx"
    target_path = os.path.join(target_dir, file_name)

    print(f"\n[JOB START] {task_id}")
    print(f" -> Judul   : {title}")
    print(f" -> Prompt  : '{prompt}'")

    # Eksekusi AI Text-to-SQL
    sql_query = natural_language_to_sql(prompt)
    results = execute_safe_query(sql_query)
    print(f" -> Hasil   : {len(results)} catatan nasabah ditemukan.")

    # Proses Masking
    processed = [apply_masking_to_record(r) if mask_data else r for r in results]

    # Ekspor ke Multi-Sheet Excel
    export_customers_to_excel(
        processed,
        target_path,
        report_title=title,
        is_masked=mask_data,
        executed_query=sql_query
    )

    print(f"[JOB DONE] Berkas Excel tersimpan di:")
    print(f" -> {target_path}")
    return target_path

def run_all_daily_tasks():
    """Menjalankan seluruh tugas preset harian."""
    print("=" * 65)
    print("[OTOMASI] MEMULAI PROSES EKSTRAKSI DATA NASABAH TERJADWAL")
    print(f"Waktu Eksekusi: {datetime.now().strftime('%d-%m-%Y %H:%M:%S WIB')}")
    print("=" * 65)

    init_database()
    generated_files = []

    for task in TASKS_PRESET:
        fpath = run_scheduled_job(task)
        generated_files.append(fpath)

    print("\n" + "=" * 65)
    print(f"[SELESAI] Seluruh {len(generated_files)} laporan Excel harian berhasil dibuat.")
    print("=" * 65)
    return generated_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bank Scheduled Automation Runner")
    parser.add_argument("--run-now", action="store_true", help="Jalankan semua tugas preset hari ini langsung")
    args = parser.parse_args()

    # Default: langsung jalankan seluruh batch
    run_all_daily_tasks()

