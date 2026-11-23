# Captura las laminas del video (PNG 1920x1080) y exporta la presentacion (PDF 16:9).
$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$base = "C:\dev\js\iot\expo_21nov\laminas"
New-Item -ItemType Directory -Force "$base\png" | Out-Null
$nombres = @{l01='01_portada';l02='02_equipo';l03='03_problema';l04='04_variables';l05='05_como_funciona';l06='06_tres_cajas';l07='07_ingenieria';l08='08_impacto';l09='09_cierre'}
foreach ($id in ($nombres.Keys | Sort-Object)) {
  $out = "$base\png\lamina_$($nombres[$id]).png"
  Start-Process -FilePath $edge -ArgumentList '--headless=new','--disable-gpu','--hide-scrollbars','--force-device-scale-factor=1','--virtual-time-budget=12000',"--user-data-dir=$base\_edge",'--window-size=1920,1080',"--screenshot=$out","file:///C:/dev/js/iot/expo_21nov/laminas/laminas.html?s=$id" -Wait
  Write-Output "$id $((Get-Item $out).Length)"
}
Remove-Item "$base\Argos_Presentacion_E2.pdf" -ErrorAction SilentlyContinue
Start-Process -FilePath $edge -ArgumentList '--headless=new','--disable-gpu','--no-pdf-header-footer','--virtual-time-budget=15000',"--user-data-dir=$base\_edge","--print-to-pdf=$base\Argos_Presentacion_E2.pdf","file:///C:/dev/js/iot/expo_21nov/laminas/laminas.html?todo=1" -Wait
Write-Output "pdf $((Get-Item "$base\Argos_Presentacion_E2.pdf").Length)"
Remove-Item -Recurse -Force "$base\_edge" -Confirm:$false
