@echo off
setlocal
cd /d "%~dp0"
echo =============================================
echo   Logistics ML Blockchain - Local Startup
echo =============================================
where python >nul 2>&1 || (echo ERROR: Python was not found. Install Python and try again.&pause&exit /b 1)
if not exist .venv\Scripts\python.exe (
  echo Creating Python virtual environment...
  python -m venv .venv || (echo ERROR: Could not create virtual environment.&pause&exit /b 1)
)
set PY=.venv\Scripts\python.exe
%PY% -m pip install -r requirements.txt
if errorlevel 1 (echo ERROR: Python dependencies could not be installed.&pause&exit /b 1)
if not exist model\logistics_model.pkl (
  echo ML model missing. Running notebook automatically is not reliable in every environment.
  echo Install Jupyter and run ml\logistics_ml.ipynb, then restart this file.
  echo A model is included in the generated project when available.
)
echo.
echo Checking Ganache at 127.0.0.1:7545...
%PY% -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:7545',timeout=2)" >nul 2>&1
if errorlevel 1 (
  echo WARNING: Ganache is not reachable at http://127.0.0.1:7545
  echo Start Ganache Desktop with the project network before recording blockchain transactions.
) else (
  echo Ganache RPC is reachable.
)
if not exist blockchain_config.json echo WARNING: blockchain_config.json is missing.
start "Logistics Flask Server" cmd /k "%PY% backend\app.py"
timeout /t 3 /nobreak >nul
start "" http://127.0.0.1:5000
echo Flask should now be available at http://127.0.0.1:5000
endlocal
