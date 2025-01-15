@echo off
echo ======================================================
echo Automating Odoo Installation and Setup on Windows
echo ======================================================

:: Step 1: Set Variables

:: set "ODOO_DIR=C:\odoo-custom"
set "ODOO_DIR=%~1

set "VENV_DIR=%ODOO_DIR%\odoo-venv"

:: set "ZIP_FILE=C:\path\to\odoo-custom.zip"  :: Replace with the full path to your Odoo ZIP file
set "ZIP_FILE=%~2

:: set "PYTHON_EXE=C:\path\to\python.exe"     :: Replace with the full path to your Python executable
set "PYTHON_EXE=python"

:: set "PSQL_EXE=C:\Program Files\PostgreSQL\15\bin\psql.exe" :: Replace with the full path to your PostgreSQL `psql.exe`
set "PSQL_EXE=psql"

set "POSTGRES_USER=odoo"
set "POSTGRES_PASSWORD=odoo"
set "ADDONS_PATH=%ODOO_DIR%\addons"
set "LOG_FILE=%ODOO_DIR%\odoo.log"

:: Step 2: Unzip Custom Odoo Code
echo Unzipping custom Odoo code...
if not exist "%ZIP_FILE%" (
    echo ERROR: ZIP file not found at "%ZIP_FILE%".
    exit /b 1
)

mkdir "%ODOO_DIR%"
tar -xvf "%ZIP_FILE%" -C "%ODOO_DIR%"
if %errorlevel% neq 0 (
    echo ERROR: Failed to unzip Odoo code.
    exit /b 1
)

:: Step 3: Set Up Python Virtual Environment
echo Setting up Python virtual environment...
cd "%ODOO_DIR%"
"%PYTHON_EXE%" -m venv "%VENV_DIR%"
if %errorlevel% neq 0 (
    echo ERROR: Failed to create a virtual environment. Ensure Python is installed correctly.
    exit /b 1
)
call "%VENV_DIR%\Scripts\activate"
"%PYTHON_EXE%" -m pip install --upgrade pip

:: Install wheel and setuptools
pip install --upgrade pip wheel setuptools

:: Step 4: Install Odoo Dependencies
echo Installing Python dependencies...
pip install -r "%ODOO_DIR%\odoo-demo\requirements.txt"
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies.
    exit /b 1
)

:: Step 5: Configure PostgreSQL
echo Configuring PostgreSQL database...
"%PSQL_EXE%" -U postgres -c "CREATE USER %POSTGRES_USER% WITH PASSWORD '%POSTGRES_PASSWORD%';"
"%PSQL_EXE%" -U postgres -c "ALTER USER %POSTGRES_USER% CREATEDB;"
if %errorlevel% neq 0 (
    echo ERROR: Failed to configure PostgreSQL. Ensure PostgreSQL is running and psql.exe is correctly set.
    exit /b 1
)

:: Step 6: Create Odoo Configuration File
echo Creating Odoo configuration file with absolute paths...
(
echo [options]
echo addons_path = %ADDONS_PATH%
echo db_host = localhost
echo db_port = 5432
echo db_user = %POSTGRES_USER%
echo db_password = %POSTGRES_PASSWORD%
echo logfile = %LOG_FILE%
) > "%ODOO_DIR%\odoo.conf"

:: Step 7: Start Odoo Server
echo Starting Odoo server...
call "%VENV_DIR%\Scripts\activate"
"%PYTHON_EXE%" "%ODOO_DIR%\odoo-demo\odoo-bin" --config="%ODOO_DIR%\odoo.conf"
if %errorlevel% neq 0 (
    echo ERROR: Failed to start Odoo server. Check logs for details.
    exit /b 1
)

echo ======================================================
echo Odoo installation and setup completed successfully!
echo Access your Odoo instance at http://localhost:8069
echo ======================================================

pause
