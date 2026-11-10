"""
Skrip Contoh: Menarik Data Nasabah dari Server API (HTTP) dan Ekspor ke Excel.
Mensimulasikan bagaimana klien / sistem luar menarik data dari Core Banking REST API.
"""

import sys
import os
from bank_automation.api_client import (
    check_server_status,
    fetch_customers_via_api,
    fetch_customers_via_ai_prompt,
    pull_from_server_and_export_excel
)

def main():
    print("=" * 65)
    print("DEMO: PENARIKAN DATA NASABAH DARI REST API SERVER KE EXCEL")
    print("=" * 65)

    # 1. Cek apakah server online
    is_online, status_info = check_server_status()
    if not is_online:
        print("\n[PERINGATAN] Server API (http://localhost:5000) sedang OFFLINE.")
        print("Silakan jalankan server terlebih dahulu:")
        print(" -> Klik 2x file 'run_server.bat' atau jalankan 'python api_server.py'")
        print("=" * 65)
        sys.exit(1)

    print("[+] Server API ONLINE!")
    print(f" -> Backend Database : {status_info.get('database_backend')}")
    print(f" -> Target Koneksi   : {status_info.get('database_target')}")

    # 2. Contoh Tarik Data via Parameter HTTP GET
    print("\n[1] Menarik Data via HTTP GET: /api/v1/customers?segmentasi=Prioritas&limit=10")
    params = {"segmentasi": "Prioritas", "limit": 10}
    customers = fetch_customers_via_api(params)
    print(f" -> Berhasil menerima {len(customers)} catatan nasabah dari Server API (JSON).")

    # 3. Contoh Tarik Data via AI Prompt POST
    prompt_test = "Tampilkan nasabah prioritas di KC Jakarta Sudirman saldo di atas 500 juta"
    print(f"\n[2] Menarik Data via AI Prompt POST: '{prompt_test}'")
    out_file = os.path.join(os.path.dirname(__file__), "output", "Laporan_Hasil_Tarik_Dari_API.xlsx")
    
    file_saved, total = pull_from_server_and_export_excel(
        prompt=prompt_test,
        output_path=out_file,
        mask_data=True
    )

    print(f" -> Berhasil memproses {total} data nasabah dari API Server.")
    print(f"[SUKSES] Berkas Excel berhasil digenerate dari respon API:")
    print(f" -> {file_saved}")
    print("=" * 65)

if __name__ == "__main__":
    main()

