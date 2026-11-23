"""Caja dht con el grabado "Cielo de Argos" (diseno 55) en el frente y en los cuatro costados (20-nov).

No toca nodos.py ni los STL lisos: parte de nodo_dht() y resta el grabado (0.4 mm) de la tapa y de la base.
La espalda no se graba (va contra la pared y sobre la cama).

  ARGOS_MODULAR=1 uv run --no-project --python 3.12 --with build123d --with matplotlib python cad/cielo_argos.py

Salida: cad/exports/modular/cielo/nodo_dht_{tapa,base}_cielo.stl y cad/renders/cielo_argos_dht.png
"""
import math
import os
import random
import sys
from pathlib import Path

os.environ["ARGOS_MODULAR"] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import nodos  # noqa: E402
from build123d import Circle, Plane, Polygon, Pos, Rectangle, RectangleRounded, export_stl, extrude, offset  # noqa: E402

HUNDIDO = nodos.DIS["hundido"]      # 0.4 mm, igual que el texto y el ojo
TRAZO = 1.0                         # ancho minimo de linea (boquilla 0.4)
MARGEN_BORDE = 2.5                  # sin grabado junto a las aristas
MARGEN_HUECO = 2.0                  # sin grabado junto a ventanas, leds, rejillas, ojo y letras
FONDO_MIN = 1.4                     # debajo del grabado debe haber material macizo hasta esta profundidad


# ── figuras 2D (coordenadas locales de cada cara) ────────────────────────────
def disco(x, y, r):
    return Pos(x, y) * Circle(r)


def estrella(x, y, R=3.0, r=0.9):
    return Polygon(*[(x + (R if j % 2 == 0 else r) * math.cos(j * math.pi / 4), y + (R if j % 2 == 0 else r) * math.sin(j * math.pi / 4))
                     for j in range(8)], align=None)


def tramo(p, q, w=TRAZO):
    dx, dy = q[0] - p[0], q[1] - p[1]
    d = math.hypot(dx, dy)
    nx, ny = -dy / d * w / 2, dx / d * w / 2
    return Polygon((p[0] - nx, p[1] - ny), (q[0] - nx, q[1] - ny), (q[0] + nx, q[1] + ny), (p[0] + nx, p[1] + ny), align=None)


def arco(cx, cy, r, a0, a1, w=TRAZO, paso=4.0):
    """Arco troceado en tramos cortos: asi un hueco de la cara solo quita el trozo que toca."""
    n = max(2, int(abs(a1 - a0) / paso))
    out = []
    for i in range(n):
        b0, b1 = math.radians(a0 + (a1 - a0) * i / n), math.radians(a0 + (a1 - a0) * (i + 1) / n + 0.3)
        m = 5
        ext = [(cx + (r + w / 2) * math.cos(b0 + (b1 - b0) * k / m), cy + (r + w / 2) * math.sin(b0 + (b1 - b0) * k / m)) for k in range(m + 1)]
        inte = [(cx + (r - w / 2) * math.cos(b0 + (b1 - b0) * k / m), cy + (r - w / 2) * math.sin(b0 + (b1 - b0) * k / m)) for k in range(m, -1, -1)]
        out.append(Polygon(*(ext + inte), align=None))
    return out


def ruta(pts, w=TRAZO, nodo=1.7, trozo=6.0):
    out = []
    for p, q in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(q[0] - p[0], q[1] - p[1]) / trozo))
        for i in range(n):
            a = (p[0] + (q[0] - p[0]) * i / n, p[1] + (q[1] - p[1]) * i / n)
            b = (p[0] + (q[0] - p[0]) * (i + 1.04) / n, p[1] + (q[1] - p[1]) * (i + 1.04) / n)
            out.append(tramo(a, b, w))
    return out + [disco(p[0], p[1], nodo) for p in pts]


def cielo_frente():
    """El diseno 55 tal cual la maqueta (misma semilla): x de -40 a 40, y de 0 a 138.5."""
    rnd = random.Random(77)
    figs = []
    for r in (58, 96, 134):
        figs += arco(60, -20, r, 90, 180)
    est = [(rnd.uniform(-39, 39), rnd.uniform(1, 137)) for _ in range(95)]
    for k, (x, y) in enumerate(est):
        if k % 9 == 0:
            figs.append(estrella(x, y))
        else:
            figs.append(disco(x, y, {0.55: 0.7, 0.7: 0.85, 1.0: 1.1}[rnd.choice((0.55, 0.7, 1.0))]))
    # las estrellas que caen cortadas por ventanas y rejillas se descartan enteras: estas reponen la densidad de la maqueta
    extra = random.Random(78)
    for _ in range(60):
        figs.append(disco(extra.uniform(-37, 37), extra.uniform(3, 135), extra.choice((0.7, 0.85, 1.1))))
    figs += ruta([(-34, 12), (-22, 40), (-33, 60), (-36, 92), (-34, 124), (-12, 134), (22, 133), (35, 112), (36, 70), (24, 48), (34, 22)])
    return figs


