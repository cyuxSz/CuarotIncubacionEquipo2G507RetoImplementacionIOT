"""Esquematico del circuito de prueba del nodo dht (NodeMCU + DHT11 + LED verde y rojo).
Uso: uv run --no-project --python 3.12 --with schemdraw --with matplotlib python docs/entregables/etapa3/esquematico_dht.py
"""
from pathlib import Path

import schemdraw
import schemdraw.elements as elm

SAL = Path(__file__).resolve().parent / "fritzing" / "esquematico_dht11.png"
ROJO, VERDE, AMARILLO, NEGRO = "#d62728", "#2ca02c", "#d4a000", "black"


def caja(d, x0, y0, x1, y1):
    for a, b in [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]:
        d.add(elm.Line().at(a).to(b))


def linea(d, a, b, color=NEGRO):
    d.add(elm.Line().at(a).to(b).color(color))


def texto(d, xy, t, **kw):
    d.add(elm.Label().at(xy).label(t, **kw))


with schemdraw.Drawing(show=False) as d:
    d.config(fontsize=13, unit=2)
    # NodeMCU
    caja(d, 0, 0, 3, 8)
    texto(d, (1.1, 3.25), "NodeMCU\nESP8266", fontsize=13)
    pines = {"3V3": 7, "D2": 5.5, "D7": 4, "D8": 2.5, "GND": 1}
    for n, y in pines.items():
        texto(d, (2.55, y), n, halign="right", fontsize=12)
    # DHT11
    caja(d, 11, 4.6, 13.4, 7.8)
    texto(d, (12.45, 6.2), "DHT11", fontsize=14)
    texto(d, (11.25, 7.0), "+", fontsize=12, halign="left")
    texto(d, (11.3, 5.5), "S", fontsize=12, halign="left")
    texto(d, (12.0, 4.95), "−", fontsize=12)
    linea(d, (3, 7), (11, 7), ROJO)
    linea(d, (3, 5.5), (11, 5.5), AMARILLO)
    texto(d, (7, 7.35), "3.3 V", fontsize=11)
    texto(d, (7, 5.85), "datos", fontsize=11)
    # LED rojo en D8
    linea(d, (3, 2.5), (6, 2.5), ROJO)
    r = d.add(elm.Resistor().down().at((6, 2.5)).length(1.6).label("220 Ω", loc="bottom"))
    led = d.add(elm.LED().down().at(r.end).length(1.6).fill(ROJO).label("LED rojo", loc="bottom"))
    linea(d, led.end, (6, -1.5))
    # LED verde en D7
    linea(d, (3, 4), (9, 4), VERDE)
    r = d.add(elm.Resistor().down().at((9, 4)).length(2.2).label("220 Ω", loc="bottom"))
    led = d.add(elm.LED().down().at(r.end).length(2).fill(VERDE).label("LED verde", loc="bottom"))
    linea(d, led.end, (9, -1.5))
    # tierra comun
    linea(d, (3, 1), (4, 1))
    linea(d, (4, 1), (4, -1.5))
    linea(d, (4, -1.5), (12, -1.5))
    linea(d, (12, 4.6), (12, -1.5))
    for x in (6, 9):
        d.add(elm.Dot().at((x, -1.5)))
    d.add(elm.Ground().at((12, -1.5)))
    texto(d, (8, -2.1), "GND", fontsize=11)
    d.save(str(SAL), dpi=200)
print("listo:", SAL)
