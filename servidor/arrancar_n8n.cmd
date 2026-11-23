@echo off
rem Arranca n8n con el Node 24 portable (el Node 26 del servidor no se toca).
rem Correrlo en su propia terminal de VS Code y dejarla abierta. Panel: http://localhost:5678
set "PATH=C:\Users\a00843900\Documents\IoT\herramientas\node-v24.22.3-win-x64;%PATH%"
rem Datos de n8n (flujos, cuenta, credenciales) en esta carpeta, en "datos\.n8n"
set "N8N_USER_FOLDER=C:\Users\a00843900\Documents\IoT\herramientas\n8n\datos"
set "N8N_HOST=localhost"
set "N8N_PORT=5678"
set "N8N_LISTEN_ADDRESS=127.0.0.1"
set "GENERIC_TIMEZONE=America/Monterrey"
set "TZ=America/Monterrey"
set "N8N_DIAGNOSTICS_ENABLED=false"
set "N8N_PERSONALIZATION_ENABLED=false"
cd /d "C:\Users\a00843900\Documents\IoT\herramientas\n8n"
call node_modules\.bin\n8n.cmd start