def cielo_costado(x0, x1, y0, y1, semilla, fr_ruta, arcos):
    """Mismo lenguaje para una cara lateral: estrellas, una constelacion y arcos de orbita."""
    rnd = random.Random(semilla)
    w, h = x1 - x0, y1 - y0
    figs = []
    for cx, cy, r, a0, a1 in arcos:
        figs += arco(x0 + cx * w, y0 + cy * h, r, a0, a1)
    for k in range(int(w * h * 0.0086)):
        x, y = rnd.uniform(x0 + 1, x1 - 1), rnd.uniform(y0 + 1, y1 - 1)
        figs.append(estrella(x, y, 2.6, 0.85) if k % 9 == 0 else disco(x, y, rnd.choice((0.7, 0.85, 1.1))))
    figs += ruta([(x0 + u * w, y0 + v * h) for u, v in fr_ruta])
    return figs


# ── grabado de una cara ──────────────────────────────────────────────────────
def caras_en(pieza, plano):
    out = []
    for f in pieza.faces():
        if f.geom_type.name != "PLANE" or f.area < 150:
            continue
        nn, c = f.normal_at(), f.center()
        if nn.dot(plano.z_dir) > 0.999 and abs((c - plano.origin).dot(plano.z_dir)) < 0.01:
            out.append(f)
    return out


def caja_local(plano, forma):
    bb = plano.to_local_coords(forma).bounding_box()
    return bb.min.X, bb.max.X, bb.min.Y, bb.max.Y


def grabar_cara(pieza, plano, generar, nombre):
    """Devuelve (pieza grabada, lista de caras 2D grabadas, cajas de las caras) para la cara `plano`."""
    hechas, cajas = [], []
    for cara in caras_en(pieza, plano):
        x0, x1, y0, y1 = caja_local(plano, cara)
        cajas.append((x0, x1, y0, y1))
        if x1 - x0 < 12 or y1 - y0 < 12:
            continue
        permitido = Pos((x0 + x1) / 2, (y0 + y1) / 2) * RectangleRounded(x1 - x0 - 2 * MARGEN_BORDE, y1 - y0 - 2 * MARGEN_BORDE, 2.0)
        for w in cara.inner_wires():
            a0, a1, b0, b1 = caja_local(plano, w)
            permitido -= Pos((a0 + a1) / 2, (b0 + b1) / 2) * Rectangle(a1 - a0 + 2 * MARGEN_HUECO, b1 - b0 + 2 * MARGEN_HUECO)
        figs = generar(x0, x1, y0, y1)
        quitadas = 0
        adentro = plano.z_dir * -1
        for fig in figs:
            try:
                partes = (fig & permitido).faces()
            except Exception:
                partes = []
            unicas = {}
            for g in partes:                               # el recorte a veces devuelve la misma cara repetida
                c = g.center()
                unicas[(round(c.X, 2), round(c.Y, 2), round(g.area, 2))] = g
            partes = list(unicas.values())
            entera = len(partes) == 1 and partes[0].area > 0.97 * fig.area
            if not entera and len(fig.vertices()) != 4 and len(fig.vertices()) != 12:
                continue                                   # estrellas y puntos: enteros o nada (sin medias lunas)
            for g in partes:
                if g.area < 0.9:
                    continue
                try:                                       # se prueba la figura engordada 1 mm: lejos de huecos y letras
                    prueba = offset(g, amount=1.0)
                    area = prueba.area
                except Exception:
                    prueba, area = g, g.area
                hondo = extrude(plano * prueba, amount=FONDO_MIN, dir=adentro)
                if (hondo & pieza).volume < area * FONDO_MIN * 0.995:   # hay un hueco, letra o pared delgada debajo
                    quitadas += 1
                    continue
                hechas.append(g)
        print(f"   {nombre}: cara {x1 - x0:.0f} x {y1 - y0:.0f} mm, {len(hechas)} figuras, {quitadas} descartadas por poco fondo", flush=True)
    for g in hechas:
        pieza -= extrude(plano * g, amount=HUNDIDO, both=True)
    return pieza, hechas, cajas


