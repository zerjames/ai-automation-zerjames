"""
Module API Client: Menarik data nasabah dari Core Banking REST API Server via HTTP.
Menggunakan library 'requests' untuk berkomunikasi dengan Server API,
lalu memproses hasil JSON dan mengekspornya ke berkas Excel resmi.
"""

import requests
import os
from .validator import apply_masking_to_record
from .excel_exporter import export_customers_to_excel
from .analytics import analyze_customer_risks

API_BASE_URL = os.getenv("BANK_API_URL", "http://localhost:5000")

def check_server_status(base_url=API_BASE_URL):
    """Memeriksa apakah Server API Core Banking sedang aktif."""
    try:
        res = requests.get(f"{base_url}/api/health", timeout=2)
        if res.status_code == 200:
            return True, res.json()
        return False, f"Server merespon dengan status {res.status_code}"
    except Exception as e:
        return False, str(e)

def fetch_customers_via_api(params=None, base_url=API_BASE_URL):
    """
    Menarik data nasabah dari Server API melalui endpoint GET /api/v1/customers.
    Contoh params: {'cabang': 'Sudirman', 'segmentasi': 'Prioritas', 'saldo_min': 500000000}
    """
    url = f"{base_url}/api/v1/customers"
    try:
        res = requests.get(url, params=params, timeout=5)
        res.raise_for_status()
        payload = res.json()
        return payload.get("data", [])
    except Exception as e:
        raise ConnectionError(f"Gagal menarik data dari Server API ({url}): {str(e)}")

def fetch_customers_via_ai_prompt(prompt: str, mask_data=True, base_url=API_BASE_URL):
    """
    Menarik data nasabah dari Server API menggunakan Prompt AI melalui endpoint POST /api/v1/ai-pull.
    """
    url = f"{base_url}/api/v1/ai-pull"
    try:
        res = requests.post(url, json={"prompt": prompt, "mask_data": mask_data}, timeout=5)
        res.raise_for_status()
        payload = res.json()
        return payload
    except Exception as e:
        raise ConnectionError(f"Gagal memproses prompt ke Server API ({url}): {str(e)}")

def pull_from_server_and_export_excel(prompt: str, output_path: str, mask_data=True, base_url=API_BASE_URL):
    """
    Workflow Lengkap:
    1. Kirim prompt ke Server API
    2. Terima JSON data nasabah dari Server API
    3. Generate dan simpan ke file Multi-Sheet Excel
    """
    payload = fetch_customers_via_ai_prompt(prompt, mask_data=mask_data, base_url=base_url)
    records = payload.get("data", [])
    sql_executed = payload.get("sql_query", "")

    export_customers_to_excel(
        records,
        output_path,
        report_title=f"LAPORAN DITARIK DARI SERVER API: {prompt.upper()}",
        is_masked=mask_data,
        executed_query=sql_executed
    )
    return output_path, len(records)

