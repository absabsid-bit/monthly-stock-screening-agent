@echo off
title Stock Agent V5.4

cd /d "%~dp0"

echo ============================================================
echo              MASTER STOCK AGENT V5.4
echo ============================================================
echo.
echo Menjalankan screening...
echo.

python master_stock_agent_v5.py

echo.
echo ============================================================
echo Proses selesai.
echo ============================================================
echo.
pause