@echo off
chcp 65001 > nul
title GDPR Scan - Web
set PORT=8777
echo Iniciando GDPR Scan Web en http://localhost:%PORT% ...
start "" http://localhost:%PORT%
py app.py
pause
