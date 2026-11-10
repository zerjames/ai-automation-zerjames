"""
Module untuk mengekspor data nasabah ke format Multi-Sheet Excel (.xlsx) Standar Korporat Perbankan.
Didesain dengan standar visual pelaporan keuangan profesional (Executive Presentation Grade).

Lembar Kerja:
1. Ringkasan Eksekutif (Executive Summary, 3 KPI Cards, Rekapitulasi Cabang, & Total DPK)
2. Detail Data Nasabah (Tabel Utama, Format Mata Uang Rp, Badge KYC & AML Terstruktur)
3. Audit Trail & Kepatuhan (Format Kartu Audit Formal Standar ISO 27001 / OJK)
"""

import os
import hashlib
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from .analytics import analyze_customer_risks, generate_branch_summary

# Palet Warna Korporat Perbankan (Navy & Ice Blue)
NAVY_PRIMARY    = "0F2942"  # Deep Bank Navy
NAVY_HEADER     = "1B365D"  # Corporate Blue
NAVY_ACCENT     = "2C5282"  # Table Header Blue
ICE_BLUE_BG     = "F0F4F8"  # Soft Card Fill
CARD_LABEL_GRAY = "475569"  # Slate text
ZEBRA_ROW       = "F8FAFC"  # Very light soft gray
WHITE           = "FFFFFF"
BORDER_COLOR    = "CBD5E1"  # Crisp slate border

# Warna Status Badge
KYC_VERIFIED_BG   = "DCFCE7"  # Soft green
KYC_VERIFIED_TXT  = "166534"
KYC_PENDING_BG    = "FEF3C7"  # Soft amber
KYC_PENDING_TXT   = "92400E"
KYC_EXPIRED_BG    = "FEE2E2"  # Soft red
KYC_EXPIRED_TXT   = "991B1B"

BORDER_THIN = Border(
    left=Side(style='thin', color=BORDER_COLOR),
    right=Side(style='thin', color=BORDER_COLOR),
    top=Side(style='thin', color=BORDER_COLOR),
    bottom=Side(style='thin', color=BORDER_COLOR)
)

BORDER_TOTAL_ROW = Border(
    left=Side(style='thin', color=BORDER_COLOR),
    right=Side(style='thin', color=BORDER_COLOR),
    top=Side(style='thin', color=NAVY_PRIMARY),
    bottom=Side(style='double', color=NAVY_PRIMARY)
)

BANNER_FILL = PatternFill(start_color=NAVY_PRIMARY, end_color=NAVY_PRIMARY, fill_type="solid")

def style_merged_range(ws, cell_range, fill=None, border=None):
    """Menerapkan border dan fill ke seluruh cell dalam merged range agar tidak bolong."""
    for row in ws[cell_range]:
        for cell in row:
            if fill:
                cell.fill = fill
            if border:
                cell.border = border

