"""Cien disenos para la tapa en diez temas (20-nov), en el estilo del diseno 55: linea fina, nodos y estrellas.
Solo maqueta: no genera piezas. Usa cad/maqueta_kit.py.

  uv run --no-project --python 3.12 --with matplotlib --with scipy python cad/maqueta_temas.py [numero de tema ...]

Salida: cad/renders/temas/tema_01_astro.png ... tema_10_tecnologia.png (10 tapas cada una, numeradas 101-200).
"""
import math
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from maqueta_kit import OJO, VC, K, tr  # noqa: E402
from maqueta_texturas import AXH, AXW, FIGH, FIGW, RAIZ, SURCO, TAPA, elementos, lente, tapa_base  # noqa: E402

PI = math.pi
pol = lambda c, r, a: (c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a)))  # noqa: E731


# ═══════════ 1. ASTRO: exploracion del espacio ═══════════
def a1(k):
    k.cielo(85, 9)
    for r in (60, 100, 140):
        k.arco(62, -24, r, 90, 180, 0.9)
    k.ruta([(-34, 12), (-22, 40), (-33, 60), (-36, 92), (-34, 124), (-12, 134), (22, 133), (35, 112), (36, 70), (24, 48), (34, 22)])
    k.ruta([(8, 44), (16, 56), (28, 58), (22, 40), (8, 44)], 0.9, 1.3)


def a2(k):
    k.cielo(45, 4)
    for i, (a, b) in enumerate(((16, 9), (27, 15), (39, 22), (53, 30), (70, 40), (90, 52))):
        k.elipse(OJO[0], OJO[1], a, b, 18, mm=0.9)
        p = pol(OJO, 1, 0)
        ang = math.radians(40 + i * 67)
        x, y = a * math.cos(ang), b * math.sin(ang)
        c, s = math.cos(math.radians(18)), math.sin(math.radians(18))
        px, py = OJO[0] + x * c - y * s, OJO[1] + x * s + y * c
        if i == 3:
            k.planeta(px, py, 3.4, True, 18)
        else:
            k.circ(px, py, 1.4 + 0.45 * i, i % 2 == 0, z=4, fondo=i % 2 == 1)


def a3(k):
    k.cielo(60, 6)
    tray = [(31 - 62 * t ** 1.6, 40 + 96 * t) for t in np.linspace(0, 1, 40)]
    k.trazos(tray, 3.2, 2.4, 1.0)
    k.cohete(31, 46, 1.25, 12)
    k.luna(-30, 126, 7, 0.4, 20)
    k.L([(-42, 38), (42, 38)], 1.0)
    for x in np.arange(-40, 42, 5):
        k.L([(x, 38), (x - 2.4, 35.2)], 0.9)


def a4(k):
    k.cielo(55, 5)
    for i in range(8):
        x, y = pol((0, 44), 37 if i % 2 == 0 else 37, 180 - i * 180 / 7)
        y = 44 + 90 * math.sin(math.radians(180 - i * 180 / 7))
        fase = i / 7
        k.circ(x, y, 4.2, True, z=3.2)
        if 0 < fase < 1:
            k.elipse(x + (0.5 - fase) * 5.2, y, 4.2 * abs(1 - 2 * fase) + 0.2, 4.35, 0, fondo=True, mm=0.0, z=3.25)
        k.circ(x, y, 4.2, mm=1.0, z=3.3)
    k.trazos([(-37, 44), (37, 44)], 2.6, 2.2)


def a5(k):
    k.cielo(50, 5)
    for ang, a, b in ((24, 47, 31), (-24, 47, 31), (90, 60, 34)):
        k.elipse(VC[0], VC[1], a, b, ang, mm=0.95)
    k.satelite(-34, 123, 0.8, 30)
    k.satelite(35, 66, 0.8, -30)
    k.nodo(33, 126, 2.0, True)
    k.nodo(-33, 64.5, 1.6)


def a6(k):
    k.cielo(55, 4)
    for x, y, l in ((30, 132, 26), (-14, 126, 20), (34, 92, 18), (-28, 58, 24), (12, 50, 18), (36, 40, 15), (-36, 104, 14), (-6, 12, 20)):
        k.cometa(x, y, 38, l)


def a7(k):
    k.cielo(45, 5, (-39, 39, 58, 137))
    xs, ys = k.monte([(-42, 46), (-30, 49), (-18, 46), (-4, 51), (10, 47), (24, 52), (42, 47)], 3.0, 1.2)
    for x, y, r in ((-28, 34), (-8, 22), (16, 36), (30, 18), (-34, 10), (4, 40)) and ((-28, 34, 5), (-8, 22, 7), (16, 36, 4), (30, 18, 6), (-34, 10, 4), (4, 40, 3)):
        k.elipse(x, y, r, r * 0.45, 0, mm=1.0, z=3.1)
        k.arco(x, y, r * 0.72, 190, 350, 0.9, 3.1, ry=r * 0.3)
    k.circ(26, 126, 8, mm=1.1)
    k.arco(26, 126, 8, 200, 20, 1.0)
    k.L([(19.5, 123), (23, 126.5), (27, 124), (31, 128)], 0.9)


def a8(k):
    k.cielo(40, 3)
    wp = [(-33, 10), (-36, 44), (-20, 52), (8, 50), (33, 44), (36, 70), (35, 110), (20, 132), (-10, 134), (-34, 122), (-36, 94)]
    k.trazos(wp, 3.0, 2.0)
    for i, p in enumerate(wp):
        k.circ(p[0], p[1], 2.6, fondo=True, mm=1.0, z=4)
        k.punto(p[0], p[1], 1.0, 4.1)
    k.cohete(-33, 4, 0.8, 0)
    k.planeta(27, 58, 4.4, True, 20)


def a9(k):
    c = (-40, 138)
    for r in np.arange(18, 190, 17):
        k.arco(c[0], c[1], r, 270, 360, 0.9)
    for a in range(275, 360, 12):
        k.L([pol(c, 12, a), pol(c, 190, a)], 0.8)
    for x, y in k.disp(46, 8):
        (k.estrella(x, y, k.r.choice((2.0, 2.8)), 4) if k.r.random() < 0.25 else k.punto(x, y, k.r.choice((0.6, 0.9, 1.3))))


def a10(k):
    k.cielo(60, 6)
    k.planeta(33, 28, 22, True, 22, 4)
    k.planeta(-30, 126, 6, True, -20, 1)
    k.circ(30, 124, 3.2, True)
    k.circ(-33, 52, 2.2, fondo=True, mm=1.0)
    k.luna(18, 56, 3.4, 0.4, 200)


# ═══════════ 2. SOLARPUNK ═══════════
def s1(k):
    k.sol(OJO[0], OJO[1], 9.5, 20, 6, False, 1.0, 2.0)
    for r in (24, 34, 46, 60):
        k.arco(OJO[0], OJO[1], r, 20, 160, 0.9)
    for s in (-1, 1):
        k.rama([(s * 36 + 2.4 * math.sin(y / 8), y) for y in np.arange(0, 140, 3)], 7.5, 7.0)


def s2(k):
    k.sol(26, 126, 6, 12, 4)
    k.edificios(34, 6, 26, True, arboles=True)
    k.L([(-42, 34), (42, 34)], 1.2)
    for x in (-36, -30, 32, 37):
        k.arbol(x, 34, 9)
    for y in (26, 18, 10, 2):
        k.ola(y, 1.2, 16, y, 0.9)
    k.nube(-26, 128, 0.9)


def s3(k):
    k.monte([(-42, 40), (-24, 50), (-6, 42), (14, 52), (30, 44), (42, 50)], 3.0, 1.2, 4.0)
    for x, y, h, f in ((-24, 50, 26, 10), (14, 52, 30, 50), (36, 47, 20, 80)):
        k.turbina(x, y, h, f)
    k.nube(-22, 126, 1.0)
    k.nube(24, 130, 0.8)
    k.sol(-2, 124, 4.5, 10, 3.2)


def s4(k):
    k.sol(OJO[0], OJO[1], 9.5, 16, 5, False, 1.0, 2.0)
    for j, y in enumerate((48, 36, 24, 12, 1)):
        for i in range(-3, 4):
            k.panel(i * 13 + (6.5 if j % 2 else 0), y, 11, 8, 0, 3, 2, 0.28)
    for x, y in ((-34, 124), (34, 126), (-33, 100), (34, 92)):
        k.hoja(x, y, 10, 60 if x < 0 else 120, False)


def s5(k):
    c = (0, 36)
    pts = [pol(c, 34, a) for a in range(0, 181, 30)]
    for r, n in ((34, 6), (22, 4), (11, 2)):
        anillo = [pol(c, r, 180 * i / n) for i in range(n + 1)]
        k.L(anillo, 1.1)
    for a in range(0, 181, 30):
        k.L([c, pol(c, 34, a)], 0.9)
    for i in range(6):
        k.L([pol(c, 34, 30 * i), pol(c, 22, 30 * i + 22.5 if i < 6 else 0)], 0.8)
    k.L([(-42, 36), (42, 36)], 1.2)
    for x in (-37, 37):
        k.arbol(x, 36, 14)
    k.sol(26, 126, 5, 12, 4)
    for x, y in ((-30, 124), (-18, 132), (-33, 100)):
        k.hoja(x, y, 9, 70, True)


def s6(k):
    for s in (-1, 1):
        k.curva(lambda t, s=s: (s * (38 - 16 * math.sin(t * PI)), 4 + 132 * t), 0, 1, 80, 1.3)
        k.curva(lambda t, s=s: (s * (30 - 24 * math.sin(t * PI) ** 2), 40 + 26 * t), 0, 1, 60, 1.1)
        k.voluta(s * 30, 126, 1.5, s)
        k.voluta(s * 31, 46, 1.2, -s)
        k.flor(s * 34, 70, 4.2, 6)
        k.flor(s * 22, 134, 3.2, 5)
    k.flor(22, 52, 4.6, 8)


def s7(k):
    for x, y in k.disp(26, 9.5):
        q = k.r.random()
        if q < 0.45:
            k.hexagono(x, y, 4.2, q < 0.12)
        elif q < 0.8:
            k.flor(x, y, 3.2, 6)
        else:
            a = k.r.uniform(0, 360)
            k.elipse(x, y, 2.6, 1.6, a, True, z=3.3)
            for s in (-1, 1):
                p = tr([(0, s * 2.4)], x, y, 1, a)[0]
                k.elipse(p[0], p[1], 1.8, 1.0, a + s * 35, mm=0.9, z=3.2)
            k.trazos([(x, y), (x - 6 * math.cos(math.radians(a)), y - 6 * math.sin(math.radians(a)) - 3)], 1.2, 1.2, 0.8)


