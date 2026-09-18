@echo off
chcp 65001 > nul
title GDPR Scan
if "%~1"=="" (
  set /p URL="Introduce la URL a analizar: "
) else (
  set URL=%~1
)
py gdpr_scan.py %URL% --out informe.html
echo.
pause
