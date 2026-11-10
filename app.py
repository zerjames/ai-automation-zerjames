"""
Web Dashboard: Bank Customer Data Automation & Reporting System
Desain Antarmuka: Enterprise Fintech / Corporate Banking (Strict Zero-Emoji, Pure SVG & CSS)
"""

import streamlit as st
import pandas as pd
import os
import importlib
import bank_automation.excel_exporter
import bank_automation.analytics
import bank_automation.validator
import bank_automation.ai_engine
import bank_automation.database

# Force reload module agar perubahan fungsi langsung aktif di memory Streamlit
importlib.reload(bank_automation.excel_exporter)
importlib.reload(bank_automation.analytics)
importlib.reload(bank_automation.validator)
importlib.reload(bank_automation.ai_engine)
importlib.reload(bank_automation.database)

from bank_automation.database import init_database, execute_safe_query, get_connection
from bank_automation.ai_engine import natural_language_to_sql
from bank_automation.validator import apply_masking_to_record
from bank_automation.excel_exporter import export_customers_to_excel
from bank_automation.analytics import analyze_customer_risks

# -----------------------------------------------------------------------------
# SVG ASSETS (Clean, crisp, enterprise icons - no emojis)
# -----------------------------------------------------------------------------
SVG_VAULT = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0EA5E9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="12" cy="12" r="4"/><path d="M12 8v1"/><path d="M12 15v1"/><path d="M8 12h1"/><path d="M15 12h1"/><path d="m15 9-1 1"/><path d="m10 14-1 1"/><path d="m9 9 1 1"/><path d="m14 14 1 1"/></svg>"""

SVG_DATABASE = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5"/><path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3"/></svg>"""

SVG_SHIELD_CHECK = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>"""

SVG_SHIELD_WARN = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#D97706" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>"""

SVG_CODE = """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>"""

SVG_DOWNLOAD = """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>"""

SVG_SEARCH = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#64748B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>"""

SVG_FILTER = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#64748B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>"""

SVG_EXCEL = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#16A34A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="16" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>"""

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Core Banking Data Extraction Portal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inisialisasi Database
init_database(populate_dummy_count=200)

