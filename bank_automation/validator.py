"""
Module untuk validasi data nasabah dan Data Masking (Perlindungan Data Pribadi / PDP).
"""

import re

def validate_nik(nik: str) -> bool:
    """Memeriksa apakah NIK terdiri dari 16 digit numerik."""
    if not nik:
        return False
    return bool(re.match(r'^\d{16}$', str(nik).strip()))

def mask_nik(nik: str) -> str:
    """Sensor 8 digit di tengah NIK untuk keamanan (contoh: 3201********1234)."""
    if not nik:
        return "-"
    s = str(nik).strip()
    if len(s) == 16:
        return f"{s[:4]}{'*' * 8}{s[-4:]}"
    return f"{s[:2]}{'*' * (max(0, len(s)-4))}{s[-2:]}" if len(s) > 4 else "****"

def mask_account_number(acc_no: str) -> str:
    """Sensor bagian tengah nomor rekening (contoh: 123-**-***999)."""
    if not acc_no:
        return "-"
    s = str(acc_no).strip()
    if len(s) >= 8:
        return f"{s[:3]}-{'*' * 4}-{s[-3:]}"
    return f"{s[:2]}***{s[-2:]}"

def mask_phone(phone: str) -> str:
    """Sensor 4 digit tengah no telepon (contoh: 0812****5678)."""
    if not phone:
        return "-"
    s = str(phone).strip()
    if len(s) >= 9:
        return f"{s[:4]}{'*' * 4}{s[-3:]}"
    return "****"

def apply_masking_to_record(customer: dict) -> dict:
    """Membuat salinan data dengan data sensitif (PII) yang telah disensor."""
    masked = customer.copy()
    masked["nik"] = mask_nik(customer.get("nik", ""))
    masked["no_rekening"] = mask_account_number(customer.get("no_rekening", ""))
    masked["no_telepon"] = mask_phone(customer.get("no_telepon", ""))
    
    # Masking email (contoh: a***@domain.com)
    email = customer.get("email", "")
    if "@" in email:
        username, domain = email.split("@", 1)
        masked_user = username[0] + "***" if len(username) > 1 else "*"
        masked["email"] = f"{masked_user}@{domain}"
        
    return masked

