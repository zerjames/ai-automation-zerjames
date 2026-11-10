"""
CLI Script: Menjalankan otomatisasi penarikan data nasabah via Terminal / Batch.
Standar Output: Enterprise Console (No Emoji, Plain Text Format).
"""

import argparse
import os
from bank_automation.database import init_database, execute_safe_query
from bank_automation.ai_engine import natural_language_to_sql
from bank_automation.validator import apply_masking_to_record
from bank_automation.excel_exporter import export_customers_to_excel

def main():
    parser = argparse.ArgumentParser(description="Bank Customer Data Extraction Automation Engine")
    parser.add_argument("--prompt", "-p", type=str, default="Tampilkan nasabah prioritas dengan saldo di atas 500 juta", help="Prompt bahasa Indonesia untuk penarikan data")
    parser.add_argument("--output", "-o", type=str, default="output/Laporan_Nasabah_Batch.xlsx", help="Path file output Excel")
    parser.add_argument("--unmask", action="store_true", help="Nonaktifkan sensor data (default: masked untuk kepatuhan PDP)")
    args = parser.parse_args()

    print("------------------------------------------------------------")
    print("[SYSTEM] CORE BANKING DATA EXTRACTION ENGINE v2.4")
    print("------------------------------------------------------------")
    
    init_database()
    
    print(f"[INPUT]  Prompt : '{args.prompt}'")
    sql_query = natural_language_to_sql(args.prompt)
    print(f"[ENGINE] SQL    : {sql_query}")
    
    print("[STATUS] Mengakses Database Core Banking (Read-Only)...")
    results = execute_safe_query(sql_query)
    print(f"[RESULT] Ditemukan {len(results)} catatan nasabah.")
    
    if not results:
        print("[NOTICE] Tidak ada catatan yang cocok. Proses selesai.")
        return

    is_masked = not args.unmask
    processed = [apply_masking_to_record(r) if is_masked else r for r in results]
    
    print(f"[EXPORT] Menyusun Workbook Multi-Sheet Excel ({'Masked PDP' if is_masked else 'Unmasked'})...")
    output_full_path = os.path.abspath(args.output)
    export_customers_to_excel(
        processed, 
        output_full_path, 
        report_title="LAPORAN DATA NASABAH (AUTOMATION BATCH)", 
        is_masked=is_masked,
        executed_query=sql_query
    )
    
    print(f"[FINISH] Berkas Excel siap di:\n         -> {output_full_path}")
    print("------------------------------------------------------------")

if __name__ == "__main__":
    main()
