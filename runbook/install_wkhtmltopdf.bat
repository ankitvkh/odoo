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
    echo Usage: install_wkhtmltopdf.bat [version] [install_path]
    echo Example: install_wkhtmltopdf.bat 0.12.6 "C:\Program Files\wkhtmltopdf"
    echo Note: Version should be in format like 0.12.6
    pause
    exit /b 1
)

:: Set variables
set WKHTML_VERSION=%~1
set INSTALL_PATH=%~2
if "%INSTALL_PATH%"=="" set INSTALL_PATH="C:\Program Files\wkhtmltopdf"

:: Remove quotes from install path if present
set INSTALL_PATH=%INSTALL_PATH:"=%

:: Set file names and paths - Corrected URL format
set DOWNLOAD_URL=https://github.com/wkhtmltopdf/packaging/releases/download/%WKHTML_VERSION%/wkhtmltox-%WKHTML_VERSION%.msvc2015-win64.exe
echo Using download URL: %DOWNLOAD_URL%

:: Create temp directory with error handling
set TEMP_DIR=%TEMP%\wkhtmltopdf_install
echo Creating temp directory: %TEMP_DIR%
if exist "%TEMP_DIR%" (
    echo Cleaning existing temp directory...
    rd /s /q "%TEMP_DIR%"
    if !ERRORLEVEL! neq 0 (
        echo Failed to clean temp directory
        pause
        exit /b 1
    )
)
mkdir "%TEMP_DIR%"
if !ERRORLEVEL! neq 0 (
    echo Failed to create temp directory
    pause
    exit /b 1
)

set INSTALLER_PATH=%TEMP_DIR%\wkhtmltopdf.exe
echo Target file: %INSTALLER_PATH%

:: Download using PowerShell with progress and error handling
echo Downloading Wkhtmltopdf %WKHTML_VERSION%...
powershell -Command "& { $ErrorActionPreference = 'Stop'; try { $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%INSTALLER_PATH%' -UseBasicParsing; Write-Host 'Download completed successfully.' } catch { Write-Host 'Error downloading file: ' $_.Exception.Message; exit 1 } }"
if %ERRORLEVEL% neq 0 (
    echo Failed to download Wkhtmltopdf
    echo Please check:
    echo 1. Download URL: %DOWNLOAD_URL%
    echo 2. Internet connectivity
    echo 3. Temp directory: %TEMP_DIR%
    echo 4. Available disk space
    echo.
    echo Attempting to display HTTP response...
    powershell -Command "& { try { $response = Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -Method Head -UseBasicParsing; Write-Host 'HTTP Status:' $response.StatusCode } catch { Write-Host 'HTTP Error:' $_.Exception.Message } }"
    pause
    exit /b 1
)

:: Verify the downloaded file and its size
if not exist "%INSTALLER_PATH%" (
    echo ERROR: Installer not found at %INSTALLER_PATH%
    pause
    exit /b 1
)

for %%I in ("%INSTALLER_PATH%") do (
    if %%~zI LSS 1000 (
        echo ERROR: Downloaded file is too small, likely failed to download properly
        echo File contents:
        type "%INSTALLER_PATH%"
        del "%INSTALLER_PATH%"
        pause
        exit /b 1
    )
    echo Downloaded file size: %%~zI bytes
)

echo File downloaded successfully to: %INSTALLER_PATH%

:: Create installation directory if it doesn't exist
mkdir "%INSTALL_PATH%" 2>nul

:: Install Wkhtmltopdf silently
echo Installing Wkhtmltopdf %WKHTML_VERSION% to "%INSTALL_PATH%"...

:: Run installer with elevated privileges
echo Starting installation...
start /wait "" "%INSTALLER_PATH%" /S /D="%INSTALL_PATH%"

:: Check installation result
if %ERRORLEVEL% neq 0 (
    echo Installation failed with error code: %ERRORLEVEL%
    rd /s /q "%TEMP_DIR%" 2>nul
    pause
    exit /b 1
)

:: Clean up
rd /s /q "%TEMP_DIR%" 2>nul

:: Verify installation
echo Verifying installation...
if exist "%INSTALL_PATH%\bin\wkhtmltopdf.exe" (
    echo Wkhtmltopdf %WKHTML_VERSION% installed successfully!
    echo Installation Details:
    echo Installation Path: %INSTALL_PATH%
    
    :: Display installed version
    echo.
    echo Installed version:
    "%INSTALL_PATH%\bin\wkhtmltopdf.exe" --version
) else (
    echo WARNING: Could not verify Wkhtmltopdf installation
    echo Expected path: "%INSTALL_PATH%\bin\wkhtmltopdf.exe" was not found
)

:: Add Wkhtmltopdf bin directory to PATH
powershell -Command "[Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';%INSTALL_PATH%\bin', 'Machine')"

echo Installation completed!
pause
endlocal