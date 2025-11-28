@echo off
echo ======================================================
echo Starting Odoo Server on Windows
echo ======================================================

:: Set Variables
set "ODOO_DIR=C:\odoo-custom"
set "VENV_DIR=%ODOO_DIR%\odoo-venv"
set "CONFIG_FILE=%ODOO_DIR%\odoo.conf"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"

:: Activate Virtual Environment and Start Odoo
echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate"
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment.
    exit /b 1
)

echo Starting Odoo server...
"%PYTHON_EXE%" "%ODOO_DIR%\odoo-bin" --config="%CONFIG_FILE%"
if %errorlevel% neq 0 (
    echo ERROR: Failed to start Odoo server. Check logs for details.
    exit /b 1
)

echo ======================================================
echo Odoo server started successfully!
echo Access your Odoo instance at http://localhost:8069
echo ======================================================

pause
