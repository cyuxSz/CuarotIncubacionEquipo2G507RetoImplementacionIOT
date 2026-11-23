"""Maqueta 2D de la tapa de la caja dht con varias texturas (20-nov). NO genera piezas: es para elegir.

Dibuja el frente de la tapa a escala (80 x 138.5 mm) con sus elementos reales (ventana de la pantalla, LED, rotulo,
boton, buzzer y persianas) y, alrededor, cada textura como grabado. Los trazos miden 1.0 mm o mas, que es lo que
se puede imprimir con el frente en la cama.

  uv run --no-project --python 3.12 --with matplotlib --with scipy python cad/maqueta_texturas.py

Salida: cad/renders/maqueta_texturas_tapa_dht.png
"""
import math
import random
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.collections import LineCollection, PatchCollection  # noqa: E402
from matplotlib.patches import Arc, Circle, Ellipse, FancyBboxPatch, Polygon, Rectangle  # noqa: E402
from scipy.spatial import Voronoi  # noqa: E402

RAIZ = Path(__file__).resolve().parent
W, H = 80.0, 138.5
TAPA, SURCO, BORDE = "#e9e6de", "#a39f95", "#8d897f"
FIGW, FIGH, AXW, AXH = 19.0, 13.6, 0.185, 0.445
XR = 88.0
PPM = AXW * FIGW * 72 / XR                       # puntos de matplotlib por mm


def lw(mm):
    return mm * PPM


def tapa_base(ax):
    ax.set_xlim(-XR / 2, XR / 2)
    alto = XR * (AXH * FIGH) / (AXW * FIGW)
    ax.set_ylim(-3, alto - 3)
    ax.set_aspect("equal")
    ax.axis("off")
    p = FancyBboxPatch((-W / 2, 0), W, H, boxstyle="round,pad=0,rounding_size=6", fc=TAPA, ec=BORDE, lw=1.2, zorder=1)
    ax.add_patch(p)
    return p


def elementos(ax):
    """Zonas libres de textura y elementos reales de la tapa (medidas del CAD)."""
    def libre(x, y, w, h, r=2.5):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=TAPA, ec="none", zorder=5))
    libre(-33.7, 74.2, 67.4, 42.9)            # ventana + 3.5 mm
    libre(-13, 118.5, 26, 12, 6)              # LED
    libre(-24.5, 64.6, 39.5, 11.4, 4)         # rotulo y ojo con sus rayos
    ax.add_patch(Circle((0, 62), 5.2, fc=TAPA, ec="none", zorder=5))
    ax.add_patch(Circle((-20, 60), 8.0, fc=TAPA, ec="none", zorder=5))
    libre(-28.5, 7.5, 57, 27, 3)              # persianas
    # pantalla
    ax.add_patch(FancyBboxPatch((-30.2, 77.2), 60.4, 36.9, boxstyle="round,pad=0,rounding_size=0.8", fc="#0c0f14",
                                ec="#5d5a53", lw=1.0, zorder=6))
    ax.text(-25, 99, "24.6", color="#dff3ff", fontsize=lw(11) / 1.0, fontweight="bold", va="center", zorder=7)
    ax.text(5, 103, "°C", color="#dff3ff", fontsize=lw(4.5), va="center", zorder=7)
    ax.text(-25, 84, "58 % HR", color="#dff3ff", fontsize=lw(5), va="center", zorder=7)
    ax.text(-25, 110.3, "EN LINEA", color="#9fc3d6", fontsize=lw(2.6), va="center", zorder=7)
    # LED, boton, buzzer
    ax.add_patch(Circle((-6, 124.5), 2.6, fc="#37b24d", ec="#2b8a3e", lw=0.8, zorder=7))
    ax.add_patch(Circle((6, 124.5), 2.6, fc="#f03e3e", ec="#c92a2a", lw=0.8, zorder=7))
    ax.add_patch(Circle((0, 62), 2.2, fc="#d6d2c8", ec=BORDE, lw=0.9, zorder=7))
    for a in range(0, 360, 60):
        ax.add_patch(Circle((-20 + 3.5 * math.cos(math.radians(a)), 60 + 3.5 * math.sin(math.radians(a))), 0.9,
                            fc="#4a4740", ec="none", zorder=7))
    ax.add_patch(Circle((-20, 60), 0.9, fc="#4a4740", ec="none", zorder=7))
    # rotulo y ojo
    ax.text(-4, 71, "Argos", color=BORDE, fontsize=lw(4.2), fontweight="bold", va="center", ha="left", zorder=7)
    ojo(ax, -15, 69.1, 14.0, BORDE, TAPA, 7)
    # persianas
    for y in (11, 16, 21, 26, 31):
        for sx in (-1, 1):
            ax.add_patch(Rectangle((sx * 14 - 12, y - 0.8), 24, 1.6, fc="#4a4740", ec="none", zorder=7))


