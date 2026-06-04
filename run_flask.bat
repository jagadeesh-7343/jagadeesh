@echo off
set CB_DB_HOST=localhost
set CB_DB_PORT=5432
set CB_DB_NAME=citizen_bridge
set CB_DB_USER=postgres
set CB_DB_PASSWORD=1437
cd /d "%~dp0"
python connet.py
