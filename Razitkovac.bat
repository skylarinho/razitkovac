@echo off
rem Launcher: first run creates .venv and installs dependencies, then starts the app.
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Prvni spusteni: pripravuji prostredi, chvili to potrva...
    where py >nul 2>nul && (py -3 -m venv .venv) || (python -m venv .venv)
    if not exist ".venv\Scripts\python.exe" (
        echo Nepodarilo se vytvorit prostredi. Je nainstalovany Python 3.11+?
        pause
        exit /b 1
    )
    ".venv\Scripts\python.exe" -m pip install -q -r requirements.txt
    if errorlevel 1 (
        echo Instalace zavislosti selhala.
        rmdir /s /q .venv
        pause
        exit /b 1
    )
)

echo Razitkovac bezi na http://127.0.0.1:5000  (zavrenim tohoto okna ho vypnete)
".venv\Scripts\python.exe" app.py
pause
