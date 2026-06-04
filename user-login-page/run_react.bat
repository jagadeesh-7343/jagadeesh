@echo off
set NODE_OPTIONS=--openssl-legacy-provider
cd /d "%~dp0"
npm start
