"""Arma el paquete de la Etapa 3 para el equipo: entregas/paquete_equipo2/ y su .zip.

Uso (desde la raiz del repo):  python docs/entregables/etapa3/armar_paquete.py
Toma todo del repo (no guarda copias): script y datos de docs/bd/etapa3, API de servidor/api-rest,
sketches de firmware/arduino_ide y los documentos modelo de entregas/etapa3_A01669847 (correr antes generar.py).
No incluye node_modules, claves ni carpetas entrega_* de pruebas.
"""
import re
import shutil
import zipfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
R = AQUI.parents[2]
SAL = R / "entregas" / "paquete_equipo2"
NODOS = ("dht", "luz", "pir", "puerta", "acel")
NO = shutil.ignore_patterns("node_modules", ".env", "secrets.h")

if SAL.exists():
    shutil.rmtree(SAL)
SAL.mkdir(parents=True)

# instrucciones y script de preparacion
for f in ("LEEME.md", "preparar_entrega.js"):
    shutil.copy(AQUI / "paquete" / f, SAL)

# 01 base de datos
bd = SAL / "01_base_de_datos"
bd.mkdir()
for f in ("ScriptCreacionBaseDatos_iot_Equipo2.sql", "datos_prueba_Equipo2.sql"):
    shutil.copy(R / "docs/bd/etapa3" / f, bd)

# 02 API: la misma del repo, con nombre y autor neutros (preparar_entrega.js pone los de cada quien)
api = SAL / "02_api_rest"
shutil.copytree(R / "servidor/api-rest", api, ignore=NO)
principal = next(api.glob("RestApi-Equipo2-*.js"))
principal = principal.rename(api / "RestApi-Equipo2-MATRICULA.js")
for f in (principal, api / "package.json", api / "LEEME.md"):
    t = re.sub(r"RestApi-Equipo2-\w+", "RestApi-Equipo2-MATRICULA", f.read_text(encoding="utf-8"))
    t = re.sub(r"^ \* Autor:.*$", " * Autor: NOMBRE (MATRICULA) — nodo NODO.", t, flags=re.M)
    f.write_text(t, encoding="utf-8", newline="\n")

# 03 firmware y 04 indicadores, uno por nodo
(SAL / "04_indicadores").mkdir()
for n in NODOS:
    shutil.copytree(R / f"firmware/arduino_ide/argos_{n}", SAL / "03_firmware" / f"argos_{n}", ignore=NO)
    t = (R / f"docs/bd/etapa3/indicadores_{n}.sql").read_text(encoding="utf-8")
    t = re.sub(r"indicadores_iot_Equipo2-\w+\.sql", "indicadores_iot_Equipo2-Matricula.sql", t, count=1)
    (SAL / "04_indicadores" / f"indicadores_{n}.sql").write_text(t, encoding="utf-8", newline="\n")

# 05 documentos modelo (los del nodo dht)
modelo = SAL / "05_modelo_de_documento"
modelo.mkdir()
mio = R / "entregas/etapa3_A01669847"
for f in ("Etapa3_Documentacion_Equipo2-A01669847.docx", "Indicadores_Equipo2-A01669847.docx",
          "Indicadores_Equipo2-A01669847.pdf"):
    if (mio / f).exists():
        shutil.copy(mio / f, modelo / f"MODELO_{f}")
    else:
        print("falta el modelo:", f)

# zip con rutas "/" (se abre igual en Windows, Mac y celular)
zip_ = SAL.with_suffix(".zip")
with zipfile.ZipFile(zip_, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(SAL.rglob("*")):
        if f.is_file():
            z.write(f, f"{SAL.name}/{f.relative_to(SAL).as_posix()}")
print("listo:", SAL.relative_to(R), "y", zip_.name, f"({zip_.stat().st_size // 1024} KB)")
