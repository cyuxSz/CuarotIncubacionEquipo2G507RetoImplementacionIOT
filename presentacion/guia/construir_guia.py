"""Arma presentacion/guia_armado.html: guia de armado para principiantes con los Fritzing por pasos y las listas
de cables (hardware/fritzing/salida). Correr despues de generar_fritzing.py --pasos, a_png y lista_cables.py.

  uv run --no-project --python 3.12 python presentacion/guia/construir_guia.py
"""
import base64
import html
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
FZ = RAIZ / "hardware" / "fritzing" / "salida"
sys.path.insert(0, str(RAIZ / "hardware" / "breadboard"))
sys.path.insert(0, str(RAIZ / "hardware" / "fritzing"))
import layouts  # noqa: E402
import lista_cables as lc  # noqa: E402

CAJAS = [("dht", "nodo_dht", "Caja dht", "Luis", "DHT22, pantalla OLED, buzzer y botón"),
         ("entrada", "estacion_entrada", "Estación de entrada", "Chema (pir) e Iván (puerta)", "sensor de movimiento y sensor de puerta"),
         ("anaquel", "estacion_anaquel", "Estación del anaquel", "Arianna (acel) y Mía (luz)", "acelerómetro y sensor de luz")]
PASOS = {1: "Placas, energía y capacitores", 2: "Resistencias y puentes", 3: "Módulos y transistor",
         4: "Cables a las piezas de la tapa"}
PUNTO = {"sólido rojo": "#cc1414", "sólido negro": "#303030", "UTP naranja": "#ef6100", "UTP verde": "#2f9e44",
         "UTP azul": "#1f5fbf", "UTP café": "#8c3b00", "UTP blanco/naranja": "#ef6100", "UTP blanco/verde": "#2f9e44",
         "UTP blanco/azul": "#1f5fbf", "UTP blanco/café": "#8c3b00"}


def img(nombre):
    datos = base64.b64encode((FZ / nombre).read_bytes()).decode()
    return f'<div class="fig"><img alt="Diagrama de Fritzing" src="data:image/png;base64,{datos}"></div>'


def filas_cables(clave):
    out = []
    for linea in (FZ / f"lista_cables_{clave}.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| (\d+) \| (\w[\w ]*) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|$", linea)
        if m:
            n, tipo, de, a, cable, largo, para = m.groups()
            energia = tipo == "puente" and re.sub(r"^\[\w+\] ", "", para).startswith(("VIN", "GND →", "3V3 →"))
            paso = 4 if tipo != "puente" else (1 if energia else 2)
            out.append(dict(n=n, de=de, a=a, cable=cable, largo=largo, para=para, paso=paso))
    return out


def chip(cable):
    rayado = "blanco/" in cable
    fondo = (f"repeating-linear-gradient(90deg,{PUNTO[cable]} 0 5px,#fff 5px 9px)" if rayado else PUNTO.get(cable, "#888"))
    return f'<span class="cable"><i style="background:{fondo}"></i>{html.escape(cable)}</span>'


def tabla_cables(filas):
    if not filas:
        return ""
    f = "".join(f'<tr><td class="n">{r["n"]}</td><td class="h">{html.escape(r["de"])}</td><td class="h">{html.escape(r["a"])}</td>'
                f'<td>{chip(r["cable"])}</td><td class="n">{r["largo"] if r["largo"] != "0" else "—"}</td>'
                f'<td>{html.escape(r["para"])}</td></tr>' for r in filas)
    return ('<div class="scroll"><table><thead><tr><th>#</th><th>De</th><th>A</th><th>Cable</th><th>cm</th><th>Para qué</th></tr>'
            f'</thead><tbody>{f}</tbody></table></div>')


