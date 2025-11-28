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
    echo Usage: install_nodejs.bat [version] [install_path]
    echo Example: install_nodejs.bat 18.16.0 "C:\Program Files\nodejs"
    echo Note: Version should be in format like 18.16.0
    pause
    exit /b 1
)

:: Set variables
set NODE_VERSION=%~1
set INSTALL_PATH=%~2
if "%INSTALL_PATH%"=="" set INSTALL_PATH="C:\Program Files\nodejs"

:: Remove quotes from install path if present
set INSTALL_PATH=%INSTALL_PATH:"=%

:: Set file names and paths
set INSTALLER_NAME=node-v%NODE_VERSION%-x64.msi
set DOWNLOAD_URL=https://nodejs.org/dist/v%NODE_VERSION%/%INSTALLER_NAME%
set TEMP_PATH=%TEMP%\%INSTALLER_NAME%

echo Download URL: %DOWNLOAD_URL%

:: Create installation directory if it doesn't exist
mkdir "%INSTALL_PATH%" 2>nul

:: Download NodeJS installer
echo Downloading NodeJS %NODE_VERSION%...
echo Downloading to: %TEMP_PATH%

powershell -Command "& { $ProgressPreference = 'Continue'; try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Write-Host 'Starting download...'; Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%TEMP_PATH%' -Verbose; if (Test-Path '%TEMP_PATH%') { Write-Host 'Download completed successfully' } else { Write-Host 'Download failed - file not found' ; exit 1 } } catch { Write-Host $_.Exception.Message; exit 1 } }"

if %ERRORLEVEL% neq 0 (
    echo Failed to download NodeJS installer
    echo Please verify that version %NODE_VERSION% exists at:
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

:: Install NodeJS silently
echo Installing NodeJS %NODE_VERSION% to "%INSTALL_PATH%"...

:: Run installer with elevated privileges
echo Starting installation...
msiexec /i "%TEMP_PATH%" ^
    /quiet ^
    /norestart ^
    INSTALLDIR="%INSTALL_PATH%" ^
    ADDLOCAL=ALL ^
    /L*V "%TEMP%\nodejs_install_log.txt"

:: Check installation result
if %ERRORLEVEL% neq 0 (
    echo Installation failed with error code: %ERRORLEVEL%
    echo Check log file for details: %TEMP%\nodejs_install_log.txt
    del "%TEMP_PATH%" 2>nul
    pause
    exit /b 1
)

:: Clean up
del "%TEMP_PATH%" 2>nul

:: Verify installation
echo Verifying installation...
if exist "%INSTALL_PATH%\node.exe" (
    echo NodeJS %NODE_VERSION% installed successfully!
    echo Installation Details:
    echo Installation Path: %INSTALL_PATH%
    
    :: Display installed versions
    echo.
    echo Installed versions:
    call node --version
    call npm --version
) else (
    echo WARNING: Could not verify NodeJS installation
)

:: Add NodeJS directory to PATH using PowerShell to avoid registry access issues
powershell -Command "[Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';%INSTALL_PATH%', 'Machine')"

:: Install common global packages (uncomment if needed)
:: echo Installing common global packages...
:: call npm install -g npm@latest
:: call npm install -g yarn
:: call npm install -g pnpm

echo Installing the LESS compiler globally !!
npm install -g less less-plugin-clean-css

echo Installed the LESS compiler globally !!

echo Installation completed!
pause
endlocal