def s8(k):
    k.sol(-27, 127, 5, 12, 4)
    k.nube(22, 128, 1.2)
    for x in np.arange(13, 33, 4.2):
        k.trazos([(x, 121), (x - 6, 100)], 2.6, 2.4, 0.9)
    k.monte([(-42, 44), (-30, 56), (-18, 46), (0, 40), (20, 46), (42, 40)], 3.0, 1.2, 4.0)
    for y in (30, 22, 14, 6):
        k.ola(y, 1.6, 15, y * 0.7, 1.0)
    k.curva(lambda t: pol((0, 80), 37, 200 - 150 * t), 0, 1, 50, 0.9)
    k.poli([(34, 100), (37.5, 95), (31, 95.5)], True)
    k.arbol(-33, 52, 12)
    k.arbol(-25, 49, 9, "pino")


def s9(k):
    for i, y in enumerate((8, 22, 36, 50)):
        k.L([(-42, y), (20 - i * 12, y), (26 - i * 12, y + 14), (42, y + 14)], 1.2)
        for x in np.arange(-38, 16 - i * 12, 7.5):
            (k.arbol(x, y, 9) if (int(x) + i) % 2 else k.arbol(x, y, 8, "pino"))
        for x in np.arange(30 - i * 12, 42, 5):
            k.rama([(x, y + 14), (x + 0.6, y + 9), (x - 0.4, y + 4)], 3.6, 3.6, True, 0.9)
    k.sol(28, 126, 5.5, 14, 4)
    k.nube(-24, 127, 1.0)


def s10(k):
    def raiz(x, y, ang, largo, nivel):
        x2, y2 = x + largo * math.cos(ang), y + largo * math.sin(ang)
        k.L([(x, y), (x2, y2)], 0.9 + 0.12 * nivel)
        if nivel:
            for s in (-1, 1):
                raiz(x2, y2, ang + s * math.radians(k.r.uniform(18, 40)), largo * 0.76, nivel - 1)
        else:
            k.punto(x2, y2, 0.9)
    k.L([(-42, 56), (42, 56)], 1.1)
    for x in (-28, -6, 18, 34):
        raiz(x, 56, math.radians(-90 + k.r.uniform(-12, 12)), 13, 5)
        k.rama([(x, 56), (x + 1.5, 66), (x - 1, 76), (x + 0.5, 86)], 6.0, 6.5, True)
    k.sol(26, 126, 5, 12, 4)


# ═══════════ 3. CYBERPUNK ═══════════
def c1(k):
    k.circ(18, 112, 26, mm=1.0)
    for y in np.arange(92, 138, 5):
        m = math.sqrt(max(0, 26 ** 2 - (y - 112) ** 2))
        k.L([(18 - m, y), (18 + m, y)], 0.9)
    k.edificios(36, 14, 52, True, z=3.2)
    k.edificios(22, 6, 26, True, z=3.5, antenas=False)
    k.L([(-42, 22), (42, 22)], 1.3, 3.6)
    for y in (16, 10, 4):
        k.trazos([(-42, y), (42, y)], 6, 3, 0.9)


def c2(k):
    for x in np.arange(-39, 40, 4.4):
        y = 139 + k.r.uniform(0, 10)
        while y > 0:
            l = k.r.choice((1.4, 1.4, 2.6, 4.2, 7))
            k.L([(x, y), (x, y - l)], 1.15 if l < 5 else 1.5)
            y -= l + k.r.choice((1.8, 2.4, 3.4, 9))