# -----------------------------------------------------------------------------
# CUSTOM CSS: HIGH-END CORPORATE FINTECH THEME
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Global Fonts & Colors */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #0F172A;
    }
    
    /* Header Card */
    .bank-header-card {
        background: linear-gradient(135deg, #0B192C 0%, #1E3E62 100%);
        border-radius: 8px;
        padding: 24px 28px;
        margin-bottom: 24px;
        border: 1px solid #1E293B;
        color: #FFFFFF;
        box-shadow: 0 4px 12px rgba(11, 25, 44, 0.12);
    }
    .bank-header-title {
        font-size: 22px;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
        color: #FFFFFF;
    }
    .bank-header-badge {
        display: inline-block;
        background: rgba(14, 165, 233, 0.15);
        color: #38BDF8;
        border: 1px solid rgba(14, 165, 233, 0.3);
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        padding: 2px 8px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .bank-header-desc {
        color: #94A3B8;
        font-size: 13px;
        margin-top: 6px;
        line-height: 1.5;
    }
    
    /* Metrics Card */
    .metric-panel {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .metric-panel-title {
        font-size: 12px;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 4px;
    }
    .metric-panel-value {
        font-size: 24px;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.03em;
    }
    .metric-panel-sub {
        font-size: 12px;
        color: #10B981;
        margin-top: 2px;
        font-weight: 500;
    }

    /* SQL Code Terminal */
    .sql-terminal {
        background-color: #090D16;
        border: 1px solid #1E293B;
        border-radius: 6px;
        padding: 14px 18px;
        margin: 12px 0 18px 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: #38BDF8;
        overflow-x: auto;
    }
    .sql-terminal-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        color: #64748B;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Quick Prompt Pills */
    .quick-title {
        font-size: 12px;
        font-weight: 600;
        color: #475569;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    /* Status Pills */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 500;
    }
    .status-badge-green {
        background: #ECFDF5;
        border: 1px solid #A7F3D0;
        color: #065F46;
    }
    .status-badge-amber {
        background: #FFFBEB;
        border: 1px solid #FDE68A;
        color: #92400E;
    }

    /* Streamlit overrides */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        font-size: 13px;
        font-weight: 600;
        color: #64748B;
        border-radius: 6px 6px 0 0;
        padding: 0 18px;
    }
    .stTabs [aria-selected="true"] {
        color: #0284C7 !important;
        border-bottom: 2px solid #0284C7 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 22px !important;
        font-weight: 700 !important;
        color: #0F172A !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 12px !important;
        font-weight: 600 !important;
        color: #64748B !important;
        text-transform: uppercase !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TOP HEADER CARD
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class="bank-header-card">
    <div class="bank-header-title">
        {SVG_VAULT}
        <span>CORE BANKING AUTOMATION PLATFORM</span>
        <span class="bank-header-badge">ENTERPRISE v2.4</span>
    </div>
    <div class="bank-header-desc">
        Sistem ekstraksi data nasabah terintegrasi SQL Database ke format Microsoft Excel (.xlsx) dengan modul AI Text-to-SQL & Kepatuhan UU Perlindungan Data Pribadi.
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:16px;">
        {SVG_VAULT}
        <span style="font-weight:700; font-size:15px; color:#0F172A; letter-spacing:-0.01em;">PORTAL KONTROL</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="quick-title">Kepatuhan Regulasi (OJK / PDP)</div>', unsafe_allow_html=True)
    mask_toggle = st.toggle(
        "Sensor Data Pribadi (Data Masking)",
        value=True,
        help="Menyensor NIK, nomor telepon, dan nomor rekening nasabah pada pratinjau dan file unduhan."
    )
    
    if mask_toggle:
        st.markdown(f"""
        <div class="status-badge status-badge-green">
            {SVG_SHIELD_CHECK} Masking Aktif (Aman Regulasi)
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="status-badge status-badge-amber">
            {SVG_SHIELD_WARN} Full Data Unmasked (Akses Terbatas)
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border:0; border-top:1px solid #E2E8F0; margin: 20px 0;'>", unsafe_allow_html=True)
    
    # DB Status
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
        {SVG_DATABASE}
        <span style="font-size:13px; font-weight:600; color:#334155;">Koneksi Core Database</span>
    </div>
    """, unsafe_allow_html=True)
    
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*), SUM(saldo_terakhir) FROM nasabah")
    total_db, total_dpk = c.fetchone()
    conn.close()

    st.metric("Total Portofolio Nasabah", f"{total_db:,} Akun")
    st.metric("Total Dana Kelolaan (DPK)", f"Rp {total_dpk:,.0f}")
    
    st.markdown("<hr style='border:0; border-top:1px solid #E2E8F0; margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:11px; color:#94A3B8; line-height:1.6;">
        Standard Arsitektur: Python 3.11, OpenPyXL, SQLite / MySQL Engine, REST API Service.
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# HELPER GENERATE EXCEL BYTES
# -----------------------------------------------------------------------------
def get_excel_file_bytes(data, title, masked, query_str):
    temp_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = os.path.join(temp_dir, "report_export.xlsx")
    try:
        export_customers_to_excel(
            customers=data, 
            output_path=temp_file, 
            report_title=title, 
            is_masked=masked, 
            executed_query=query_str
        )
    except TypeError:
        # Backward-compatible fallback
        export_customers_to_excel(data, temp_file, title, masked)
        
    with open(temp_file, "rb") as f:
        content = f.read()
    return content

# -----------------------------------------------------------------------------
# TABS INTERFACE
# -----------------------------------------------------------------------------
tab_ai, tab_form = st.tabs([
    "Natural Language Query (AI Text-to-SQL)",
    "Parameter Query (Filter Terstruktur)"
])

# =============================================================================
# TAB 1: NATURAL LANGUAGE QUERY (AI TEXT-TO-SQL)
# =============================================================================
with tab_ai:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
        {SVG_SEARCH}
        <span style="font-size:14px; font-weight:600; color:#334155;">Pencarian Data Menggunakan Bahasa Alami</span>
    </div>
    <div style="font-size:13px; color:#64748B; margin-bottom:14px;">
        Ketik kriteria data yang ingin ditarik. Mesin AI akan menyusun sintaks SQL yang sesuai dan mengekstrak data dari database bank.
    </div>
    """, unsafe_allow_html=True)

    # Preset Buttons
    st.markdown('<div class="quick-title">Contoh Kueri Cepat:</div>', unsafe_allow_html=True)
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    
    selected_preset = None
    if col_p1.button("Cari Nama: Rendy Marbun", use_container_width=True):
        selected_preset = "Cari nasabah bernama Rendy Marbun"
    if col_p2.button("Prioritas Saldo > 1 Milyar", use_container_width=True):
        selected_preset = "Tampilkan nasabah prioritas dengan saldo di atas 1 milyar"
    if col_p3.button("KYC Pending di Surabaya", use_container_width=True):
        selected_preset = "Cari nasabah di Surabaya yang status KYC nya pending"
    if col_p4.button("Top 10 Saldo Terbesar", use_container_width=True):
        selected_preset = "Tampilkan 10 nasabah dengan saldo terbesar"

    default_query_text = selected_preset if selected_preset else "Cari nasabah bernama Rendy Marbun"
    user_prompt = st.text_input("Instruksi Penarikan Data:", value=default_query_text, placeholder="Contoh: Cari nasabah bernama Rendy, atau NIK 3201..., atau nasabah prioritas...")

    try:
        sql_generated = natural_language_to_sql(user_prompt)
        
        # Display SQL Terminal Box
        st.markdown(f"""
        <div class="sql-terminal">
            <div class="sql-terminal-label">{SVG_CODE} Generated SQL Query (Read-Only Mode)</div>
            <div>{sql_generated}</div>
        </div>
        """, unsafe_allow_html=True)
        
        raw_results = execute_safe_query(sql_generated)
        
        if raw_results:
            processed_data = [apply_masking_to_record(row) if mask_toggle else row for row in raw_results]
            analyzed_data = analyze_customer_risks(processed_data)
            
            # Metrics Row
            total_kriteria_saldo = sum(r['saldo_terakhir'] for r in raw_results)
            flagged_count = sum(1 for r in analyzed_data if r.get('is_flagged'))
            
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Jumlah Rekening Ditarik", f"{len(raw_results):,} Akun")
            with m2:
                st.metric("Total Dana Terkumpul", f"Rp {total_kriteria_saldo:,.0f}")
            with m3:
                st.metric("Nasabah Terdeteksi Anomali", f"{flagged_count} Rekening")
            with m4:
                st.metric("Status Data", "TERMASKING" if mask_toggle else "UNMASKED")

            # Data Table Preview
            df = pd.DataFrame(analyzed_data)
            display_cols = ["cif", "no_rekening", "nama_nasabah", "nik", "cabang_pembuka", "segmentasi", "saldo_terakhir", "status_kyc", "compliance_flags"]
            df_table = df[display_cols].copy()
            df_table["saldo_terakhir"] = df_table["saldo_terakhir"].apply(lambda x: f"Rp {x:,.0f}")
            df_table.rename(columns={
                "cif": "CIF",
                "no_rekening": "No. Rekening",
                "nama_nasabah": "Nama Nasabah",
                "nik": "NIK",
                "cabang_pembuka": "Cabang",
                "segmentasi": "Segmentasi",
                "saldo_terakhir": "Saldo Terakhir",
                "status_kyc": "Status KYC",
                "compliance_flags": "Analisis Risiko"
            }, inplace=True)
            
            st.dataframe(df_table, use_container_width=True, height=340)

            # Action Download Button
            excel_bytes = get_excel_file_bytes(
                processed_data, 
                "LAPORAN DATA NASABAH (AI EXTRACTION)", 
                mask_toggle,
                sql_generated
            )
            
            col_down, col_space = st.columns([1, 2])
            with col_down:
                st.download_button(
                    label="Download Laporan Excel Standar Audit (.xlsx)",
                    data=excel_bytes,
                    file_name="Laporan_Nasabah_Bank_Audit.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        else:
            st.info("Kueri berhasil dijalankan, namun tidak ada catatan nasabah yang cocok dengan kriteria tersebut.")
    except Exception as ex:
        st.error(f"Kegagalan eksekusi query: {str(ex)}")

# =============================================================================
# TAB 2: PARAMETER QUERY (FILTER TERSTRUKTUR)
# =============================================================================
with tab_form:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
        {SVG_FILTER}
        <span style="font-size:14px; font-weight:600; color:#334155;">Penyaringan Berdasarkan Parameter Baku</span>
    </div>
    <div style="font-size:13px; color:#64748B; margin-bottom:14px;">
        Gunakan parameter berikut untuk kebutuhan audit dan rekapitulasi rutin staf operasional backoffice.
    </div>
    """, unsafe_allow_html=True)
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        cabang_list = [
            "Semua Cabang",
            "KC Jakarta Sudirman",
            "KC Jakarta Thamrin",
            "KC Bandung Asia Afrika",
            "KC Surabaya Darmo",
            "KC Medan Balai Kota",
            "KC Semarang Pemuda",
            "KC Makassar Ratulangi",
            "KC Denpasar Gajah Mada"
        ]
        param_cabang = st.selectbox("Kantor Cabang Pengelola:", cabang_list)
        
    with col_c2:
        seg_list = ["Semua Segmentasi", "Reguler", "Gold", "Prioritas / High Net Worth"]
        param_seg = st.selectbox("Segmentasi Nasabah:", seg_list)
        
    with col_c3:
        kyc_list = ["Semua Status", "Verified", "Pending Review", "Expired"]
        param_kyc = st.selectbox("Status Verifikasi Dokumen (KYC):", kyc_list)
        
    param_saldo_min = st.number_input(
        "Batas Minimal Saldo Rekening (IDR):", 
        min_value=0, 
        value=0, 
        step=50_000_000, 
        format="%d"
    )

    # Build SQL
    sql_filter = "SELECT * FROM nasabah WHERE 1=1"
    if param_cabang != "Semua Cabang":
        sql_filter += f" AND cabang_pembuka = '{param_cabang}'"
    if param_seg != "Semua Segmentasi":
        sql_filter += f" AND segmentasi = '{param_seg}'"
    if param_kyc != "Semua Status":
        sql_filter += f" AND status_kyc = '{param_kyc}'"
    if param_saldo_min > 0:
        sql_filter += f" AND saldo_terakhir >= {param_saldo_min}"
        
    sql_filter += " ORDER BY saldo_terakhir DESC LIMIT 200"

    # Display Query
    st.markdown(f"""
    <div class="sql-terminal">
        <div class="sql-terminal-label">{SVG_CODE} Parameter Generated Query</div>
        <div>{sql_filter}</div>
    </div>
    """, unsafe_allow_html=True)

    results_filter = execute_safe_query(sql_filter)
    
    if results_filter:
        processed_filter = [apply_masking_to_record(r) if mask_toggle else r for r in results_filter]
        analyzed_filter = analyze_customer_risks(processed_filter)
        
        sum_saldo = sum(r['saldo_terakhir'] for r in results_filter)
        
        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("Total Data Ditemukan", f"{len(results_filter):,} Akun")
        with k2:
            st.metric("Akumulasi Saldo DPK", f"Rp {sum_saldo:,.0f}")
        with k3:
            st.metric("Cabang Terfilter", param_cabang)

        df_f = pd.DataFrame(analyzed_filter)
        cols_filter_view = ["cif", "no_rekening", "nama_nasabah", "nik", "cabang_pembuka", "segmentasi", "saldo_terakhir", "status_kyc", "compliance_flags"]
        df_f_table = df_f[cols_filter_view].copy()
        df_f_table["saldo_terakhir"] = df_f_table["saldo_terakhir"].apply(lambda x: f"Rp {x:,.0f}")
        df_f_table.rename(columns={
            "cif": "CIF",
            "no_rekening": "No. Rekening",
            "nama_nasabah": "Nama Nasabah",
            "nik": "NIK",
            "cabang_pembuka": "Cabang",
            "segmentasi": "Segmentasi",
            "saldo_terakhir": "Saldo Terakhir",
            "status_kyc": "Status KYC",
            "compliance_flags": "Analisis Risiko"
        }, inplace=True)
        
        st.dataframe(df_f_table, use_container_width=True, height=340)

        excel_bytes_filter = get_excel_file_bytes(
            processed_filter, 
            f"LAPORAN NASABAH - {param_cabang.upper()}", 
            mask_toggle,
            sql_filter
        )
        
        col_down_f, _ = st.columns([1, 2])
        with col_down_f:
            st.download_button(
                label="Download Laporan Terfilter (.xlsx)",
                data=excel_bytes_filter,
                file_name=f"Laporan_Nasabah_{param_cabang.replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="btn_down_filter",
                use_container_width=True
            )
    else:
        st.info("Tidak ada data nasabah yang memenuhi seluruh filter parameter yang dipilih.")
