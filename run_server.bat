@echo off
title Core Banking REST API Server
echo ============================================================
echo Menjalankan Core Banking REST API Server (Flask)...
echo ============================================================
echo Server Endpoint: http://localhost:5000
echo Cek Status     : http://localhost:5000/api/health
echo Tarik Nasabah  : http://localhost:5000/api/v1/customers
echo ============================================================
echo.
python api_server.py
pause