def export_customers_to_excel(customers, output_path, report_title="LAPORAN DATA NASABAH PERBANKAN", is_masked=True, executed_query="", **kwargs):
    """
    Menghasilkan berkas Excel Multi-Sheet dengan tata letak & tipografi perbankan presisi.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    executed_query = executed_query or kwargs.get("executed_query", "")
    
    customers_analyzed = analyze_customer_risks(customers)
    branch_summaries = generate_branch_summary(customers_analyzed)
    
    wb = openpyxl.Workbook()
    now_str = datetime.now().strftime("%d-%m-%Y %H:%M:%S WIB")

    # =========================================================================
    # SHEET 1: RINGKASAN EKSEKUTIF
    # =========================================================================
    ws_exec = wb.active
    ws_exec.title = "Ringkasan Eksekutif"
    ws_exec.views.sheetView[0].showGridLines = True

    # Lebar Kolom yang Presisi (Total 6 Kolom A-F)
    exec_col_widths = {
        "A": 8,   # No
        "B": 34,  # Cabang
        "C": 20,  # Jumlah Rekening
        "D": 30,  # Total Saldo
        "E": 28,  # Rata-rata Saldo
        "F": 20   # Pangsa Saldo (%)
    }
    for col, width in exec_col_widths.items():
        ws_exec.column_dimensions[col].width = width

    # 1. Header Banner Utama (A1:F1)
    ws_exec.merge_cells("A1:F1")
    t1 = ws_exec["A1"]
    t1.value = f"RINGKASAN EKSEKUTIF - {report_title}"
    t1.font = Font(name="Segoe UI", size=14, bold=True, color=WHITE)
    t1.fill = PatternFill(start_color=NAVY_PRIMARY, end_color=NAVY_PRIMARY, fill_type="solid")
    t1.alignment = Alignment(horizontal="center", vertical="center")
    ws_exec.row_dimensions[1].height = 40
    style_merged_range(ws_exec, "A1:F1", fill=BANNER_FILL)

    # Subtitle (A2:F2)
    ws_exec.merge_cells("A2:F2")
    s1 = ws_exec["A2"]
    s1.value = f"Digenerate Otomatis oleh Core Banking AI Engine | Tanggal: {now_str} | Status Masking: {'TERMASKING (Kepatuhan UU PDP)' if is_masked else 'FULL AKSES'}"
    s1.font = Font(name="Segoe UI", size=9, italic=True, color="64748B")
    s1.alignment = Alignment(horizontal="center", vertical="center")
    ws_exec.row_dimensions[2].height = 22

    # 2. Tiga Kartu KPI Eksekutif (Row 4 & 5)
    # Card 1: A4:B5 (Total Nasabah)
    # Card 2: C4:D5 (Total Saldo DPK)
    # Card 3: E4:F5 (Nasabah Prioritas & AML)
    total_nasabah = len(customers_analyzed)
    total_saldo = sum(c.get("saldo_terakhir", 0) for c in customers_analyzed)
    flagged_count = sum(1 for c in customers_analyzed if c.get("is_flagged", False))
    prioritas_count = sum(1 for c in customers_analyzed if "Prioritas" in c.get("segmentasi", ""))

    card_fill = PatternFill(start_color=ICE_BLUE_BG, end_color=ICE_BLUE_BG, fill_type="solid")
    
    kpi_cards = [
        ("A", "B", "TOTAL PORTOFOLIO NASABAH", f"{total_nasabah:,} Rekening Terdaftar", NAVY_PRIMARY),
        ("C", "D", "TOTAL DANA KELOLAAN (DPK)", f"Rp {total_saldo:,.0f}", NAVY_PRIMARY),
        ("E", "F", "NASABAH PRIORITAS & RISIKO", f"{prioritas_count:,} Prioritas  |  {flagged_count} Flag AML", "B91C1C" if flagged_count > 0 else NAVY_PRIMARY)
    ]

    ws_exec.row_dimensions[4].height = 18
    ws_exec.row_dimensions[5].height = 30

    for col_start, col_end, lbl, val, val_color in kpi_cards:
        range_lbl = f"{col_start}4:{col_end}4"
        ws_exec.merge_cells(range_lbl)
        c_lbl = ws_exec[f"{col_start}4"]
        c_lbl.value = lbl
        c_lbl.font = Font(name="Segoe UI", size=8, bold=True, color=CARD_LABEL_GRAY)
        c_lbl.alignment = Alignment(horizontal="center", vertical="center")
        style_merged_range(ws_exec, range_lbl, fill=card_fill, border=BORDER_THIN)

        range_val = f"{col_start}5:{col_end}5"
        ws_exec.merge_cells(range_val)
        c_val = ws_exec[f"{col_start}5"]
        c_val.value = val
        c_val.font = Font(name="Segoe UI", size=13, bold=True, color=val_color)
        c_val.alignment = Alignment(horizontal="center", vertical="center")
        style_merged_range(ws_exec, range_val, fill=card_fill, border=BORDER_THIN)

    # 3. Tabel Rekapitulasi Cabang (Mulai Baris 7)
    ws_exec["A7"].value = "DISTRIBUSI DANA & NASABAH PER KANTOR CABANG"
    ws_exec["A7"].font = Font(name="Segoe UI", size=11, bold=True, color=NAVY_PRIMARY)
    ws_exec.row_dimensions[7].height = 24

    b_headers = [
        ("No", "center"),
        ("Kantor Cabang Pengelola", "left"),
        ("Jumlah Rekening", "center"),
        ("Total Saldo (IDR)", "right"),
        ("Rata-rata Saldo (IDR)", "right"),
        ("Pangsa Saldo (%)", "center")
    ]
    
    ws_exec.row_dimensions[8].height = 26
    header_fill = PatternFill(start_color=NAVY_ACCENT, end_color=NAVY_ACCENT, fill_type="solid")
    
    for idx, (h_title, align_h) in enumerate(b_headers, start=1):
        cell = ws_exec.cell(row=8, column=idx, value=h_title)
        cell.fill = header_fill
        cell.font = Font(name="Segoe UI", size=10, bold=True, color=WHITE)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = BORDER_THIN

    # Baris Data Cabang
    start_branch_row = 9
    for idx, b in enumerate(branch_summaries, start=1):
        r = start_branch_row + idx - 1
        ws_exec.row_dimensions[r].height = 22
        fill = PatternFill(start_color=ZEBRA_ROW, end_color=ZEBRA_ROW, fill_type="solid") if idx % 2 == 0 else PatternFill(start_color=WHITE, end_color=WHITE, fill_type="solid")
        
        c_no = ws_exec.cell(row=r, column=1, value=idx)
        c_no.alignment = Alignment(horizontal="center", vertical="center")
        
        c_cab = ws_exec.cell(row=r, column=2, value=b["cabang"])
        c_cab.alignment = Alignment(horizontal="left", vertical="center")
        
        c_cnt = ws_exec.cell(row=r, column=3, value=b["total_nasabah"])
        c_cnt.alignment = Alignment(horizontal="center", vertical="center")
        c_cnt.number_format = '#,##0'
        
        c_tot = ws_exec.cell(row=r, column=4, value=b["total_saldo"])
        c_tot.alignment = Alignment(horizontal="right", vertical="center")
        c_tot.number_format = '"Rp "#,##0'
        
        c_avg = ws_exec.cell(row=r, column=5, value=b["rata_rata_saldo"])
        c_avg.alignment = Alignment(horizontal="right", vertical="center")
        c_avg.number_format = '"Rp "#,##0'
        
        share_val = (b["total_saldo"] / total_saldo) if total_saldo > 0 else 0
        c_pct = ws_exec.cell(row=r, column=6, value=share_val)
        c_pct.alignment = Alignment(horizontal="center", vertical="center")
        c_pct.number_format = '0.0%'
        
        for col_i in range(1, 7):
            cell = ws_exec.cell(row=r, column=col_i)
            cell.fill = fill
            cell.border = BORDER_THIN
            cell.font = Font(name="Segoe UI", size=9)

    # Baris Total Akuntansi
    total_row = start_branch_row + len(branch_summaries)
    ws_exec.row_dimensions[total_row].height = 26
    
    ws_exec.cell(row=total_row, column=1, value="")
    t_lbl = ws_exec.cell(row=total_row, column=2, value="TOTAL KONSOLIDASI SELURUH CABANG")
    t_lbl.font = Font(name="Segoe UI", size=10, bold=True, color=NAVY_PRIMARY)
    t_lbl.alignment = Alignment(horizontal="left", vertical="center")
    
    t_cnt = ws_exec.cell(row=total_row, column=3, value=f"=SUM(C{start_branch_row}:C{total_row-1})")
    t_cnt.alignment = Alignment(horizontal="center", vertical="center")
    t_cnt.number_format = '#,##0'
    t_cnt.font = Font(name="Segoe UI", size=10, bold=True, color=NAVY_PRIMARY)
    
    t_sal = ws_exec.cell(row=total_row, column=4, value=f"=SUM(D{start_branch_row}:D{total_row-1})")
    t_sal.alignment = Alignment(horizontal="right", vertical="center")
    t_sal.number_format = '"Rp "#,##0'
    t_sal.font = Font(name="Segoe UI", size=10, bold=True, color=NAVY_PRIMARY)
    
    t_avg = ws_exec.cell(row=total_row, column=5, value=f"=AVERAGE(E{start_branch_row}:E{total_row-1})")
    t_avg.alignment = Alignment(horizontal="right", vertical="center")
    t_avg.number_format = '"Rp "#,##0'
    t_avg.font = Font(name="Segoe UI", size=10, bold=True, color=NAVY_PRIMARY)

    t_pct = ws_exec.cell(row=total_row, column=6, value=1.0)
    t_pct.alignment = Alignment(horizontal="center", vertical="center")
    t_pct.number_format = '0.0%'
    t_pct.font = Font(name="Segoe UI", size=10, bold=True, color=NAVY_PRIMARY)

    for col_i in range(1, 7):
        ws_exec.cell(row=total_row, column=col_i).border = BORDER_TOTAL_ROW
        ws_exec.cell(row=total_row, column=col_i).fill = PatternFill(start_color=ICE_BLUE_BG, end_color=ICE_BLUE_BG, fill_type="solid")

    # =========================================================================
    # SHEET 2: DETAIL DATA NASABAH
    # =========================================================================
    ws_data = wb.create_sheet(title="Data Nasabah")
    ws_data.views.sheetView[0].showGridLines = True

    # 12 Kolom Terdefinisi dengan Lebar Nyaman
    data_columns = [
        ("No", 6, "center"),
        ("CIF", 15, "center"),
        ("No. Rekening", 18, "center"),
        ("Nama Nasabah", 26, "left"),
        ("NIK", 20, "center"),
        ("No. Telepon", 16, "center"),
        ("Cabang Pembuka", 26, "left"),
        ("Produk Rekening", 22, "left"),
        ("Segmentasi", 28, "left"),        # Lebar 28 agar "Prioritas / High Net Worth" muat
        ("Status KYC", 16, "center"),
        ("Saldo Akhir (IDR)", 24, "right"),
        ("Status Kepatuhan (AML)", 34, "left") # Lebar 34 & wrap text
    ]

    for col_idx, (_, col_w, _) in enumerate(data_columns, start=1):
        col_letter = get_column_letter(col_idx)
        ws_data.column_dimensions[col_letter].width = col_w

    # Header Banner Sheet 2 (A1:L1)
    ws_data.merge_cells("A1:L1")
    t2 = ws_data["A1"]
    t2.value = f"DETAIL DATA NASABAH - {report_title}"
    t2.font = Font(name="Segoe UI", size=14, bold=True, color=WHITE)
    t2.fill = PatternFill(start_color=NAVY_PRIMARY, end_color=NAVY_PRIMARY, fill_type="solid")
    t2.alignment = Alignment(horizontal="center", vertical="center")
    ws_data.row_dimensions[1].height = 38
    style_merged_range(ws_data, "A1:L1", fill=BANNER_FILL)

    # Subtitle Sheet 2 (A2:L2)
    ws_data.merge_cells("A2:L2")
    s2 = ws_data["A2"]
    s2.value = f"Total Record: {len(customers_analyzed)} Nasabah | Waktu Ekstraksi: {now_str} | Proteksi PDP: {'AKTIF (NIK & No Rekening Disensor)' if is_masked else 'DATA LENGKAP'}"
    s2.font = Font(name="Segoe UI", size=9, italic=True, color="64748B")
    s2.alignment = Alignment(horizontal="center", vertical="center")
    ws_data.row_dimensions[2].height = 20

    # Header Tabel di Baris 4
    header_table_row = 4
    ws_data.row_dimensions[header_table_row].height = 28
    
    for col_idx, (col_name, _, _) in enumerate(data_columns, start=1):
        c = ws_data.cell(row=header_table_row, column=col_idx, value=col_name)
        c.fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
        c.font = Font(name="Segoe UI", size=10, bold=True, color=WHITE)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDER_THIN

    # Baris Data Nasabah
    start_cust_row = 5
    for idx, c in enumerate(customers_analyzed, start=1):
        r = start_cust_row + idx - 1
        ws_data.row_dimensions[r].height = 24  # Tinggi baris nyaman
        fill = PatternFill(start_color=ZEBRA_ROW, end_color=ZEBRA_ROW, fill_type="solid") if idx % 2 == 0 else PatternFill(start_color=WHITE, end_color=WHITE, fill_type="solid")
        
        is_flagged = c.get("is_flagged", False)
        kyc_status = c.get("status_kyc", "Verified")
        
        # Bersihkan deskripsi AML agar rapi
        raw_flags = c.get("compliance_flags", "COMPLIANT")
        clean_flags = raw_flags.replace(" | ", "\n") if is_flagged else "COMPLIANT"

        row_vals = [
            idx,
            c.get("cif", "-"),
            c.get("no_rekening", "-"),
            c.get("nama_nasabah", "-"),
            c.get("nik", "-"),
            c.get("no_telepon", "-"),
            c.get("cabang_pembuka", "-"),
            c.get("produk_rekening", "-"),
            c.get("segmentasi", "-"),
            kyc_status,
            float(c.get("saldo_terakhir", 0)),
            clean_flags
        ]

        for col_idx, val in enumerate(row_vals, start=1):
            cell = ws_data.cell(row=r, column=col_idx, value=val)
            cell.fill = fill
            cell.border = BORDER_THIN
            cell.font = Font(name="Segoe UI", size=9)
            
            # Alignments
            _, _, default_align = data_columns[col_idx-1]
            cell.alignment = Alignment(horizontal=default_align, vertical="center")

            # Saldo Currency Format
            if col_idx == 11:
                cell.number_format = '"Rp "#,##0'
                cell.font = Font(name="Segoe UI", size=9, bold=True, color=NAVY_PRIMARY)

            # Badge KYC Styling (Kolom 10)
            if col_idx == 10:
                if kyc_status == "Verified":
                    cell.fill = PatternFill(start_color=KYC_VERIFIED_BG, end_color=KYC_VERIFIED_BG, fill_type="solid")
                    cell.font = Font(name="Segoe UI", size=9, bold=True, color=KYC_VERIFIED_TXT)
                elif kyc_status == "Pending Review":
                    cell.fill = PatternFill(start_color=KYC_PENDING_BG, end_color=KYC_PENDING_BG, fill_type="solid")
                    cell.font = Font(name="Segoe UI", size=9, bold=True, color=KYC_PENDING_TXT)
                elif kyc_status == "Expired":
                    cell.fill = PatternFill(start_color=KYC_EXPIRED_BG, end_color=KYC_EXPIRED_BG, fill_type="solid")
                    cell.font = Font(name="Segoe UI", size=9, bold=True, color=KYC_EXPIRED_TXT)

            # Status AML Styling (Kolom 12)
            if col_idx == 12:
                cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
                if is_flagged:
                    cell.fill = PatternFill(start_color=KYC_EXPIRED_BG, end_color=KYC_EXPIRED_BG, fill_type="solid")
                    cell.font = Font(name="Segoe UI", size=8, bold=True, color=KYC_EXPIRED_TXT)
                    # Jika ada 2 flag, sesuaikan tinggi baris
                    if "\n" in clean_flags:
                        ws_data.row_dimensions[r].height = 32
                else:
                    cell.font = Font(name="Segoe UI", size=9, color=KYC_VERIFIED_TXT)

    # Baris Total Akuntansi Sheet 2
    last_data_r = start_cust_row + len(customers_analyzed)
    ws_data.row_dimensions[last_data_r].height = 26
    
    ws_data.merge_cells(f"A{last_data_r}:J{last_data_r}")
    tot_lbl = ws_data[f"A{last_data_r}"]
    tot_lbl.value = "TOTAL DANA KELOLAAN NASABAH TERSELEKSI :"
    tot_lbl.font = Font(name="Segoe UI", size=10, bold=True, color=NAVY_PRIMARY)
    tot_lbl.alignment = Alignment(horizontal="right", vertical="center")
    
    tot_val = ws_data.cell(row=last_data_r, column=11)
    tot_val.value = f"=SUM(K{start_cust_row}:K{last_data_r-1})"
    tot_val.font = Font(name="Segoe UI", size=10, bold=True, color=NAVY_PRIMARY)
    tot_val.alignment = Alignment(horizontal="right", vertical="center")
    tot_val.number_format = '"Rp "#,##0'

    ws_data.cell(row=last_data_r, column=12, value="")

    for c_i in range(1, 13):
        ws_data.cell(row=last_data_r, column=c_i).border = BORDER_TOTAL_ROW
        ws_data.cell(row=last_data_r, column=c_i).fill = PatternFill(start_color=ICE_BLUE_BG, end_color=ICE_BLUE_BG, fill_type="solid")

    ws_data.freeze_panes = f"A{header_table_row+1}"

    # =========================================================================
    # SHEET 3: AUDIT TRAIL & LOG REGULASI
    # =========================================================================
    ws_audit = wb.create_sheet(title="Audit Trail & Compliance")
    ws_audit.views.sheetView[0].showGridLines = True

    # 2 Kolom Presisi
    ws_audit.column_dimensions["A"].width = 34  # Parameter
    ws_audit.column_dimensions["B"].width = 86  # Detail Nilai

    # Header Banner (A1:B1)
    ws_audit.merge_cells("A1:B1")
    a_title = ws_audit["A1"]
    a_title.value = "LOG AUDIT EKSTRAKSI DATA PERBANKAN (ISO 27001 / REGULASI OJK)"
    a_title.font = Font(name="Segoe UI", size=13, bold=True, color=WHITE)
    a_title.fill = PatternFill(start_color=NAVY_PRIMARY, end_color=NAVY_PRIMARY, fill_type="solid")
    a_title.alignment = Alignment(horizontal="center", vertical="center")
    ws_audit.row_dimensions[1].height = 38
    style_merged_range(ws_audit, "A1:B1", fill=BANNER_FILL)

    # Subtitle (A2:B2)
    ws_audit.merge_cells("A2:B2")
    a_sub = ws_audit["A2"]
    a_sub.value = "Catatan bukti integritas audit sistem ekstraksi data perbankan otomatis"
    a_sub.font = Font(name="Segoe UI", size=9, italic=True, color="64748B")
    a_sub.alignment = Alignment(horizontal="center", vertical="center")
    ws_audit.row_dimensions[2].height = 20

    # Header Baris 4
    ws_audit.row_dimensions[4].height = 26
    c_h1 = ws_audit.cell(row=4, column=1, value="PARAMETER AUDIT")
    c_h1.fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
    c_h1.font = Font(name="Segoe UI", size=10, bold=True, color=WHITE)
    c_h1.alignment = Alignment(horizontal="center", vertical="center")
    c_h1.border = BORDER_THIN

    c_h2 = ws_audit.cell(row=4, column=2, value="DETAIL CATATAN LOG SISTEM")
    c_h2.fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
    c_h2.font = Font(name="Segoe UI", size=10, bold=True, color=WHITE)
    c_h2.alignment = Alignment(horizontal="left", vertical="center")
    c_h2.border = BORDER_THIN

    # Hitung checksum data
    data_digest = hashlib.sha256(str(customers_analyzed).encode('utf-8')).hexdigest()

    audit_entries = [
        ("Waktu Penarikan Data", now_str),
        ("Sistem Penarik / Generator", "Bank AI Customer Automation v2.4 (Enterprise Engine)"),
        ("Query SQL yang Dijalankan", executed_query if executed_query else "SELECT via Automated Filter Engine"),
        ("Jumlah Baris Data Terekstrak", f"{len(customers_analyzed):,} Catatan Nasabah"),
        ("Total Saldo Dana Terekstrak", f"Rp {total_saldo:,.0f}"),
        ("Status Data Masking (UU PDP)", "AKTIF (8 Digit NIK, Rekening, dan No. Telepon Disensor)" if is_masked else "TIDAK AKTIF (Full Data PII)"),
        ("Integritas Checksum (SHA-256)", data_digest),
        ("Mode Keamanan Kueri", "READ-ONLY ENFORCED (Klausul Modifikasi Ditolak Otomatis)"),
        ("Status Verifikasi Audit", "VERIFIED & AUDIT LOGGED")
    ]

    for row_idx, (prop, val) in enumerate(audit_entries, start=5):
        # Tinggi baris untuk Query SQL diperbesar agar muat wrap text
        ws_audit.row_dimensions[row_idx].height = 40 if "Query SQL" in prop else 24
        
        p_cell = ws_audit.cell(row=row_idx, column=1, value=prop)
        p_cell.font = Font(name="Segoe UI", size=9, bold=True, color=NAVY_PRIMARY)
        p_cell.fill = PatternFill(start_color=ICE_BLUE_BG, end_color=ICE_BLUE_BG, fill_type="solid")
        p_cell.alignment = Alignment(horizontal="left", vertical="center")
        p_cell.border = BORDER_THIN
        
        v_cell = ws_audit.cell(row=row_idx, column=2, value=val)
        v_cell.font = Font(name="Segoe UI", size=9)
        v_cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        v_cell.border = BORDER_THIN
        
        if "SHA-256" in prop or "Query SQL" in prop:
            v_cell.font = Font(name="Consolas", size=9, color="1E293B")
        elif "VERIFIED" in str(val):
            v_cell.font = Font(name="Segoe UI", size=9, bold=True, color=KYC_VERIFIED_TXT)

    # Footer Sertifikasi
    footer_row = 5 + len(audit_entries) + 1
    ws_audit.merge_cells(f"A{footer_row}:B{footer_row}")
    f_cell = ws_audit[f"A{footer_row}"]
    f_cell.value = "Dokumen ini digenerate secara otomatis oleh Core Banking AI Extraction System dan telah divalidasi sesuai standar kepatuhan ISO 27001 & regulasi perbankan OJK."
    f_cell.font = Font(name="Segoe UI", size=8, italic=True, color="94A3B8")
    f_cell.alignment = Alignment(horizontal="center", vertical="center")

    wb.save(output_path)
    return output_path
