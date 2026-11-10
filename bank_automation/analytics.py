"""
Module Analitik & Deteksi Risiko Nasabah (AML & Regulatory Compliance).
Mendeteksi anomali pada profil nasabah untuk kebutuhan pelaporan Audit & Risk Management.
"""

def analyze_customer_risks(customers):
    """
    Memeriksa setiap data nasabah dan menambahkan indikator risiko & compliance.
    """
    flagged_records = []
    
    for c in customers:
        item = c.copy()
        flags = []
        
        saldo = float(item.get("saldo_terakhir", 0))
        kyc = item.get("status_kyc", "")
        risk = item.get("skor_risiko", "")
        segment = item.get("segmentasi", "")
        
        # Aturan 1: Saldo besar (> 500 jt) tapi KYC Expired/Pending (AML Alert)
        if saldo >= 500_000_000 and kyc in ["Expired", "Pending Review"]:
            flags.append("HIGH DPK WITH UNVERIFIED KYC")
            
        # Aturan 2: High Risk Profile dengan saldo di atas batas wajar reguler
        if risk == "Tinggi" and saldo > 100_000_000:
            flags.append("HIGH RISK ACCOUNT MONITORING")
            
        # Aturan 3: Nasabah Prioritas dengan KYC Expired
        if "Prioritas" in segment and kyc == "Expired":
            flags.append("PRIORITY KYC EXPIRED - ACTION NEEDED")
            
        item["compliance_flags"] = " | ".join(flags) if flags else "COMPLIANT"
        item["is_flagged"] = len(flags) > 0
        flagged_records.append(item)
        
    return flagged_records

def generate_branch_summary(customers):
    """Menghitung agregasi saldo dan jumlah nasabah per cabang."""
    branch_map = {}
    for c in customers:
        cabang = c.get("cabang_pembuka", "Lainnya")
        saldo = float(c.get("saldo_terakhir", 0))
        
        if cabang not in branch_map:
            branch_map[cabang] = {"count": 0, "total_saldo": 0.0}
            
        branch_map[cabang]["count"] += 1
        branch_map[cabang]["total_saldo"] += saldo
        
    summary_list = [
        {
            "cabang": k,
            "total_nasabah": v["count"],
            "total_saldo": v["total_saldo"],
            "rata_rata_saldo": v["total_saldo"] / v["count"] if v["count"] > 0 else 0
        }
        for k, v in branch_map.items()
    ]
    
    summary_list.sort(key=lambda x: x["total_saldo"], reverse=True)
    return summary_list