def lente(cx, cy, ancho, alto, giro=0.0, n=40):
    """Almendra del logotipo (dos arcos de circulo) como lista de puntos."""
    a, h = ancho / 2, alto / 2
    rad = (a * a + h * h) / (2 * h)
    th = math.asin(a / rad)
    arriba = [(rad * math.sin(-th + 2 * th * k / n), rad * math.cos(-th + 2 * th * k / n) - (rad - h)) for k in range(n + 1)]
    pts = arriba + [(-x, -y) for x, y in arriba]
    c, s = math.cos(giro), math.sin(giro)
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts]


def ojo(ax, cx, cy, ancho, color, fondo, z, rayos=True, clip=None):
    """Ojo de Argos como en el logotipo: almendra, pupila cuadrada y tres rayos (mismas cotas que cad/nodos.py)."""
    alto = ancho * 0.447
    pup = alto - 2.0 - 1.7
    ps = [Polygon(lente(cx, cy, ancho, alto), fc=color, ec="none", zorder=z),
          Polygon(lente(cx, cy, ancho - 2.2, alto - 2.0), fc=fondo, ec="none", zorder=z),
          Rectangle((cx - pup / 2, cy - pup / 2), pup, pup, fc=color, ec="none", zorder=z)]
    if rayos:
        for x, y, g in ((0, alto / 2 + 2.07, 0), (-0.213 * ancho, alto / 2 + 1.57, 25), (0.213 * ancho, alto / 2 + 1.57, -25)):
            c, s = math.cos(math.radians(g)), math.sin(math.radians(g))
            esq = [(-0.5, -1.0), (0.5, -1.0), (0.5, 1.0), (-0.5, 1.0)]
            ps.append(Polygon([(cx + x + u * c - v * s, cy + y + u * s + v * c) for u, v in esq], fc=color, ec="none", zorder=z))
    for p in ps:
        ax.add_patch(p)
        if clip is not None:
            p.set_clip_path(clip)


# ── texturas ────────────────────────────────────────────────────────────────
def filotaxia(ax, clip):
    ps = []
    for n in range(1, 1100):
        r, th = 2.35 * math.sqrt(n), n * math.radians(137.508)
        ps.append(Circle((r * math.cos(th), 52 + r * math.sin(th)), 0.5 + 0.011 * r))
    c = PatchCollection(ps, fc=SURCO, ec="none", zorder=3)
    ax.add_collection(c)
    c.set_clip_path(clip)


def voronoi(ax, clip):
    rng = np.random.default_rng(7)
    pts = np.column_stack([rng.uniform(-55, 55, 95), rng.uniform(-15, 155, 95)])
    v = Voronoi(pts)
    seg = [[v.vertices[a], v.vertices[b]] for a, b in v.ridge_vertices if a >= 0 and b >= 0]
    c = LineCollection(seg, colors=SURCO, linewidths=lw(1.1), capstyle="round", zorder=3)
    ax.add_collection(c)
    c.set_clip_path(clip)


def topografia(ax, clip):
    rng = np.random.default_rng(11)
    x, y = np.meshgrid(np.linspace(-42, 42, 220), np.linspace(-2, 141, 360))
    z = np.zeros_like(x)
    for _ in range(7):
        cx, cy, s, a = rng.uniform(-40, 40), rng.uniform(0, 140), rng.uniform(16, 34), rng.uniform(0.6, 1.4)
        z += a * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * s * s))
    cs = ax.contour(x, y, z, levels=13, colors=SURCO, linewidths=lw(1.0), zorder=3)
    try:
        cs.set_clip_path(clip)
    except Exception:
        for col in cs.collections:
            col.set_clip_path(clip)


def circuito(ax, clip):
    rnd = random.Random(5)
    dirs = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
    paso = 4.0
    for _ in range(46):
        x, y = rnd.randrange(-10, 11) * paso, rnd.randrange(0, 35) * paso
        d = rnd.choice((0, 2, 4, 6))
        pts = [(x, y)]
        for _ in range(rnd.randint(2, 4)):
            n = rnd.randint(2, 6)
            x, y = x + dirs[d][0] * n * paso, y + dirs[d][1] * n * paso
            pts.append((x, y))
            d = (d + rnd.choice((-1, 1))) % 8
        ln, = ax.plot(*zip(*pts), color=SURCO, lw=lw(1.0), solid_joinstyle="round", solid_capstyle="round", zorder=3)
        ln.set_clip_path(clip)
        for px, py in (pts[0], pts[-1]):
            for r, col in ((1.7, SURCO), (0.65, TAPA)):
                c = Circle((px, py), r, fc=col, ec="none", zorder=4)
                ax.add_patch(c)
                c.set_clip_path(clip)


