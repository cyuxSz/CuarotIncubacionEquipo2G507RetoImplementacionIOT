"""Segunda tanda de texturas para la tapa (20-nov): 20 ideas mas, sobre la misma maqueta de cad/maqueta_texturas.py.

  uv run --no-project --python 3.12 --with matplotlib --with scipy python cad/maqueta_texturas2.py

Salida: cad/renders/maqueta_texturas_tapa_dht_2.png y _3.png (10 tapas cada una). No genera piezas.
"""
import math
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.collections import LineCollection, PatchCollection  # noqa: E402
from matplotlib.patches import Arc, Circle, Polygon, Rectangle  # noqa: E402
from scipy.spatial import Delaunay  # noqa: E402

from maqueta_texturas import AXH, AXW, FIGH, FIGW, RAIZ, SURCO, TAPA, elementos, lente, lw, ojo, tapa_base  # noqa: E402

OJO = (-15.0, 69.1)


def linea(ax, clip, xs, ys, mm=1.0, z=3, color=SURCO):
    ln, = ax.plot(xs, ys, color=color, lw=lw(mm), solid_capstyle="round", solid_joinstyle="round", zorder=z)
    ln.set_clip_path(clip)


def parche(ax, clip, p):
    ax.add_patch(p)
    p.set_clip_path(clip)


def coleccion(ax, clip, ps, **kw):
    c = PatchCollection(ps, zorder=3, **{"fc": SURCO, "ec": "none", **kw})
    ax.add_collection(c)
    c.set_clip_path(clip)


def empacar(rnd, radios, hueco=1.1, intentos=7000):
    puestos = []
    for _ in range(intentos):
        r = rnd.choice(radios)
        x, y = rnd.uniform(-40, 40), rnd.uniform(0, 139)
        if all((x - a) ** 2 + (y - b) ** 2 > (r + c + hueco) ** 2 for a, b, c in puestos):
            puestos.append((x, y, r))
    return puestos


# ── del mito y del logotipo ─────────────────────────────────────────────────
def cien_ojos(ax, clip):
    """Argos Panoptes, el gigante de los cien ojos."""
    rnd = random.Random(100)
    for x, y, r in empacar(rnd, (3.4, 4.0, 4.6), hueco=1.4):
        ojo(ax, x, y, 2 * r, SURCO, TAPA, 3, rayos=False, clip=clip)


def pavo_real(ax, clip):
    """Hera puso los ojos de Argos en la cola del pavo real: escamas con su ojo."""
    r = 6.4
    for j in range(0, 26):
        for i in range(-5, 6):
            x, y = i * 2 * r + (r if j % 2 else 0), j * r * 0.92
            parche(ax, clip, Arc((x, y), 2 * r, 2 * r, theta1=0, theta2=180, color=SURCO, lw=lw(1.0), zorder=3))
            parche(ax, clip, Circle((x, y + r * 0.42), 1.25, fc=SURCO, ec="none", zorder=3))


def destello(ax, clip):
    """Los tres rayos del logotipo, multiplicados: rayos que salen del ojo."""
    rnd = random.Random(8)
    for k in range(40):
        a = math.radians(k * 9 + 2)
        r = 11.0 + rnd.uniform(0, 4)
        while r < 150:
            largo = rnd.uniform(3.5, 9)
            linea(ax, clip, [OJO[0] + r * math.cos(a), OJO[0] + (r + largo) * math.cos(a)],
                  [OJO[1] + r * math.sin(a), OJO[1] + (r + largo) * math.sin(a)], 1.0 + min(1.2, r / 90))
            r += largo + rnd.uniform(3.0, 6.0)


def pixeles(ax, clip):
    """La pupila cuadrada del logotipo: pixeles que se disuelven hacia arriba."""
    rnd = random.Random(4)
    ps = [Rectangle((-39.9 + i * 4.2, 1.0 + j * 4.2), 3.1, 3.1) for j in range(33) for i in range(19)
          if rnd.random() < (1 - j / 33) ** 1.7]
    coleccion(ax, clip, ps)


