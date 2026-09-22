@echo off
chcp 65001 > nul
title GDPR Scan - Web
echo Iniciando GDPR Scan Web en http://localhost:8000 ...
start "" http://localhost:8000
py app.py
pause