def c3(k):
    k.corchetes(-37, 71, 37, 120, 8, 1.4)
    k.corchetes(-39, 2, 39, 136, 5, 1.1)
    k.mira(OJO[0], OJO[1], 11.5, 1, 16)
    for y in np.arange(40, 62, 4.4):
        k.L([(14, y), (14 + k.r.uniform(6, 22), y)], 1.2)
    for i in range(6):
        k.hexagono(-33 + (i % 2) * 6.4, 40 + (i // 2) * 7.4 + (i % 2) * 3.7, 3.6, i == 3)
    for x in np.arange(-34, 36, 3.2):
        k.L([(x, 133), (x, 133 - (4 if int(x) % 3 == 0 else 2))], 0.9)
    k.trazos([(-37, 125), (-16, 125)], 2, 1.6)
    k.trazos([(16, 125), (37, 125)], 2, 1.6)


def c4(k):
    hz = 58
    k.L([(-42, hz), (42, hz)], 1.3)
    for i in range(1, 9):
        y = hz - 58 * (i / 8) ** 1.9
        k.L([(-42, y), (42, y)], 0.9 + 0.05 * i)
    for x in np.arange(-150, 151, 14):
        k.L([(x * 0.12, hz), (x, -4)], 0.95)
    c = (0, hz)
    k.arco(c[0], c[1], 30, 0, 180, 1.2)
    for j, y in enumerate(np.arange(hz + 3, hz + 30, 4.4)):
        m = math.sqrt(max(0, 30 ** 2 - (y - hz) ** 2))
        k.L([(-m, y), (m, y)], 1.0 + 0.1 * j)
    k.cielo(26, 3, (-39, 39, 118, 137))


def c5(k):
    for _ in range(30):
        y, h = k.r.uniform(2, 136), k.r.choice((1.2, 1.2, 2.2, 3.4))
        x, w = k.r.uniform(-42, 30), k.r.choice((6, 10, 16, 26, 40))
        k.rect(x + w / 2, y, w, h, True)
    for _ in range(46):
        k.rect(k.r.uniform(-39, 39), k.r.uniform(2, 136), k.r.choice((1.4, 2.2)), k.r.choice((1.4, 2.2)), True)
    for y in (40, 52, 126):
        k.L([(-42, y), (-10, y), (-10, y + 2.6), (18, y + 2.6), (18, y - 1.4), (42, y - 1.4)], 1.0)


def c6(k):
    for x in np.arange(-36, 40, 12):
        k.L([(x, 0), (x, 139)], 0.9)
    for y in np.arange(4, 140, 12):
        k.L([(-42, y), (42, y)], 0.9)
    for x in np.arange(-30, 40, 12):
        for y in np.arange(10, 140, 12):
            q = k.r.random()
            if q < 0.4:
                k.rect(x, y, 7, 7, mm=1.0)
            elif q < 0.6:
                k.rect(x, y, 7, 7, True)
            elif q < 0.72:
                k.circ(x, y, 3.2, mm=1.0)
    k.L([(-36, 4), (-36, 52), (12, 52), (12, 64), (36, 64), (36, 124), (12, 124)], 2.0, 3.6)
    k.nodo(-36, 4, 2.6, True)
    k.nodo(12, 124, 2.6, True)


def c7(k):
    r = 6.0
    dx, dy = math.sqrt(3) * r, 1.5 * r
    for j in range(0, 16):
        for i in range(-4, 5):
            x, y = i * dx + (dx / 2 if j % 2 else 0), j * dy
            q = k.r.random()
            if q < 0.34:
                k.hexagono(x, y, r - 0.9)
            elif q < 0.42:
                k.hexagono(x, y, r - 0.9, True)
            elif q < 0.5:
                k.hexagono(x, y, r - 0.9)
                k.hexagono(x, y, r - 3.2)
    for _ in range(5):
        x, y = k.r.uniform(-34, 34), k.r.uniform(6, 132)
        k.trazos([(x, y), (x + 16, y), (x + 20, y + 5)], 2.4, 1.6, 0.9)


def c8(k):
    for i, x0 in enumerate(np.arange(-34, 38, 5.6)):
        f = k.r.uniform(0, 6)
        k.curva(lambda t, x0=x0, f=f, i=i: (x0 + 5 * math.sin(t * 4.2 + f) * t + (i % 3 - 1) * 6 * t, 139 - (58 + (i * 37 % 60)) * t), 0, 1, 60, 1.2)
        xf, yf = x0 + 5 * math.sin(4.2 + f) + (i % 3 - 1) * 6, 139 - (58 + (i * 37 % 60))
        k.rect(xf, yf - 2.2, 3.2, 4.4, True)
        for d in (-0.8, 0.8):
            k.L([(xf + d, yf - 4.4), (xf + d, yf - 6.6)], 0.8)


def c9(k):
    for y0 in (128, 44):
        k.L([(-42, y0 + 6), (42, y0 + 6)], 1.2)
        k.L([(-42, y0 - 6), (42, y0 - 6)], 1.2)
        for x in np.arange(-48, 46, 7.5):
            k.poli([(x, y0 - 6), (x + 3.6, y0 - 6), (x + 9.6, y0 + 6), (x + 6, y0 + 6)], True)
    for x in np.arange(-36, 40, 9):
        k.L([(x - 3, 24), (x, 28), (x + 3, 24)], 1.4)
        k.L([(x - 3, 19), (x, 23), (x + 3, 19)], 1.4)
    for x in np.arange(-38, 39, 2.6):
        if k.r.random() < 0.62:
            k.rect(x, 9, k.r.choice((1.0, 1.6)), 10, True)
    k.corchetes(-38, 56, 38, 62, 4)


def c10(k):
    for r in (27, 36, 46, 58, 72, 88):
        k.circ(VC[0], VC[1], r, mm=0.95)
    for a in range(0, 360, 6):
        l = 4.5 if a % 30 == 0 else 2.2
        k.L([pol(VC, 46, a), pol(VC, 46 + l, a)], 0.9)
    for a in (45, 135, 225, 315):
        k.L([pol(VC, 27, a), pol(VC, 100, a)], 0.9)
    for a, r in ((20, 58), (160, 72), (250, 58), (300, 72), (200, 88)):
        p = pol(VC, r, a)
        k.nodo(p[0], p[1], 2.2, True)


# ═══════════ 4. VIDEOJUEGOS (figuras genericas, originales) ═══════════
PX = {"corazon": [".##.##.", "#######", "#######", ".#####.", "..###..", "...#..."],
      "moneda": [".###.", "#...#", "#.#.#", "#.#.#", "#...#", ".###."],
      "llave": [".##....", "#..####", "#..#.#.", ".##...."],
      "pocion": ["..#..", "..#..", ".###.", "#####", "#####", ".###."],
      "espada": ["......#", ".....##", "....##.", "#..##..", ".###...", ".##....", "#..#..."],
      "estrella": ["..#..", "#####", ".###.", ".#.#.", "#...#"],
      "gema": [".###.", "#####", ".###.", "..#.."],
      "seta": [".###.", "#####", "#####", ".#.#.", ".###."]}


def v1(k):
    nombres = list(PX)
    for i, (x, y) in enumerate(k.disp(24, 13, (-38, 28, 12, 136))):
        k.pixel(x, y, PX[nombres[i % len(nombres)]], 1.55)


def v2(k):
    for x, y, w in ((-30, 12, 22), (8, 22, 26), (-22, 40, 20), (20, 50, 18), (-34, 60, 12), (-34, 124, 16), (16, 128, 22), (34, 100, 8), (-36, 92, 8)):
        k.rect(x + w / 2, y, w, 3.2, mm=1.0)
        for xx in np.arange(x + 2, x + w - 1, 4):
            k.L([(xx, y - 1.6), (xx - 1.6, y + 1.6)], 0.8)
        for xx in np.arange(x + 3, x + w - 2, 5.5):
            if k.r.random() < 0.6:
                k.circ(xx, y + 5.4, 1.5, mm=1.0)
    for x, y0, y1 in ((-12, 12, 40), (30, 22, 50), (-30, 40, 60)):
        k.L([(x - 1.8, y0), (x - 1.8, y1)], 1.0)
        k.L([(x + 1.8, y0), (x + 1.8, y1)], 1.0)
        for y in np.arange(y0 + 2, y1, 3.6):
            k.L([(x - 1.8, y), (x + 1.8, y)], 0.9)
    k.L([(34, 130), (34, 138)], 1.1)
    k.poli([(34, 138), (39, 136), (34, 134)], True)
    k.pixel(-28, 20, PX["estrella"], 1.5)


def v3(k):
    nx, ny, t = 13, 23, 6.1
    vis, par = set(), set()
    pila = [(0, 0)]
    vis.add((0, 0))
    while pila:
        x, y = pila[-1]
        vec = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= x + dx < nx and 0 <= y + dy < ny and (x + dx, y + dy) not in vis]
        if vec:
            n = k.r.choice(vec)
            par.add(frozenset(((x, y), n)))
            vis.add(n)
            pila.append(n)
        else:
            pila.pop()
    x0, y0 = -nx * t / 2, 0.2
    for x in range(nx):
        for y in range(ny):
            if x + 1 < nx and frozenset(((x, y), (x + 1, y))) not in par:
                k.L([(x0 + (x + 1) * t, y0 + y * t), (x0 + (x + 1) * t, y0 + (y + 1) * t)], 1.1)
            if y + 1 < ny and frozenset(((x, y), (x, y + 1))) not in par:
                k.L([(x0 + x * t, y0 + (y + 1) * t), (x0 + (x + 1) * t, y0 + (y + 1) * t)], 1.1)


def v4(k):
    salas = [(-28, 126, 18, 14), (22, 128, 24, 12), (-34, 96, 9, 26), (35, 92, 8, 30), (-26, 50, 22, 18), (24, 48, 26, 20), (-6, 4, 30, 5),
             (-34, 16, 10, 20), (34, 18, 10, 22)]
    for x, y, w, h in salas:
        k.rect(x, y, w, h, mm=1.2)
        for xx in np.arange(x - w / 2 + 2.5, x + w / 2 - 1, 4.2):
            for yy in np.arange(y - h / 2 + 2.5, y + h / 2 - 1, 4.2):
                k.punto(xx, yy, 0.45)
    for a, b in (((-19, 126), (10, 128)), ((-34, 119), (-34, 109)), ((35, 122), (35, 107)), ((-34, 83), (-30, 59)), ((35, 77), (32, 58)),
                 ((-15, 50), (11, 48)), ((-34, 41), (-34, 26)), ((34, 38), (34, 29)), ((-29, 8), (-21, 4)), ((29, 9), (9, 4))):
        k.trazos([a, b], 2.0, 1.4, 1.0)
    k.pixel(21, 132, PX["llave"], 1.4)
    k.pixel(-30, 53, PX["pocion"], 1.3)
    k.pixel(20, 52, PX["gema"], 1.5)


def v5(k):
    piezas = [((0, 0), (1, 0), (2, 0), (3, 0)), ((0, 0), (1, 0), (0, 1), (1, 1)), ((0, 0), (1, 0), (2, 0), (1, 1)), ((0, 0), (0, 1), (1, 1), (2, 1)),
              ((0, 0), (1, 0), (1, 1), (2, 1))]
    t = 5.2
    ocup = set()
    for col in range(-7, 8):
        alto = k.r.choice((1, 2, 2, 3, 4))
        for f in range(alto):
            ocup.add((col, f))
    for col, f in ocup:
        k.rect(col * t + t / 2 - 0.5, f * t + t / 2 + 36.6, t - 1.1, t - 1.1, k.r.random() < 0.3, 1.0)
    for x, y, p, lleno in ((-30, 124, 0, False), (20, 126, 2, True), (-34, 92, 3, False), (33, 100, 1, True), (22, 64, 4, False), (-36, 66, 2, False)):
        for dx, dy in piezas[p]:
            k.rect(x + dx * t, y + dy * t, t - 1.1, t - 1.1, lleno, 1.0)
    k.L([(-39, 36), (39, 36)], 1.3)


def v6(k):
    def cruz(x, y, t):
        k.poli(tr([(-1, -3), (1, -3), (1, -1), (3, -1), (3, 1), (1, 1), (1, 3), (-1, 3), (-1, 1), (-3, 1), (-3, -1), (-1, -1)], x, y, t), mm=1.1)
    cruz(-24, 48, 2.6)
    for a in (45, 135, 225, 315):
        p = pol((24, 48), 6.6, a)
        k.circ(p[0], p[1], 3.0, a in (45, 225), 1.1)
    for x in (-3, 5):
        k.poli(tr(lente(0, 0, 6, 2.2), x + 4, 40, 1, 0), mm=1.0)
    cruz(-30, 126, 1.6)
    cruz(31, 127, 1.6)
    for x, y in k.disp(20, 9, (-38, 38, 2, 136)):
        q = k.r.randrange(4)
        (k.circ(x, y, 2.2, mm=1.0) if q == 0 else k.rect(x, y, 4, 4, mm=1.0, ang=45) if q == 1 else
         k.poli([pol((x, y), 2.8, 90 + 120 * i) for i in range(3)], mm=1.0) if q == 2 else (k.L([(x - 2, y - 2), (x + 2, y + 2)], 1.1), k.L([(x - 2, y + 2), (x + 2, y - 2)], 1.1)))


def v7(k):
    niv = [[(0, 6)], [(-22, 22), (0, 24), (22, 22)], [(-32, 42), (-14, 46), (6, 44), (26, 46)], [(-34, 62), (30, 60), (36, 78)], [(-36, 92), (36, 100)],
           [(-34, 122), (34, 124)], [(-20, 134), (20, 134)]]
    for a, b in zip(niv, niv[1:]):
        for p in b:
            q = min(a, key=lambda u: abs(u[0] - p[0]))
            k.L([q, (q[0], (q[1] + p[1]) / 2), (p[0], (q[1] + p[1]) / 2), p], 1.0)
    for i, fila in enumerate(niv):
        for j, (x, y) in enumerate(fila):
            q = (i + j) % 3
            if q == 0:
                k.circ(x, y, 3.6, fondo=True, mm=1.2, z=4)
                k.punto(x, y, 1.3, 4.1)
            elif q == 1:
                k.poli([pol((x, y), 4.0, 30 + 60 * n) for n in range(6)], fondo=True, mm=1.2, z=4)
            else:
                k.poli([pol((x, y), 4.2, 90 * n) for n in range(4)], True, z=4)


def v8(k):
    for i in range(5):
        k.pixel(-38 + i * 11.2, 137, PX["corazon"] if i < 3 else [".##.##.", "#..#..#", "#.....#", ".#...#.", "..#.#..", "...#..."], 1.45)
    for j, (w, y) in enumerate(((52, 122), (34, 120.5))):
        pass
    k.rect(16, 62, 44, 4.6, mm=1.1)
    k.rect(8, 62, 26, 3.0, True)
    k.rect(16, 54, 44, 4.6, mm=1.1)
    k.rect(0, 54, 10, 3.0, True)
    for i, d in enumerate("004820"):
        k.siete(-6 + i * 6.6, 40, d, 1.9)
    k.rect(-30, 46, 18, 18, mm=1.2)
    k.L([(-36, 40), (-36, 50), (-28, 50), (-28, 44), (-24, 44)], 0.9)
    k.punto(-26, 50, 1.2)
    k.pixel(-37, 12, PX["moneda"], 1.3)
    k.pixel(30, 9, PX["espada"], 1.2)
    for x in np.arange(-36, 38, 6):
        k.L([(x, 126), (x + 3.4, 126)], 1.2)


def v9(k):
    t = 9.0
    for j in range(-2, 18):
        for i in range(-6, 7):
            x, y = i * t + (t / 2 if j % 2 else 0), j * t * 0.5 + 2
            k.poli([(x, y + t * 0.25), (x + t / 2, y), (x, y - t * 0.25), (x - t / 2, y)], mm=0.85)
            if k.r.random() < 0.14 and y > 36:
                h = k.r.choice((5, 9, 13))
                k.poli([(x - t / 2, y), (x - t / 2, y + h), (x, y + h - t * 0.25), (x, y - t * 0.25)], fondo=True, mm=1.0, z=3.3 + (140 - y) * 0.001)
                k.poli([(x + t / 2, y), (x + t / 2, y + h), (x, y + h - t * 0.25), (x, y - t * 0.25)], True, z=3.3 + (140 - y) * 0.001)
                k.poli([(x, y + h + t * 0.25), (x + t / 2, y + h), (x, y + h - t * 0.25), (x - t / 2, y + h)], fondo=True, mm=1.0, z=3.3 + (140 - y) * 0.001)


def v10(k):
    for j, y in enumerate((134, 128, 122)):
        for x in np.arange(-36, 38, 8.2):
            if abs(x) > 14 or j == 0:
                k.rect(x + (4.1 if j % 2 else 0), y, 7, 3.6, j == 1, 1.0)
    pts = [(-30, 40), (-10, 64), (10, 40), (34, 62), (20, 40)]
    pts = [(-36, 44), (-22, 62), (-8, 40.5), (10, 64), (30, 40.5), (38, 52)]
    k.trazos(pts, 1.2, 2.2, 1.2)
    k.punto(38, 52, 1.8)
    k.rect(24, 37.6, 16, 2.8, True)
    k.L([(-39, 36), (-39, 66)], 1.1)
    k.L([(39, 36), (39, 66)], 1.1)
    for i, d in enumerate("0120"):
        k.siete(-36 + i * 6, 4, d, 1.6)
    for i in range(3):
        k.circ(24 + i * 6, 7, 1.8, i == 0)


# ═══════════ 5. MITOLOGIA CHINA ═══════════
def ch1(k):
    cuerpo = lambda t: (30 * math.sin(t * 2.6 * PI + 0.6) * (0.55 + 0.45 * t), 6 + 126 * t)  # noqa: E731
    for d in (-2.6, 2.6):
        k.curva(lambda t, d=d: (cuerpo(t)[0] + d, cuerpo(t)[1]), 0, 1, 160, 1.1)
    for t in np.linspace(0.03, 0.97, 44):
        x, y = cuerpo(t)
        k.arco(x, y - 1.2, 2.5, 20, 160, 0.85)
        if int(t * 100) % 4 == 0:
            k.poli([(x - 2.6, y), (x - 6.2, y + 1.6), (x - 2.6, y + 2.8)], True)
    hx, hy = cuerpo(1.0)
    k.poli(lente(hx + 2, hy + 1, 13, 7, 0.4), fondo=True, mm=1.2, z=3.4)
    k.punto(hx + 4, hy + 2.6, 1.0, 3.5)
    for s in (0.25, 0.75):
        k.curva(lambda t, s=s: (hx + 8 + 9 * t, hy + (s - 0.5) * 6 + 4 * math.sin(t * 5 + s * 9)), 0, 1, 30, 0.9)
    for x, y, t_, g in ((-28, 124, 1.5, 1), (30, 60, 1.4, -1), (-30, 48, 1.3, 1), (30, 118, 1.2, -1)):
        k.voluta(x, y, t_, g)


def ch2(k):
    for i, (x, y) in enumerate(k.disp(17, 17, (-34, 34, 6, 134))):
        k.voluta(x, y, k.r.choice((1.2, 1.5, 1.8)), 1 if i % 2 else -1)


def ch3(k):
    k.circ(22, 124, 8, mm=1.2)
    k.monte([(-42, 50), (-34, 66), (-28, 54), (-20, 74), (-12, 52), (-2, 46), (8, 58), (16, 44), (28, 62), (36, 48), (42, 52)], 3.0, 1.2, 3.6)
    k.monte([(-42, 38), (-26, 46), (-10, 36), (6, 44), (22, 34), (42, 42)], 3.2, 1.1, 3.6)
    for y in (26, 19, 12, 5):
        k.ola(y, 2.2, 13, y, 1.0, z=3.5)
    k.voluta(-26, 124, 1.5, 1)
    k.voluta(-34, 100, 1.1, 1)
    for x, y in ((-6, 132), (2, 128), (30, 104)):
        k.ave(x, y, 0.8)


def ch4(k):
    bits = ["111", "011", "101", "001", "000", "100", "010", "110"]
    for r in (13.5, 31, 46):
        k.poli([pol(OJO, r, 22.5 + 45 * i) for i in range(8)], mm=1.0)
    for i, b in enumerate(bits):
        p = pol(OJO, 22.5, 45 * i)
        k.trigrama(p[0], p[1], b, 1.0, 45 * i - 90)
    for i in range(8):
        k.L([pol(OJO, 31, 22.5 + 45 * i), pol(OJO, 46, 22.5 + 45 * i)], 0.9)
    for x, y, g in ((26, 126, -1), (-30, 126, 1), (30, 16, -1)):
        k.voluta(x, y, 1.4, g)


def ch5(k):
    t = 11.0
    for i in range(-4, 5):
        for j in range(0, 14):
            x, y = i * t, j * t - 4
            q = (i * 7 + j * 3) % 4
            if q == 0:
                k.L([(x, y), (x + t, y), (x + t, y + t * 0.55)], 1.1)
            elif q == 1:
                k.L([(x, y + t), (x, y + t * 0.3), (x + t * 0.6, y + t * 0.3)], 1.1)
            elif q == 2:
                k.L([(x + t * 0.3, y), (x + t * 0.3, y + t * 0.7), (x + t, y + t * 0.7)], 1.1)
            else:
                k.rect(x + t / 2, y + t / 2, t * 0.42, t * 0.42, mm=1.1)
    k.rect(0, 69.2, 80, 138.4, mm=1.4)


def ch6(k):
    def loto(x, y, r):
        for a in (30, 60, 90, 120, 150):
            k.hoja(x, y, r * (1.0 if a == 90 else 0.86), a, False, False, 0.5, 3.3)
        k.arco(x, y - 0.6, r * 0.9, 200, 340, 1.0, 3.3, ry=r * 0.35)
    for x, y, r in ((-26, 46, 9), (24, 54, 8), (-30, 124, 7), (32, 122, 6)):
        loto(x, y, r)
        for rr in (r * 1.3, r * 1.75):
            k.arco(x, y - 2, rr, 185, 355, 0.9, ry=rr * 0.3)
    for x, y, a in ((2, 40, 20), (30, 30, 200), (-34, 20, -30), (12, 128, 160)):
        k.pez(x, y, 0.9, a)
        k.circ(x - 6, y + 5, 1.1, mm=0.8)
    for y in (10, 3):
        k.ola(y, 1.6, 15, y, 0.9)


def ch7(k):
    k.circ(-16, 118, 20, mm=1.1)
    k.pagoda(26, 38, 1.6, 4)
    k.L([(-42, 38), (42, 38)], 1.2)
    for x, y, g in ((-28, 128, 1), (4, 132, -1), (-32, 58, 1), (-6, 46, 1)):
        k.voluta(x, y, 1.3, g)
    for x in (-36, -28, 8):
        k.arbol(x, 38, 10, "pino")
    for y in (28, 20, 12, 4):
        k.ola(y, 1.6, 16, y, 0.9)


def ch8(k):
    for x, y, t_, a in ((-26, 126, 1.5, 12), (22, 132, 1.2, -8), (30, 108, 1.0, 10), (-33, 98, 1.0, -6), (26, 56, 1.4, 8), (-30, 46, 1.1, -10), (4, 44, 0.9, 4)):
        k.ave(x, y, t_, a)
        k.L(tr([(0, -0.6), (0.8, -4.4), (1.8, -5.4)], x, y, t_, a), 0.9)
    k.circ(28, 126, 6.5, mm=1.1)
    for x, y, g in ((-30, 62, 1), (30, 40, -1), (-6, 14, 1), (30, 86, -1)):
        k.voluta(x, y, 1.3, g)
    k.rama([(-42, 30), (-30, 36), (-18, 34), (-8, 40)], 5, 6, True)


def ch9(k):
    ps = k.disp(15, 16, (-34, 34, 6, 134))
    for a, b in zip(ps, ps[1:]):
        k.L([a, b], 0.9, 2.9)
    for i, (x, y) in enumerate(ps):
        if i % 3 == 2:
            for g in (0, 45):
                k.rect(x, y, 8.4, 8.4, fondo=True, mm=1.1, ang=g, z=3.2)
            k.rect(x, y, 3.2, 3.2, True, ang=45, z=3.3)
        else:
            k.circ(x, y, 5.2, fondo=True, mm=1.2, z=3.2)
            k.rect(x, y, 3.2, 3.2, fondo=True, mm=1.0, z=3.3)
            for a in (45, 135, 225, 315):
                p = pol((x, y), 3.7, a)
                k.punto(p[0], p[1], 0.55, 3.3)


def ch10(k):
    k.L([(-42, 136), (42, 136)], 1.1)
    for x, largo, t_ in ((-33, 12, 1.0), (-20, 22, 1.25), (22, 16, 1.1), (34, 30, 0.9), (30, 86, 1.0), (-34, 78, 0.9)):
        y = 136 - largo - 7 * t_
        k.L([(x, 136 if largo < 40 else y + 20), (x, y + 6 * t_)], 0.9)
        k.elipse(x, y, 4.6 * t_, 6.2 * t_, 0, fondo=True, mm=1.2, z=3.2)
        for d in (-2.3, 0, 2.3):
            k.arco(x + d * t_ * 0.0, y, abs(d) * t_ + 0.01, 0, 360, 0.8, 3.3, ry=6.2 * t_)
        k.rect(x, y + 6.4 * t_, 4 * t_, 1.4 * t_, True, z=3.3)
        k.rect(x, y - 6.4 * t_, 4 * t_, 1.4 * t_, True, z=3.3)
        for d in (-1.2, 0, 1.2):
            k.L([(x + d * t_, y - 7 * t_), (x + d * t_, y - 12 * t_)], 0.8)
    for x, y, g in ((-26, 50, 1), (24, 44, -1), (0, 14, 1)):
        k.voluta(x, y, 1.4, g)


# ═══════════ 6. MITOLOGIA GRIEGA ═══════════
def g1(k):
    for y in (130, 119, 44, 2):
        k.greca(y, 1.05)
    k.laurel(22, 56, 12, 9, 200, 520, 22, 6)
    for x in (-38, 38):
        k.L([(x, 0), (x, 139)], 1.2)


def g2(k):
    k.poli([(-40, 120), (0, 137), (40, 120)], mm=1.3)
    k.poli([(-31, 122), (0, 134), (31, 122)], mm=0.9)
    k.rect(0, 118.5, 80, 3, mm=1.1)
    for x in (-35.5, 35.5):
        k.columna(x, 40, 77, 5.2)
    for y, w in ((38.5, 80), (35.5, 84), (32.5, 88)):
        k.rect(0, y, w, 3, mm=1.1)
    for x in np.arange(-36, 38, 6):
        k.L([(x, 117), (x, 113.5)], 0.9)
    k.greca(4, 1.0)
    k.laurel(22, 54, 11, 8, 200, 520, 24, 5.5)


def g3(k):
    for i, r in enumerate(np.arange(11, 96, 6.4)):
        g = (i * 137) % 360
        k.arco(OJO[0], OJO[1], r, g + 14, g + 346, 1.1)
        if i % 2 == 0:
            p0, p1 = pol(OJO, r, g + 180), pol(OJO, r + 6.4, g + 180)
            k.L([p0, p1], 1.1)


def g4(k):
    k.cielo(46, 4)
    base = (0, -8)
    for i, a in enumerate(range(30, 151, 10)):
        l = 96 + (18 if i % 2 else 0) + (26 if i % 4 == 0 else 0)
        k.L([base, pol(base, l, a)], 0.9)
        p = pol(base, l, a)
        k.poli(lente(p[0], p[1], 9.5, 6.4, math.radians(a)), fondo=True, mm=1.0, z=3.3)
        k.punto(p[0], p[1], 1.5, 3.4)
    for r in (20, 34, 48):
        k.arco(base[0], base[1], r, 30, 150, 0.9)


def g5(k):
    k.laurel(VC[0], VC[1], 37, 27, 250, 430, 9.5, 8.5)
    k.laurel(VC[0], VC[1], 37, 27, 70, 250, 9.5, 8.5)
    k.greca(1.5, 1.0)
    for x, y in ((-32, 44), (32, 44), (-34, 132), (34, 132)):
        k.estrella(x, y, 3.2, 8)


def g6(k):
    def anfora(x, y, t_):
        pts = [(0, 0), (2.2, 0), (2.6, 1), (1.6, 2), (4.6, 6), (5.2, 10), (3.6, 14), (1.8, 16), (2.4, 19), (3, 20)]
        full = [(x + u * t_, y + v * t_) for u, v in pts] + [(x - u * t_, y + v * t_) for u, v in pts[::-1]]
        k.poli(full, fondo=True, mm=1.2, z=3.2)
        for v in (7.5, 11.5):
            k.L([(x - 4.6 * t_, y + v * t_), (x + 4.6 * t_, y + v * t_)], 0.9, 3.3)
        for s in (-1, 1):
            k.arco(x + s * 3.9 * t_, y + 16 * t_, 2.8 * t_, 90 if s > 0 else -90, 270 if s > 0 else 90, 1.0, 3.3, ry=3.4 * t_)
    for x, y, t_ in ((26, 38, 1.15), (-30, 118, 0.85)):
        anfora(x, y, t_)
    k.rama([(-42, 44), (-30, 50), (-18, 48), (-8, 54)], 5, 6.5, True)
    k.rama([(42, 122), (30, 128), (18, 126), (8, 132)], 5, 6.5, True)
    k.rama([(-40, 8), (-24, 14), (-8, 10), (8, 16), (24, 12), (40, 18)], 5, 6, True)
    k.greca(0.5, 0.9)


def g7(k):
    for y in (128, 46, 6):
        for x in np.arange(-44, 44, 11):
            k.curva(lambda a, x=x, y=y: (x + 5.5 + (0.5 + 0.36 * a) * math.cos(a + PI), y + 3.4 + (0.5 + 0.36 * a) * math.sin(a + PI)), 0, 2.6 * PI, 40, 1.0)
            k.L([(x, y), (x + 11, y)], 1.0)
    for x, t_ in ((30, 1.0),):
        k.L([(x, 14), (x, 44)], 1.3)
    k.L([(26, 60), (26, 20)], 1.4)
    for d in (-5, 0, 5):
        k.L([(26 + d, 54), (26 + d, 64)], 1.3)
        k.poli([(26 + d - 1.6, 63), (26 + d, 67), (26 + d + 1.6, 63)], True)
    k.L([(21, 54), (31, 54)], 1.3)
    for y in (36, 28, 20):
        k.ola(y, 2.0, 14, y, 0.95, -42, 16)


def g8(k):
    k.cielo(48, 5)
    x, y, t_ = 24, 40, 1.25
    k.poli([(x - 6 * t_, y + 16 * t_), (x - 7 * t_, y + 6 * t_), (x - 4 * t_, y), (x + 4 * t_, y), (x + 7 * t_, y + 6 * t_), (x + 6 * t_, y + 16 * t_)], mm=1.3)
    k.L([(x - 7.6 * t_, y + 16 * t_), (x + 7.6 * t_, y + 16 * t_)], 1.5)
    for d in (-3.6, -1.2, 1.2, 3.6):
        k.L([(x + d * t_, y + 1.2 * t_), (x + d * t_, y + 16 * t_)], 0.85)
    k.ruta([(-34, 46), (-28, 58), (-34, 122), (-22, 132), (10, 134), (30, 126), (36, 104)], 0.9, 1.5)
    k.laurel(-28, 46, 8, 6, 200, 520, 30, 5)


def g9(k):
    base = (OJO[0], OJO[1])
    for i, a in enumerate(range(0, 360, 15)):
        l = 26 + (i % 3) * 16 + (20 if i % 2 else 0)
        k.L([pol(base, 12, a), pol(base, l, a)], 0.9)
        p = pol(base, l + 3, a)
        k.poli(lente(p[0], p[1], 9, 5.6, math.radians(a)), fondo=True, mm=1.0, z=3.3)
        k.rect(p[0], p[1], 1.9, 1.9, True, ang=a, z=3.4)
        for d in (5, 9, 13):
            q = pol(base, 12 + d, a)
            for s in (-1, 1):
                k.L([q, pol(q, 2.6, a + s * 50)], 0.75)


def g10(k):
    k.monte([(-42, 40), (-28, 60), (-18, 54), (-6, 78), (4, 60), (14, 66), (26, 46), (42, 40)], 3.0, 1.3, 3.8)
    for x, y, t_ in ((-26, 124, 1.2), (20, 128, 1.4), (30, 104, 0.9), (-33, 100, 0.9)):
        k.nube(x, y, t_)
    for x, y, t_, a in ((-24, 108, 0.9, 8), (22, 112, 1.0, -6), (32, 88, 0.7, 4)):
        k.rayo(x, y, t_, a)
    k.greca(1.5, 1.0)
    k.columna(34, 12, 28, 5)


# ═══════════ 7. MITOLOGIA NORDICA ═══════════
def n1(k):
    def rama(x, y, ang, largo, nivel, arriba):
        x2, y2 = x + largo * math.cos(ang), y + largo * math.sin(ang)
        k.L([(x, y), (x2, y2)], 0.9 + 0.2 * nivel)
        if nivel:
            for s in (-1, 1):
                rama(x2, y2, ang + s * math.radians(k.r.uniform(20, 36)), largo * 0.74, nivel - 1, arriba)
        elif arriba:
            k.punto(x2, y2, 1.0)
    k.L([(0, 36), (0, 70)], 2.4)
    rama(0, 70, PI / 2, 22, 6, True)
    rama(0, 36, -PI / 2, 12, 5, False)
    k.circ(0, 60, 62, mm=1.0)
    k.circ(0, 60, 66, mm=0.9)


def n2(k):
    nombres = ["ansuz", "raido", "gebo", "isa", "tiwaz", "berkano", "laguz", "dagaz", "kenaz", "fehu", "uruz", "mannaz"]
    for sx in (-37.5, 33.5):
        for i, y in enumerate(np.arange(4, 134, 9.4)):
            k.runa(sx, y, nombres[(i + (0 if sx < 0 else 5)) % 12], 3.2, 1.2)
    for x0, y in ((-26, 124), (-26, 46), (-26, 2)):
        for i, x in enumerate(np.arange(x0, 30, 6.4)):
            if not (y == 124 and -14 < x < 12):
                k.runa(x, y, nombres[(i * 5 + int(y)) % 12], 3.0, 1.2)
    for y in (135.5, 41.5):
        k.L([(-30, y), (30, y)], 1.0)


def n3(k):
    k.cielo(40, 4, (-39, 39, 100, 137))
    x, y = 2, 40
    k.poli([(x - 30, y + 10), (x - 22, y), (x + 20, y), (x + 30, y + 10), (x + 22, y + 5), (x - 22, y + 5)], fondo=True, mm=1.3, z=3.3)
    k.curva(lambda t: (x + 30 + 3 * math.sin(t * 3), y + 10 + 10 * t), 0, 1, 20, 1.3)
    k.curva(lambda t: (x + 30.5 + 3 * math.cos(t * 5), y + 21.5 + 3 * math.sin(t * 5)), 0, 1, 20, 1.2)
    k.L([(x, y + 5), (x, y + 30)], 1.3, 3.4)
    for xx in np.arange(x - 18, x + 20, 6):
        k.circ(xx, y + 3.2, 2.5, fondo=True, mm=1.0, z=3.5)
        k.punto(xx, y + 3.2, 0.7, 3.6)
    for y_ in (30, 23, 16, 9, 2):
        k.ola(y_, 2.2, 13, y_, 1.0, z=3.7)
    k.luna(-30, 126, 6.5, 0.4, 20)


def n4(k):
    for y0 in (130, 122, 46, 4):
        for f in (0, PI):
            k.ola(y0, 2.8, 12, f, 1.4)
    for x0 in (-37, 37):
        for f in (0, PI):
            k.curva(lambda t, x0=x0, f=f: (x0 + 2.6 * math.sin(2 * PI * t * 11 + f), 139 * t), 0, 1, 200, 1.4)
    for x, y in ((-37, 126), (37, 126), (-37, 46), (37, 46), (-37, 4), (37, 4)):
        k.rect(x, y, 7.5, 7.5, fondo=True, mm=1.2, ang=45, z=3.4)
        k.punto(x, y, 1.2, 3.5)


def n5(k):
    def cuervo(x, y, t_, s):
        k.poli(tr([(-8 * s, 2), (-2 * s, 3.6), (4 * s, 2.6), (8 * s, 4.6), (5 * s, 0.6), (9 * s, -0.6), (3 * s, -1.4), (-3 * s, -1), (-9 * s, -5)], x, y, t_), True, z=3.3)
    k.circ(0, 118, 15, mm=1.1)
    cuervo(-24, 128, 1.0, 1)
    cuervo(26, 126, 1.0, -1)
    k.monte([(-42, 44), (-30, 52), (-16, 44), (0, 50), (18, 43), (42, 50)], 3.0, 1.2)
    for x in np.arange(-38, 40, 7):
        k.arbol(x, 34 + (int(x) % 3) * 2, 12 + (int(x) % 4), "pino")
    for x, y in ((-34, 100), (34, 96), (-30, 74), (34, 70)):
        k.estrella(x, y, 2.4)


def n6(k):
    for x0 in np.arange(-38, 40, 4.6):
        f, h = k.r.uniform(0, 6), k.r.uniform(26, 58)
        k.curva(lambda t, x0=x0, f=f, h=h: (x0 + 2.2 * math.sin(t * 5 + f), 138 - h * t), 0, 1, 40, 0.9 + 0.5 * k.r.random())
    k.monte([(-42, 40), (-32, 58), (-24, 48), (-12, 70), (-2, 52), (10, 62), (20, 46), (32, 60), (42, 44)], 3.0, 1.3, 3.6)
    for x, y in ((-12, 70), (10, 62), (-32, 58), (32, 60)):
        k.L([(x - 3, y - 5), (x - 1, y - 3.4), (x + 1, y - 5.4), (x + 3, y - 3.6)], 0.9, 3.4)
    for y in (24, 16, 8):
        k.ola(y, 1.8, 14, y, 0.95, z=3.5)


def n7(k):
    for r in (33, 39):
        k.elipse(VC[0], VC[1], r + 6, r - 4, 0, mm=1.2)
    for a in range(0, 360, 8):
        p0 = (VC[0] + 39.6 * math.cos(math.radians(a)), VC[1] + 29.6 * math.sin(math.radians(a)))
        p1 = (VC[0] + 44.4 * math.cos(math.radians(a + 4)), VC[1] + 34.4 * math.sin(math.radians(a + 4)))
        k.L([p0, p1], 0.85)
    hx, hy = VC[0] + 42 * math.cos(math.radians(250)), VC[1] + 32 * math.sin(math.radians(250))
    k.poli(lente(hx, hy, 14, 8, math.radians(165)), fondo=True, mm=1.2, z=3.4)
    k.punto(hx - 3, hy + 1.2, 1.1, 3.5)
    k.L([(hx - 7, hy + 1.5), (hx - 11, hy + 3), (hx - 10, hy)], 0.9, 3.5)
    for x in np.arange(-38, 40, 9.4):
        k.runa(x, 4, ["ansuz", "raido", "gebo", "isa", "tiwaz", "berkano", "laguz", "dagaz", "kenaz"][int((x + 38) / 9.4) % 9], 2.6, 1.1)


def n8(k):
    x, y = 24, 38
    k.rect(x, y + 18, 16, 9, fondo=True, mm=1.3, z=3.3)
    k.rect(x, y + 8, 3.6, 12, fondo=True, mm=1.2, z=3.2)
    k.rect(x, y + 1.4, 5.6, 2.8, True, z=3.3)
    for d in (-4, 0, 4):
        k.L([(x + d, y + 15), (x + d, y + 21)], 0.85, 3.4)
    for x_, y_, t_, a in ((-28, 118, 1.1, 10), (28, 122, 1.0, -12), (-32, 52, 0.9, -8), (0, 12, 0.9, 6)):
        k.rayo(x_, y_, t_, a)
    for x_, y_, t_ in ((-24, 132, 1.0), (22, 134, 0.9), (-6, 46, 0.8)):
        k.nube(x_, y_, t_)
    for x_ in np.arange(-38, 40, 9.4):
        k.runa(x_, 1.5, "tiwaz" if int(x_) % 2 else "isa", 2.2, 1.0)


def n9(k):
    for i, a in enumerate(range(0, 360, 45)):
        l = 62 if i % 2 == 0 else 50
        k.L([pol(OJO, 12, a), pol(OJO, l, a)], 1.2)
        for d, w in ((0.45, 4), (0.62, 5.5), (0.8, 4)):
            q = pol(OJO, l * d + 6, a)
            k.L([pol(q, w, a + 90), pol(q, w, a - 90)], 1.1)
        p = pol(OJO, l, a)
        if i % 2 == 0:
            k.arco(p[0], p[1], 3.4, a - 90, a + 90, 1.1)
        else:
            k.L([pol(p, 3.6, a + 135), p, pol(p, 3.6, a - 135)], 1.1)
    for r in (72, 78):
        k.circ(OJO[0], OJO[1], r, mm=0.95)


def n10(k):
    for i, (x, y) in enumerate(k.disp(13, 19.5, (-32, 32, 6, 134))):
        r = 9.0
        k.circ(x, y, r, fondo=True, mm=1.3, z=3.2)
        k.circ(x, y, 2.2, True, z=3.4)
        if i % 3 == 0:
            for a in (0, 90):
                k.L([pol((x, y), r, a), pol((x, y), r, a + 180)], 0.95, 3.3)
        elif i % 3 == 1:
            for a in range(0, 360, 45):
                k.L([pol((x, y), 3.4, a), pol((x, y), r, a + 30)], 0.9, 3.3)
        else:
            k.circ(x, y, r * 0.62, mm=0.95, z=3.3)
            for a in range(0, 360, 30):
                p = pol((x, y), r * 0.82, a)
                k.punto(p[0], p[1], 0.55, 3.3)


# ═══════════ 8. JAPON ═══════════
def j1(k):
    r = 6.4
    for j in range(0, 10):
        for i in range(-5, 6):
            x, y = i * 2 * r + (r if j % 2 else 0), j * r * 0.9
            for f in (1.0, 0.66, 0.34):
                k.arco(x, y, r * f, 0, 180, 0.95)
    k.circ(22, 124, 9, True)
    for x, y, t_ in ((-22, 126, 1.2), (-32, 102, 0.9)):
        k.nube(x, y, t_)


def j2(k):
    k.circ(-20, 120, 10, mm=1.2)
    xs, ys = k.monte([(-42, 40), (-26, 44), (-9, 70), (-5, 67), (-1, 70), (3, 66), (8, 70), (26, 44), (42, 40)], 3.0, 1.3)
    k.L([(-12, 62), (-8, 58), (-4, 62), (0, 58), (4, 62), (8, 58), (11, 62)], 1.0, 3.2)
    for y in (36, 28, 20, 12, 4):
        k.trazos([(-42, y), (42, y)], 9, 3.4, 0.95)
    for x, y, t_ in ((24, 128, 1.1), (30, 104, 0.8)):
        k.nube(x, y, t_)
    for x, y in ((4, 132), (10, 128), (-2, 126)):
        k.ave(x, y, 0.7)


def j3(k):
    k.torii(20, 38, 1.75)
    k.L([(-42, 38), (42, 38)], 1.2)
    k.poli([(14, 38), (26, 38), (36, 0), (4, 0)], mm=1.0)
    for y in (30, 21, 11):
        k.L([(14 - (38 - y) * 0.26, y), (26 + (38 - y) * 0.26, y)], 0.9)
    for x in (-36, -28, -18):
        k.arbol(x, 38, 13, "pino")
    k.circ(-22, 124, 8, mm=1.2)
    k.nube(22, 128, 1.0)
    for x, y in ((-32, 22), (-20, 12), (-34, 6)):
        k.circ(x, y, 3.4, mm=1.0)


def j4(k):
    k.L([(-42, 130), (-26, 126), (-10, 132), (8, 124), (22, 130)], 1.6)
    k.L([(-26, 126), (-32, 108), (-36, 96)], 1.3)
    k.L([(8, 124), (20, 118), (34, 120)], 1.2)
    k.L([(42, 44), (28, 52), (14, 46), (2, 54)], 1.5)
    k.L([(28, 52), (32, 66)], 1.2)
    for x, y in ((-34, 132), (-18, 130), (-2, 128), (16, 127), (30, 121), (-33, 104), (-36, 92), (36, 46), (22, 50), (8, 50), (32, 62), (33, 70)):
        k.sakura(x, y, 3.3)
    for x, y in k.disp(16, 8, (-36, 36, 4, 40)):
        k.hoja(x, y, 3.6, k.r.uniform(0, 360), True, False, 0.6)


def j5(k):
    k.curva(lambda t: (-42 + 70 * t, 40 + 36 * t ** 0.8 + 16 * math.sin(t * PI) ** 2), 0, 1, 80, 1.4)
    k.curva(lambda t: (28 + 13 * math.cos(PI * (0.5 - 1.5 * t)), 78 + 12 * math.sin(PI * (0.5 - 1.5 * t)) - 4 * t), 0, 1, 50, 1.4)
    for i in range(1, 6):
        k.curva(lambda t, i=i: (-42 + 62 * t, 40 - i * 7 + 30 * t ** (0.9 + 0.12 * i) + 8 * math.sin(t * PI)), 0, 1, 60, 1.0)
    for a in range(-60, 100, 22):
        p = pol((28, 80), 16, a)
        k.circ(p[0], p[1], 1.6, mm=0.9)
        q = pol((28, 80), 21, a + 9)
        k.punto(q[0], q[1], 0.8)
    k.circ(-24, 124, 8, True)
    for y in (10, 3):
        k.ola(y, 2.2, 13, y, 1.0)


def j6(k):
    for x, y, a in ((-24, 48, 25), (24, 56, 200), (30, 124, 150), (-30, 122, -30), (4, 40, 80)):
        k.pez(x, y, 1.5, a)
    for x, y in ((-10, 56), (34, 40), (-34, 100), (20, 132), (-6, 12), (30, 94)):
        for r in (3, 6.2, 9.6):
            k.arco(x, y, r, 0, 360, 0.9, ry=r * 0.45)
    for x, y in ((-34, 62), (12, 48), (-20, 130)):
        k.hoja(x, y, 7, 60, True)


def j7(k):
    for x in (-36, -29, 31, 37):
        k.bambu(x, -2, 142)
    k.bambu(22, -2, 76)
    k.circ(-8, 126, 7, mm=1.2)
    for x, y, a in ((-20, 52), (10, 58), (-14, 44)) and ((-20, 52, 20), (10, 58, 160), (-14, 44, 200)):
        k.hoja(x, y, 9, a, True, False, 0.24)


def j8(k):
    for i, (x, y) in enumerate(k.disp(11, 21, (-28, 28, 12, 130))):
        k.abanico(x, y - 5, 10.5, 90 + k.r.uniform(-28, 28), 130, 8)
    for x, y in k.disp(14, 9, (-38, 38, 4, 136)):
        k.punto(x, y, 0.8)


def j9(k):
    def grulla(x, y, t_, a):
        k.poli(tr([(0, 0), (-9, 5), (-2, 1.2)], x, y, t_, a), fondo=True, mm=1.0, z=3.3)
        k.poli(tr([(0, 0), (9, 5), (2, 1.2)], x, y, t_, a), fondo=True, mm=1.0, z=3.3)
        k.poli(tr([(-2, 1.2), (0, 7), (2, 1.2), (0, -1.2)], x, y, t_, a), True, z=3.35)
        k.L(tr([(0, 7), (1.6, 10), (4, 9.2)], x, y, t_, a), 1.0, 3.4)
        k.L(tr([(0, -1.2), (-1, -6)], x, y, t_, a), 1.0, 3.4)
    for x, y, t_, a in ((-26, 124, 1.0, 20), (22, 130, 0.9, -15), (30, 60, 1.2, 10), (-30, 50, 1.0, -20), (2, 44, 0.8, 5), (-32, 96, 0.8, 30), (33, 96, 0.8, -25)):
        grulla(x, y, t_, a)
    for x, y, t_ in ((-6, 16, 1.0), (28, 22, 0.9)):
        k.nube(x, y, t_)
    k.circ(-8, 128, 6, True)


def j10(k):
    for x in np.arange(-40, 41, 13.33):
        k.L([(x, 0), (x, 139)], 1.3)
    for y in np.arange(0, 140, 17.3):
        k.L([(-40, y), (40, y)], 0.95)
    k.arco(18, 50, 15, 30, 350, 3.4, 3.6)
    k.arco(18, 50, 15, 345, 352, 1.4, 3.6)
    k.rama([(-42, 126), (-32, 130), (-22, 126)], 4.6, 5.6, True)


# ═══════════ 9. UNIVERSO ═══════════
def u1(k):
    k.cielo(60, 4)
    k.galaxia(OJO[0], OJO[1], 62, 2, 1.7, True)
    k.galaxia(28, 126, 9, 2, 1.2, False)


def u2(k):
    for i, (a, b) in enumerate(((40, 26), (46, 30), (53, 35), (61, 41), (70, 48), (80, 56))):
        k.elipse(VC[0], VC[1], a, b, -14, mm=0.9 + 0.12 * (5 - i))
    for a in range(0, 360, 10):
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        p0 = tr([(34 * c, 22 * s)], VC[0], VC[1], 1, -14)[0]
        p1 = tr([(38.6 * c, 25 * s)], VC[0], VC[1], 1, -14)[0]
        k.L([p0, p1], 0.85)
    k.cielo(34, 3)


def u3(k):
    ps = k.disp(70, 6.4)
    for i, p in enumerate(ps):
        d = sorted(ps, key=lambda q: math.hypot(q[0] - p[0], q[1] - p[1]))[1:3]
        for q in d:
            k.L([p, q], 0.85, 2.9)
    for i, p in enumerate(ps):
        k.punto(p[0], p[1], 1.9 if i % 9 == 0 else 1.0, 4)


def u4(k):
    c = (-2, 48)
    for f in (0, PI):
        k.curva(lambda t, f=f: (c[0] + (4 + 4.4 * t) * math.cos(t + f), c[1] + (4 + 4.4 * t) * math.sin(t + f)), 0, 9.5 * PI, 500, 1.0)
    for f in (0, PI):
        p = (c[0] + 4 * math.cos(f), c[1] + 4 * math.sin(f))
        k.punto(p[0], p[1], 2.2, 4)


def u5(k):
    c = (20, 50)

    def mapa(x, y):
        dx, dy = x - c[0], y - c[1]
        d = math.hypot(dx, dy) + 1e-6
        f = 1 - 0.62 * math.exp(-(d / 22) ** 2)
        return c[0] + dx * f, c[1] + dy * f
    for v in np.arange(-70, 180, 5.4):
        k.L([mapa(x, v) for x in np.linspace(-60, 80, 160)], 0.9)
        k.L([mapa(v - 30, y) for y in np.linspace(-20, 160, 160)], 0.9)
    k.punto(c[0], c[1], 3.2, 4)
    k.planeta(-28, 126, 4, True, 20)


def u6(k):
    o = (-40, 0)
    for i, r in enumerate((14, 26, 40, 56, 74, 94, 116, 140)):
        k.arco(o[0], o[1], r, 0, 90, 0.9 + 0.08 * i)
    for a in (8, 26, 45, 64, 82):
        k.trazos([pol(o, 10, a), pol(o, 150, a)], 2.6, 2.4, 0.85)
    for i, r in enumerate((20, 33, 48, 65, 84, 105, 128)):
        for a in np.arange(12, 90, 180 / (i + 2)):
            p = pol(o, r, a + i * 5)
            (k.galaxia(p[0], p[1], 3.4, 2, 0.9, False) if i > 3 and int(a) % 2 == 0 else k.punto(p[0], p[1], 0.7 + 0.1 * i))
    k.estrella(o[0] + 3, o[1] + 3, 5, 8)


def u7(k):
    for x, y in k.disp(900, 1.9, intentos=9000):
        d1 = math.exp(-((x + 16) ** 2 + (y - 46) ** 2) / 700)
        d2 = math.exp(-((x - 20) ** 2 + (y - 122) ** 2) / 500)
        d3 = math.exp(-((x - 30) ** 2 + (y - 40) ** 2) / 300)
        d = d1 + d2 + 0.8 * d3
        if k.r.random() < 0.12 + 0.95 * d:
            k.punto(x, y, 0.42 + 0.75 * min(1, d))
    for x, y in ((-16, 46), (20, 122), (30, 40)):
        k.estrella(x, y, 3.4, 4)


def u8(k):
    for i, (x, y) in enumerate(k.disp(16, 15, (-33, 33, 6, 133))):
        r = k.r.choice((5.5, 7, 9))
        k.circ(x, y, r, mm=1.0)
        k.arco(x, y, r * 0.8, 100, 160, 0.85)
        if i % 3 == 0:
            k.galaxia(x, y, r * 0.62, 2, 1.0, False)
        elif i % 3 == 1:
            for _ in range(7):
                a, d = k.r.uniform(0, 360), k.r.uniform(0, r * 0.62)
                p = pol((x, y), d, a)
                k.punto(p[0], p[1], 0.6)
        else:
            k.planeta(x, y, r * 0.3, True, 20)


def u9(k):
    for i in range(15):
        a = i * 24 + k.r.uniform(-4, 4)
        l = k.r.uniform(26, 96)
        k.L([pol(OJO, 12, a), pol(OJO, l, a)], 0.95)
        for d in np.arange(l - 14, l - 1, 2.2):
            if k.r.random() < 0.6:
                q = pol(OJO, d, a)
                k.L([pol(q, 1.9, a + 90), pol(q, 1.9, a - 90)], 0.85)
        p = pol(OJO, l, a)
        k.punto(p[0], p[1], 1.2)
    k.cielo(26, 2)


def u10(k):
    for g in (0, 60, 120):
        k.elipse(-27, 16, 10, 4, g, mm=0.95)
    k.punto(-27, 16, 1.8)
    k.trazos([(-18, 22), (10, 44)], 2.2, 2.0, 0.85)
    for i, (a, b) in enumerate(((7, 3), (12, 5.4), (18, 8))):
        k.elipse(22, 52, a, b, 14, mm=0.9)
    k.punto(22, 52, 2.0)
    k.punto(33, 56.5, 1.1)
    k.trazos([(30, 64), (33, 100)], 2.2, 2.0, 0.85)
    k.galaxia(24, 124, 14, 2, 1.5, True)
    k.trazos([(8, 128), (-18, 130)], 2.2, 2.0, 0.85)
    for x, y in k.disp(10, 5, (-38, -20, 116, 136)):
        k.galaxia(x, y, 2.4, 2, 0.8, False)
    k.cielo(30, 2)


# ═══════════ 10. FULL TECNOLOGICO ═══════════
def t1(k):
    for i in range(9):
        d = 3.0 * i
        k.pista([(-40 + d, 0), (-40 + d, 30 - d), (-22 + d, 48 - d), (-22 + d, 58 + i * 0.6)], 1.0, True)
        k.pista([(40 - d, 139), (40 - d, 108 + d * 0.4), (33 - d * 0.2, 100 + d * 0.3)], 1.0, False)
    for i in range(7):
        d = 3.0 * i
        k.pista([(40, 20 + d), (22 - d, 20 + d), (10 - d, 32 + d), (10 - d, 44 + d * 0.4)], 1.0, True)
        k.pista([(-40, 132 - d), (-36 + d * 0.4, 132 - d), (-34 + d * 0.4, 122 - d * 0.2)], 1.0, i % 2 == 0)
    for x, y in ((28, 56), (33, 64), (22, 64), (-33, 100), (-36, 88)):
        k.nodo(x, y, 1.9, True)
    k.rect(26, 126, 14, 9, mm=1.2)
    for x in np.arange(21, 32, 2.6):
        k.L([(x, 130.5), (x, 133)], 0.9)
        k.L([(x, 121.5), (x, 119)], 0.9)


def t2(k):
    for r in np.arange(13, 150, 7.2):
        k.arco(OJO[0], OJO[1], r, 22, 68, 1.0 + 0.4 * (int(r) % 2))
        k.arco(OJO[0], OJO[1], r, 202, 248, 0.9)
    for x, y in ((30, 126), (34, 96), (-30, 20), (14, 10), (-36, 44)):
        k.nodo(x, y, 2.2, True)
        for rr in (4.5, 7):
            k.arco(x, y, rr, 60, 120, 0.9)
    k.trazos([(-30, 20), (14, 10)], 2.2, 1.8)
    k.trazos([(30, 126), (34, 96)], 2.2, 1.8)


def t3(k):
    nodos = {"dht": (-33, 124), "pir": (33, 126), "puerta": (34, 52), "acel": (-34, 46), "luz": (0, 6)}
    borde = {"dht": (-34, 110), "pir": (34, 110), "puerta": (34, 84), "acel": (-34, 84), "luz": (0, 40)}
    for n, p in nodos.items():
        b = borde[n]
        k.L([p, (p[0], (p[1] + b[1]) / 2), (b[0], (p[1] + b[1]) / 2), b], 1.0)
        m = ((p[0] + b[0]) / 2, (p[1] + b[1]) / 2)
        k.rect(m[0], m[1], 3.4, 2.2, True, z=4)
        k.hexagono(p[0], p[1], 5.6, False, 1.3)
        k.circ(p[0], p[1], 2.0, True, z=4)
    for x in np.arange(-36, 38, 6):
        k.punto(x, 136, 0.6)
        k.punto(x, 2, 0.6)
    k.corchetes(-39, 0.5, 39, 138, 5)


def t4(k):
    def resistencia(x, y, horizontal=True):
        z = [(0, 0), (2, 0), (3, 2), (5, -2), (7, 2), (9, -2), (11, 2), (12, 0), (14, 0)]
        k.L([(x + u, y + v) if horizontal else (x + v, y + u) for u, v in z], 1.0)

    def capacitor(x, y):
        k.L([(x, y), (x + 5, y)], 1.0)
        k.L([(x + 5, y - 3), (x + 5, y + 3)], 1.2)
        k.L([(x + 7, y - 3), (x + 7, y + 3)], 1.2)
        k.L([(x + 7, y), (x + 12, y)], 1.0)

    def tierra(x, y):
        k.L([(x, y), (x, y - 3)], 1.0)
        for i, w in enumerate((3.4, 2.2, 1.0)):
            k.L([(x - w, y - 3 - i * 1.5), (x + w, y - 3 - i * 1.5)], 1.0)
    k.L([(-36, 132), (36, 132)], 1.0)
    k.L([(-36, 132), (-36, 44), (-22, 44)], 1.0)
    resistencia(-22, 44)
    k.L([(-8, 44), (4, 44)], 1.0)
    capacitor(4, 44)
    k.L([(16, 44), (36, 44), (36, 132)], 1.0)
    for x in (-36, 36):
        k.nodo(x, 60, 1.4)
    resistencia(36, 62, False)
    resistencia(-36, 80, False)
    k.L([(4, 44), (4, 38)], 1.0)
    tierra(4, 38)
    k.L([(-20, 132), (-20, 126)], 1.0)
    k.poli([(-23, 126), (-17, 126), (-20, 121)], mm=1.0)
    k.L([(-23, 121), (-17, 121)], 1.1)
    k.L([(-20, 121), (-20, 117)], 1.0)
    for x, y in ((-36, 132), (36, 132), (4, 44), (-20, 132)):
        k.nodo(x, y, 1.4)
    capacitor(14, 132)
    for x in (-30, 26):
        k.L([(x, 14), (x + 8, 14)], 1.0)
        k.circ(x + 12, 14, 4, mm=1.0)
        k.L([(x + 16, 14), (x + 22, 14)], 1.0) if x < 0 else None
    tierra(-10, 20)


def t5(k):
    for j, y in enumerate((126, 44, 22, 3)):
        txt = ("2468", "22-28", "40-60", "8266")[j]
        x = -34 if j else 16
        for i, d in enumerate(txt):
            k.siete(x + i * 8.6 + (-22 if j == 0 else 0) * 0 + (0 if j else 0), y, d, 2.4)
    for x in np.arange(-36, 38, 3.4):
        k.punto(x, 38, 0.55)
        k.punto(x, 60, 0.55)
    for y in np.arange(64, 120, 5.6):
        for x in (-37, -33.4, 33.4, 37):
            (k.rect(x, y, 2.2, 3.4, True) if k.r.random() < 0.5 else k.rect(x, y, 2.2, 3.4, mm=0.85))


def t6(k):
    def partir(x, y, w, h, n):
        if n == 0 or min(w, h) < 9:
            q = k.r.random()
            k.rect(x + w / 2, y + h / 2, w - 1.8, h - 1.8, q < 0.14, 1.0)
            if 0.14 <= q < 0.5 and min(w, h) > 8:
                for v in np.arange(y + 3.2, y + h - 2.4, 2.8):
                    k.L([(x + 2.6, v), (x + w - 2.6, v)], 0.8)
            elif 0.5 <= q < 0.7:
                for u in np.arange(x + 3, x + w - 2, 3):
                    for v in np.arange(y + 3, y + h - 2, 3):
                        k.punto(u, v, 0.5)
            return
        if (w > h and k.r.random() < 0.8) or h < 12:
            f = k.r.uniform(0.35, 0.65)
            partir(x, y, w * f, h, n - 1)
            partir(x + w * f, y, w * (1 - f), h, n - 1)
        else:
            f = k.r.uniform(0.35, 0.65)
            partir(x, y, w, h * f, n - 1)
            partir(x, y + h * f, w, h * (1 - f), n - 1)
    partir(-38, 4, 76, 131, 5)
    for x in np.arange(-36, 38, 3.6):
        k.L([(x, 1), (x, 3.4)], 0.9)
        k.L([(x, 135.6), (x, 138)], 0.9)


def t7(k):
    for j, y0 in enumerate(np.arange(130, 2, -9.6)):
        x, pts, alto = -42.0, [], k.r.random() < 0.5
        paso = 3.6 if j == 0 else None
        while x < 42:
            w = paso or k.r.choice((3.6, 7.2, 10.8, 14.4))
            pts += [(x, y0 + (4.4 if alto else 0)), (x + w, y0 + (4.4 if alto else 0))]
            x += w
            alto = not alto
        k.L(pts, 1.05)
    for x in (-21.6, 14.4):
        k.trazos([(x, 0), (x, 139)], 2.0, 2.0, 0.8)


def t8(k):
    for x in np.arange(-37.5, 39, 5.0):
        for y in np.arange(3, 138, 5.0):
            k.punto(x, y, 0.62)
    for x in (-40, 40):
        k.L([(x, 0), (x, 139)], 0.9)
    for a, b in (((-32.5, 43), (-12.5, 43)), ((17.5, 48), (32.5, 48)), ((-32.5, 123), (-17.5, 128)), ((22.5, 133), (32.5, 123)), ((-32.5, 58), (-32.5, 98)),
                 ((32.5, 63), (32.5, 108)), ((-2.5, 3), (22.5, 3))):
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + (4 if a[1] == b[1] else 0) + (0 if a[1] == b[1] else 0))
        k.curva(lambda t, a=a, b=b, m=m: ((1 - t) ** 2 * a[0] + 2 * t * (1 - t) * (m[0] + (5 if a[0] == b[0] else 0)) + t * t * b[0],
                                           (1 - t) ** 2 * a[1] + 2 * t * (1 - t) * (m[1] + 4) + t * t * b[1]), 0, 1, 30, 1.5)
        k.nodo(a[0], a[1], 1.2)
        k.nodo(b[0], b[1], 1.2)
    k.rect(22.5, 58, 4, 9, True)
    k.circ(-22.5, 53, 3.4, fondo=True, mm=1.1, z=3.4)