def truchet(ax, clip):
    rnd = random.Random(3)
    t = 8.0
    for i in range(-6, 6):
        for j in range(0, 19):
            x0, y0 = i * t, j * t - 4
            cs = ((x0, y0, 0), (x0 + t, y0 + t, 180)) if rnd.random() < 0.5 else ((x0 + t, y0, 90), (x0, y0 + t, 270))
            for cx, cy, a in cs:
                arc = Arc((cx, cy), t, t, angle=0, theta1=a, theta2=a + 90, color=SURCO, lw=lw(1.1), zorder=3)
                ax.add_patch(arc)
                arc.set_clip_path(clip)


def binario(ax, clip):
    bits = "".join(f"{ord(ch):08b}" for ch in "ARGOS ")
    k, px, py = 0, 4.6, 4.3
    ps = []
    for fila in range(34):
        y = 137 - fila * py
        for col in range(17):
            x = -36.8 + col * px
            if bits[k % len(bits)] == "1":
                ps.append(FancyBboxPatch((x - 1.7, y - 0.8), 3.4, 1.6, boxstyle="round,pad=0,rounding_size=0.8"))
            else:
                ps.append(Circle((x, y), 0.75))
            k += 1
    c = PatchCollection(ps, fc=SURCO, ec="none", zorder=3)
    ax.add_collection(c)
    c.set_clip_path(clip)


def colonias(ax, clip):
    rnd = random.Random(21)
    puestos = []
    for _ in range(6000):
        r = rnd.choice((1.1, 1.3, 1.6, 2.2, 3.0, 4.2, 5.6))
        x, y = rnd.uniform(-40, 40), rnd.uniform(0, 139)
        if all((x - a) ** 2 + (y - b) ** 2 > (r + c + 1.1) ** 2 for a, b, c in puestos):
            puestos.append((x, y, r))
    for x, y, r in puestos:
        if r >= 3.0:
            ps = [Circle((x, y), r, fc="none", ec=SURCO, lw=lw(1.0), zorder=3), Circle((x, y), r * 0.3, fc=SURCO, ec="none", zorder=3)]
        else:
            ps = [Circle((x, y), r, fc=SURCO, ec="none", zorder=3)]
        for p in ps:
            ax.add_patch(p)
            p.set_clip_path(clip)


def mirada(ax, clip):
    """Ondas que salen del ojo de Argos."""
    for r in np.arange(8.5, 150, 4.6):
        c = Circle((-15, 69.1), r, fc="none", ec=SURCO, lw=lw(1.0), zorder=3)
        ax.add_patch(c)
        c.set_clip_path(clip)


def panal_fundido(ax, clip):
    r0, trazo = 3.3, 1.0
    dx = math.sqrt(3) * r0 + trazo
    dy = dx * math.sqrt(3) / 2
    ps = []
    for j in range(0, 30):
        for i in range(-8, 9):
            x, y = i * dx + (dx / 2 if j % 2 else 0), j * dy
            r = r0 * max(0.0, 1 - y / 150) ** 1.6
            if r > 0.55:
                ps.append(Polygon([(x + r * math.cos(math.radians(30 + 60 * k)), y + r * math.sin(math.radians(30 + 60 * k)))
                                   for k in range(6)]))
    c = PatchCollection(ps, fc=SURCO, ec="none", zorder=3)
    ax.add_collection(c)
    c.set_clip_path(clip)


OPCIONES = [
    ("Sin textura (como está hoy)", None),
    ("7. Filotaxia: la espiral de las plantas", filotaxia),
    ("8. Células (Voronoi)", voronoi),
    ("9. Curvas de nivel", topografia),
    ("10. Circuito impreso", circuito),
    ("11. Laberinto de arcos", truchet),
    ("12. «ARGOS» en binario", binario),
    ("13. Colonias de cultivo", colonias),
    ("14. La mirada de Argos", mirada),
    ("15. Panal que se desvanece", panal_fundido),
]


def main():
    fig = plt.figure(figsize=(FIGW, FIGH), facecolor="white")
    for k, (titulo, fn) in enumerate(OPCIONES):
        col, fila = k % 5, k // 5
        ax = fig.add_axes([0.012 + col * 0.198, 0.50 - fila * 0.49, AXW, AXH])
        clip = tapa_base(ax)
        if fn:
            fn(ax, clip)
        elementos(ax)
        ax.text(0, 141.5, titulo, ha="center", va="bottom", fontsize=12.5)
    fig.text(0.5, 0.985, "Tapa de la caja dht con cada textura (maqueta a escala; el grabado real es de 0.4 mm, más sutil que aquí)",
             ha="center", va="top", fontsize=13)
    salida = RAIZ / "renders" / "maqueta_texturas_tapa_dht.png"
    fig.savefig(salida, dpi=100)
    print("escrito", salida)


if __name__ == "__main__":
    main()
