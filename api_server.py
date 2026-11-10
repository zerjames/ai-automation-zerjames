"""
REST API Service untuk Bank AI Automation.
Memungkinkan sistem internal lain (Portal Web PHP/Laravel, Core Banking, dll)
untuk menarik data nasabah dan men-download file Excel otomatis.
"""

from flask import Flask, request, jsonify, send_file
import os
import io
from bank_automation.database import init_database, execute_safe_query
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
    return jsonify({
        "status": "ONLINE",
        "service": "Bank AI Customer Automation API",
        "version": "2.0.0",
        "compliance": ["OJK", "BI", "UU PDP"]
    })

@app.route("/api/query", methods=["POST"])
def query_customers():
    """
    Endpoint untuk mengekstrak data nasabah menggunakan AI Prompt.
    Body JSON:
    {
        "prompt": "Tampilkan nasabah prioritas di KC Sudirman",
        "mask_data": true
    }
    """
    body = request.get_json(silent=True) or {}
    prompt = body.get("prompt", "Tampilkan 10 nasabah dengan saldo terbesar")
    mask_data = body.get("mask_data", True)
    
    try:
        sql_query = natural_language_to_sql(prompt)
        raw_data = execute_safe_query(sql_query)
        
        # Proses masking & risk flags
        processed = [apply_masking_to_record(r) if mask_data else r for r in raw_data]
        analyzed = analyze_customer_risks(processed)
        
        return jsonify({
            "success": True,
            "prompt": prompt,
            "sql_query": sql_query,
            "total_found": len(analyzed),
            "data": analyzed
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/export-excel", methods=["POST", "GET"])
def export_excel():
    """
    Endpoint untuk mendownload langsung file Excel hasil query AI.
    Query Param atau JSON Body: ?prompt=...&mask=true
    """
    if request.method == "POST":
        body = request.get_json(silent=True) or {}
        prompt = body.get("prompt", "Tampilkan 20 nasabah")
        mask_data = body.get("mask_data", True)
    else:
        prompt = request.args.get("prompt", "Tampilkan 20 nasabah")
        mask_data = request.args.get("mask", "true").lower() == "true"
        
    try:
        sql_query = natural_language_to_sql(prompt)
        raw_data = execute_safe_query(sql_query)
        processed = [apply_masking_to_record(r) if mask_data else r for r in raw_data]
        
        target_path = os.path.join(OUTPUT_DIR, "Laporan_API_Export.xlsx")
        export_customers_to_excel(
            processed, 
            target_path, 
            report_title=f"LAPORAN API: {prompt.upper()}", 
            is_masked=mask_data,
            executed_query=sql_query
        )
        
        return send_file(
            target_path,
            as_attachment=True,
            download_name="Laporan_Nasabah_Bank.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

if __name__ == "__main__":
    print("🚀 Bank AI Automation API Server berjalan di port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=False)

