"""Kit de motivos para las maquetas de textura en el estilo del diseno 55 (linea fina, nodos y estrellas).
Lo usa cad/maqueta_temas.py. Todo se dibuja como grabado (SURCO) sobre la tapa; nada de esto genera piezas."""
import math
import random

import numpy as np
from matplotlib.patches import Arc, Circle, Ellipse, Polygon, Rectangle, Wedge

from maqueta_texturas import SURCO, TAPA, lente, lw
from maqueta_texturas2 import coleccion, linea, parche

OJO = (-15.0, 69.1)
VC = (0.0, 95.65)


def tr(pts, x=0.0, y=0.0, t=1.0, ang=0.0):
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return [(x + t * (u * c - v * s), y + t * (u * s + v * c)) for u, v in pts]


class K:
    def __init__(self, ax, clip, semilla=0):
        self.ax, self.clip, self.r = ax, clip, random.Random(semilla)

    # ── basicos ──
    def L(self, pts, mm=1.0, z=3, c=SURCO):
        linea(self.ax, self.clip, [p[0] for p in pts], [p[1] for p in pts], mm, z, c)

    def P(self, p):
        parche(self.ax, self.clip, p)

    def poli(self, pts, lleno=False, mm=1.0, z=3, fondo=False):
        self.P(Polygon(pts, fc=SURCO if lleno else (TAPA if fondo else "none"), ec="none" if lleno else SURCO, lw=lw(mm),
                       zorder=z, joinstyle="round"))

    def circ(self, x, y, r, lleno=False, mm=1.0, z=3, fondo=False):
        self.P(Circle((x, y), r, fc=SURCO if lleno else (TAPA if fondo else "none"), ec="none" if lleno else SURCO, lw=lw(mm), zorder=z))

    def elipse(self, x, y, a, b, ang=0.0, lleno=False, mm=1.0, z=3, fondo=False):
        self.P(Ellipse((x, y), 2 * a, 2 * b, angle=ang, fc=SURCO if lleno else (TAPA if fondo else "none"),
                       ec="none" if lleno else SURCO, lw=lw(mm), zorder=z))

    def rect(self, x, y, w, h, lleno=False, mm=1.0, ang=0.0, z=3, fondo=False):
        self.P(Rectangle((x - w / 2, y - h / 2), w, h, angle=ang, rotation_point="center", fc=SURCO if lleno else (TAPA if fondo else "none"),
                         ec="none" if lleno else SURCO, lw=lw(mm), zorder=z))

    def arco(self, x, y, r, a1, a2, mm=1.0, z=3, ry=None):
        self.P(Arc((x, y), 2 * r, 2 * (ry or r), theta1=a1, theta2=a2, color=SURCO, lw=lw(mm), zorder=z))

    def cuna(self, x, y, r, a1, a2, z=3):
        self.P(Wedge((x, y), r, a1, a2, fc=SURCO, ec="none", zorder=z))

    def punto(self, x, y, r=0.7, z=3):
        self.circ(x, y, r, True, z=z)

    def curva(self, f, t0, t1, n=120, mm=1.0, z=3):
        self.L([f(t0 + (t1 - t0) * k / n) for k in range(n + 1)], mm, z)

    def trazos(self, pts, largo=3.0, hueco=2.2, mm=1.0):
        """Linea discontinua a lo largo de una polilinea."""
        acum, dibujar, ini = 0.0, True, pts[0]
        for a, b in zip(pts, pts[1:]):
            d = math.hypot(b[0] - a[0], b[1] - a[1])
            pos = 0.0
            while pos < d:
                paso = min((largo if dibujar else hueco) - acum, d - pos)
                q = (a[0] + (b[0] - a[0]) * (pos + paso) / d, a[1] + (b[1] - a[1]) * (pos + paso) / d)
                if dibujar:
                    self.L([ini, q], mm)
                ini, pos, acum = q, pos + paso, acum + paso
                if acum >= (largo if dibujar else hueco) - 1e-9:
                    dibujar, acum = not dibujar, 0.0

    def disp(self, n, sep, zona=(-38, 38, 2, 136), intentos=4000):
        """n posiciones al azar separadas al menos `sep`."""
        ps = []
        for _ in range(intentos):
            p = (self.r.uniform(zona[0], zona[1]), self.r.uniform(zona[2], zona[3]))
            if all(math.hypot(p[0] - q[0], p[1] - q[1]) > sep for q in ps):
                ps.append(p)
                if len(ps) >= n:
                    break
        return ps

    # ── cielo ──
    def estrella(self, x, y, r=2.6, puntas=4, ang=0.0, lleno=True, mm=1.0):
        pts = [(x + (r if j % 2 == 0 else r * 0.3) * math.cos(math.radians(ang) + j * math.pi / puntas),
                y + (r if j % 2 == 0 else r * 0.3) * math.sin(math.radians(ang) + j * math.pi / puntas)) for j in range(2 * puntas)]
        self.poli(pts, lleno, mm)

    def cielo(self, n=70, grandes=7, zona=(-39, 39, 1, 137)):
        coleccion(self.ax, self.clip, [Circle((self.r.uniform(zona[0], zona[1]), self.r.uniform(zona[2], zona[3])),
                                               self.r.choice((0.5, 0.6, 0.8, 1.0))) for _ in range(n)])
        for x, y in self.disp(grandes, 14, zona):
            self.estrella(x, y, self.r.choice((2.2, 2.8, 3.4)))

    def nodo(self, x, y, r=1.6, hueco=False):
        self.circ(x, y, r, True, z=4)
        if hueco:
            self.P(Circle((x, y), r * 0.45, fc=TAPA, ec="none", zorder=4))

    def ruta(self, pts, mm=0.9, r=1.6, hueco=False):
        self.L(pts, mm)
        for p in pts:
            self.nodo(p[0], p[1], r, hueco)

    def planeta(self, x, y, r, anillo=True, ang=20.0, bandas=0):
        if anillo:
            self.elipse(x, y, r * 1.9, r * 0.55, ang, mm=1.0, z=3)
        self.circ(x, y, r, fondo=True, mm=1.1, z=3.2)
        for k in range(bandas):
            yy = y - r + 2 * r * (k + 1) / (bandas + 1)
            m = math.sqrt(max(0.0, r * r - (yy - y) ** 2)) * 0.82
            self.L([(x - m, yy), (x + m, yy)], 0.9, 3.3)
        if anillo:
            self.arco(x, y, r * 1.9, 180, 360, 1.0, 3.4, ry=r * 0.55) if abs(ang) < 1 else None

    def luna(self, x, y, r, corr=0.45, ang=30.0):
        self.circ(x, y, r, True, z=3)
        self.P(Circle((x + r * corr * 1.6 * math.cos(math.radians(ang)), y + r * corr * 1.6 * math.sin(math.radians(ang))), r * 0.92,
                      fc=TAPA, ec="none", zorder=3.05))

    def cometa(self, x, y, ang=35.0, largo=20.0):
        c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        for d, f in ((-1.1, 0.75), (0.0, 1.0), (1.1, 0.75)):
            self.L([(x - d * s, y + d * c), (x - d * s - largo * f * c, y + d * c - largo * f * s)], 0.9)
        self.punto(x, y, 2.1, 4)

    def cohete(self, x, y, t=1.0, ang=0.0):
        self.poli(tr([(-2, -5), (-2, 3), (0, 7), (2, 3), (2, -5)], x, y, t, ang), fondo=True, mm=1.1, z=3.3)
        self.poli(tr([(-2, -5), (-4.2, -7), (-2, -1.5)], x, y, t, ang), True, z=3.3)
        self.poli(tr([(2, -5), (4.2, -7), (2, -1.5)], x, y, t, ang), True, z=3.3)
        p = tr([(0, 1.6)], x, y, t, ang)[0]
        self.circ(p[0], p[1], 1.1 * t, True, z=3.4)
        for u in (-1.1, 0.0, 1.1):
            self.L(tr([(u, -6.2), (u * 1.5, -9.5 - (2 if u == 0 else 0))], x, y, t, ang), 0.9)

    def satelite(self, x, y, t=1.0, ang=0.0):
        self.rect(x, y, 4 * t, 4 * t, fondo=True, mm=1.0, ang=ang, z=3.3)
        for s in (-1, 1):
            p = tr([(s * 6.2, 0)], x, y, t, ang)[0]
            self.rect(p[0], p[1], 6.4 * t, 3.2 * t, mm=1.0, ang=ang, z=3.3, fondo=True)
            self.L(tr([(s * 6.2, -1.6), (s * 6.2, 1.6)], x, y, t, ang), 0.8, 3.4)
            self.L(tr([(s * 2, 0), (s * 3, 0)], x, y, t, ang), 0.9, 3.4)
        self.L(tr([(0, 2), (0, 4.4)], x, y, t, ang), 0.9, 3.4)
        p = tr([(0, 5.0)], x, y, t, ang)[0]
        self.punto(p[0], p[1], 0.9, 3.4)

    def galaxia(self, x, y, r, brazos=2, vueltas=1.5, puntos=True):
        for b in range(brazos):
            f0 = 2 * math.pi * b / brazos
            pts = [(x + r * (k / 90) * math.cos(f0 + vueltas * 2 * math.pi * k / 90), y + r * 0.72 * (k / 90) * math.sin(f0 + vueltas * 2 * math.pi * k / 90))
                   for k in range(6, 91)]
            if puntos:
                coleccion(self.ax, self.clip, [Circle((p[0] + self.r.uniform(-1.2, 1.2), p[1] + self.r.uniform(-1.2, 1.2)),
                                                      self.r.choice((0.5, 0.65, 0.9))) for p in pts for _ in range(2)])
            else:
                self.L(pts, 1.0)
        self.punto(x, y, r * 0.11 + 0.9, 4)

    def sol(self, x, y, r, n=12, largo=4.0, lleno=False, mm=1.0, hueco=1.4):
        self.circ(x, y, r, lleno, mm)
        for k in range(n):
            a = 2 * math.pi * k / n
            f = largo if k % 2 == 0 else largo * 0.6
            self.L([(x + (r + hueco) * math.cos(a), y + (r + hueco) * math.sin(a)), (x + (r + hueco + f) * math.cos(a), y + (r + hueco + f) * math.sin(a))], mm)

    # ── paisaje ──
    def nube(self, x, y, t=1.0, z=3.2):
        for dx, dy, r in ((-4.2, 0, 3.0), (-0.6, 2.2, 4.0), (4.0, 0.3, 3.2)):
            self.circ(x + dx * t, y + dy * t, r * t, fondo=True, mm=1.0, z=z)
        self.rect(x, y - 1.6 * t, 12.4 * t, 3.4 * t, fondo=True, mm=0.0, z=z + 0.01)
        self.P(Rectangle((x - 6.2 * t, y - 3.2 * t), 12.4 * t, 3.3 * t, fc=TAPA, ec="none", zorder=z + 0.02))
        self.L([(x - 7.2 * t, y - 3.1 * t), (x + 7.2 * t, y - 3.1 * t)], 1.0, z + 0.03)

    def voluta(self, x, y, t=1.0, giro=1):
        """Nube auspiciosa: una espiral con cola."""
        self.curva(lambda a: (x + giro * t * (0.6 + 0.52 * a) * math.cos(a), y + t * (0.6 + 0.52 * a) * math.sin(a)), 0.4, 3.6 * math.pi, 80, 1.0)
        self.curva(lambda a: (x + giro * t * (6.5 + 7 * a), y - t * (1.0 + 1.6 * math.sin(a * 2.4))), 0.0, 1.0, 20, 1.0)

    def ola(self, y0, amp=2.4, wl=14.0, fase=0.0, mm=1.0, x0=-42.0, x1=42.0, z=3):
        self.L([(x, y0 + amp * math.sin(2 * math.pi * x / wl + fase)) for x in np.linspace(x0, x1, 160)], mm, z)

    def monte(self, pts, z=3.0, mm=1.2, rayas=0.0):
        xs = np.linspace(-42, 42, 220)
        ys = np.interp(xs, [p[0] for p in pts], [p[1] for p in pts])
        f = self.ax.fill_between(xs, 0, ys, color=TAPA, zorder=z)
        f.set_clip_path(self.clip)
        self.L(list(zip(xs, ys)), mm, z + 0.02)
        if rayas:
            for y in np.arange(rayas, max(ys), rayas * 2.6 + 2.2):
                seg = [(x, y) for x, c in zip(xs, ys) if c > y + 1.6]
                if len(seg) > 3:
                    self.L([seg[0], seg[-1]], 0.85, z + 0.03)
        return xs, ys

    def hoja(self, x, y, largo, ang, lleno=False, nerv=True, ancho=0.42, z=3):
        c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        cx, cy = x + largo / 2 * c, y + largo / 2 * s
        self.poli(lente(cx, cy, largo, largo * ancho, math.radians(ang)), lleno, 1.0, z, fondo=not lleno)
        if nerv:
            linea(self.ax, self.clip, [x + largo * 0.12 * c, x + largo * 0.88 * c], [y + largo * 0.12 * s, y + largo * 0.88 * s], 0.8, z + 0.05,
                  TAPA if lleno else SURCO)

    def rama(self, pts, cada=6.0, largo=6.5, lleno=True, mm=1.2):
        self.L(pts, mm)
        acum, lado = 0.0, 1
        for a, b in zip(pts, pts[1:]):
            d = math.hypot(b[0] - a[0], b[1] - a[1])
            acum += d
            if acum >= cada:
                acum = 0.0
                ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) + lado * 48
                self.hoja(b[0], b[1], largo, ang, lleno)
                lado = -lado

    def flor(self, x, y, r=3.2, petalos=5, centro=True, lleno=False):
        for k in range(petalos):
            a = 360 * k / petalos + 90
            self.hoja(x, y, r * 1.25, a, lleno, False, 0.62, 3.2)
        if centro:
            self.circ(x, y, r * 0.3, True, z=3.4)

    def arbol(self, x, y, h, tipo="copa"):
        if tipo == "pino":
            self.L([(x, y), (x, y + h * 0.25)], 1.1)
            for k in range(3):
                self.poli([(x - h * (0.3 - 0.07 * k), y + h * (0.2 + 0.25 * k)), (x + h * (0.3 - 0.07 * k), y + h * (0.2 + 0.25 * k)),
                           (x, y + h * (0.55 + 0.22 * k))], fondo=True, mm=1.0, z=3.3)
        else:
            self.L([(x, y), (x, y + h * 0.55)], 1.2)
            self.circ(x, y + h * 0.7, h * 0.3, fondo=True, mm=1.0, z=3.3)
            self.L([(x, y + h * 0.5), (x - h * 0.13, y + h * 0.68)], 0.9, 3.4)
            self.L([(x, y + h * 0.56), (x + h * 0.12, y + h * 0.74)], 0.9, 3.4)

    def edificios(self, y0, hmin, hmax, ventanas=True, x0=-42.0, x1=42.0, z=3.0, antenas=True, arboles=False):
        x = x0
        while x < x1:
            w, h = self.r.choice((5, 6.5, 8, 10)), self.r.uniform(hmin, hmax)
            self.P(Rectangle((x, y0), w, h, fc=TAPA, ec=SURCO, lw=lw(1.0), zorder=z))
            if ventanas:
                for vy in np.arange(y0 + 2.6, y0 + h - 2.2, 3.6):
                    for vx in np.arange(x + 1.6, x + w - 1.6, 2.6):
                        if self.r.random() < 0.55:
                            self.P(Rectangle((vx, vy), 1.1, 1.5, fc=SURCO, ec="none", zorder=z + 0.02))
            if antenas and self.r.random() < 0.35:
                self.L([(x + w / 2, y0 + h), (x + w / 2, y0 + h + self.r.uniform(3, 8))], 0.9, z + 0.02)
            if arboles and self.r.random() < 0.6:
                for ax_ in np.arange(x + 1.6, x + w - 1, 2.8):
                    self.circ(ax_, y0 + h + 1.3, 1.4, True, z=z + 0.02)
            x += w + self.r.choice((0, 0, 1.2))

    def turbina(self, x, y, h, fase=0.0, pala=9.0):
        self.L([(x, y), (x, y + h)], 1.2, 3.3)
        for k in range(3):
            self.hoja(x, y + h, pala, fase + 120 * k + 90, False, False, 0.2, 3.35)
        self.punto(x, y + h, 1.1, 3.4)

    def panel(self, x, y, w, h, ang=0.0, nx=3, ny=2, sesgo=0.0):
        esq = lambda u, v: tr([(u * w - w / 2 + sesgo * v * h, v * h - h / 2)], x, y, 1.0, ang)[0]  # noqa: E731
        self.poli([esq(0, 0), esq(1, 0), esq(1, 1), esq(0, 1)], fondo=True, mm=1.0, z=3.3)
        for i in range(1, nx):
            self.L([esq(i / nx, 0), esq(i / nx, 1)], 0.8, 3.35)
        for j in range(1, ny):
            self.L([esq(0, j / ny), esq(1, j / ny)], 0.8, 3.35)

    # ── maquina ──
    def engrane(self, x, y, r, n=10, hueco=True, fase=0.0):
        pts = []
        for k in range(n):
            a0 = fase + 2 * math.pi * k / n
            for da, rr in ((-0.5, r), (-0.28, r + 2.0), (0.28, r + 2.0), (0.5, r)):
                pts.append((x + rr * math.cos(a0 + da * math.pi / n * 1.2), y + rr * math.sin(a0 + da * math.pi / n * 1.2)))
        self.poli(pts, fondo=True, mm=1.0, z=3.2)
        if hueco:
            self.circ(x, y, r * 0.38, mm=1.0, z=3.3)

    def pista(self, pts, mm=1.0, pad=True, ini=False):
        self.L(pts, mm)
        if pad:
            self.nodo(pts[-1][0], pts[-1][1], 1.5, True)
        if ini:
            self.nodo(pts[0][0], pts[0][1], 1.5, True)

    def pixel(self, x, y, mapa, t=1.6):
        coleccion(self.ax, self.clip, [Rectangle((x + i * t, y - (j + 1) * t), t * 0.9, t * 0.9) for j, fila in enumerate(mapa)
                                       for i, ch in enumerate(fila) if ch != "."])

    def corchetes(self, x0, y0, x1, y1, largo=6.0, mm=1.2):
        for sx, sy, cx, cy in ((1, 1, x0, y0), (-1, 1, x1, y0), (-1, -1, x1, y1), (1, -1, x0, y1)):
            self.L([(cx + sx * largo, cy), (cx, cy), (cx, cy + sy * largo)], mm)

    def mira(self, x, y, r, n=3, marcas=12):
        for k in range(n):
            self.circ(x, y, r * (k + 1) / n, mm=1.0)
        for k in range(marcas):
            a = 2 * math.pi * k / marcas
            self.L([(x + r * 1.04 * math.cos(a), y + r * 1.04 * math.sin(a)), (x + r * 1.16 * math.cos(a), y + r * 1.16 * math.sin(a))], 0.9)
        for a in (0, 90, 180, 270):
            c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
            self.L([(x + r * 0.5 * c, y + r * 0.5 * s), (x + r * 1.3 * c, y + r * 1.3 * s)], 0.9)

    def siete(self, x, y, digito, t=1.0):
        seg = {"a": ((0, 4), (2, 4)), "b": ((2, 4), (2, 2)), "c": ((2, 2), (2, 0)), "d": ((0, 0), (2, 0)), "e": ((0, 2), (0, 0)),
               "f": ((0, 4), (0, 2)), "g": ((0, 2), (2, 2))}
        on = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc", "7": "abc", "8": "abcdefg",
              "9": "abcdfg", "-": "g"}[digito]
        for k in on:
            (a, b), (c, d) = seg[k]
            self.L([(x + a * t, y + b * t), (x + c * t, y + d * t)], 1.1)

    def hexagono(self, x, y, r, lleno=False, mm=1.0, ang=30.0):
        self.poli([(x + r * math.cos(math.radians(ang + 60 * k)), y + r * math.sin(math.radians(ang + 60 * k))) for k in range(6)], lleno, mm)

    # ── mitos ──
    def greca(self, y0, t=1.0, x0=-43.0, x1=43.0, mm=1.1):
        u = [(0, 0), (0, 6), (6, 6), (6, 2), (2, 2), (2, 4), (4, 4)]
        x = x0
        while x < x1:
            self.L([(x + p[0] * t, y0 + p[1] * t) for p in u], mm)
            self.L([(x, y0), (x + 8.6 * t, y0)], mm)
            x += 8.6 * t

    def columna(self, x, y, h, w=6.0):
        self.rect(x, y + 1.0, w + 3, 2.0, fondo=True, mm=1.0, z=3.2)
        self.rect(x, y + h - 1.0, w + 3, 2.0, fondo=True, mm=1.0, z=3.2)
        self.rect(x, y + h / 2, w, h - 4, fondo=True, mm=1.0, z=3.15)
        for dx in (-w / 4, 0, w / 4):
            self.L([(x + dx, y + 3.2), (x + dx, y + h - 3.2)], 0.8, 3.25)

    def laurel(self, x, y, a, b, a0=200.0, a1=520.0, cada=9.0, largo=7.0):
        n = int((a1 - a0) / cada)
        for k in range(n + 1):
            ang = math.radians(a0 + cada * k)
            px, py = x + a * math.cos(ang), y + b * math.sin(ang)
            tang = math.degrees(math.atan2(b * math.cos(ang), -a * math.sin(ang)))
            for s in (-1, 1):
                self.hoja(px, py, largo, tang + s * 38, True, False, 0.36)

    RUNAS = {"ansuz": [(0, 0, 0, 2), (0, 2, 0.8, 1.5), (0, 1.4, 0.8, 0.9)], "raido": [(0, 0, 0, 2), (0, 2, 0.8, 1.6), (0.8, 1.6, 0, 1.1), (0, 1.1, 0.8, 0)],
             "gebo": [(0, 0, 1, 2), (1, 0, 0, 2)], "isa": [(0.5, 0, 0.5, 2)], "tiwaz": [(0.5, 0, 0.5, 2), (0.5, 2, 0, 1.4), (0.5, 2, 1, 1.4)],
             "berkano": [(0, 0, 0, 2), (0, 2, 0.8, 1.5), (0.8, 1.5, 0, 1), (0, 1, 0.8, 0.5), (0.8, 0.5, 0, 0)], "laguz": [(0.2, 0, 0.2, 2), (0.2, 2, 0.9, 1.3)],
             "dagaz": [(0, 0, 0, 2), (1, 0, 1, 2), (0, 2, 1, 0), (0, 0, 1, 2)], "kenaz": [(0.9, 1.8, 0.1, 1), (0.1, 1, 0.9, 0.2)],
             "fehu": [(0.2, 0, 0.2, 2), (0.2, 1.0, 0.9, 1.7), (0.2, 1.5, 0.9, 2.2)], "uruz": [(0, 0, 0, 2), (0, 2, 0.9, 1.3), (0.9, 1.3, 0.9, 0)],
             "mannaz": [(0, 0, 0, 2), (1, 0, 1, 2), (0, 2, 1, 1), (1, 2, 0, 1)]}

    def runa(self, x, y, nombre, t=3.0, mm=1.2):
        for a, b, c, d in self.RUNAS[nombre]:
            self.L([(x + a * t, y + b * t), (x + c * t, y + d * t)], mm)

    def trigrama(self, x, y, bits, t=1.0, ang=0.0):
        for k, b in enumerate(bits):
            v = (k - 1) * 2.4
            if b == "1":
                self.L(tr([(-4, v), (4, v)], x, y, t, ang), 1.3)
            else:
                self.L(tr([(-4, v), (-0.9, v)], x, y, t, ang), 1.3)
                self.L(tr([(0.9, v), (4, v)], x, y, t, ang), 1.3)

    def torii(self, x, y, t=1.0):
        self.L([(x - 7.5 * t, y + 13 * t), (x - 4 * t, y + 12 * t), (x + 4 * t, y + 12 * t), (x + 7.5 * t, y + 13 * t)], 1.8, 3.3)
        self.L([(x - 6 * t, y + 9.5 * t), (x + 6 * t, y + 9.5 * t)], 1.3, 3.3)
        for s in (-1, 1):
            self.L([(x + s * 4.4 * t, y), (x + s * 4.0 * t, y + 12 * t)], 1.5, 3.3)
        self.L([(x, y + 9.5 * t), (x, y + 12 * t)], 1.1, 3.3)

    def pagoda(self, x, y, t=1.0, pisos=4):
        for k in range(pisos):
            w, yy = (11 - 2 * k) * t, y + k * 6.5 * t
            self.rect(x, yy + 2 * t, w * 0.62, 4 * t, fondo=True, mm=1.0, z=3.2)
            self.L([(x - w * 0.72, yy + 4.2 * t), (x - w * 0.55, yy + 5.2 * t), (x + w * 0.55, yy + 5.2 * t), (x + w * 0.72, yy + 4.2 * t)], 1.4, 3.3)
        self.L([(x, y + pisos * 6.5 * t - 1.2 * t), (x, y + pisos * 6.5 * t + 4 * t)], 1.0, 3.3)

    def ave(self, x, y, t=1.0, ang=0.0):
        self.L(tr([(-4, 1.8), (-1.6, 0.4), (0, -0.6), (1.6, 0.4), (4, 1.8)], x, y, t, ang), 1.1)

    def pez(self, x, y, t=1.0, ang=0.0):
        self.poli(tr([(u, v) for u, v in lente(0, 0, 9, 3.6)], x, y, t, ang), fondo=True, mm=1.0, z=3.2)
        self.poli(tr([(-4.4, 0), (-7.6, 2.2), (-6.6, 0), (-7.6, -2.2)], x, y, t, ang), True, z=3.2)
        p = tr([(2.6, 0.4)], x, y, t, ang)[0]
        self.punto(p[0], p[1], 0.5 * t, 3.3)

    def abanico(self, x, y, r=9.0, ang=90.0, ab=120.0, n=7):
        self.cuna(x, y, r * 0.22, ang - ab / 2, ang + ab / 2, 3.3)
        self.arco(x, y, r, ang - ab / 2, ang + ab / 2, 1.1, 3.3)
        self.arco(x, y, r * 0.55, ang - ab / 2, ang + ab / 2, 0.9, 3.3)
        for k in range(n):
            a = math.radians(ang - ab / 2 + ab * k / (n - 1))
            self.L([(x, y), (x + r * math.cos(a), y + r * math.sin(a))], 0.9, 3.3)

    def bambu(self, x, y0, y1, hojas=True):
        y = y0
        while y < y1:
            seg = self.r.uniform(9, 14)
            self.rect(x, y + seg / 2, 2.6, seg - 1.2, fondo=True, mm=1.0, z=3.2)
            if hojas and self.r.random() < 0.6:
                s = self.r.choice((-1, 1))
                for d in (20, 45):
                    self.hoja(x + s * 1.3, y + seg, 8.5, 90 - s * (90 - d), True, False, 0.24, 3.3)
            y += seg

    def sakura(self, x, y, r=3.0):
        self.flor(x, y, r, 5, True, False)

    def rayo(self, x, y, t=1.0, ang=0.0, lleno=True):
        self.poli(tr([(0, 9), (-3.2, 0.6), (-0.6, 0.6), (-2.4, -9), (3.4, 1.8), (0.6, 1.8), (2.6, 9)], x, y, t, ang), lleno, 1.0, 3.3)