def t9(k):
    eng = [(-22, 46, 11, 12, 0.0), (-2.5, 52, 6.5, 8, 0.4), (24, 50, 15, 16, 0.1), (-28, 124, 8, 10, 0.2), (28, 126, 9, 10, 0.5), (34, 92, 5, 7, 0.0),
           (-34, 96, 5, 7, 0.3), (-8, 12, 9, 10, 0.2), (14, 8, 6, 8, 0.5)]
    for x, y, r, n, f in eng:
        k.engrane(x, y, r, n, True, f)
    for (x, y, r, n, f), a0 in zip(eng[:3], (40, 200, 120)):
        k.arco(x, y, r + 5.5, a0, a0 + 80, 0.9)
        p = pol((x, y), r + 5.5, a0 + 80)
        k.poli([pol(p, 2.2, a0 + 80 + 90 + 150 * s) for s in (0, 1, -1)], True)


def t10(k):
    for i in range(6):
        d = 3.2 * i
        k.L([(-40, 126 - d), (-36.5 + d * 0.1, 126 - d), (-36.5 + d * 0.1, 72 + d), (-36.5 + d * 0.1, 60 + d * 0.5)], 1.15)
        k.L([(40, 14 + d), (20 - d, 14 + d), (20 - d, 40 + d * 0.5)], 1.15)
        k.L([(-40, 20 + d * 0.9), (-24 + d, 20 + d * 0.9), (-24 + d, 40)], 1.15)
        k.L([(40, 134 - d), (16 + d, 134 - d), (16 + d, 122)], 1.15)
    for x, y in ((-10, 131), (10, 16), (-34, 30), (30, 126)):
        k.poli([pol((x, y), 3.0, a_ + (0 if x < 0 else 180)) for a_ in (0, 140, 220)], True, z=4)
    for x, y in ((36, 60), (36, 70), (36, 80), (36, 90), (36, 100), (-36, 104), (-36, 112)):
        k.nodo(x, y, 1.7, True)
    for x in np.arange(-30, 32, 4):
        k.rect(x, 2.4, 2.2, 3.4, True)


