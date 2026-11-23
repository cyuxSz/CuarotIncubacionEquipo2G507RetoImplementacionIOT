"""Lista de cables de corte de cada caja (de layouts.py): color real, largo y de dónde a dónde.

Uso: python hardware/fritzing/lista_cables.py   ->   hardware/fritzing/salida/lista_cables_<caja>.md
Largo de puente = distancia entre orificios (2.54 mm de paso) + 1.6 cm para pelar y doblar las dos puntas.
Los cables a piezas externas llevan un largo supuesto: ajustarlo al armar.
"""
import math
import sys
from collections import defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1] / "hardware" / "breadboard"))
import layouts  # noqa: E402

SALIDA = AQUI / "salida"
CAJAS = {"dht": "nodo_dht", "entrada": "estacion_entrada", "anaquel": "estacion_anaquel"}
UTP = {"naranja": "UTP naranja", "azul": "UTP azul", "verde": "UTP verde", "cafe": "UTP café",
       "morado": "UTP blanco/naranja", "amarillo": "UTP blanco/verde", "gris": "UTP blanco/azul",
       "blanco": "UTP blanco/café", "rojo": "sólido rojo", "negro": "sólido negro"}
LARGO_EXTERNO = {"DHT22": 20, "OLED": 20, "PIR": 25, "LDR": 100, "Reed": 0, "Entrada5V": 10}


# Letras como vienen IMPRESAS en la MB-102 (y en la imagen de Fritzing): con el USB de los NodeMCU a la izquierda,
# la fila "a" de layouts.py queda arriba y la protoboard la marca como J (generar_fritzing.py refleja a<->j).
IMPRESA = dict(zip("abcdefghij", "JIHGFEDCBA"))
RIEL_TXT = {"A_5V": "riel de arriba +5V (línea roja)", "A_GND": "riel de arriba GND (línea azul)",
            "J_3V3": "riel de abajo +3V3 (línea roja)", "J_GND": "riel de abajo GND (línea azul)"}


TITULO_PIEZA = {"Entrada5V": "Entrada de 5 V (módulo USB-C)", "LED": "LED verde y LED rojo", "Boton": "Botón",
                "Buzzer": "Buzzer", "DHT22": "Sensor DHT22", "OLED": "Pantalla OLED", "PIR": "Sensor de movimiento",
                "Reed": "Sensor de puerta", "LDR": "Fotorresistencia", "Rele": "Módulo de relés"}
ORDEN_PIEZA = ["Entrada5V", "LED", "Boton", "Buzzer", "DHT22", "OLED", "PIR", "Reed", "LDR", "Rele"]


def grupo_pieza(disp):
    """'pir_LED_V' -> ('pir', 'LED'); 'OLED' -> ('', 'OLED'). Los dos LED de un nodo forman una sola pieza."""
    nodo, base = disp.split("_", 1) if disp.split("_")[0] in ("acel", "luz", "pir", "puerta") else ("", disp)
    return nodo, "LED" if base.startswith("LED_") else base


def piezas(lay):
    """Piezas externas de una distribucion, en el orden en que conviene conectarlas:
    [(clave, titulo, {disp, ...})]. La usan generar_fritzing.py --partes y la guia de armado."""
    grupos = {}
    for e in lay["externos"]:
        grupos.setdefault(grupo_pieza(e["disp"]), set()).add(e["disp"])
    orden = sorted(grupos, key=lambda g: (ORDEN_PIEZA.index(g[1]) if g[1] in ORDEN_PIEZA else 99, g[0]))
    return [(f"{nodo}_{base}".strip("_").lower(), TITULO_PIEZA.get(base, base) + (f" del nodo {nodo}" if nodo else ""),
             grupos[(nodo, base)]) for nodo, base in orden]


def impreso(h):
    """'a48' -> 'J48'; 'A_5V:34' -> 'riel de arriba +5V (línea roja), col. 34'; otro texto igual."""
    import re
    if ":" in h and h.split(":")[0] in RIEL_TXT:
        r, c = h.split(":")
        return f"{RIEL_TXT[r]}, col. {c}"
    m = re.fullmatch(r"([a-j])(\d{1,2})", h)
    return f"{IMPRESA[m[1]]}{m[2]}" if m else h


