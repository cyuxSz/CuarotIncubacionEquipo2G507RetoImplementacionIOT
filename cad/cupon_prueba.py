"""Cupon de prueba de impresion: en ~10 g de PETG reune lo que mas puede fallar de las cajas, con las MISMAS
funciones y parametros de cad/nodos.py, para afinar la impresora antes de gastar horas en una caja.

Uso (desde la raiz):
    uv run --no-project --python 3.12 --with "build123d>=0.10,<0.14" --with matplotlib python cad/cupon_prueba.py

Salida: cad/exports/modular/cupon_prueba.stl (las dos piezas ya acomodadas en la cama) y cupon_prueba.step,
mas cupon_prueba_base.stl y cupon_prueba_tapa.stl por separado.

Que trae y que revisar:
  base  pared de 2 mm con una lengua elastica (ranuras con alivio redondo y rampa en la raiz) y una columna con
        hueco de 5.6 mm  ->  la lengua flexiona sin blanquearse ni romperse en la raiz
  tapa  placa de 2.5 mm, se imprime con el FRENTE EN LA CAMA igual que las tapas reales:
        pestana con cartela (entra en la lengua y hace "clic"), perno de 5.0 mm (entra en el hueco con la holgura
        de diseno, 0.3 mm por lado), agujero de LED de 5.5 mm (el LED de 5 mm entra justo), persiana a 45 grados
        (sin hilos colgando), ojo de Argos, los 5 iconos y el texto "Argos" hundidos 0.4 mm (se leen, sin cerrarse)
"""
import os

os.environ["ARGOS_MODULAR"] = "1"

from build123d import Compound, Plane, Pos, Rot, export_step, export_stl  # noqa: E402

import nodos  # noqa: E402
from nodos import DIS, caja, cil, grabar, icono, lengua_pared, med, ojo_argos, persiana, pestana_tapa, texto  # noqa: E402

SALIDA = nodos.RAIZ / "exports" / "modular"
LARGO = 58.0          # y
X0_TAPA = 14.0        # la tapa va de x = 14 a x = W/2 = 40  (26 x 58 mm)
DB = 16.0             # altura de la pared: la lengua mide lo mismo que en la caja
Y_BROCHE = 15.0
PERNO = (33.5, 42.5, 5.0, 5.0)   # x, y, diametro, largo


def cupon():
    p, W, hg, t = DIS["pared"], DIS["ancho"], DIS["holgura"], DIS["tapa"]
    xo = W / 2 - p - hg
    D = DB + t
    # ── base: piso angosto, pared con la lengua, respaldo de la pestana y columna con hueco ──
    base = caja(28.0, 0, 0, W / 2 - 28.0, LARGO, p)
    base += caja(W / 2 - p, 0, 0, p, LARGO, DB)
    suma, resta = lengua_pared(1, W, p, DB, Y_BROCHE)
    base = base - resta + suma
    # respaldo detras de la pestana (en la caja lo da la tapa completa, que no puede moverse hacia adentro)
    base += caja(xo - 3.0 - hg - 1.6, Y_BROCHE - 8.5, p, 1.6, 17.0, DB - 1.0 - p)
    px, py, pd, pl = PERNO
    base += caja(px - 4.5, py - 4.5, p, W / 2 - p - (px - 4.5), 9.0, DB - p)
    base -= cil(px, py, DB - pl - 1.0, pd + 2 * hg, pl + 1.1)

    # ── tapa: placa con pestana, perno, agujero de LED, persiana y grabados ──
    tapa = caja(X0_TAPA, 0, DB, W / 2 - X0_TAPA, LARGO, t)
    tapa += pestana_tapa(1, W, p, DB, Y_BROCHE)
    tapa += cil(px, py, DB - pl, pd, pl)
    tapa -= cil(20.0, 7.0, DB - 0.1, med("led", "agujero"), t + 0.2)
    tapa -= persiana(26.0, 33.5, 16.0, DIS["ranura"], DB, D)

    def frente(x, y):
        return Plane(origin=(x, y, D), z_dir=(0, 0, 1))

    tapa -= grabar(frente(31.0, 7.0), icono("dht"))
    tapa -= grabar(frente(26.0, 17.0), ojo_argos())
    tapa -= texto("Argos", 4.2, frente(26.0, 25.0), DIS["hundido"])
    tapa -= grabar(frente(19.0, 42.5), icono("pir"))
    tapa -= grabar(frente(26.5, 42.5), icono("puerta"))
    tapa -= grabar(frente(20.5, 52.5), icono("acel"))
    tapa -= grabar(frente(32.5, 52.0), icono("luz"))
    return base, tapa


def a_cama(s, voltear=False):
    if voltear:
        s = Rot(180, 0, 0) * s
    bb = s.bounding_box()
    return Pos(-bb.min.X, -bb.min.Y, -bb.min.Z) * s


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    base, tapa = cupon()
    choque = (base & tapa).volume
    cama_base = a_cama(base)
    cama_tapa = Pos(cama_base.bounding_box().max.X + 2.0, 0, 0) * a_cama(tapa, voltear=True)   # frente en la cama
    juntas = Compound(children=[cama_base, cama_tapa])
    export_step(Compound(children=[base, tapa]), str(SALIDA / "cupon_prueba.step"))
    export_stl(juntas, str(SALIDA / "cupon_prueba.stl"), tolerance=0.02, angular_tolerance=0.2)
    export_stl(cama_base, str(SALIDA / "cupon_prueba_base.stl"), tolerance=0.02, angular_tolerance=0.2)
    export_stl(cama_tapa, str(SALIDA / "cupon_prueba_tapa.stl"), tolerance=0.02, angular_tolerance=0.2)
    masa = 0.0
    for nombre, s in (("base", base), ("tapa", tapa)):
        bb = s.bounding_box().size
        g = s.volume / 1000 * DIS["densidad_petg"]
        masa += g
        print(f"cupon {nombre}: {bb.X:.1f} x {bb.Y:.1f} x {bb.Z:.1f} mm, {g:.1f} g de PETG (macizo), "
              f"{len(s.solids())} solido(s)")
    bb = juntas.bounding_box().size
    print(f"en la cama: {bb.X:.1f} x {bb.Y:.1f} x {bb.Z:.1f} mm, {masa:.1f} g en total")
    print(f"choque base-tapa: {choque:.3f} mm3 (debe ser 0)")


if __name__ == "__main__":
    main()
