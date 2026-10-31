@echo off
REM VolGuard AI - one-click backend launcher (Windows).
REM Usage: run_server.bat [--reload]   (set PORT=8001 first to change port)
setlocal EnableDelayedExpansion
cd /d "%~dp0"

if "%PORT%"=="" set PORT=8000
set RELOAD=
if /I "%~1"=="--reload" set RELOAD=--reload

set PY=
where py >nul 2>nul && set PY=py -3
if "%PY%"=="" where python >nul 2>nul && set PY=python
if "%PY%"=="" (
  echo [VolGuard] Python 3.10+ not found. Install it from python.org and tick "Add to PATH".
  exit /b 1
)

REM 1. virtual environment
set VENV=
for %%D in (.venv ..\.venv venv ..\venv) do (
  if "!VENV!"=="" if exist "%%D\Scripts\activate.bat" set VENV=%%D
)
if "%VENV%"=="" (
  echo [VolGuard] Creating virtual environment .venv ...
  %PY% -m venv .venv || exit /b 1
  set VENV=.venv
)
call "%VENV%\Scripts\activate.bat"

REM 2. dependencies
python -c "import fastapi, uvicorn, pandas, numpy, arch, yfinance" >nul 2>nul
if errorlevel 1 (
  echo [VolGuard] Installing dependencies ...
  python -m pip install --quiet --upgrade pip
  python -m pip install --quiet -r requirements.txt || exit /b 1
)

REM 3. offline mode: respect user setting, otherwise auto-detect Yahoo reachability
if "%VOLGUARD_OFFLINE%"=="" (
  python -c "import socket; socket.create_connection(('query1.finance.yahoo.com', 443), 3).close()" >nul 2>nul
  if errorlevel 1 (
    set VOLGUARD_OFFLINE=1
    echo [VolGuard] Yahoo Finance unreachable: using bundled offline CSV.
  ) else (
    set VOLGUARD_OFFLINE=0
    echo [VolGuard] Yahoo Finance reachable: live data with CSV fallback.
  )
)

REM 4. port check
python -c "import socket,sys; s=socket.socket(); sys.exit(0 if s.connect_ex(('127.0.0.1', %PORT%))==0 else 1)"
if not errorlevel 1 (
  echo [VolGuard] Port %PORT% already in use. Close the other process or set PORT=8001 and rerun.
  exit /b 1
)

echo [VolGuard] API:  http://localhost:%PORT%   Docs: http://localhost:%PORT%/docs
python -m uvicorn api:app --host 0.0.0.0 --port %PORT% %RELOAD%
endlocal
