"""
Server API Core Banking (Simulasi Server Bank).
Menyediakan REST API resmi untuk membaca data nasabah dari database (MySQL / SQL).
Endpoint ini yang dihubungi oleh script Python AI Automation untuk menarik data.
"""

from flask import Flask, request, jsonify, send_file
import os
import pymysql
from bank_automation.database import execute_safe_query, get_active_db_info, init_database
from bank_automation.ai_engine import natural_language_to_sql
from bank_automation.validator import apply_masking_to_record
from bank_automation.excel_exporter import export_customers_to_excel
from bank_automation.analytics import analyze_customer_risks

app = Flask(__name__)
init_database()

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/api/health", methods=["GET"])
def health():
    """Cek status server dan database."""
    db_info = get_active_db_info()
    return jsonify({
        "status": "ONLINE",
        "service": "Core Banking REST API Server",
        "version": "2.4.0",
        "database_backend": db_info["name"],
        "database_target": db_info["target"],
        "compliance": ["OJK", "BI", "UU PDP"]
    })

@app.route("/api/v1/customers", methods=["GET"])
def get_customers():
    """
    Endpoint Server untuk mengambil data nasabah dari database.
    Mendukung filter via Query Parameters:
    - nama: string
    - cabang: string
    - segmentasi: string (Reguler, Gold, Prioritas)
    - status_kyc: string (Verified, Pending Review, Expired)
    - saldo_min: float
    - limit: int
    """
    nama = request.args.get("nama")
    cabang = request.args.get("cabang")
    segmentasi = request.args.get("segmentasi")
    status_kyc = request.args.get("status_kyc")
    saldo_min = request.args.get("saldo_min", type=float)
    cif = request.args.get("cif")
    nik = request.args.get("nik")
    limit = request.args.get("limit", default=100, type=int)

    conditions = []
    if nama:
        safe_name = nama.replace("'", "''")
        conditions.append(f"nama_nasabah LIKE '%{safe_name}%'")
    if cabang:
        safe_cabang = cabang.replace("'", "''")
        conditions.append(f"cabang_pembuka LIKE '%{safe_cabang}%'")
    if segmentasi:
        conditions.append(f"segmentasi LIKE '%{segmentasi}%'")
    if status_kyc:
        conditions.append(f"status_kyc = '{status_kyc}'")
    if saldo_min is not None and saldo_min > 0:
        conditions.append(f"saldo_terakhir >= {saldo_min}")
    if cif:
        conditions.append(f"cif = '{cif.upper()}'")
    if nik:
        conditions.append(f"nik LIKE '%{nik}%'")

    sql = "SELECT * FROM nasabah"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += f" ORDER BY saldo_terakhir DESC LIMIT {min(limit, 500)}"

    try:
        data = execute_safe_query(sql)
        return jsonify({
            "status": "SUCCESS",
            "server": "Core Banking API Server",
            "sql_executed": sql,
            "total_records": len(data),
            "data": data
        })
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@app.route("/api/v1/ai-pull", methods=["POST"])
def ai_pull_customers():
    """
    Endpoint Server AI: Menerima Prompt Bahasa Indonesia, menerjemahkan ke SQL,
    mengekstrak data dari database, dan mengembalikan respon JSON.
    """
    body = request.get_json(silent=True) or {}
    prompt = body.get("prompt", "Tampilkan 20 nasabah")
    mask_pdp = body.get("mask_data", True)

    try:
        sql_query = natural_language_to_sql(prompt)
        raw_data = execute_safe_query(sql_query)
        processed = [apply_masking_to_record(r) if mask_pdp else r for r in raw_data]
        analyzed = analyze_customer_risks(processed)

        return jsonify({
            "status": "SUCCESS",
            "prompt": prompt,
            "sql_query": sql_query,
            "total_found": len(analyzed),
            "data": analyzed
        })
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 400

@app.route("/api/v1/export-excel", methods=["GET", "POST"])
def export_excel_from_api():
    """
    Endpoint Server untuk langsung men-download berkas Excel resmi.
    """
    if request.method == "POST":
        body = request.get_json(silent=True) or {}
        prompt = body.get("prompt", "Tampilkan 20 nasabah")
        mask_pdp = body.get("mask_data", True)
    else:
        prompt = request.args.get("prompt", "Tampilkan 20 nasabah")
        mask_pdp = request.args.get("mask", "true").lower() == "true"

    try:
        sql_query = natural_language_to_sql(prompt)
        raw_data = execute_safe_query(sql_query)
        processed = [apply_masking_to_record(r) if mask_pdp else r for r in raw_data]

        target_file = os.path.join(OUTPUT_DIR, "Laporan_API_Server_Export.xlsx")
        export_customers_to_excel(
            processed,
            target_file,
            report_title=f"LAPORAN SERVER API: {prompt.upper()}",
            is_masked=mask_pdp,
            executed_query=sql_query
        )

        return send_file(
            target_file,
            as_attachment=True,
            download_name="Laporan_Nasabah_API_Server.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 400

if __name__ == "__main__":
    print("=" * 65)
    print("[SERVER] CORE BANKING REST API SERVER AKTIF")
    print("Endpoint: http://localhost:5000")
    print("Test URL: http://localhost:5000/api/health")
    print("=" * 65)
    app.run(host="0.0.0.0", port=5000, debug=False)