def espiral(ax, clip):
    t = np.linspace(2.2 * math.pi, 62 * math.pi, 4000)
    r = 4.6 * t / (2 * math.pi)
    linea(ax, clip, OJO[0] + r * np.cos(t), OJO[1] + r * np.sin(t))


def moire(ax, clip):
    for cx, cy, r0 in ((OJO[0], OJO[1], 9.5), (22.0, 126.0, 3.0)):
        for r in np.arange(r0, 170, 6.2):
            parche(ax, clip, Circle((cx, cy), r, fc="none", ec=SURCO, lw=lw(1.0), zorder=3))


def medio_tono(ax, clip):
    ps = []
    for j in range(42):
        for i in range(25):
            x, y = -40.2 + i * 3.35 + (1.675 if j % 2 else 0), 0.8 + j * 3.35
            d = math.hypot(x - OJO[0], y - OJO[1])
            ps.append(Circle((x, y), max(0.5, 1.5 - d / 78)))
    coleccion(ax, clip, ps)


# ── de las plantas y del cultivo ────────────────────────────────────────────
def ramas(ax, clip):
    rnd = random.Random(12)

    def rama(x, y, ang, largo, nivel):
        x2, y2 = x + largo * math.cos(ang), y + largo * math.sin(ang)
        linea(ax, clip, [x, x2], [y, y2], 1.0 + 0.16 * nivel)
        if nivel:
            for s in (-1, 1):
                rama(x2, y2, ang + s * math.radians(rnd.uniform(17, 34)), largo * rnd.uniform(0.68, 0.82), nivel - 1)
    for x0, niv, l0 in ((-22, 7, 25), (20, 7, 28), (-2, 6, 19)):
        rama(x0, -2, math.radians(90 + rnd.uniform(-7, 7)), l0, niv)


def hojas(ax, clip):
    rnd = random.Random(31)
    for x, y, r in empacar(rnd, (3.2, 4.2, 5.4), hueco=1.3):
        g = rnd.uniform(0, math.pi)
        parche(ax, clip, Polygon(lente(x, y, 2 * r, r * 0.95, g), fc=SURCO, ec="none", zorder=3))
        linea(ax, clip, [x - 0.72 * r * math.cos(g), x + 0.72 * r * math.cos(g)],
              [y - 0.72 * r * math.sin(g), y + 0.72 * r * math.sin(g)], 0.8, 4, TAPA)


def gotas(ax, clip):
    """Humedad: gotas de condensacion."""
    rnd = random.Random(17)
    for x, y, r in empacar(rnd, (1.3, 1.7, 2.3, 3.2), hueco=1.5, intentos=5000):
        t = np.linspace(math.radians(-55), math.radians(235), 30)
        pts = list(zip(x + r * np.cos(t), y + r * np.sin(t))) + [(x, y + 2.25 * r)]
        parche(ax, clip, Polygon(pts, fc=SURCO, ec="none", zorder=3))


def anillos(ax, clip):
    """Anillos de crecimiento de un tronco."""
    rnd = random.Random(2)
    th = np.linspace(0, 2 * math.pi, 400)
    for k in range(2, 42):
        f1, f2 = rnd.uniform(0, 6.28), rnd.uniform(0, 6.28)
        r = k * 4.3 * (1 + 0.05 * np.sin(3 * th + f1) + 0.03 * np.sin(7 * th + f2))
        linea(ax, clip, -26 + r * np.cos(th), 22 + r * np.sin(th))


def helice(ax, clip):
    """Doble helice: lo que el cultivo in vitro multiplica."""
    x = np.linspace(-42, 42, 500)
    for y0 in np.arange(6, 140, 14.5):
        f = (y0 * 0.37) % 6.28
        a, b = y0 + 4.2 * np.sin(x / 5.6 + f), y0 - 4.2 * np.sin(x / 5.6 + f)
        linea(ax, clip, x, a)
        linea(ax, clip, x, b)
        for xr in np.arange(-41, 42, 3.4):
            d = 4.2 * math.sin(xr / 5.6 + f)
            if abs(d) > 1.6:
                linea(ax, clip, [xr, xr], [y0 + d, y0 - d], 0.9)


