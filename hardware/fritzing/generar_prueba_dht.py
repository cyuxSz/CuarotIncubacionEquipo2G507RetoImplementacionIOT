"""Diagrama en Fritzing del montaje de la entrega (Etapa 3): NodeMCU + modulo DHT11 + LED verde y rojo.
Reusa el generador de los nodos. El modulo DHT11 se dibuja con la parte DHT22 de Fritzing (mismos 3 cables).
Uso (desde la raiz): uv run --no-project --python 3.12 --with svgelements python hardware/fritzing/generar_prueba_dht.py
"""
import os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import generar_fritzing as g
import layouts as L

lay = dict(
    titulo="Prueba de la entrega: DHT11 + 2 LED",
    intro="NodeMCU, modulo DHT11 en D2 y LED verde (D7) y rojo (D8), todo sobre la protoboard.",
    puentes=[p for p in L.ALIMENTACION if p["de"] != "a1"] + [
        L.P("j6", "c18", "verde", "D7 -> resistencia del LED verde", 11.40),
        L.P("j5", "c25", "rojo", "D8 -> resistencia del LED rojo", 11.62),
        L.P("j13", "j27", "amarillo", "D2 -> columna 27 (S del DHT11)", 12.06),
        L.P("a23", "A_GND:23", "negro", "Pata corta del LED verde -> GND"),
        L.P("a30", "A_GND:30", "negro", "Pata corta del LED rojo -> GND"),
    ],
    componentes=[
        L.R("R5", "220 Ω", "b18", "b22", "LED verde"),
        L.R("R6", "220 Ω", "b25", "b29", "LED rojo"),
        {"ref": "LED_V", "tipo": "LED", "valor": "verde", "pines": {"A": "d22", "K": "d23"}, "nota": ""},
        {"ref": "LED_R", "tipo": "LED", "valor": "rojo", "pines": {"A": "d29", "K": "d30"}, "nota": ""},
    ],
    externos=[
        L.E("DHT22", "VCC", "J_3V3:26", "naranja", "+ del modulo"),
        L.E("DHT22", "DATA", "h27", "amarillo", "S del modulo"),
        L.E("DHT22", "GND", "J_GND:28", "negro", "- del modulo"),
    ],
    redes={**L.REDES_BASE, "GND": {"NodeMCU.GND", "LED_V.K", "LED_R.K", "DHT22.GND"},
           "3V3": {"NodeMCU.3V3", "DHT22.VCC"}, "DATA": {"NodeMCU.D2", "DHT22.DATA"}},
    verificacion="",
)
nombre = "prueba_dht11"
g.SALIDA = Path(__file__).resolve().parent / "salida_prueba"
g.instalar_partes()
b = g.Boceto()
insts = g.protoboard(b, lay)
insts["LED_V"]["props"] = {"color": "Green (570nm)"}
insts["LED_R"]["props"] = {"color": "Red (633nm)"}
g.esquematico(b, lay, insts)
g.pcb_por_defecto(b)
print("ok", g.empacar(nombre, b.xml("Argos - prueba DHT11")).name)
subprocess.run([str(g.FZ / "Fritzing.exe"), "-svg", str(g.SALIDA)], check=True, timeout=600)
print("svg en", g.SALIDA)
