@echo off
cd /d d:\dashboard
echo Testing Python...
"C:\Users\raison\AppData\Local\Programs\Python\Python311\python.exe" --version
echo.
echo Testing pip...
"C:\Users\raison\AppData\Local\Programs\Python\Python311\python.exe" -m pip --version
echo.
echo Installing streamlit...
"C:\Users\raison\AppData\Local\Programs\Python\Python311\python.exe" -m pip install streamlit plotly pandas openpyxl xlrd numpy -v
pause
