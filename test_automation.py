"""
Automated Test Suite untuk Bank AI Automation System.
Menguji:
1. Text-to-SQL Parsing Engine (Akurasi sintaks & parameter)
2. SQL Safety Guardrails (Mencegah SQL Injection & manipulasi data)
3. Data Masking Compliance (Sesuai UU Perlindungan Data Pribadi)
4. Multi-Sheet Excel Exporter (Validasi struktur lembar kerja)
"""

import unittest
import os
import sqlite3
import openpyxl
from bank_automation.ai_engine import natural_language_to_sql, parse_nominal
from bank_automation.validator import validate_nik, mask_nik, mask_account_number, mask_phone, apply_masking_to_record
from bank_automation.database import execute_safe_query, init_database
from bank_automation.excel_exporter import export_customers_to_excel
from bank_automation.analytics import analyze_customer_risks

class TestBankAutomation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_database(populate_dummy_count=50)

    def test_nominal_parser(self):
        """Memastikan konversi nominal bahasa Indonesia akurat."""
        self.assertEqual(parse_nominal("500 juta"), 500_000_000.0)
        self.assertEqual(parse_nominal("1.5 milyar"), 1_500_000_000.0)
        self.assertEqual(parse_nominal("50jt"), 50_000_000.0)

    def test_text_to_sql_generation(self):
        """Memastikan prompt menghasilkan kueri SQL SELECT yang valid."""
        sql1 = natural_language_to_sql("Tampilkan nasabah prioritas di KC Jakarta Sudirman")
        self.assertTrue(sql1.startswith("SELECT * FROM nasabah"))
        self.assertIn("segmentasi LIKE '%Prioritas%'", sql1)
        self.assertIn("cabang_pembuka LIKE '%KC Jakarta Sudirman%'", sql1)

        sql2 = natural_language_to_sql("Cari nasabah dengan status KYC pending")
        self.assertIn("status_kyc = 'Pending Review'", sql2)

        # Uji pencarian nama nasabah
        sql3 = natural_language_to_sql("Cari nasabah bernama Rendy Marbun")
        self.assertIn("nama_nasabah LIKE '%Rendy Marbun%'", sql3)

        # Uji pencarian CIF dan NIK
        sql4 = natural_language_to_sql("Cari CIF10130601")
        self.assertIn("cif = 'CIF10130601'", sql4)

    def test_sql_safety_guardrails(self):
        """Memastikan hanya SELECT yang diizinkan dan query destruktif ditolak."""
        # Query SELECT aman harus berjalan
        res = execute_safe_query("SELECT id, nama_nasabah FROM nasabah LIMIT 5")
        self.assertTrue(len(res) > 0)

        # Query modifikasi harus raise ValueError
        with self.assertRaises(ValueError):
            execute_safe_query("DROP TABLE nasabah")
        with self.assertRaises(ValueError):
            execute_safe_query("DELETE FROM nasabah WHERE id = 1")
        with self.assertRaises(ValueError):
            execute_safe_query("UPDATE nasabah SET saldo_terakhir = 0")

    def test_data_masking_pdp(self):
        """Memastikan fungsi sensor data pribadi bekerja sesuai standar."""
        nik_raw = "3201123456789012"
        nik_masked = mask_nik(nik_raw)
        self.assertEqual(nik_masked, "3201********9012")
        self.assertEqual(len(nik_masked), 16)

        acc_raw = "123-45-678901"
        acc_masked = mask_account_number(acc_raw)
        self.assertIn("****", acc_masked)

        phone_raw = "081234567890"
        phone_masked = mask_phone(phone_raw)
        self.assertEqual(phone_masked, "0812****890")

    def test_multisheet_excel_generation(self):
        """Memastikan berkas Excel yang dihasilkan memiliki 3 sheet standar audit."""
        sample_data = execute_safe_query("SELECT * FROM nasabah LIMIT 10")
        output_file = os.path.join(os.path.dirname(__file__), "output", "test_report.xlsx")
        
        export_customers_to_excel(sample_data, output_file, report_title="TEST AUDIT REPORT")
        self.assertTrue(os.path.exists(output_file))

        wb = openpyxl.load_workbook(output_file)
        expected_sheets = ["Ringkasan Eksekutif", "Data Nasabah", "Audit Trail & Compliance"]
        self.assertEqual(wb.sheetnames, expected_sheets)
        wb.close()

if __name__ == "__main__":
    unittest.main()

