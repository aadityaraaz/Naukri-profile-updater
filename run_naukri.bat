@echo off
setlocal
REM Simple runner: hardcoded email/password, no prompts.

REM Jump to this script's folder
cd /d "%~dp0"

REM Prefer workspace venv Python; fallback to system python
set "PY=%~dp0.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

REM Hardcoded credentials
set "EMAIL=email"
set "PASS=password"

REM Optional: uncomment if you want to force a browser/profile
REM set "BROWSER=edge"
REM set "BROWSER_USER_DATA_DIR=C:\Users\adity\AppData\Local\Microsoft\Edge\User Data"
REM set "BROWSER_PROFILE=Default"

"%PY%" -X utf8 "%~dp0naukriProfileUpdate.py" --email "%EMAIL%" --password "%PASS%"
set "EXITCODE=%ERRORLEVEL%"

endlocal & exit /b %EXITCODE%