TEMAS = [
    ("tema_01_astro", "Tema 1: astro", [("Constelaciones", a1), ("Sistema solar", a2), ("Lanzamiento", a3), ("Fases de la luna", a4),
                                         ("Órbitas y satélites", a5), ("Lluvia de cometas", a6), ("Superficie lunar", a7), ("Ruta de misión", a8),
                                         ("Carta celeste", a9), ("Planeta anillado", a10)]),
    ("tema_02_solarpunk", "Tema 2: solarpunk", [("Sol y enredaderas", s1), ("Ciudad verde", s2), ("Parque eólico", s3), ("Granja solar", s4),
                                                 ("Domo invernadero", s5), ("Art nouveau", s6), ("Abejas y flores", s7), ("Ciclo del agua", s8),
                                                 ("Terrazas", s9), ("Raíces y brotes", s10)]),
    ("tema_03_cyberpunk", "Tema 3: cyberpunk", [("Ciudad de noche", c1), ("Lluvia de datos", c2), ("Visor", c3), ("Horizonte de rejilla", c4),
                                                 ("Glitch", c5), ("Mapa de sector", c6), ("Colmena digital", c7), ("Cables", c8),
                                                 ("Señalética", c9), ("Retícula", c10)]),
    ("tema_04_videojuegos", "Tema 4: videojuegos", [("Objetos pixelados", v1), ("Nivel de plataformas", v2), ("Laberinto", v3), ("Mazmorra", v4),
                                                     ("Bloques", v5), ("Controles", v6), ("Árbol de habilidades", v7), ("Marcador", v8),
                                                     ("Mundo isométrico", v9), ("Rebote", v10)]),
    ("tema_05_china", "Tema 5: mitología china", [("Dragón entre nubes", ch1), ("Nubes auspiciosas", ch2), ("Montañas y agua", ch3), ("Ocho trigramas", ch4),
                                                   ("Celosía", ch5), ("Lotos y peces", ch6), ("Pagoda y luna", ch7), ("Grullas", ch8),
                                                   ("Monedas y nudos", ch9), ("Linternas", ch10)]),
    ("tema_06_grecia", "Tema 6: mitología griega", [("Meandros", g1), ("Templo", g2), ("Laberinto", g3), ("Cola del pavo real", g4),
                                                     ("Corona de laurel", g5), ("Ánforas y olivo", g6), ("Mar y tridente", g7), ("Lira y estrellas", g8),
                                                     ("Los ojos de Argos", g9), ("Olimpo", g10)]),
    ("tema_07_nordica", "Tema 7: mitología nórdica", [("Árbol del mundo", n1), ("Runas", n2), ("Barco largo", n3), ("Trenzado", n4),
                                                       ("Cuervos", n5), ("Aurora", n6), ("Serpiente del mundo", n7), ("Martillo y rayos", n8),
                                                       ("Brújula", n9), ("Escudos", n10)]),
    ("tema_08_japon", "Tema 8: Japón", [("Olas seigaiha", j1), ("Monte y sol", j2), ("Torii", j3), ("Cerezo en flor", j4), ("La gran ola", j5),
                                         ("Estanque de koi", j6), ("Bambú", j7), ("Abanicos", j8), ("Grullas de papel", j9), ("Shoji y ensō", j10)]),
    ("tema_09_universo", "Tema 9: universo", [("Galaxia espiral", u1), ("Agujero negro", u2), ("Red cósmica", u3), ("Ondas gravitacionales", u4),
                                               ("Espacio-tiempo", u5), ("Expansión", u6), ("Nebulosa", u7), ("Multiverso", u8),
                                               ("Mapa de púlsares", u9), ("Del átomo a la galaxia", u10)]),
    ("tema_10_tecnologia", "Tema 10: full tecnológico", [("Pistas de circuito", t1), ("Señal inalámbrica", t2), ("Los cinco nodos", t3), ("Esquemático", t4),
                                                          ("Siete segmentos", t5), ("Plano del chip", t6), ("Analizador lógico", t7), ("Protoboard", t8),
                                                          ("Engranes", t9), ("Bus de datos", t10)]),
]


