@echo off
title Dashboard Streamlit
cd /d d:\dashboard
echo ============================================
echo Menjalankan Dashboard Streamlit...
echo ============================================
echo.
echo Aplikasi akan membuka di: http://localhost:8501
echo Tekan Ctrl+C untuk menghentikan aplikasi
echo.
"C:\Users\raison\AppData\Local\Programs\Python\Python311\python.exe" -m streamlit run beranda.py --logger.level=debug