# ── de los datos y de la electronica ────────────────────────────────────────
def red(ax, clip):
    """Los 5 nodos conectados: una red."""
    rnd = random.Random(55)
    pts = [(x, y) for x, y, _ in empacar(rnd, (5.5,), hueco=1.5, intentos=900)]
    arr = np.array(pts)
    seg = set()
    for i, p in enumerate(arr):
        d = np.hypot(*(arr - p).T)
        for j in np.argsort(d)[1:3]:
            seg.add((min(i, int(j)), max(i, int(j))))
    c = LineCollection([[pts[i], pts[j]] for i, j in seg], colors=SURCO, linewidths=lw(1.0), zorder=3)
    ax.add_collection(c)
    c.set_clip_path(clip)
    for k, (x, y) in enumerate(pts):
        parche(ax, clip, Circle((x, y), 2.4 if k % 6 == 0 else 1.5, fc=SURCO, ec="none", zorder=4))
        if k % 6 == 0:
            parche(ax, clip, Circle((x, y), 1.0, fc=TAPA, ec="none", zorder=4))


def franjas(ax, clip):
    """Franjas de clima: cada barra es una lectura; mas ancha = mas calor."""
    rnd = random.Random(9)
    x = -39.0
    while x < 39:
        w = rnd.choice((1.0, 1.0, 1.4, 1.9, 2.6))
        parche(ax, clip, Rectangle((x, 0), w, 139, fc=SURCO, ec="none", zorder=3))
        x += w + rnd.choice((1.2, 1.6, 2.2))


def crestas(ax, clip):
    """Cada linea es un dia de mediciones."""
    rnd = random.Random(23)
    x = np.linspace(-42, 42, 300)
    for k, y0 in enumerate(np.arange(134, 0, -4.6)):
        y = np.full_like(x, y0)
        for _ in range(3):
            c, s, a = rnd.uniform(-28, 28), rnd.uniform(4, 10), rnd.uniform(0, 7.5)
            y += a * np.exp(-((x - c) ** 2) / (2 * s * s))
        f = ax.fill_between(x, y0 - 4.6, y, color=TAPA, zorder=3 + k * 0.01)
        f.set_clip_path(clip)
        linea(ax, clip, x, y, 1.0, 3.005 + k * 0.01)


def flujo(ax, clip):
    """Corrientes de aire alrededor del sensor."""
    x, y = np.meshgrid(np.linspace(-42, 42, 60), np.linspace(-2, 141, 100))
    u = 1.0 + 0.9 * np.cos(y / 17.0) + 0.5 * np.sin(x / 11.0)
    v = 0.9 * np.sin(x / 13.0) - 0.6 * np.cos(y / 23.0)
    s = ax.streamplot(x, y, u, v, density=(1.05, 1.75), color=SURCO, linewidth=lw(1.0), arrowstyle="-", zorder=3)
    s.lines.set_clip_path(clip)


def triangulos(ax, clip):
    rng = np.random.default_rng(14)
    pts = np.column_stack([rng.uniform(-48, 48, 70), rng.uniform(-8, 147, 70)])
    tri = Delaunay(pts)
    seg = {(min(a, b), max(a, b)) for s in tri.simplices for a, b in ((s[0], s[1]), (s[1], s[2]), (s[0], s[2]))}
    c = LineCollection([[pts[a], pts[b]] for a, b in seg], colors=SURCO, linewidths=lw(1.0), capstyle="round", zorder=3)
    ax.add_collection(c)
    c.set_clip_path(clip)


