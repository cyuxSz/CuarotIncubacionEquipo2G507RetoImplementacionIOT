"""Protoboard (400 o 830 puntos, 1 o 2 NodeMCU): chequeo de conexiones, dibujo (SVG/PNG) y tablas (MD).

Uso (desde la raiz del proyecto):
    uv run --no-project --python 3.12 --with matplotlib python hardware/breadboard/protoboard.py [nodo ...]

Las distribuciones viven en layouts.py. Este script:
  1. valida que cada orificio exista, se use una sola vez y no quede bajo el NodeMCU;
  2. calcula las redes electricas (tiras de 5, rieles, puentes) y las compara con la red esperada;
  3. genera <nodo>_protoboard.svg/.png y <nodo>_protoboard.md.
Sale con codigo 1 si algun chequeo falla.
"""
import math
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, Rectangle  # noqa: E402

from layouts import (LAYOUTS, NODEMCU_LADO_A, NODEMCU_LADO_J, NODEMCU_CUERPO, PASO, placas, puntos,  # noqa: E402
                     FILA_X as X, columnas as cols, orificio as parse)

FILAS = "abcdefghij"
RIELES = {"A_GND": "GND", "A_5V": "5V", "J_3V3": "3V3", "J_GND": "GND"}
COLORES = {"rojo": "#d62728", "naranja": "#ff7f0e", "negro": "#222222", "amarillo": "#e5c100",
           "azul": "#1f5fbf", "verde": "#2ca02c", "blanco": "#f4f4f4", "gris": "#8c8c8c",
           "cafe": "#8c564b", "morado": "#7b3fa0"}
SALIDA = Path(__file__).parent


# ── orificios ────────────────────────────────────────────────────────────────
def tira(h, lay=None):
    fila, col = parse(h)
    if fila in RIELES:
        corte = (lay or {}).get("rieles_partidos")
        return fila if not corte else f"{fila}{'_izq' if col < corte else '_der'}"
    return f"{'S' if fila in 'abcde' else 'I'}{col}"


def xy(h):
    fila, col = parse(h)
    return X[fila] * PASO, -col * PASO


def bajo_nodemcu(h, lay):
    fila, col = parse(h)
    c0, c1 = NODEMCU_CUERPO["columnas"]
    return fila in "bcdefghi" and any(c0 + m["col0"] - 1 <= col <= c1 + m["col0"] - 1 for m in placas(lay))


def es_pin_nodemcu(h, lay):
    fila, col = parse(h)
    return any((fila == "b" and col - m["col0"] + 1 in NODEMCU_LADO_A) or
               (fila == "i" and col - m["col0"] + 1 in NODEMCU_LADO_J) for m in placas(lay))


def es_nodemcu(nombre, lay):
    return nombre.split(".")[0] in {m["nombre"] for m in placas(lay)}


# ── chequeos ─────────────────────────────────────────────────────────────────
def terminales(lay):
    """Lista (dispositivo.pin, orificio) de todo lo que entra en la protoboard."""
    t = []
    for m in placas(lay):
        for col, nombre in NODEMCU_LADO_A.items():
            t.append((f"{m['nombre']}.{nombre}", f"b{col + m['col0'] - 1}"))
        for col, nombre in NODEMCU_LADO_J.items():
            t.append((f"{m['nombre']}.{nombre}", f"i{col + m['col0'] - 1}"))
    for c in lay["componentes"]:
        for pin, h in c["pines"].items():
            t.append((f"{c['ref']}.{pin}", h))
    for e in lay["externos"]:
        t.append((f"{e['disp']}.{e['pin']}", e["orificio"]))
    return t