def main():
    n = nodos.nodo_dht()
    W, H, D = n["W"], n["H"], n["D"]
    tapa0, base0 = n["piezas"]["tapa"], n["piezas"]["base"]
    planos = {
        "frente": (Plane(origin=(0, 0, D), x_dir=(1, 0, 0), z_dir=(0, 0, 1)), lambda *c: cielo_frente()),
        "costado derecho": (Plane(origin=(W / 2, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0)),
                            lambda *c: cielo_costado(*c, 11, [(0.04, 0.3), (0.16, 0.74), (0.3, 0.4), (0.45, 0.7), (0.6, 0.3), (0.76, 0.66), (0.95, 0.4)],
                                                     [(1.0, -0.6, 70, 95, 160)])),
        "costado izquierdo": (Plane(origin=(-W / 2, 0, 0), x_dir=(0, -1, 0), z_dir=(-1, 0, 0)),
                              lambda *c: cielo_costado(*c, 23, [(0.05, 0.62), (0.2, 0.28), (0.36, 0.68), (0.52, 0.34), (0.7, 0.72), (0.84, 0.3), (0.96, 0.6)],
                                                       [(0.0, -0.6, 70, 20, 85)])),
        "cara superior": (Plane(origin=(0, H, 0), x_dir=(-1, 0, 0), z_dir=(0, 1, 0)),
                          lambda *c: cielo_costado(*c, 31, [(0.08, 0.3), (0.3, 0.7), (0.55, 0.36), (0.78, 0.7), (0.93, 0.34)], [(0.5, -0.9, 52, 55, 125)])),
        "cara inferior": (Plane(origin=(0, 0, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0)),
                          lambda *c: cielo_costado(*c, 47, [(0.07, 0.66), (0.28, 0.3), (0.5, 0.66), (0.72, 0.3), (0.93, 0.62)], [(0.5, -0.9, 52, 55, 125)])),
    }
    tapa, base, dibujo = tapa0, base0, {}
    for nombre, (plano, gen) in planos.items():
        if nombre == "frente":
            tapa, hechas, cajas = grabar_cara(tapa, plano, gen, nombre)
            origen = tapa0
        else:
            base, hechas, cajas = grabar_cara(base, plano, gen, nombre)
            origen = base0
        dibujo[nombre] = (plano, hechas, caras_en(origen, plano))

    salida = nodos.SALIDA / "cielo"
    salida.mkdir(parents=True, exist_ok=True)
    ok = True
    for nom, s0, s in (("tapa", tapa0, tapa), ("base", base0, base)):
        solidos = len(s.solids())
        quitado = s0.volume - s.volume
        print(f"{nom}: {solidos} solido(s), valido {s.is_valid}, grabado {quitado:.0f} mm3 "
              f"({quitado / HUNDIDO:.0f} mm2 de dibujo), masa {s.volume / 1000 * nodos.DIS['densidad_petg']:.1f} g")
        ok &= solidos == 1 and s.is_valid
        export_stl(nodos.a_cama(nom, s), str(salida / f"nodo_dht_{nom}_cielo.stl"), tolerance=0.02, angular_tolerance=0.2)
    vista(dibujo)
    sys.exit(0 if ok else 1)


def vista(dibujo):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection

    def tri(plano, cara):
        vs, ts = plano.to_local_coords(cara).tessellate(0.05)
        return [[(vs[i].X, vs[i].Y) for i in t] for t in ts]

    fig = plt.figure(figsize=(15, 11), facecolor="white")
    huecos = {"frente": [0.36, 0.06, 0.28, 0.86], "costado izquierdo": [0.04, 0.06, 0.26, 0.4], "costado derecho": [0.70, 0.06, 0.26, 0.4],
              "cara superior": [0.04, 0.56, 0.26, 0.34], "cara inferior": [0.70, 0.56, 0.26, 0.34]}
    for nombre, (plano, hechas, caras) in dibujo.items():
        ax = fig.add_axes(huecos[nombre])
        lisos = [t for c in caras for t in tri(plano, c)]
        graba = [t for g in hechas for t in tri(plano, plano * g)]
        if nombre.startswith("costado"):      # de pie, como se ven en la caja
            lisos = [[(y, x) for x, y in t] for t in lisos]
            graba = [[(y, x) for x, y in t] for t in graba]
        ax.add_collection(PolyCollection(lisos, facecolors="#e8e4da", edgecolors="#e8e4da", linewidths=0.3))
        ax.add_collection(PolyCollection(graba, facecolors="#8f897a", edgecolors="#8f897a", linewidths=0.3))
        ax.autoscale()
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(nombre, fontsize=12)
    fig.text(0.5, 0.985, "Caja dht con el Cielo de Argos: lo oscuro es el grabado real del STL (0.4 mm); lo blanco son ventanas, rejillas y ranuras",
             ha="center", va="top", fontsize=12)
    destino = nodos.RAIZ / "renders" / "cielo_argos_dht.png"
    fig.savefig(destino, dpi=110)
    print("escrito", destino)


if __name__ == "__main__":
    main()