def cubos(ax, clip):
    r = 6.2
    dx, dy = math.sqrt(3) * r, 1.5 * r
    seg = []
    for j in range(-1, 17):
        for i in range(-5, 6):
            cx, cy = i * dx + (dx / 2 if j % 2 else 0), j * dy
            v = [(cx + r * math.cos(math.radians(30 + 60 * k)), cy + r * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
            seg += [[v[k], v[(k + 1) % 6]] for k in range(6)] + [[(cx, cy), v[k]] for k in (0, 2, 4)]
    c = LineCollection(seg, colors=SURCO, linewidths=lw(1.0), capstyle="round", zorder=3)
    ax.add_collection(c)
    c.set_clip_path(clip)


# ── de la cultura y del oficio ──────────────────────────────────────────────
def greca(ax, clip):
    """Greca escalonada, como en los textiles y la arquitectura de Mexico."""
    u = [(0, 0), (0, 6), (6, 6), (6, 2), (2, 2), (2, 4), (4, 4)]
    for y0 in np.arange(2.5, 140, 11.5):
        for k in range(-6, 6):
            x0 = k * 8.6 + (4.3 if int(y0 / 11.5) % 2 else 0)
            linea(ax, clip, [x0 + p[0] for p in u], [y0 + p[1] for p in u], 1.1)
            linea(ax, clip, [x0, x0 + 8.6], [y0, y0], 1.1)


def espiga(ax, clip):
    seg = []
    for j in range(0, 30):
        for i in range(-9, 10):
            x, y = i * 5.0, j * 5.0
            s = 1 if (i + j) % 2 else -1
            seg.append([(x - 1.9, y - 1.9 * s), (x + 1.9, y + 1.9 * s)])
    c = LineCollection(seg, colors=SURCO, linewidths=lw(1.2), capstyle="round", zorder=3)
    ax.add_collection(c)
    c.set_clip_path(clip)


def cesteria(ax, clip):
    ps = []
    for j in range(0, 24):
        for i in range(-7, 8):
            x, y = i * 6.4, j * 6.4
            if (i + j) % 2:
                ps += [Rectangle((x - 2.6, y - 2.1 + k * 1.6 - 0.5), 5.2, 1.0) for k in range(3)]
            else:
                ps += [Rectangle((x - 2.1 + k * 1.6 - 0.5, y - 2.6), 1.0, 5.2) for k in range(3)]
    coleccion(ax, clip, ps)


TANDAS = [
    ("maqueta_texturas_tapa_dht_2.png", "Segunda tanda: del mito, del logotipo y de las plantas", [
        ("16. Los cien ojos de Argos", cien_ojos), ("17. Cola de pavo real", pavo_real),
        ("18. Destello del ojo", destello), ("19. Pixeles que se disuelven", pixeles),
        ("20. Espiral desde el ojo", espiral), ("21. Dos miradas (moiré)", moire),
        ("22. Medio tono desde el ojo", medio_tono), ("23. Ramas", ramas),
        ("24. Hojas", hojas), ("25. Gotas de humedad", gotas)]),
    ("maqueta_texturas_tapa_dht_3.png", "Tercera tanda: del cultivo, de los datos y del oficio", [
        ("26. Anillos de crecimiento", anillos), ("27. Doble hélice", helice),
        ("28. Red de nodos", red), ("29. Franjas de clima", franjas),
        ("30. Crestas de datos", crestas), ("31. Corrientes de aire", flujo),
        ("32. Triángulos", triangulos), ("33. Cubos isométricos", cubos),
        ("34. Greca escalonada", greca), ("35. Espiga", espiga)]),
]


def main():
    for archivo, encabezado, opciones in TANDAS:
        fig = plt.figure(figsize=(FIGW, FIGH), facecolor="white")
        for k, (titulo, fn) in enumerate(opciones):
            col, fila = k % 5, k // 5
            ax = fig.add_axes([0.012 + col * 0.198, 0.50 - fila * 0.49, AXW, AXH])
            clip = tapa_base(ax)
            fn(ax, clip)
            elementos(ax)
            ax.text(0, 141.5, titulo, ha="center", va="bottom", fontsize=12.5)
        fig.text(0.5, 0.985, f"{encabezado} (maqueta a escala; el grabado real es de 0.4 mm, más sutil que aquí)",
                 ha="center", va="top", fontsize=13)
        fig.savefig(RAIZ / "renders" / archivo, dpi=100)
        plt.close(fig)
        print("escrito", archivo)


if __name__ == "__main__":
    main()