def main(cuales):
    destino = RAIZ / "renders" / "temas"
    destino.mkdir(parents=True, exist_ok=True)
    for nt, (archivo, encabezado, opciones) in enumerate(TEMAS, 1):
        if cuales and nt not in cuales:
            continue
        fig = plt.figure(figsize=(FIGW, FIGH), facecolor="white")
        for i, (titulo, fn) in enumerate(opciones):
            num = 100 + (nt - 1) * 10 + i + 1
            ax = fig.add_axes([0.012 + (i % 5) * 0.198, 0.50 - (i // 5) * 0.49, AXW, AXH])
            clip = tapa_base(ax)
            try:
                fn(K(ax, clip, num))
            except Exception as err:
                print(f"ERROR en {num} {titulo}: {err!r}")
            elementos(ax)
            ax.text(0, 141.5, f"{num}. {titulo}", ha="center", va="bottom", fontsize=12.5)
        fig.text(0.5, 0.985, f"{encabezado} (maqueta a escala; el grabado real es de 0.4 mm, más sutil que aquí)", ha="center", va="top", fontsize=13)
        fig.savefig(destino / f"{archivo}.png", dpi=100)
        plt.close(fig)
        print("escrito", archivo)


if __name__ == "__main__":
    main({int(a) for a in sys.argv[1:]})
