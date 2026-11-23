# Arranca el servidor de Argos en esta PC SIN Docker: las 5 API de los nodos (puertos 3001-3005)
# y el servicio central (panel en http://localhost:3000). Cada uno en su ventana, para ver su registro.
#
# Antes (una sola vez): ver servidor/LEEME.md  (MySQL con la base argos, los dos archivos .env, npm install).
# Uso:      powershell -ExecutionPolicy Bypass -File servidor\arrancar.ps1
# Detener:  cerrar las 6 ventanas.
$aqui = Split-Path -Parent $MyInvocation.MyCommand.Path
foreach ($carpeta in 'api-rest', 'central') {
  if (-not (Test-Path "$aqui\$carpeta\.env")) { Write-Host "Falta $carpeta\.env (copia la plantilla y llenala; ver LEEME.md)" -ForegroundColor Red; exit 1 }
  if (-not (Test-Path "$aqui\$carpeta\node_modules")) { Write-Host "Falta 'npm install' en servidor\$carpeta" -ForegroundColor Red; exit 1 }
}
$puertos = [ordered]@{ dht = 3001; luz = 3002; pir = 3003; puerta = 3004; acel = 3005 }
# Si algun puerto ya esta en uso, el servidor ya esta corriendo (o quedo una ventana vieja): dos copias duplican las alertas.
$ocupados = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -ge 3000 -and $_.LocalPort -le 3005 } | Select-Object -ExpandProperty LocalPort -Unique)
if ($ocupados.Count -gt 0) {
  Write-Host "Ya hay algo escuchando en: $($ocupados -join ', '). Cierra las ventanas de Argos que sigan abiertas y vuelve a correr esto." -ForegroundColor Red
  exit 1
}
# Cada ventana relanza su proceso si se cae (espera 3 s). Para detenerlo de verdad: cerrar la ventana.
# OJO: no hagas clic dentro de las ventanas; en la consola clasica seleccionar texto congela el proceso (Esc lo suelta).
$bucle = "while (`$true) { {0}; Write-Host 'El proceso termino: se relanza en 3 s (cierra la ventana para detenerlo)' -ForegroundColor Yellow; Start-Sleep 3 }"
foreach ($nodo in $puertos.Keys) {
  # Las variables de la ventana mandan sobre las del .env: asi un solo .env sirve para las 5 API.
  $orden = "`$env:NODO='$nodo'; `$env:PUERTO='$($puertos[$nodo])'; `$Host.UI.RawUI.WindowTitle='Argos API $nodo'; " + $bucle.Replace('{0}', 'node --env-file=.env .')
  Start-Process powershell -WorkingDirectory "$aqui\api-rest" -ArgumentList '-NoExit', '-Command', $orden
}
Start-Process powershell -WorkingDirectory "$aqui\central" -ArgumentList '-NoExit', '-Command', ("`$Host.UI.RawUI.WindowTitle='Argos central'; " + $bucle.Replace('{0}', 'node --env-file=.env central.js'))
Write-Host "Listo. Panel: http://localhost:3000   API: puertos 3001 (dht), 3002 (luz), 3003 (pir), 3004 (puerta), 3005 (acel)"
Write-Host "En el secrets.h de cada nodo: API_HOST = la IP de esta PC en el WiFi (ipconfig) y API_PORT = el puerto de su nodo."
