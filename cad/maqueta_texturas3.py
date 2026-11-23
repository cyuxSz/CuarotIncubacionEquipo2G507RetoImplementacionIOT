"""Tercera tanda (20-nov): 50 disenos mas para la tapa, ahora COMPUESTOS con los elementos de la tapa (la pantalla
como pupila, como chip, como roca de un jardin zen...) y no solo patrones repetidos. Solo maqueta: no genera piezas.

  uv run --no-project --python 3.12 --with matplotlib --with scipy python cad/maqueta_texturas3.py

Salida: cad/renders/maqueta_texturas_tapa_dht_4.png ... _8.png (10 tapas cada una).
"""
import math
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402
from matplotlib.patches import Arc, Circle, FancyBboxPatch, PathPatch, Polygon, Rectangle, Wedge  # noqa: E402
from matplotlib.textpath import TextPath  # noqa: E402
from matplotlib.transforms import Affine2D  # noqa: E402
from scipy.spatial import Voronoi  # noqa: E402

from maqueta_texturas import AXH, AXW, FIGH, FIGW, PPM, RAIZ, SURCO, TAPA, elementos, lente, lw, ojo, tapa_base  # noqa: E402
from maqueta_texturas2 import coleccion, empacar, linea, parche  # noqa: E402

OJO = (-15.0, 69.1)
VC = (0.0, 95.65)                       # centro de la ventana
VW, VH = 30.2, 18.45                    # medios lados de la ventana
X, Y = np.meshgrid(np.linspace(-42, 42, 250), np.linspace(-2, 141, 420))
RECTS = [(-30.2, 30.2, 77.2, 114.1), (-13, 13, 118.5, 130.5), (-24.5, 15, 64.6, 76.0), (-28.5, 28.5, 7.5, 34.5)]
CIRCS = [(0, 62, 5.2), (-20, 60, 8.0)]


def d_rect(x0, x1, y0, y1):
    return np.hypot(np.maximum(np.maximum(x0 - X, X - x1), 0), np.maximum(np.maximum(y0 - Y, Y - y1), 0))


def distancias():
    return [d_rect(*r) for r in RECTS] + [np.maximum(np.hypot(X - cx, Y - cy) - r, 0) for cx, cy, r in CIRCS]


def centros_y():
    return [(r[2] + r[3]) / 2 for r in RECTS] + [c[1] for c in CIRCS]


def curvas(ax, clip, z, niveles, mm=1.0):
    cs = ax.contour(X, Y, z, levels=niveles, colors=SURCO, linewidths=lw(mm), linestyles="solid", zorder=3)
    try:
        cs.set_clip_path(clip)
    except Exception:
        for c in cs.collections:
            c.set_clip_path(clip)


def relleno(ax, clip, x, y, z, niveles):
    cs = ax.contourf(x, y, z, levels=niveles, colors=[SURCO], zorder=3)
    try:
        cs.set_clip_path(clip)
    except Exception:
        for c in cs.collections:
            c.set_clip_path(clip)


def segmentos(ax, clip, seg, mm=1.0):
    c = LineCollection(seg, colors=SURCO, linewidths=lw(mm), capstyle="round", zorder=3)
    ax.add_collection(c)
    c.set_clip_path(clip)


def texto(ax, clip, x, y, s, mm, **kw):
    t = ax.text(x, y, s, color=SURCO, fontsize=mm * PPM / 0.72, zorder=3, **{"ha": "center", "va": "center", **kw})
    t.set_clip_path(clip)
    t.set_clip_on(True)


def borde_ventana(th, margen=4.2):
    """Punto del contorno de la ventana (con margen) en la direccion th desde su centro."""
    c, s = math.cos(th), math.sin(th)
    k = min((VW + margen) / max(abs(c), 1e-6), (VH + margen) / max(abs(s), 1e-6))
    return VC[0] + k * c, VC[1] + k * s


# ════ lamina 4: la pantalla es el ojo ═══════════════════════════════════════
def parpados(ax, clip):
    for k in range(8):
        pts = lente(VC[0], VC[1], 96 + 24 * k, 60 + 15 * k)
        parche(ax, clip, Polygon(pts, fc="none", ec=SURCO, lw=lw(1.0 + 0.12 * k), zorder=3))


def iris(ax, clip):
    rnd = random.Random(1)
    for k in range(260):
        th = 2 * math.pi * k / 260 + rnd.uniform(-0.01, 0.01)
        x0, y0 = borde_ventana(th, 4.4)
        largo = rnd.choice((4, 6, 9, 13, 19, 28, 44))
        linea(ax, clip, [x0, x0 + largo * math.cos(th)], [y0, y0 + largo * math.sin(th)], 1.0)


def ecos(ax, clip):
    for k in range(1, 24):
        pad = 1.2 + 4.4 * k
        parche(ax, clip, FancyBboxPatch((VC[0] - VW, VC[1] - VH), 2 * VW, 2 * VH, boxstyle=f"round,pad={pad},rounding_size={pad + 0.8}",
                                        fc="none", ec=SURCO, lw=lw(1.0), zorder=3))


def zen(ax, clip):
    curvas(ax, clip, np.minimum.reduce(distancias()), np.arange(4.6, 70, 4.4))


def corriente(ax, clip):
    psi = Y.copy()
    for d, cy in zip(distancias(), centros_y()):
        psi -= (Y - cy) * np.exp(-(d / 8.0) ** 2)
    curvas(ax, clip, psi, np.arange(-2, 142, 3.7))