def nota_impresa(n):
    import re
    n = re.sub(r"\b([a-j])(\d{1,2})\b", lambda m: f"{IMPRESA[m[1]]}{m[2]}", n)
    n = re.sub(r"\bfila ([a-j])\b", lambda m: f"fila {IMPRESA[m[1]]}", n)
    n = re.sub(r"\bfilas ([a-j])→([a-j])\b", lambda m: f"filas {IMPRESA[m[1]]}→{IMPRESA[m[2]]}", n)
    n = re.sub(r"\bfilas ([a-j])-([a-j])\b", lambda m: f"filas {IMPRESA[m[1]]}-{IMPRESA[m[2]]}", n)
    n = n.replace("riel GND lado A", "riel GND de arriba").replace("riel GND lado J", "riel GND de abajo")
    return n


def pos(h):
    fila, col = layouts.orificio(h)
    return layouts.FILA_X[fila], col


def largo_puente(p):
    (y0, c0), (y1, c1) = pos(p["de"]), pos(p["a"])
    cm = (abs(c1 - c0) + abs(y1 - y0)) * 0.254
    return math.ceil((cm + 1.6) * 2) / 2


def largo_externo(e):
    base = e["disp"].split("_", 1)[-1] if e["disp"].split("_")[0] in ("acel", "luz", "pir", "puerta") else e["disp"]
    return LARGO_EXTERNO.get(base, 15)


def generar(caja):
    lay = layouts.LAYOUTS[CAJAS[caja]]
    filas, tot = [], defaultdict(lambda: [0, 0.0])
    for p in lay["puentes"]:
        L = largo_puente(p)
        filas.append(("puente", impreso(p["de"]), impreso(p["a"]), UTP[p["color"]], L, nota_impresa(p["nota"])))
    for e in lay["externos"]:
        L = largo_externo(e)
        nota = e.get("nota", "")
        if L == 0:
            nota = (nota + " Usa el cable propio del MC-38: no se corta cable.").strip()
        filas.append(("a pieza", f'{e["disp"]}.{e["pin"]}', impreso(e["orificio"]), UTP[e["color"]], L, nota_impresa(nota)))
    for _, _, _, c, L, _ in filas:
        if L:
            tot[c][0] += 1
            tot[c][1] += L
    out = [f"# Cables de la caja {caja}", "",
           f"{lay['titulo']}. Largos estimados desde la distancia entre orificios; los de pieza externa son supuestos "
           "(ajustar al armar).", "",
           "**Letras de fila como vienen impresas en la protoboard y en la imagen de Fritzing**, con el USB de los "
           "NodeMCU hacia la izquierda: J arriba, A abajo. Rieles: arriba +5V (línea roja) y GND (línea azul); "
           "abajo GND (línea azul) y +3V3 (línea roja). Los 4 rieles son continuos de punta a punta.", "",
           "| # | Tipo | De | A | Cable | Largo (cm) | Para qué |", "|---|---|---|---|---|---|---|"]
    for i, (t, a, b, c, L, n) in enumerate(filas, 1):
        out.append(f"| {i} | {t} | {a} | {b} | {c} | {L:g} | {n.replace('|', '/')} |")
    out += ["", "## Totales por cable", "", "| Cable | Cantidad | Largo total (cm) |", "|---|---|---|"]
    for c, (n, L) in sorted(tot.items()):
        out.append(f"| {c} | {n} | {L:g} |")
    out.append(f"| **Total** | **{sum(v[0] for v in tot.values())}** | **{sum(v[1] for v in tot.values()):g}** |")
    (SALIDA / f"lista_cables_{caja}.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    return filas, tot


if __name__ == "__main__":
    gran = defaultdict(lambda: [0, 0.0])
    for caja in CAJAS:
        _, tot = generar(caja)
        for c, (n, L) in tot.items():
            gran[c][0] += n
            gran[c][1] += L
        print("ok", caja)
    print("\nTOTAL 3 cajas")
    for c, (n, L) in sorted(gran.items()):
        print(f"  {c:22s} {n:3d} cables  {L / 100:5.2f} m")
    print(f"  {'':22s} {sum(v[0] for v in gran.values()):3d} cables  {sum(v[1] for v in gran.values()) / 100:5.2f} m")