def chequear(lay):
    errores = []
    usados = defaultdict(list)
    for nombre, h in terminales(lay):
        usados[h].append(nombre)
    for p in lay["puentes"]:
        usados[p["de"]].append("puente")
        usados[p["a"]].append("puente")
    for h, quien in usados.items():
        fila, col = parse(h)
        if not (1 <= col <= cols(lay)) or (fila not in RIELES and fila not in FILAS):
            errores.append(f"orificio inexistente {h}")
        if len(quien) > 1 and not (fila in RIELES):
            errores.append(f"orificio {h} usado {len(quien)} veces: {quien}")
        if bajo_nodemcu(h, lay) and not es_pin_nodemcu(h, lay):
            errores.append(f"orificio {h} queda bajo el NodeMCU ({quien})")
    # rieles: dos cosas en el mismo punto del mismo riel tampoco
    for h, quien in usados.items():
        if parse(h)[0] in RIELES and len(quien) > 1:
            errores.append(f"punto de riel {h} usado {len(quien)} veces: {quien}")

    # redes: union-find sobre tiras
    padre = {}

    def raiz(a):
        padre.setdefault(a, a)
        while padre[a] != a:
            padre[a] = padre[padre[a]]
            a = padre[a]
        return a

    def unir(a, b):
        padre[raiz(a)] = raiz(b)

    for p in lay["puentes"]:
        unir(tira(p["de"], lay), tira(p["a"], lay))
    # conexiones internas del NodeMCU: pines con el mismo nombre (GND, 3V3)
    por_nombre = defaultdict(list)
    for nombre, h in terminales(lay):
        if es_nodemcu(nombre, lay):
            por_nombre[nombre].append(tira(h, lay))
    for tiras in por_nombre.values():
        for t in tiras[1:]:
            unir(tiras[0], t)

    redes = defaultdict(set)
    for nombre, h in terminales(lay):
        redes[raiz(tira(h, lay))].add(nombre)
    calculadas = {frozenset(r) for r in redes.values()
                  if len({n for n in r}) > 1 and not all(es_nodemcu(n, lay) for n in r)}
    esperadas = {frozenset(m) for m in lay["redes"].values()}
    for r in esperadas - calculadas:
        errores.append(f"red esperada no encontrada: {sorted(r)}")
    for r in calculadas - esperadas:
        errores.append(f"red inesperada: {sorted(r)}")
    return errores, redes


def ruta(p):
    """Puente recto, o en escuadra por un carril (en pasos) si el puente lo indica."""
    (xa, ya), (xb, yb) = xy(p["de"]), xy(p["a"])
    if "carril" not in p:
        return [xa, xb], [ya, yb]
    xc = p["carril"] * PASO
    return [xa, xc, xc, xb], [ya, ya, yb, yb]


