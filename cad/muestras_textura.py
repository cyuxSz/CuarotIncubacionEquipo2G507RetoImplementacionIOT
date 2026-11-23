"""Muestras de textura para el frente de las tapas (20-nov): cuadros de 32 x 32 x 2.5 mm, uno por textura.

No toca las cajas: es un catalogo para elegir antes de aplicar nada. Cada cuadro se imprime igual que una tapa,
con el FRENTE EN LA CAMA: la textura es un grabado de 0.4 mm (como el rotulo "Argos") con trazos de 1.0 mm o mas,
que es lo que ya se valido para imprimir sin soportes. Lleva un marco liso de 2 mm y una esquina recortada
(abajo a la izquierda viendo el frente) para saber como va orientado.

  uv run --no-project --python 3.12 --with "build123d>=0.10,<0.14" --with matplotlib python cad/muestras_textura.py

Salida: cad/exports/muestras/muestra_<n>_<nombre>.stl, muestras_textura_todas.stl (los 6 en una cama) y
cad/renders/muestras_textura.png (como se ven de frente).
"""
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from build123d import (Align, Axis, Box, Cylinder, Plane, Pos, RegularPolygon, Rot, export_stl, extrude,  # noqa: E402
                       mirror)

RAIZ = Path(__file__).resolve().parent
SALIDA = RAIZ / "exports" / "muestras"
LADO, ESPESOR, MARCO, HONDO = 32.0, 2.5, 2.0, 0.4
C, MIN = Align.CENTER, Align.MIN
ZONA = LADO - 2 * MARCO


def zona():
    return Box(ZONA, ZONA, HONDO, align=(C, C, MIN))


def rayas(ang, ancho, paso):
    s = None
    for k in range(-14, 15):
        b = Rot(0, 0, ang) * Pos(k * paso, 0, 0) * Box(ancho, 90, HONDO, align=(C, C, MIN))
        s = b if s is None else s + b
    return s & zona()


def panal():
    r, trazo = 3.2, 1.0
    dx = math.sqrt(3) * r + trazo
    dy = dx * math.sqrt(3) / 2
    celdas = None
    for j in range(-4, 5):
        for i in range(-4, 5):
            x = i * dx + (dx / 2 if j % 2 else 0)
            c = Pos(x, j * dy, 0) * extrude(RegularPolygon(r, 6, rotation=30), amount=HONDO)
            celdas = c if celdas is None else celdas + c
    return zona() - celdas


def puntos():
    s, paso = None, 3.5
    n = int(ZONA // paso)
    for j in range(n):
        d = 2.6 - 1.5 * j / (n - 1)          # de 2.6 mm abajo a 1.1 mm arriba: efecto de degradado
        for i in range(n):
            c = Pos((i - (n - 1) / 2) * paso, (j - (n - 1) / 2) * paso, 0) * \
                Cylinder(d / 2, HONDO, align=(C, C, MIN))
            s = c if s is None else s + c
    return s


def ondas():
    s = Cylinder(1.3, HONDO, align=(C, C, MIN))
    for r in (4.0, 7.0, 10.0, 13.0, 16.0, 19.0):
        s += Cylinder(r + 0.55, HONDO, align=(C, C, MIN)) - Cylinder(r - 0.55, HONDO + 0.1, align=(C, C, MIN))
    return s & zona()


TEXTURAS = [
    ("panal", "Panal de hexágonos", panal),
    ("diagonal", "Estrías diagonales", lambda: rayas(45, 1.2, 3.4)),
    ("persiana", "Estrías horizontales", lambda: rayas(90, 1.2, 3.2)),
    ("puntos", "Puntos en degradado", puntos),
    ("ondas", "Ondas concéntricas", ondas),
    ("rombos", "Rombos", lambda: rayas(45, 1.0, 5.0) + rayas(-45, 1.0, 5.0)),
]


def cuadro(grabado):
    """Cuadro con el frente en z = 0 (la cama). Se modela viendo el frente y al final se refleja en x, porque
    al imprimirlo boca abajo y voltearlo la imagen queda en espejo."""
    base = Box(LADO, LADO, ESPESOR, align=(C, C, MIN))
    base -= Pos(-LADO / 2, -LADO / 2, 0) * Rot(0, 0, 45) * Box(4.2, 4.2, ESPESOR * 3, align=(C, C, C))  # esquina
    return base - grabado


def contornos(solido):
    """Poligonos (x, y) de las caras del frente (z = 0), para dibujar la vista previa."""
    caras = [f for f in solido.faces() if abs(f.center().Z) < 1e-6 and abs(f.normal_at().Z) > 0.99]
    res = []
    for f in caras:
        ext = [f.outer_wire().position_at(t / 240) for t in range(241)]
        huecos = [[w.position_at(t / 120) for t in range(121)] for w in f.inner_wires()]
        res.append(([(p.X, p.Y) for p in ext], [[(p.X, p.Y) for p in h] for h in huecos]))
    return res


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    fig, ejes = plt.subplots(2, 3, figsize=(10.5, 7.4), facecolor="white")
    todos = None
    for k, (clave, nombre, fn) in enumerate(TEXTURAS):
        vista = cuadro(fn())                       # como se ve de frente
        pieza = mirror(vista, Plane.YZ)            # como va en la cama
        export_stl(pieza, str(SALIDA / f"muestra_{k + 1}_{clave}.stl"), tolerance=0.02, angular_tolerance=0.2)
        col, fila = k % 3, k // 3
        # en la cama se acomodan en espejo para que, al voltearlos, queden en el mismo orden que la imagen
        puesto = Pos((1 - col) * (LADO + 5), (0.5 - fila) * (LADO + 5), 0) * pieza
        todos = puesto if todos is None else todos + puesto
        ax = ejes[fila][col]
        ax.set_facecolor("white")
        ax.fill([-16, 16, 16, -16], [-16, -16, 16, 16], color="#3a3f47")          # fondo = grabado (hundido)
        for ext, huecos in contornos(vista):
            ax.fill(*zip(*ext), color="#e9ecef", linewidth=0)
            for h in huecos:
                ax.fill(*zip(*h), color="#3a3f47", linewidth=0)
        ax.set_xlim(-17, 17)
        ax.set_ylim(-17, 17)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(f"{k + 1}. {nombre}", fontsize=13, pad=6)
        vol = pieza.volume / 1000
        print(f"ok muestra_{k + 1}_{clave}: {len(pieza.solids())} solido(s), {vol:.2f} cm3")
    export_stl(todos, str(SALIDA / "muestras_textura_todas.stl"), tolerance=0.02, angular_tolerance=0.2)
    bb = todos.bounding_box().size
    print(f"ok muestras_textura_todas: {bb.X:.0f} x {bb.Y:.0f} x {bb.Z:.1f} mm, {todos.volume / 1000 * 1.27:.0f} g de PETG")
    fig.suptitle("Texturas para el frente de las tapas: claro = superficie, oscuro = grabado de 0.4 mm",
                 fontsize=12, y=0.98)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    (RAIZ / "renders").mkdir(exist_ok=True)
    fig.savefig(RAIZ / "renders" / "muestras_textura.png", dpi=130)


if __name__ == "__main__":
    main()