def tabla_comps(lay, tipos):
    filas = []
    for c in lay["componentes"]:
        if c["tipo"] not in tipos:
            continue
        pines = " · ".join(f"{k}: {lc.impreso(v)}" for k, v in c["pines"].items())
        filas.append(f'<tr><td>{html.escape(c["ref"].replace("_", " "))}</td><td>{html.escape(c["valor"])}</td>'
                     f'<td class="h">{html.escape(pines)}</td><td>{html.escape(lc.nota_impresa(c.get("nota", "")).replace("**", ""))}</td></tr>')
    if not filas:
        return ""
    return ('<div class="scroll"><table><thead><tr><th>Pieza</th><th>Valor</th><th>Orificios</th><th>Nota</th></tr></thead>'
            f'<tbody>{"".join(filas)}</tbody></table></div>')


def seccion_caja(clave, nombre, titulo, quien, que):
    lay = layouts.LAYOUTS[nombre]
    cables = filas_cables(clave)
    estacion = len(layouts.placas(lay)) > 1
    o = [f'<section id="caja-{clave}"><h2>{titulo}</h2><p class="lead">{que.capitalize()}. Arma: {quien}.</p>']
    textos = {
        1: ("Clava " + ("los dos NodeMCU" if estacion else "el NodeMCU") + " con el micro-USB a la izquierda, pon los puentes "
            "cortos de energía y el capacitor de cada placa. " +
            ("<b>La placa de la derecha no lleva el puente naranja al riel de +3V3.</b>" if estacion else "")),
        2: "Resistencias acostadas cruzando el canal y los puentes de señal. Los puentes largos corren por el hueco entre la "
           "fila A y el riel de abajo, uno junto a otro, sin encimarse. Hazlos planos, pegados a la protoboard.",
        3: ("Ahora los módulos, que quedan encima de los puentes cortos que acabas de poner." if clave == "anaquel" else
            "El transistor 2N2222 de lata metálica: la pestañita marca el emisor." if clave == "dht" else
            "Esta caja no lleva módulos ni transistor sobre la protoboard: pasa al paso 4."),
        4: "Estas piezas no van clavadas: van en la tapa o fuera de la caja. A cada una se le suelda su cable (ver «Soldar») "
           "y la otra punta, pelada y estañada, entra al orificio indicado.",
    }
    for p in (1, 2, 3, 4):
        o.append(f'<h3><span class="paso">Paso {p}</span> {PASOS[p]}</h3><p>{textos[p]}</p>')
        o.append(img(f"{nombre}_paso{p}_breadboard.png"))
        tipos = {1: ("C",), 2: ("R",), 3: ("M", "Q"), 4: ()}[p]
        o.append(tabla_comps(lay, tipos))
        if p < 4:
            o.append(tabla_cables([c for c in cables if c["paso"] == p]))
            continue
        # Paso 4, pieza por pieza: una imagen con SOLO los cables de esa pieza y su tabla.
        o.append('<p>Arriba está el circuito completo. Abajo va <b>una pieza a la vez</b>: conecta sus cables, '
                 'palomea su tabla y pasa a la siguiente.</p>')
        for i, (pieza, nombre_pieza, disps) in enumerate(lc.piezas(lay), 1):
            suyos = [c for c in cables if c["paso"] == 4 and c["de"].rsplit(".", 1)[0] in disps]
            o.append(f'<h4><span class="paso">4.{i}</span> {html.escape(nombre_pieza)}</h4>')
            o.append(img(f"{nombre}_parte{i}_{pieza}_breadboard.png"))
            o.append(tabla_cables(suyos))
        if p == 2:
            o.append('<p class="nota"><b>Prueba sin energía.</b> Multímetro en continuidad: no debe pitar entre +5V y GND, '
                     'ni entre +3V3 y GND. Si pita, hay un corto: no conectes nada hasta encontrarlo.</p>')
    o.append("</section>")
    return "\n".join(o)


if __name__ == "__main__":
    cuerpo = "\n".join(seccion_caja(*c) for c in CAJAS)
    plantilla = (AQUI / "plantilla.html").read_text(encoding="utf-8")
    salida = RAIZ / "presentacion" / "guia_armado.html"
    salida.write_text(plantilla.replace("<!--__CAJAS__-->", cuerpo), encoding="utf-8")
    print("escrito", salida, round(salida.stat().st_size / 1024), "KB")