# ── dibujo ───────────────────────────────────────────────────────────────────
def dibujar(nodo, lay):
    COLS = cols(lay)
    fig, ax = plt.subplots(figsize=(8.5, 11 * max(1.0, COLS / 30)))
    ax.set_aspect("equal")
    ax.axis("off")
    x0, x1 = (X["A_GND"] - 1.3) * PASO, (X["J_3V3"] + 1.3) * PASO
    ax.add_patch(Rectangle((x0, -(COLS + 1.2) * PASO), x1 - x0, (COLS + 0.4) * PASO,
                           fc="#fbfbf7", ec="#999999", lw=0.8))
    ax.add_patch(Rectangle((4.6 * PASO, -(COLS + 0.8) * PASO), 1.8 * PASO, (COLS - 0.6) * PASO,
                           fc="#e6e6e0", ec="none"))
    # rieles
    for riel, color in (("A_GND", "#1f5fbf"), ("A_5V", "#d62728"), ("J_3V3", "#ff7f0e"), ("J_GND", "#1f5fbf")):
        x = X[riel] * PASO
        ax.plot([x, x], [-0.5 * PASO, -(COLS + 0.5) * PASO], color=color, lw=0.6, alpha=0.6)
        ax.text(x, 0.6 * PASO, RIELES[riel], ha="center", va="bottom", fontsize=6, color=color, rotation=90)
        for c in range(1, COLS + 1):
            ax.add_patch(Rectangle((x - 0.35, -c * PASO - 0.35), 0.7, 0.7, fc="#555555", ec="none"))
    # orificios y numeracion
    for c in range(1, COLS + 1):
        for f in FILAS:
            x, y = xy(f"{f}{c}")
            ax.add_patch(Rectangle((x - 0.35, y - 0.35), 0.7, 0.7, fc="#555555", ec="none"))
        ax.text((X["A_GND"] - 0.9) * PASO, -c * PASO, str(c), ha="right", va="center", fontsize=5.5)
        ax.text((X["J_3V3"] + 0.9) * PASO, -c * PASO, str(c), ha="left", va="center", fontsize=5.5)
    for f in FILAS:
        ax.text(X[f] * PASO, 0.4 * PASO, f, ha="center", va="bottom", fontsize=7, weight="bold")
    # NodeMCU (uno o dos)
    for m in placas(lay):
        d = m["col0"] - 1
        ax.add_patch(Rectangle(((1 - 0.6) * PASO, -(NODEMCU_CUERPO["borde_antena"] + d) * PASO),
                               (10 - 1 + 1.2) * PASO,
                               (NODEMCU_CUERPO["borde_antena"] - NODEMCU_CUERPO["borde_usb"]) * PASO,
                               fc="#2b5d8a", ec="#123", alpha=0.25, lw=0.8))
        ax.text(5.5 * PASO, -(9 + d) * PASO, f"{m['nombre']}\n(Amica, vista superior)", ha="center",
                va="center", fontsize=7, color="#123", rotation=90)
        ax.add_patch(Rectangle((3.5 * PASO, -(NODEMCU_CUERPO["borde_usb"] + d + 0.2) * PASO), 4 * PASO,
                               1.6 * PASO, fc="#bbbbbb", ec="#444", lw=0.6))
        ax.text(5.5 * PASO, -(NODEMCU_CUERPO["borde_usb"] + d - 0.6) * PASO, "micro-USB", ha="center",
                va="center", fontsize=5)
        for col, nombre in NODEMCU_LADO_A.items():
            x, y = xy(f"b{col + d}")
            ax.add_patch(Circle((x, y), 0.6, fc="#c9a227", ec="#555", lw=0.3))
            ax.text(x + 0.9, y + 0.9, nombre, ha="left", va="bottom", fontsize=3.6, color="#123")
        for col, nombre in NODEMCU_LADO_J.items():
            x, y = xy(f"i{col + d}")
            ax.add_patch(Circle((x, y), 0.6, fc="#c9a227", ec="#555", lw=0.3))
            ax.text(x - 0.9, y + 0.9, nombre, ha="right", va="bottom", fontsize=3.6, color="#123")
    corte = lay.get("rieles_partidos")
    if corte:
        for riel in ("A_GND", "A_5V", "J_3V3", "J_GND"):
            x = X[riel] * PASO
            ax.plot([x - 0.8, x + 0.8], [-(corte - 0.5) * PASO] * 2, color="#b03030", lw=1.2, zorder=5)
        ax.text((X["J_3V3"] + 2.4) * PASO, -(corte - 0.5) * PASO, "rieles partidos", fontsize=5,
                color="#b03030", va="center")
    # puentes
    for p in lay["puentes"]:
        xs, ys = ruta(p)
        col = COLORES[p["color"]]
        ax.plot(xs, ys, color="#555" if p["color"] == "blanco" else col,
                lw=2.6 if p["color"] == "blanco" else 2.0, solid_capstyle="round", zorder=4)
        if p["color"] == "blanco":
            ax.plot(xs, ys, color=col, lw=1.6, solid_capstyle="round", zorder=4)
    # componentes
    for c in lay["componentes"]:
        pts = [xy(h) for h in c["pines"].values()]
        if c["tipo"] == "R":
            (xa, ya), (xb, yb) = pts
            ax.plot([xa, xb], [ya, yb], color="#777", lw=0.8, zorder=5)
            xm, ym = (xa + xb) / 2, (ya + yb) / 2
            ang = math.degrees(math.atan2(yb - ya, xb - xa))
            ax.add_patch(Rectangle((xm - 2.6, ym - 0.9), 5.2, 1.8, angle=0, rotation_point="center",
                                   fc="#d8c08a", ec="#6b5a2e", lw=0.6, zorder=6,
                                   transform=matplotlib.transforms.Affine2D().rotate_deg_around(xm, ym, ang)
                                   + ax.transData))
            ax.text(xm, ym - 1.6, f"{c['ref']} {c['valor']}", ha="center", va="top", fontsize=5, zorder=7)
        elif c["tipo"] == "Q":
            for (x, y), pin in zip(pts, c["pines"]):
                ax.add_patch(Circle((x, y), 0.7, fc="#111", ec="none", zorder=6))
                ax.text(x, y + 1.2, pin, ha="center", va="bottom", fontsize=5, zorder=7)
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            ax.add_patch(Rectangle((min(xs) + 1.6, min(ys) - 1.2), 2.4, max(ys) - min(ys) + 2.4,
                                   fc="#333", ec="none", alpha=0.85, zorder=5))
            ax.text(min(xs) + 4.6, sum(ys) / 3, f"{c['ref']}\n{c['valor']}", ha="left", va="center",
                    fontsize=5, zorder=7)
        elif c["tipo"] == "M":
            xs = [q[0] for q in pts]
            ys = [q[1] for q in pts]
            ax.add_patch(Rectangle((min(xs) - 1.6, min(ys) - 1.6), max(xs) - min(xs) + 3.2, max(ys) - min(ys) + 3.2,
                                   fc="#3d7a3d", ec="#123", alpha=0.35, zorder=5))
            for (x, y), pin in zip(pts, c["pines"]):
                ax.add_patch(Circle((x, y), 0.7, fc="#c9a227", ec="#555", lw=0.3, zorder=6))
                ax.text(x + 1.0, y, pin, ha="left", va="center", fontsize=3.8, zorder=7)
            ax.text(min(xs) - 2.0, (min(ys) + max(ys)) / 2, c["ref"], ha="right", va="center", fontsize=6,
                    rotation=90, zorder=7)
        elif c["tipo"] == "C":
            xm = sum(p[0] for p in pts) / 2
            ym = sum(p[1] for p in pts) / 2
            ax.add_patch(Circle((xm, ym), 3.0, fc="#2a3f8f", ec="#111", lw=0.6, alpha=0.9, zorder=6))
            ax.text(xm, ym, f"{c['ref']}\n220µF", ha="center", va="center", fontsize=4.5, color="w", zorder=7)
            xp, yp = xy(c["pines"]["+"])
            ax.text(xp, yp - 3.6, "+", ha="center", va="center", fontsize=7, weight="bold", zorder=7)
    # cables externos: etiqueta al costado, sin encimarse
    ocupado = {"izq": [], "der": []}
    for e in sorted(lay["externos"], key=lambda e: -xy(e["orificio"])[1]):
        x, y = xy(e["orificio"])
        lado = "izq" if x < 6 * PASO else "der"
        ty = y
        while any(abs(ty - o) < 2.6 for o in ocupado[lado]):
            ty -= 2.6
        ocupado[lado].append(ty)
        tx = (X["A_GND"] - 3.2) * PASO if lado == "izq" else (X["J_3V3"] + 3.2) * PASO
        col = COLORES[e["color"]]
        ax.add_patch(Circle((x, y), 0.9, fc=col, ec="#000", lw=0.5, zorder=8))
        ax.plot([x, tx], [y, ty], color=col if e["color"] != "blanco" else "#999", lw=0.7, ls="--", zorder=3)
        ax.text(tx + (-0.5 if lado == "izq" else 0.5), ty, f"{e['disp']} {e['pin']}",
                ha="right" if lado == "izq" else "left", va="center", fontsize=6)
    ax.set_title(f"{lay['titulo']}: protoboard de {puntos(lay)} puntos "
                 "(borrador, verificar con piezas reales)", fontsize=9)
    ax.text(x0, -(COLS + 2.8) * PASO,
            "Puntos de color = cable Dupont M-H hacia un modulo fuera de la protoboard.  "
            "Lineas gruesas = puentes cortos (UTP solido).\nRieles lado A: 5V (interior) y GND (exterior). "
            "Rieles lado J: 3V3 (interior) y GND (exterior). La GND de ambos lados se une por el NodeMCU.",
            fontsize=5.5, va="top")
    ax.set_xlim(x0 - 45, x1 + 45)
    ax.set_ylim(-(COLS + 6) * PASO, 6 * PASO)
    fig.tight_layout()
    for ext in ("svg", "png"):
        fig.savefig(SALIDA / f"{nodo}_protoboard.{ext}", dpi=220 if ext == "png" else None,
                    bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


# ── tablas ───────────────────────────────────────────────────────────────────
def largo_puente(p):
    xs, ys = ruta(p)
    mm = sum(math.hypot(xs[i + 1] - xs[i], ys[i + 1] - ys[i]) for i in range(len(xs) - 1)) + 8
    return int(5 * math.ceil(mm / 5))


def describir(h):
    fila, col = parse(h)
    if fila in RIELES:
        return f"riel {fila.replace('_', ' ')} (junto a col. {col})"
    return h


def markdown(nodo, lay, errores, redes):
    L = [f"# Nodo `{lay['titulo']}`: circuito en protoboard",
         "",
         f"Generado por `hardware/breadboard/protoboard.py` desde `layouts.py`. Dibujo: "
         f"[{nodo}_protoboard.svg]({nodo}_protoboard.svg) / [png]({nodo}_protoboard.png).",
         "",
         "> **Borrador.** Pinout del NodeMCU Amica, medidas de la protoboard y pinout de los módulos son "
         "nominales: verificar con la serigrafía y el multímetro antes de energizar.",
         "",
         lay.get("intro", ""),
         "",
         "## Convenciones",
         "",
         f"- Protoboard de {puntos(lay)} puntos: columnas 1–{cols(lay)}, filas a–e y f–j "
         "(cada columna de 5 está unida), canal central.",
         "- Rieles del lado A (junto a la fila a): **5V/VIN interior**, **GND exterior**. "
         "Rieles del lado J: **3V3 interior**, **GND exterior**. Rotularlos con cinta.",
         "- NodeMCU Amica con el micro-USB hacia la columna 1; pines en las filas **b** (lado A0/VIN) e **i** "
         "(lado D0–D8). Cada pin deja **un solo orificio libre** (fila a o j).",
         "- Puentes cortos con cable UTP sólido; módulos fuera de la placa con Dupont macho-hembra del kit.",
         "",
         "## Componentes",
         "",
         "| Ref. | Valor | Orificios | Polaridad / nota |",
         "|---|---|---|---|"]
    for c in lay["componentes"]:
        hs = ", ".join(f"{p}: {describir(h)}" for p, h in c["pines"].items())
        L.append(f"| {c['ref']} | {c['valor']} | {hs} | {c.get('nota', '')} |")
    L += ["", "## Conexiones punto a punto", "",
          "| # | De | A | Color | Largo aprox. | Para qué |", "|---|---|---|---|---|---|"]
    n = 1
    for p in lay["puentes"]:
        L.append(f"| {n} | {describir(p['de'])} | {describir(p['a'])} | {p['color']} | "
                 f"{largo_puente(p)} mm | {p['nota']} |")
        n += 1
    for e in lay["externos"]:
        L.append(f"| {n} | {describir(e['orificio'])} | {e['disp']} · {e['pin']} | {e['color']} | "
                 f"{e.get('largo', 'Dupont 10–20 cm')} | {e.get('nota', '')} |")
        n += 1
    L += ["", "## Mapa de orificios", "", "| Orificio | Qué entra |", "|---|---|"]
    mapa = defaultdict(list)
    for nombre, h in terminales(lay):
        mapa[h].append(nombre)
    for p in lay["puentes"]:
        mapa[p["de"]].append(f"puente → {p['a']}")
        mapa[p["a"]].append(f"puente ← {p['de']}")

    def orden(h):
        f, c = parse(h)
        return (c, f)
    for h in sorted(mapa, key=orden):
        if h[0] in "bi" and all(es_nodemcu(x, lay) for x in mapa[h]):
            continue
        L.append(f"| {describir(h)} | {', '.join(mapa[h])} |")
    L += ["", "## Redes resultantes (calculadas)", "", "| Red | Miembros |", "|---|---|"]
    nombres = {frozenset(v): k for k, v in lay["redes"].items()}
    for r in sorted(redes.values(), key=lambda r: sorted(r)):
        r = frozenset(r)
        if len(r) < 2 or all(es_nodemcu(n, lay) for n in r):
            continue
        L.append(f"| {nombres.get(r, '¿?')} | {', '.join(sorted(r))} |")
    L += ["", "## Chequeo automático", ""]
    L.append("✔ Sin errores: todos los orificios existen, ninguno se repite ni queda bajo el NodeMCU, y las "
             "redes coinciden con la red esperada." if not errores else
             "✘ Errores:\n" + "\n".join(f"- {e}" for e in errores))
    L += ["", "## Verificación eléctrica (por escrito, sin simulador)", "", lay["verificacion"].strip(), ""]
    (SALIDA / f"{nodo}_protoboard.md").write_text("\n".join(L), encoding="utf-8")


def main(nodos):
    falla = False
    for nodo in nodos or LAYOUTS:
        lay = LAYOUTS[nodo]
        errores, redes = chequear(lay)
        dibujar(nodo, lay)
        markdown(nodo, lay, errores, redes)
        print(f"{nodo}: {'OK' if not errores else 'ERRORES'}")
        for e in errores:
            print("   ", e)
        falla |= bool(errores)
    sys.exit(1 if falla else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