def chip(ax, clip):
    rnd = random.Random(6)
    lados = [((VW + 3.9, y), (1, 0), (0, 1 if y > VC[1] else -1)) for y in np.arange(79.5, 113, 4.2)] + \
            [((-VW - 3.9, y), (-1, 0), (0, 1 if y > VC[1] else -1)) for y in np.arange(79.5, 113, 4.2)] + \
            [((x, VC[1] + VH + 3.9), (0, 1), (1 if x > 0 else -1, 0)) for x in np.arange(-27.3, 28, 4.2)] + \
            [((x, VC[1] - VH - 3.9), (0, -1), (1 if x > 0 else -1, 0)) for x in np.arange(-27.3, 28, 4.2)]
    for (x, y), n, t in lados:
        a, b, c = rnd.uniform(1.5, 3.5), rnd.choice((0, 3, 6, 10, 16)), rnd.uniform(3, 45)
        p = [(x, y), (x + n[0] * a, y + n[1] * a)]
        p.append((p[-1][0] + (n[0] + t[0]) * b, p[-1][1] + (n[1] + t[1]) * b))
        p.append((p[-1][0] + n[0] * c, p[-1][1] + n[1] * c))
        linea(ax, clip, [q[0] for q in p], [q[1] for q in p], 1.0)
        parche(ax, clip, Circle(p[-1], 1.5, fc=SURCO, ec="none", zorder=4))
        parche(ax, clip, Circle(p[-1], 0.6, fc=TAPA, ec="none", zorder=4))


def sol_naciente(ax, clip):
    for a in range(0, 360, 10):
        parche(ax, clip, Wedge(VC, 190, a, a + 4.6, fc=SURCO, ec="none", zorder=3))


def plano(ax, clip):
    def cota(p, q, s, giro=0):
        ax.annotate("", p, q, arrowprops=dict(arrowstyle="<->", color=SURCO, lw=lw(0.9), shrinkA=0, shrinkB=0), zorder=3)
        texto(ax, clip, (p[0] + q[0]) / 2 + (2.6 if giro else 0), (p[1] + q[1]) / 2 + (0 if giro else 2.6), s, 2.6, rotation=giro)
    for y in np.arange(4, 138, 9.5):                       # ejes de simetria en trazo y punto
        linea(ax, clip, [0, 0], [y, y + 6], 0.9)
        parche(ax, clip, Circle((0, y + 7.6), 0.5, fc=SURCO, ec="none", zorder=3))
    for x in np.arange(-38, 38, 9.5):
        linea(ax, clip, [x, x + 6], [VC[1], VC[1]], 0.9)
    cota((-36.6, 77.2), (-36.6, 114.1), "36.9", 90)
    cota((-30.2, 71.6), (30.2, 71.6), "60.4")
    cota((-40, 3.2), (40, 3.2), "80")
    cota((36.6, 0), (36.6, 138.5), "138.5", 90)
    for x, y in ((-36, 134), (36, 134), (-36, 40), (36, 40), (-36, 58), (36, 58)):
        linea(ax, clip, [x - 2.4, x + 2.4], [y, y], 0.9)
        linea(ax, clip, [x, x], [y - 2.4, y + 2.4], 0.9)
    texto(ax, clip, 24, 124.5, "2 × Ø5", 2.6)
    texto(ax, clip, 17, 60, "ARGOS-DHT-01", 2.4)
    texto(ax, clip, 20, 53, "ESC 1:1 · PETG", 2.4)
    texto(ax, clip, 20, 46, "R6 · e = 2.5", 2.4)


def radar(ax, clip):
    for r in np.arange(11, 160, 9.2):
        parche(ax, clip, Circle(OJO, r, fc="none", ec=SURCO, lw=lw(1.0), zorder=3))
    for a in range(0, 180, 30):
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        linea(ax, clip, [OJO[0] - 160 * c, OJO[0] + 160 * c], [OJO[1] - 160 * s, OJO[1] + 160 * s], 0.9)
    parche(ax, clip, Wedge(OJO, 160, -48, -22, fc=SURCO, ec="none", alpha=0.55, zorder=3))
    rnd = random.Random(3)
    for _ in range(16):
        parche(ax, clip, Circle((rnd.uniform(-38, 38), rnd.uniform(2, 136)), rnd.choice((1.1, 1.5, 2.0)), fc=SURCO, ec="none", zorder=4))


