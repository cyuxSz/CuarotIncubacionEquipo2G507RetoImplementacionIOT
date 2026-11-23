"""Fritzing solo con lo que se revisa del DHT22 del nodo dht: 3V3 y GND a los rieles de abajo, puente D4 -> columna 24,
R1 de 10 kOhm (pull-up) y los 3 cables del DHT22. Usa el generador de Luis sin modificarlo; salida en esta carpeta.
Uso: set FRITZING_DIR y correr con uv + svgelements.
"""
import shutil, subprocess, sys
from pathlib import Path

RAIZ = Path(r"C:\dev\js\iot\chema_22nov\Argos_completo_22nov\hardware")
sys.path.insert(0, str(RAIZ / "fritzing"))
import generar_fritzing as g  # noqa: E402
import layouts as L           # noqa: E402

base = L.LAYOUTS["nodo_dht"]
ref = {"R1"}
lay = dict(
    titulo="Revisión del DHT22 (D4)",
    intro="",
    puentes=[p for p in base["puentes"] if (p["de"], p["a"]) in {("j1", "J_3V3:1"), ("j2", "J_GND:2"), ("j11", "h24")}],
    componentes=[c for c in base["componentes"] if c["ref"] in ref],
    externos=[e for e in base["externos"] if e["disp"] == "DHT22"],
    redes={"3V3": {"NodeMCU.3V3", "R1.2", "DHT22.VCC"}, "GND": {"NodeMCU.GND", "DHT22.GND"},
           "DATA": {"NodeMCU.D4", "DHT22.DATA", "R1.1"}},
    verificacion="",
)
assert len(lay["puentes"]) == 3 and len(lay["componentes"]) == 1 and len(lay["externos"]) == 3, lay

AQUI = Path(__file__).resolve().parent
# El DHT22 real es un módulo de 3 pines (+ out −): pieza propia en la copia local de partes/.
g.PROPIAS = AQUI / "partes"
g.PARTES["DHT22"] = (g.PROPIAS / "argos_dht22_3p.fzp", g.PROPIAS / "svg", {"VCC": "connector0", "DATA": "connector1", "GND": "connector2"})
g.SALIDA = AQUI / "salida"
g.SALIDA.mkdir(exist_ok=True)
g.instalar_partes()
b = g.Boceto()
g.protoboard(b, lay)
g.pcb_por_defecto(b)
fzz = g.empacar("revision_dht22_d4", b.xml("Argos · nodo dht · revisión del DHT22 (D4, R1, rieles)"))
print("ok", fzz)
subprocess.run([str(g.FZ / "Fritzing.exe"), "-svg", str(g.SALIDA)], check=True, timeout=600)
sys.path.insert(0, str(RAIZ / "fritzing"))
import a_png  # noqa: E402
for s in g.SALIDA.glob("*_breadboard.svg"):
    print("png", a_png.a_png(s))
