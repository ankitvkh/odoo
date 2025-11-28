PostgreSQL Silent Installation Script

@echo off
setlocal enabledelayedexpansion

:: Check for admin rights and self-elevate if needed
NET SESSION >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process -Verb RunAs -FilePath '%0' -ArgumentList '%*'"
    exit /b
)

:: Check if version parameter is provided
if "%~1"=="" (
    echo Usage: install_postgresql.bat [version] [password] [install_path]
    echo Example: install_postgresql.bat 15.4 mypassword "C:\Program Files\PostgreSQL"
    pause
    exit /b 1
)

:: Set variables
set PG_VERSION=%~1
set PG_PASSWORD=%~2
if "%PG_PASSWORD%"=="" set PG_PASSWORD=postgres
set INSTALL_PATH=%~3
if "%INSTALL_PATH%"=="" set INSTALL_PATH="C:\Program Files\PostgreSQL"

:: Remove quotes from install path if present
set INSTALL_PATH=%INSTALL_PATH:"=%

:: Set file names and paths
set INSTALLER_NAME=postgresql-%PG_VERSION%-1-windows-x64.exe
set DOWNLOAD_URL=https://get.enterprisedb.com/postgresql/%INSTALLER_NAME%
set TEMP_PATH=%TEMP%\%INSTALLER_NAME%

echo Download URL: %DOWNLOAD_URL%

:: Create installation directory if it doesn't exist
mkdir "%INSTALL_PATH%" 2>nul

:: Download PostgreSQL installer
echo Downloading PostgreSQL %PG_VERSION%...
echo Downloading to: %TEMP_PATH%

powershell -Command "& { $ProgressPreference = 'Continue'; try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Write-Host 'Starting download...'; Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%TEMP_PATH%' -Verbose; if (Test-Path '%TEMP_PATH%') { Write-Host 'Download completed successfully' } else { Write-Host 'Download failed - file not found' ; exit 1 } } catch { Write-Host $_.Exception.Message; exit 1 } }"

if %ERRORLEVEL% neq 0 (
    echo Failed to download PostgreSQL installer
    echo Please verify that version %PG_VERSION% exists at:
    echo %DOWNLOAD_URL%
    pause
    exit /b 1
)

:: Verify the downloaded file exists
if not exist "%TEMP_PATH%" (
    echo ERROR: Downloaded file not found at %TEMP_PATH%
    pause
    exit /b 1
)

:: Install PostgreSQL silently
echo Installing PostgreSQL %PG_VERSION% to "%INSTALL_PATH%"...

:: Create response file for silent installation
set RESPONSE_FILE=%TEMP%\response.conf
(
    echo InstallationDirectory=%INSTALL_PATH%\%PG_VERSION%
    echo DataDirectory=%INSTALL_PATH%\%PG_VERSION%\data
    echo SuperPassword=%PG_PASSWORD%
    echo Port=5432
    echo Locale=English
) > "%RESPONSE_FILE%"

:: Run installer with elevated privileges
echo Starting installation...
start /wait "" "%TEMP_PATH%" ^
    --unattendedmodeui minimal ^
    --mode unattended ^
    --disable-components stackbuilder ^
    --superaccount postgres ^
    --superpassword "%PG_PASSWORD%" ^
    --serverport 5432 ^
    --prefix "%INSTALL_PATH%\%PG_VERSION%" ^
    --datadir "%INSTALL_PATH%\%PG_VERSION%\data" ^
    --servicename postgresql-%PG_VERSION% ^
    --serviceaccount postgres ^
    --install_runtimes 0

:: Check installation result
if %ERRORLEVEL% neq 0 (
    echo Installation failed with error code: %ERRORLEVEL%
    del "%TEMP_PATH%" 2>nul
    del "%RESPONSE_FILE%" 2>nul
    pause
    exit /b 1
)

:: Clean up
del "%TEMP_PATH%" 2>nul
del "%RESPONSE_FILE%" 2>nul

:: Verify installation
echo Verifying installation...
if exist "%INSTALL_PATH%\%PG_VERSION%\bin\psql.exe" (
    echo PostgreSQL %PG_VERSION% installed successfully!
    echo Installation Details:
    echo Server: localhost
    echo Port: 5432
    echo Superuser: postgres
    echo Password: %PG_PASSWORD%
    echo Installation Path: %INSTALL_PATH%\%PG_VERSION%
) else (
    echo WARNING: Could not verify PostgreSQL installation
)

:: Add PostgreSQL bin directory to PATH using PowerShell to avoid registry access issues
powershell -Command "[Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';%INSTALL_PATH%\%PG_VERSION%\bin', 'Machine')"

echo Installation completed!
pause
endlocal