def guardia(ax, clip):
    for r, n in ((16, 8), (28, 14), (40, 20), (52, 26), (64, 32), (76, 38)):
        for k in range(n):
            a = 2 * math.pi * (k + 0.5 * (r // 12 % 2)) / n
            x, y = OJO[0] + r * math.cos(a), OJO[1] + r * math.sin(a)
            parche(ax, clip, Polygon(lente(x, y, 8.6, 3.9, a + math.pi / 2), fc="none", ec=SURCO, lw=lw(1.0), zorder=3))
            parche(ax, clip, Rectangle((x - 0.75, y - 0.75), 1.5, 1.5, angle=math.degrees(a), rotation_point="center",
                                       fc=SURCO, ec="none", zorder=3))


# ════ lamina 5: naturaleza generativa ══════════════════════════════════════
def turing(ax, clip):
    rng = np.random.default_rng(5)
    ny, nx = 290, 176
    u, v = np.ones((ny, nx)), np.zeros((ny, nx))
    for _ in range(60):
        j, i = rng.integers(4, ny - 10), rng.integers(4, nx - 10)
        u[j:j + 6, i:i + 6], v[j:j + 6, i:i + 6] = 0.5, 0.25
    lap = lambda a: np.roll(a, 1, 0) + np.roll(a, -1, 0) + np.roll(a, 1, 1) + np.roll(a, -1, 1) - 4 * a  # noqa: E731
    for _ in range(5200):
        uvv = u * v * v
        u += 0.16 * lap(u) - uvv + 0.037 * (1 - u)
        v += 0.08 * lap(v) + uvv - 0.097 * v
    gx, gy = np.meshgrid(np.linspace(-44, 44, nx), np.linspace(-3, 142, ny))
    relleno(ax, clip, gx, gy, v, [0.2, 2.0])


def enredadera(ax, clip):
    y = np.linspace(-2, 141, 300)
    for s in (-1, 1):
        x = s * 35.4 + 2.3 * np.sin(y / 7.5 + (0 if s < 0 else 1.6))
        linea(ax, clip, x, y, 1.3)
        for k, yy in enumerate(np.arange(4, 138, 6.8)):
            xx = s * 35.4 + 2.3 * math.sin(yy / 7.5 + (0 if s < 0 else 1.6))
            lado = 1 if k % 2 else -1
            g = math.radians(90 - lado * 52)
            cx, cy = xx + 3.9 * math.cos(g), yy + 3.9 * math.sin(g)
            parche(ax, clip, Polygon(lente(cx, cy, 7.4, 3.3, g), fc=SURCO, ec="none", zorder=3))
    for x0 in (-24, -12, 12, 24):                          # zarcillos que cuelgan de arriba
        t = np.linspace(0, 5.5 * math.pi, 120)
        linea(ax, clip, x0 + (0.5 + 0.22 * t) * np.cos(t), 133 - 0.5 * t + (0.5 + 0.22 * t) * np.sin(t), 1.0)


def helechos(ax, clip):
    """Un solo helecho de Barnsley que cruza toda la tapa."""
    rnd = random.Random(42)
    x = y = 0.0
    ps = []
    g = math.radians(-20)
    for _ in range(5200):
        r = rnd.random()
        if r < 0.01:
            x, y = 0.0, 0.16 * y
        elif r < 0.86:
            x, y = 0.85 * x + 0.04 * y, -0.04 * x + 0.85 * y + 1.6
        elif r < 0.93:
            x, y = 0.2 * x - 0.26 * y, 0.23 * x + 0.22 * y + 1.6
        else:
            x, y = -0.15 * x + 0.28 * y, 0.26 * x + 0.24 * y + 0.44
        px, py = x * 15.5, y * 15.0
        ps.append(Circle((-34 + px * math.cos(g) - py * math.sin(g), -4 + px * math.sin(g) + py * math.cos(g)), 0.6))
    coleccion(ax, clip, ps)


def nervadura(ax, clip):
    linea(ax, clip, [0, 0], [-2, 141], 1.7)
    t = np.linspace(0, 1, 40)
    for k, y0 in enumerate(np.arange(2, 138, 8.5)):
        for s in (-1, 1):
            xs, ys = s * 42 * t, y0 + (0 if s < 0 else 4.2) + 24 * t ** 1.5
            linea(ax, clip, xs, ys, 1.2)
            for j in (10, 18, 26, 34):
                linea(ax, clip, [xs[j], xs[j] + s * 1.5], [ys[j], ys[j] - 5.4], 0.9)


def girasol(ax, clip):
    ps = [Circle((VC[0] + 1.95 * math.sqrt(n) * math.cos(n * 2.39996), VC[1] + 1.95 * math.sqrt(n) * math.sin(n * 2.39996)),
                 0.55 + 0.012 * n ** 0.5 * 1.95) for n in range(1, 520)]
    coleccion(ax, clip, ps)
    for capa, (n, r, largo) in enumerate(((34, 57, 22), (34, 74, 26))):
        for k in range(n):
            a = 2 * math.pi * (k + 0.5 * capa) / n
            parche(ax, clip, Polygon(lente(VC[0] + r * math.cos(a), VC[1] + r * math.sin(a), largo, 7.2, a), fc="none", ec=SURCO,
                                     lw=lw(1.0), zorder=3))


def panal_organico(ax, clip):
    rnd = random.Random(19)
    r = 4.4
    dx, dy = math.sqrt(3) * r, 1.5 * r
    for j in range(-1, 23):
        for i in range(-6, 7):
            cx, cy = i * dx + (dx / 2 if j % 2 else 0), j * dy
            pts = [(cx + (r - 0.6) * math.cos(math.radians(30 + 60 * k)), cy + (r - 0.6) * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
            q = rnd.random()
            if q < 0.2:
                parche(ax, clip, Polygon(pts, fc=SURCO, ec="none", zorder=3))
            elif q < 0.78:
                parche(ax, clip, Polygon(pts, fc="none", ec=SURCO, lw=lw(1.0), zorder=3))


def agua(ax, clip):
    for cx, cy, n in ((-22, 50, 13), (24, 126, 10), (30, 44, 8), (-34, 122, 7)):
        for k in range(1, n):
            parche(ax, clip, Circle((cx, cy), 4.4 * k, fc="none", ec=SURCO, lw=lw(max(0.8, 1.5 - 0.08 * k)), zorder=3))


def veta(ax, clip):
    z = X + 7 * np.sin(Y / 23) + 4 * np.sin(Y / 9 + X / 15) + 15 * np.exp(-((X - 14) ** 2 + (Y - 52) ** 2) / 170) \
        - 12 * np.exp(-((X + 20) ** 2 + (Y - 122) ** 2) / 120)
    curvas(ax, clip, z, np.arange(-70, 70, 3.8))


def kintsugi(ax, clip):
    rng = np.random.default_rng(33)
    v = Voronoi(np.column_stack([rng.uniform(-60, 60, 22), rng.uniform(-20, 160, 22)]))
    for a, b in v.ridge_vertices:
        if a < 0 or b < 0:
            continue
        p, q = v.vertices[a], v.vertices[b]
        n = max(2, int(np.hypot(*(q - p)) / 5))
        t = np.linspace(0, 1, n + 1)
        nrm = np.array([-(q - p)[1], (q - p)[0]]) / (np.hypot(*(q - p)) + 1e-9)
        des = np.concatenate([[0], rng.uniform(-1.6, 1.6, n - 1), [0]])
        pts = p[None, :] + t[:, None] * (q - p)[None, :] + des[:, None] * nrm[None, :]
        linea(ax, clip, pts[:, 0], pts[:, 1], rng.choice((1.0, 1.3, 1.8)))


def constelacion(ax, clip):
    rnd = random.Random(77)
    for r in (58, 96, 134):
        parche(ax, clip, Arc((60, -20), 2 * r, 2 * r, theta1=90, theta2=180, color=SURCO, lw=lw(0.9), zorder=3))
    est = [(rnd.uniform(-39, 39), rnd.uniform(1, 137)) for _ in range(95)]
    for k, (x, y) in enumerate(est):
        if k % 9 == 0:
            parche(ax, clip, Polygon([(x + (3.0 if j % 2 == 0 else 0.9) * math.cos(j * math.pi / 4), y + (3.0 if j % 2 == 0 else 0.9) * math.sin(j * math.pi / 4))
                                      for j in range(8)], fc=SURCO, ec="none", zorder=3))
        else:
            parche(ax, clip, Circle((x, y), rnd.choice((0.55, 0.7, 1.0)), fc=SURCO, ec="none", zorder=3))
    ruta = [(-34, 12), (-22, 40), (-33, 60), (-36, 92), (-34, 124), (-12, 134), (22, 133), (35, 112), (36, 70), (24, 48), (34, 22)]
    linea(ax, clip, [p[0] for p in ruta], [p[1] for p in ruta], 0.9)
    for p in ruta:
        parche(ax, clip, Circle(p, 1.7, fc=SURCO, ec="none", zorder=4))


# ════ lamina 6: geometria que engana ═══════════════════════════════════════
def abombada(ax, clip):
    def mapa(x, y):
        dx, dy = x - VC[0], y - VC[1]
        k = 0.62 * np.exp(-(dx ** 2 + dy ** 2) / (2 * 34.0 ** 2))
        return x + dx * k, y + dy * k
    t = np.linspace(-80, 220, 500)
    for c in np.arange(-70, 71, 5.0):
        linea(ax, clip, *mapa(np.full_like(t, c), t))
    for c in np.arange(-40, 200, 5.0):
        linea(ax, clip, *mapa(t - 70, np.full_like(t, c)))


def vortice(ax, clip):
    th = np.linspace(0, 13.5, 400)
    r = 8.5 * np.exp(0.215 * th)
    for k in range(26):
        a = th + 2 * math.pi * k / 26
        linea(ax, clip, OJO[0] + r * np.cos(a), OJO[1] + r * np.sin(a), 1.0)


def colina(ax, clip):
    x = np.linspace(-42, 42, 300)
    for y0 in np.arange(1, 150, 4.1):
        y = y0 + 13 * np.exp(-((x - 12) ** 2) / (2 * 15 ** 2)) * math.exp(-((y0 - 52) ** 2) / (2 * 20 ** 2)) \
            - 9 * np.exp(-((x + 22) ** 2) / (2 * 11 ** 2)) * math.exp(-((y0 - 128) ** 2) / (2 * 14 ** 2))
        linea(ax, clip, x, y)


def ojo_por_grosor(ax, clip):
    x = np.linspace(-42, 42, 320)
    a, h = 62.0, 44.0
    rad = (a * a + h * h) / (2 * h)
    media = np.sqrt(np.maximum(rad ** 2 - x ** 2, 0)) - (rad - h)
    for y0 in np.arange(1.5, 139, 4.1):
        dentro = np.clip((1 - np.abs(y0 - VC[1]) / np.maximum(media, 0.1)) * 5, 0, 1)
        g = 0.45 + 1.05 * dentro
        f = ax.fill_between(x, y0 - g, y0 + g, color=SURCO, lw=0, zorder=3)
        f.set_clip_path(clip)


def moire_rejillas(ax, clip):
    seg = []
    for ang in (86.0, 94.0):
        c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        for k in np.arange(-70, 70, 3.5):
            px, py = k * s, 70 - k * c
            seg.append([(px - 120 * c, py - 120 * s), (px + 120 * c, py + 120 * s)])
    segmentos(ax, clip, seg, 1.05)


def asanoha(ax, clip):
    a = 13.0
    h = a * math.sqrt(3) / 2
    seg = []
    for j in range(-1, 19):
        for i in range(-5, 6):
            x0, y0 = i * a + (a / 2 if j % 2 else 0), j * h
            for tri in (((x0, y0), (x0 + a, y0), (x0 + a / 2, y0 + h)), ((x0 + a / 2, y0 + h), (x0 + 3 * a / 2, y0 + h), (x0 + a, y0))):
                cx, cy = sum(p[0] for p in tri) / 3, sum(p[1] for p in tri) / 3
                seg += [[tri[k], tri[(k + 1) % 3]] for k in range(3)] + [[(cx, cy), p] for p in tri]
    segmentos(ax, clip, seg, 0.95)


def shippo(ax, clip):
    r = 7.2
    p = r * math.sqrt(2)
    for j in range(-1, 16):
        for i in range(-5, 6):
            parche(ax, clip, Circle((i * p, j * p), r, fc="none", ec=SURCO, lw=lw(1.0), zorder=3))
            parche(ax, clip, Circle((i * p + p / 2, j * p + p / 2), r, fc="none", ec=SURCO, lw=lw(1.0), zorder=3))


def estrella8(ax, clip):
    p, s = 15.5, 5.4
    for j in range(0, 11):
        for i in range(-3, 4):
            cx, cy = i * p, j * p - 4
            for g in (0, 45):
                parche(ax, clip, Rectangle((cx - s, cy - s), 2 * s, 2 * s, angle=g, rotation_point="center", fc="none", ec=SURCO,
                                           lw=lw(1.0), zorder=3))
            parche(ax, clip, Rectangle((cx + p / 2 - 1.5, cy + p / 2 - 1.5), 3, 3, angle=45, rotation_point="center", fc=SURCO,
                                       ec="none", zorder=3))


def bauhaus(ax, clip):
    rnd = random.Random(26)
    t = 10.0
    for j in range(0, 15):
        for i in range(-4, 4):
            x0, y0, q = i * t, j * t - 3, rnd.random()
            if q < 0.36:
                k = rnd.randrange(4)
                c = [(x0, y0), (x0 + t, y0), (x0 + t, y0 + t), (x0, y0 + t)][k]
                parche(ax, clip, Wedge(c, t - 1.0, 90 * k, 90 * k + 90, fc=SURCO, ec="none", zorder=3))
            elif q < 0.52:
                parche(ax, clip, Circle((x0 + t / 2, y0 + t / 2), 3.3, fc=SURCO, ec="none", zorder=3))
            elif q < 0.68:
                parche(ax, clip, Circle((x0 + t / 2, y0 + t / 2), 3.4, fc="none", ec=SURCO, lw=lw(1.2), zorder=3))
            elif q < 0.82:
                for d in (2.5, 5.0, 7.5):
                    linea(ax, clip, [x0 + 1, x0 + t - 1], [y0 + d, y0 + d], 1.1)


def memphis(ax, clip):
    rnd = random.Random(80)
    for x, y, _ in empacar(rnd, (4.4,), hueco=1.0, intentos=2500):
        q, g = rnd.randrange(6), rnd.uniform(0, math.pi)
        c, s = math.cos(g), math.sin(g)
        if q == 0:
            t = np.linspace(-3.6, 3.6, 40)
            linea(ax, clip, x + t * c - 1.3 * np.sin(t * 2.6) * s, y + t * s + 1.3 * np.sin(t * 2.6) * c, 1.1)
        elif q == 1:
            parche(ax, clip, Polygon([(x + 3.4 * math.cos(g + k * 2.094), y + 3.4 * math.sin(g + k * 2.094)) for k in range(3)],
                                     fc="none", ec=SURCO, lw=lw(1.1), zorder=3))
        elif q == 2:
            parche(ax, clip, Circle((x, y), 2.6, fc="none", ec=SURCO, lw=lw(1.1), zorder=3))
        elif q == 3:
            zs = [(-3.6, -1.2), (-1.8, 1.2), (0, -1.2), (1.8, 1.2), (3.6, -1.2)]
            linea(ax, clip, [x + u * c - w * s for u, w in zs], [y + u * s + w * c for u, w in zs], 1.1)
        elif q == 4:
            for u, w in ((-1.7, -1.7), (1.7, -1.7), (-1.7, 1.7), (1.7, 1.7), (0, 0)):
                parche(ax, clip, Circle((x + u, y + w), 0.8, fc=SURCO, ec="none", zorder=3))
        else:
            linea(ax, clip, [x - 2.8, x + 2.8], [y, y], 1.2)
            linea(ax, clip, [x, x], [y - 2.8, y + 2.8], 1.2)


# ════ lamina 7: datos y maquina ════════════════════════════════════════════
def osciloscopio(ax, clip):
    coleccion(ax, clip, [Circle((x, y), 0.5) for x in np.arange(-38.5, 40, 7) for y in np.arange(3.5, 140, 7)])
    x = np.linspace(-42, 42, 400)
    linea(ax, clip, x, 50 + 11 * np.sin(x / 4.6) * np.exp(-(x / 30) ** 2) + 2 * np.sin(x / 1.4), 1.3)
    linea(ax, clip, x, 132 + 3.6 * np.sign(np.sin(x / 5.5)), 1.2)
    linea(ax, clip, x, 41 + 2.5 * np.sin(x / 9), 1.0)


def barras(ax, clip):
    rnd = random.Random(15)
    for y0 in np.arange(1, 125, 23.0):
        x = -38.5
        while x < 38.5:
            w = rnd.choice((1.0, 1.0, 1.5, 2.2))
            parche(ax, clip, Rectangle((x, y0 + 4.2), w, 16.2, fc=SURCO, ec="none", zorder=3))
            x += w + rnd.choice((1.0, 1.5, 2.2))
        texto(ax, clip, 0, y0 + 1.9, "7 501234 567890  ARGOS  G507", 2.3, family="monospace")


def qr(ax, clip):
    rng = np.random.default_rng(64)
    m, nx, ny = 1.95, 42, 72
    bits = rng.random((ny, nx)) < 0.47
    for (j0, i0) in ((0, 0), (0, nx - 7), (ny - 7, 0)):
        bits[j0:j0 + 7, i0:i0 + 7] = True
        bits[j0 + 1:j0 + 6, i0 + 1:i0 + 6] = False
        bits[j0 + 2:j0 + 5, i0 + 2:i0 + 5] = True
    coleccion(ax, clip, [Rectangle((-41 + i * m, 139.5 - (j + 1) * m), m, m) for j in range(ny) for i in range(nx) if bits[j, i]])


LETRAS = {"A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
          "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
          "G": ["01111", "10000", "10000", "10111", "10001", "10001", "01111"],
          "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
          "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"]}


def matriz(ax, clip):
    p, ps = 2.35, []
    cols = [c for ch in "ARGOS" for c in list(zip(*LETRAS[ch])) + [("0",) * 7]][:-1]
    for j in range(60):
        fila = j % 10
        for i in range(34):
            on = fila < 7 and 2 <= i < 2 + len(cols) and cols[i - 2][fila] == "1"
            ps.append(Circle((-38.8 + i * p, 138 - j * p), 1.02 if on else 0.42))
    coleccion(ax, clip, ps)


def braille(ax, clip):
    cod = {"A": (1,), "R": (1, 2, 3, 5), "G": (1, 2, 4, 5), "O": (1, 3, 5), "S": (2, 3, 4), " ": ()}
    pos = {1: (0, 2), 2: (0, 1), 3: (0, 0), 4: (1, 2), 5: (1, 1), 6: (1, 0)}
    ps, frase = [], "ARGOS "
    for j in range(13):
        for i in range(11):
            ch = frase[(i + j * 2) % len(frase)]
            for n, (u, w) in pos.items():
                ps.append(Circle((-37.5 + i * 7.2 + u * 2.7, 131 - j * 10.6 + w * 2.7), 1.05 if n in cod[ch] else 0.4))
    coleccion(ax, clip, ps)


def regla(ax, clip):
    for k, y in enumerate(np.arange(1, 138, 2.0)):
        largo = 6.0 if k % 5 == 0 else 3.0
        linea(ax, clip, [-40, -40 + largo], [y, y], 0.9)
        linea(ax, clip, [40, 40 - largo * 0.8], [y + 1, y + 1], 0.9)
        if k % 5 == 0:
            texto(ax, clip, -31.4, y, f"{k // 5}", 2.5)
            texto(ax, clip, 33.2, y + 1, f"{16 + k // 5}", 2.3)
    for x in np.arange(-26, 27, 2.0):
        linea(ax, clip, [x, x], [138.5, 138.5 - (4.6 if round(x) % 10 == 4 else 2.4)], 0.9)
    texto(ax, clip, 33.0, 136.2, "°C", 2.6)
    texto(ax, clip, -31.5, 136.2, "cm", 2.6)
    texto(ax, clip, 22, 52, "T  22 a 28 °C", 2.6)
    texto(ax, clip, 22, 45, "HR 40 a 60 %", 2.6)


def clima(ax, clip):
    z = 2.2 * np.exp(-((X + 18) ** 2 + (Y - 46) ** 2) / 500) - 1.8 * np.exp(-((X - 26) ** 2 + (Y - 126) ** 2) / 420) \
        + 1.2 * np.exp(-((X - 34) ** 2 + (Y - 40) ** 2) / 300) + 0.004 * Y
    curvas(ax, clip, z, 15, 0.95)
    texto(ax, clip, 23, 48, "B", 6.0, fontweight="bold")
    texto(ax, clip, 34, 133, "A", 6.0, fontweight="bold")
    t = np.linspace(0, 1, 60)
    fx, fy = -40 + 26 * t + 8 * np.sin(t * 3), 2 + 60 * t
    linea(ax, clip, fx, fy, 1.4)
    for k in range(4, 58, 7):
        parche(ax, clip, Polygon([(fx[k], fy[k]), (fx[k + 2], fy[k + 2]), (fx[k + 1] + 3.4, fy[k + 1] - 1.6)], fc=SURCO, ec="none", zorder=3))


def histograma(ax, clip):
    rnd = random.Random(48)
    for k, x in enumerate(np.arange(-39.3, 39, 4.4)):
        alto = 18 + 105 * math.exp(-((k - 9) / 5.2) ** 2) + rnd.uniform(-9, 9)
        parche(ax, clip, Rectangle((x, 0), 3.0, alto, fc=SURCO, ec="none", zorder=3))


def dispersion(ax, clip):
    rng = np.random.default_rng(91)
    linea(ax, clip, [-36, -36, 38], [136, 4, 4], 1.3)
    for v in np.arange(-26, 38, 10):
        linea(ax, clip, [v, v], [4, 1.5], 1.0)
    for v in np.arange(14, 136, 10):
        linea(ax, clip, [-36, -38.5], [v, v], 1.0)
    x = rng.uniform(-32, 36, 150)
    y = 68 + 1.45 * x + rng.normal(0, 13, 150)
    coleccion(ax, clip, [Circle((a, b), 0.95) for a, b in zip(x, y)])
    linea(ax, clip, [-34, 37], [68 - 1.45 * 34, 68 + 1.45 * 37], 1.2)


def tarjeta(ax, clip):
    rng = np.random.default_rng(1401)
    ps = [Rectangle((-39 + i * 2.95, 3 + j * 6.2), 1.55, 3.9) for j in range(22) for i in range(27) if rng.random() < 0.2]
    coleccion(ax, clip, ps)
    for j in range(22):
        texto(ax, clip, 38.6, 5 + j * 6.2, str(j % 10), 2.0, family="monospace")


# ════ lamina 8: Mexico, Monterrey y remate ═════════════════════════════════
def cerro(ax, clip):
    silla = [(-42, 15), (-33, 19), (-25, 27), (-17, 42), (-13, 52), (-9, 49), (-4, 40), (2, 37), (7, 41), (12, 55), (15, 61),
             (18, 57), (23, 43), (30, 30), (42, 22)]
    xs = np.linspace(-42, 42, 260)
    for capa, (esc, base) in enumerate(((0.62, 30.0), (0.42, 22.0), (0.26, 14.0))):
        px = [p[0] + capa * 9 for p in silla]
        cresta = np.interp(xs, px, [base + p[1] * esc for p in silla])
        f = ax.fill_between(xs, 0, cresta, color=TAPA, zorder=3 + capa * 0.1)
        f.set_clip_path(clip)
        linea(ax, clip, xs, cresta, 1.3, 3.05 + capa * 0.1)
        for y in np.arange(base - 12 + capa * 1.5, base + 60, 3.6):
            m = cresta > y + 1.4
            seg, ini = [], None
            for k in range(len(xs)):
                if m[k] and ini is None:
                    ini = xs[k]
                if ini is not None and (not m[k] or k == len(xs) - 1):
                    seg.append([(ini, y), (xs[k], y)])
                    ini = None
            c = LineCollection(seg, colors=SURCO, linewidths=lw(0.9), zorder=3.06 + capa * 0.1)
            ax.add_collection(c)
            c.set_clip_path(clip)
    for a in range(0, 181, 12):                            # el ojo como sol: rayos largos sobre el cerro
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        for r0, r1 in ((13, 22), (26, 44), (49, 90)):
            linea(ax, clip, [OJO[0] + r0 * c, OJO[0] + r1 * c], [OJO[1] + 4 + r0 * s, OJO[1] + 4 + r1 * s], 1.0, 2.9)


def papel_picado(ax, clip):
    for fila, y0 in enumerate(np.arange(136, -10, -21.0)):
        linea(ax, clip, [-42, 42], [y0, y0], 1.0)
        for i in range(-3, 4):
            x0 = i * 20.5 + (10.25 if fila % 2 else 0)
            t = np.linspace(0, math.pi, 12)
            fest = [(x0 - 8.5 + 17 * k / 4 + 2.125 - 2.125 * math.cos(a), y0 - 15.5 - 2.0 * math.sin(a)) for k in range(4) for a in t]
            parche(ax, clip, Polygon([(x0 - 8.5, y0), (x0 + 8.5, y0), (x0 + 8.5, y0 - 15.5)] + fest[::-1] + [(x0 - 8.5, y0 - 15.5)],
                                     fc="none", ec=SURCO, lw=lw(1.0), zorder=3))
            parche(ax, clip, Circle((x0, y0 - 7.6), 3.1, fc="none", ec=SURCO, lw=lw(1.0), zorder=3))
            for a in range(0, 360, 45):
                parche(ax, clip, Polygon(lente(x0 + 5.3 * math.cos(math.radians(a)), y0 - 7.6 + 5.3 * math.sin(math.radians(a)), 3.0, 1.5,
                                               math.radians(a)), fc=SURCO, ec="none", zorder=3))
            parche(ax, clip, Circle((x0, y0 - 7.6), 1.1, fc=SURCO, ec="none", zorder=3))


def sarape(ax, clip):
    ritmo = [2.6, 1.0, 1.0, 1.6, 1.0, 3.4, 1.0, 1.6, 1.0, 1.0]
    y, k = 0.0, 0
    while y < 139:
        g = ritmo[k % len(ritmo)]
        parche(ax, clip, Rectangle((-41, y), 82, g, fc=SURCO, ec="none", zorder=3))
        y += g + (1.3 if g < 2 else 2.2)
        k += 1
    for y0 in (48, 126, 2):
        for i in range(-5, 6):
            parche(ax, clip, Polygon([(i * 9, y0 - 7), (i * 9 + 4.5, y0), (i * 9, y0 + 7), (i * 9 - 4.5, y0)], fc=TAPA, ec=SURCO,
                                     lw=lw(1.2), zorder=3.2))
            parche(ax, clip, Polygon([(i * 9, y0 - 2.6), (i * 9 + 1.7, y0), (i * 9, y0 + 2.6), (i * 9 - 1.7, y0)], fc=SURCO, ec="none", zorder=3.3))


def azulejo(ax, clip):
    t = 16.0
    for j in range(0, 10):
        for i in range(-3, 3):
            x0, y0 = i * t, j * t - 5
            parche(ax, clip, Rectangle((x0, y0), t, t, fc="none", ec=SURCO, lw=lw(0.9), zorder=3))
            for k, c in enumerate(((x0, y0), (x0 + t, y0), (x0 + t, y0 + t), (x0, y0 + t))):
                parche(ax, clip, Arc(c, t - 3, t - 3, theta1=90 * k, theta2=90 * k + 90, color=SURCO, lw=lw(1.1), zorder=3))
            parche(ax, clip, Polygon([(x0 + t / 2 + (3.6 if q % 2 == 0 else 1.2) * math.cos(q * math.pi / 4),
                                       y0 + t / 2 + (3.6 if q % 2 == 0 else 1.2) * math.sin(q * math.pi / 4)) for q in range(8)],
                                     fc=SURCO, ec="none", zorder=3))


def sol(ax, clip):
    for r in (11.5, 19, 28, 39, 52, 67, 84, 103):
        parche(ax, clip, Circle(OJO, r, fc="none", ec=SURCO, lw=lw(1.2), zorder=3))
    for r0, r1, n in ((12.6, 17.8, 12), (20.2, 26.8, 20), (29.4, 37.6, 28), (40.6, 50.4, 36), (53.8, 65.2, 44), (69, 82, 52), (86, 101, 60)):
        for k in range(n):
            a, da = 2 * math.pi * k / n, math.pi / n * 0.62
            parche(ax, clip, Polygon([(OJO[0] + r0 * math.cos(a - da), OJO[1] + r0 * math.sin(a - da)),
                                      (OJO[0] + r0 * math.cos(a + da), OJO[1] + r0 * math.sin(a + da)),
                                      (OJO[0] + r1 * math.cos(a), OJO[1] + r1 * math.sin(a))], fc=SURCO, ec="none", zorder=3))


def agave(ax, clip):
    for capa, (n, largo, ancho, r) in enumerate(((16, 66, 15, 40), (16, 46, 12, 30))):
        for k in range(n):
            a = 2 * math.pi * (k + 0.5 * capa) / n
            cx, cy = VC[0] + r * math.cos(a), VC[1] + r * math.sin(a)
            parche(ax, clip, Polygon(lente(cx, cy, largo, ancho, a), fc=TAPA, ec=SURCO, lw=lw(1.2), zorder=3 + capa * 0.2))
            linea(ax, clip, [cx - largo * 0.36 * math.cos(a), cx + largo * 0.4 * math.cos(a)],
                  [cy - largo * 0.36 * math.sin(a), cy + largo * 0.4 * math.sin(a)], 0.9, 3.1 + capa * 0.2)


def letras(ax, clip):
    fp = FontProperties(family="DejaVu Sans", weight="bold")
    for k, ch in enumerate("ARGOS"):
        tp = TextPath((0, 0), ch, size=30, prop=fp)
        bb = tp.get_extents()
        s = min(58 / bb.width, 23.5 / bb.height)
        tr = Affine2D().translate(-bb.x0 - bb.width / 2, -bb.y0 - bb.height / 2).scale(s).translate(0, 124.5 - k * 27.4)
        parche(ax, clip, PathPatch(tr.transform_path(tp), fc="none", ec=SURCO, lw=lw(1.3), zorder=3))


def microtexto(ax, clip):
    frase = "ARGOS · MONTERREY · G507 · NODO DHT · T 22–28 °C · HR 40–60 % · IN VITRO · "
    for k, y in enumerate(np.arange(134.0, 3, -4.5)):
        s = (frase * 3)[(k * 11) % len(frase):][:37]
        texto(ax, clip, 0, y, s, 2.4, family="monospace", fontweight="bold")


def fotoperiodo(ax, clip):
    parche(ax, clip, Arc((0, 44), 70, 172, theta1=0, theta2=180, color=SURCO, lw=lw(1.0), zorder=3))
    for x in np.arange(-41, 41, 4.2):
        linea(ax, clip, [x, x + 2.4], [44, 44], 1.0)
    for k in range(9):
        a = math.pi * (1 - k / 8)
        x, y = 35 * math.cos(a), 44 + 86 * math.sin(a)
        r = 2.0 + 1.5 * math.sin(a)
        parche(ax, clip, Circle((x, y), r + 1.6, fc=TAPA, ec="none", zorder=3.1))
        parche(ax, clip, Circle((x, y), r, fc=SURCO, ec="none", zorder=3.2))
        for q in range(8):
            c, s = math.cos(q * math.pi / 4), math.sin(q * math.pi / 4)
            linea(ax, clip, [x + (r + 1.5) * c, x + (r + 1.5 + 2.6 * math.sin(a) + 0.4) * c],
                  [y + (r + 1.5) * s, y + (r + 1.5 + 2.6 * math.sin(a) + 0.4) * s], 1.0, 3.2)
    for x, y in ((-30, 30), (-14, 22), (16, 26), (33, 34)):       # la noche, bajo el horizonte
        parche(ax, clip, Circle((x, y), 3.2, fc=SURCO, ec="none", zorder=3))
        parche(ax, clip, Circle((x + 1.5, y + 0.9), 2.7, fc=TAPA, ec="none", zorder=3.01))
    for h, x in (("06", -35), ("12", 0), ("18", 35)):
        texto(ax, clip, x, 39.4, h, 2.6, fontweight="bold")


def hoja_circuito(ax, clip):
    parche(ax, clip, Polygon(lente(0, 70, 176, 84, math.pi / 2), fc="none", ec=SURCO, lw=lw(1.5), zorder=3))
    linea(ax, clip, [0, 0], [-2, 141], 1.8)
    rnd = random.Random(10)
    for k, y0 in enumerate(np.arange(4, 132, 7.4)):
        s = 1 if k % 2 else -1
        medio = 41 * math.sqrt(max(0.0, 1 - ((y0 + 12 - 70) / 88) ** 2)) - 5
        b = max(4.0, medio - 5 - rnd.uniform(0, 7))
        p = [(0, y0), (s * 3.2, y0), (s * (3.2 + b), y0 + b), (s * (3.2 + b + 3.5), y0 + b)]
        linea(ax, clip, [q[0] for q in p], [q[1] for q in p], 1.1)
        parche(ax, clip, Circle(p[-1], 1.55, fc=SURCO, ec="none", zorder=4))
        parche(ax, clip, Circle(p[-1], 0.62, fc=TAPA, ec="none", zorder=4))
        if b > 12:
            m = (s * (3.2 + b * 0.5), y0 + b * 0.5)
            linea(ax, clip, [m[0], m[0] + s * 5.5], [m[1], m[1]], 1.0)
            parche(ax, clip, Circle((m[0] + s * 5.5, m[1]), 1.2, fc=SURCO, ec="none", zorder=4))


TANDAS = [
    ("maqueta_texturas_tapa_dht_4.png", "Lámina 4: la pantalla es el ojo", [
        ("36. Párpados: la pantalla es la pupila", parpados), ("37. Iris", iris), ("38. Ecos de la pantalla", ecos),
        ("39. Jardín zen", zen), ("40. Corriente que rodea", corriente), ("41. La pantalla es un chip", chip),
        ("42. Sol naciente", sol_naciente), ("43. Plano técnico", plano), ("44. Radar", radar), ("45. Guardia de ojos", guardia)]),
    ("maqueta_texturas_tapa_dht_5.png", "Lámina 5: naturaleza generativa", [
        ("46. Coral (reacción-difusión)", turing), ("47. Enredadera", enredadera), ("48. Helechos", helechos),
        ("49. La tapa es una hoja", nervadura), ("50. Girasol", girasol), ("51. Panal orgánico", panal_organico),
        ("52. Lluvia sobre agua", agua), ("53. Veta de madera", veta), ("54. Kintsugi", kintsugi), ("55. Cielo de Argos", constelacion)]),
    ("maqueta_texturas_tapa_dht_6.png", "Lámina 6: geometría que engaña", [
        ("56. Rejilla abombada", abombada), ("57. Vórtice", vortice), ("58. Relieve de líneas", colina),
        ("59. Ojo dibujado con grosores", ojo_por_grosor), ("60. Moiré de dos rejillas", moire_rejillas), ("61. Asanoha", asanoha),
        ("62. Shippo", shippo), ("63. Estrella de ocho puntas", estrella8), ("64. Bauhaus", bauhaus), ("65. Memphis", memphis)]),
    ("maqueta_texturas_tapa_dht_7.png", "Lámina 7: datos y máquina", [
        ("66. Osciloscopio", osciloscopio), ("67. Código de barras", barras), ("68. Código QR", qr),
        ("69. «ARGOS» en matriz de puntos", matriz), ("70. «ARGOS» en braille", braille), ("71. Regla y termómetro", regla),
        ("72. Mapa del clima", clima), ("73. Histograma", histograma), ("74. Gráfica de dispersión", dispersion),
        ("75. Tarjeta perforada", tarjeta)]),
    ("maqueta_texturas_tapa_dht_8.png", "Lámina 8: México, Monterrey y remate", [
        ("76. Amanecer en el Cerro de la Silla", cerro), ("77. Papel picado", papel_picado), ("78. Sarape", sarape),
        ("79. Azulejo", azulejo), ("80. Sol de anillos", sol), ("81. Agave", agave), ("82. Letras gigantes", letras),
        ("83. Microtexto", microtexto), ("84. Fotoperiodo", fotoperiodo), ("85. Hoja-circuito", hoja_circuito)]),
]


def main():
    for archivo, encabezado, opciones in TANDAS:
        fig = plt.figure(figsize=(FIGW, FIGH), facecolor="white")
        for k, (titulo, fn) in enumerate(opciones):
            col, fila = k % 5, k // 5
            ax = fig.add_axes([0.012 + col * 0.198, 0.50 - fila * 0.49, AXW, AXH])
            clip = tapa_base(ax)
            try:
                fn(ax, clip)
            except Exception as err:                       # una textura con error no tira la lamina
                print("ERROR en", titulo, "->", repr(err))
            elementos(ax)
            ax.text(0, 141.5, titulo, ha="center", va="bottom", fontsize=12.5)
        fig.text(0.5, 0.985, f"{encabezado} (maqueta a escala; el grabado real es de 0.4 mm, más sutil que aquí)",
                 ha="center", va="top", fontsize=13)
        fig.savefig(RAIZ / "renders" / archivo, dpi=100)
        plt.close(fig)
        print("escrito", archivo)


if __name__ == "__main__":
    main()
