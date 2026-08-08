@echo off
title Richard OS — Setup
REM ---------------------------------------------------------------
REM STAGE 1 — Terms & Conditions (agree checkbox)
REM ---------------------------------------------------------------
echo.
echo  ============================================
echo   RICHARD OS  —  Setup  (Windows)
echo  ============================================
echo.
echo  Richard OS is a personal AI operating system.
echo  By installing you agree to the MIT License
echo  and the terms at docs/PORTFOLIO.md.
echo.
:agree
set /p AGREE=Type YES to accept the license and continue: 
if /i not "%AGREE%"=="YES" (
  echo   You must type YES to accept.
  goto agree
)
echo   [1/3] License agreed ✓

REM ---------------------------------------------------------------
REM STAGE 2 — Install location + shortcuts + optional permissions
REM ---------------------------------------------------------------
set DEST=%USERPROFILE%\RichardOS
set /p DEST=Install to [%DEST%]: 
if "%DEST%"=="" set DEST=%USERPROFILE%\RichardOS

echo   Choose optional permissions (you can change later in Settings):
echo     1 = Desktop shortcut  2 = Start-menu icon
set /p OPT=Desktop shortcut? (Y/n): 
if /i "%OPT%"=="n" (set SHORTCUT=0) else (set SHORTCUT=1)
echo   [2/3] Install location + shortcuts chosen ✓

REM ---------------------------------------------------------------
REM STAGE 3 — copy files, run verify, fetch user guide
REM ---------------------------------------------------------------
echo   Installing to %DEST% ...
if not exist "%DEST%" mkdir "%DEST%"
xcopy /E /I /Y "%~dp0..\..\..\*" "%DEST%\richard-os\" >nul 2>&1
echo   [3/3] Files copied. Verifying packages...

cd /d "%DEST%\richard-os"
if exist .venv\Scripts\python.exe (
  ".venv\Scripts\python.exe" scripts\verify_install.py
) else (
  echo   (venv not bundled — python -m venv .venv && pip install -r requirements.txt to complete)
)
echo.
echo   Richard OS installed. Run:
echo     cd "%DEST%\richard-os"  &&  ".venv\Scripts\python.exe" scripts\desktop_launcher.py
pause
