"""Regenera todo lo que sale de las fuentes (layouts.py, medidas.json, firmware/src) y corre los chequeos.

Uso (desde la raiz, Git Bash o PowerShell):
    python regenerar.py              hardware + firmware (rapido) y copias de presentacion/
    python regenerar.py --cad        ademas las carcasas, renders, visor web y 3MF (varios minutos)
    python regenerar.py --compilar   ademas compila los 6 entornos con PlatformIO (nunca flashea)
    python regenerar.py --revisar    no deja cambios sin avisar: sale con 1 si algun archivo generado
                                     de texto cambio (es decir, estaba desactualizado)
Sale con 1 si falla algun chequeo.
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
UV = ["uv", "run", "--no-project", "--python", "3.12"]
B123D = UV + ["--with", "build123d>=0.10,<0.14", "--with", "matplotlib", "python"]
PIO = Path.home() / ".local/bin/pio.exe"
GRAPHVIZ = r"C:\Program Files\Graphviz\bin"
CAJAS = ("dht", "entrada", "anaquel")

PASOS = [  # (nombre, comando, carpeta)
    ("protoboard y chequeo de redes", UV + ["--with", "matplotlib", "python", "protoboard.py"], "hardware/breadboard"),
    ("prompts de armado", ["python", "hardware/breadboard/prompts.py"], "."),
    ("WireViz (YAML)", ["python", "hardware/wiring/generar_wireviz.py"], "."),
    ("esquematicos", UV + ["--with", "schemdraw", "--with", "matplotlib", "python", "hardware/esquematicos/esquematicos.py"], "."),
    ("pines firmware = layouts", ["python", "hardware/chequeo_pines.py"], "."),
    ("reglas del buzzer (prueba en PC)", ["python", "firmware/herramientas/prueba_alarma.py"], "."),
    ("sketches de Arduino IDE", ["python", "firmware/herramientas/exportar_arduino.py"], "."),
    ("vista de la OLED", UV + ["--with", "pillow", "python", "firmware/herramientas/oled_host.py"], "."),
]
PASOS_CAD = [(f"cad/{s}.py", B123D + [f"cad/{s}.py"], ".") for s in
             ("nodos", "caja_potencia", "pruebas_ldr", "pruebas_mc38", "pruebas", "escenas", "web", "accesorios_vista",
              "exportar_3mf")]
PASOS_CAD.insert(1, ("cad/nodos.py anaquel_rele (submodulo opcional)", B123D + ["cad/nodos.py", "anaquel_rele"], "."))
# copias que sirve presentacion/ (el artifact no puede leer fuera de su carpeta)
COPIAS = ([(f"cad/renders/{f}", "img") for f in (
    "capuchon_ldr_corte.png", "capuchon_ldr_iso.png", "niveles_anaquel.png", "niveles_dht.png", "niveles_entrada.png",
    "nodo_anaquel_vistas.png", "nodo_dht_escena_anaquel.png", "nodo_dht_explosionada.png", "nodo_dht_vistas.png",
    "nodo_entrada_vistas.png", "porta_iman_iso.png", "porta_sensor_iso.png", "soporte_ldr_iso.png")]
          + [(f"hardware/breadboard/{c}_protoboard.png", "protoboard") for c in
             ("nodo_dht", "estacion_entrada", "estacion_anaquel")]
          + [(f"hardware/wiring/nodo_{c}.png", "cableado") for c in CAJAS]
          + [(f"hardware/esquematicos/nodo_{n}.svg", "esquematicos") for n in ("dht", "luz", "pir", "puerta", "acel")])
VIGILADOS = ("hardware/breadboard/*.md", "hardware/wiring/*.yml", "docs/prompts_armado.md",
             "firmware/arduino_ide/*/*.cpp", "firmware/arduino_ide/*/*.h", "presentacion/nodos.json")


def huellas():
    return {p: hashlib.md5(p.read_bytes()).hexdigest() for g in VIGILADOS for p in RAIZ.glob(g)}


def correr(nombre, cmd, carpeta, env=None):
    print(f"-- {nombre}")
    r = subprocess.run(cmd, cwd=RAIZ / carpeta, env=env, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    if r.returncode:
        print((r.stdout + r.stderr)[-2500:])
    return r.returncode == 0


def wireviz():
    env = {**os.environ, "PATH": GRAPHVIZ + os.pathsep + os.environ["PATH"]}
    exe = RAIZ / ".venv" / "Scripts" / "wireviz.exe"
    return all(correr(f"WireViz {c}", [str(exe), f"hardware/wiring/nodo_{c}.yml"], ".", env) for c in CAJAS)


def copiar():
    for origen, carpeta in COPIAS:
        src, dst = RAIZ / origen, RAIZ / "presentacion" / carpeta / Path(origen).name
        if src.suffix == ".svg":   # sin DOCTYPE: el visor lo incrusta tal cual
            dst.write_text(re.sub(r"<!DOCTYPE[^>]*>\s*", "", src.read_text(encoding="utf-8")), encoding="utf-8")
        else:
            shutil.copy2(src, dst)
    print(f"-- {len(COPIAS)} copias a presentacion/")


def main(args):
    antes = huellas()
    ok = True
    for paso in PASOS + (PASOS_CAD if "--cad" in args else []):
        ok &= correr(*paso)
    ok &= wireviz()
    if "--compilar" in args:
        env = {**os.environ, "PLATFORMIO_WORKSPACE_DIR": str(Path.home() / ".platformio/ws/incumonitor")}
        ok &= correr("PlatformIO (solo compilar)", [str(PIO), "run", "-d", "firmware", "-e", "dht", "-e", "dht_sin_oled",
                                                    "-e", "luz", "-e", "luz_rele", "-e", "pir", "-e", "puerta", "-e", "acel"], ".", env)
    copiar()
    cambiados = sorted(str(p.relative_to(RAIZ)) for p, h in huellas().items() if antes.get(p) != h)
    print("\nArchivos generados que cambiaron:", *cambiados or ["ninguno"], sep="\n  ")
    if "--revisar" in args and cambiados:
        print("Estaban desactualizados respecto a sus fuentes.")
        ok = False
    print("\nOK" if ok else "\nHAY FALLAS")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main(sys.argv[1:])
