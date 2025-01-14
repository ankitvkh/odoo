@echo off
setlocal enabledelayedexpansion

:: Check if version parameter is provided
if "%~1"=="" (
    echo Usage: install_python.bat [version] [install_path]
    echo Example: install_python.bat 3.10.11 C:\Python
    exit /b 1
)

:: Set variables
set PYTHON_VERSION=%~1
set INSTALL_PATH=%~2
if "%INSTALL_PATH%"=="" set INSTALL_PATH=C:\Python

:: Set file names and paths
set INSTALLER_NAME=python-%PYTHON_VERSION%-amd64.exe
set DOWNLOAD_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/%INSTALLER_NAME%
set TEMP_PATH=%TEMP%\%INSTALLER_NAME%
set FINAL_INSTALL_PATH=%INSTALL_PATH%\Python%PYTHON_VERSION:~0,1%%PYTHON_VERSION:~2,1%

echo Download URL: %DOWNLOAD_URL%

:: Create installation directory if it doesn't exist
if not exist "%INSTALL_PATH%" mkdir "%INSTALL_PATH%"

:: Download Python installer with improved error handling
echo Downloading Python %PYTHON_VERSION%...
echo Downloading to: %TEMP_PATH%

powershell -Command "& { $ProgressPreference = 'Continue'; try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Write-Host 'Starting download...'; Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%TEMP_PATH%' -Verbose; if (Test-Path '%TEMP_PATH%') { Write-Host 'Download completed successfully' } else { Write-Host 'Download failed - file not found' ; exit 1 } } catch { Write-Host $_.Exception.Message; exit 1 } }"

if %ERRORLEVEL% neq 0 (
    echo Failed to download Python installer
    echo Please verify that version %PYTHON_VERSION% exists at:
    echo %DOWNLOAD_URL%
    exit /b 1
)

:: Verify the downloaded file exists
if not exist "%TEMP_PATH%" (
    echo ERROR: Downloaded file not found at %TEMP_PATH%
    exit /b 1
)

:: Install Python with complete silent installation parameters
echo Installing Python %PYTHON_VERSION% to %FINAL_INSTALL_PATH%...
start /wait "" "%TEMP_PATH%" /quiet /passive /norestart InstallAllUsers=0 TargetDir="%FINAL_INSTALL_PATH%" PrependPath=1 Include_test=0 Include_pip=1 Shortcuts=0 AssociateFiles=0 CompileAll=1

if %ERRORLEVEL% neq 0 (
    echo Installation failed
    del "%TEMP_PATH%"
    exit /b 1
)

:: Clean up
del "%TEMP_PATH%"

:: Verify installation
echo Verifying installation...
if exist "%FINAL_INSTALL_PATH%\python.exe" (
    "%FINAL_INSTALL_PATH%\python.exe" --version
    echo Python %PYTHON_VERSION% installed successfully!
) else (
    echo WARNING: Could not verify Python installation
)

endlocal