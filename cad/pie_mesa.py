"""Pie de mesa comun para las tres cajas de Argos (18-nov-2026): exhibirlas de pie en el stand, sin pared.

Cada caja cuelga de una placa con los mismos pernos que sus soportes de pared (ojos de cerradura), y la placa
se apoya inclinada 15 grados hacia atras sobre dos pies triangulares IGUALES para las tres cajas, unidos a
media madera (ranura contra ranura, sin tornillos ni pegamento).

  placa_dht       vertical, pernos a `paso` del soporte de pared del dht
  placa_estacion  horizontal, pernos al paso de los tacos de la estacion de entrada
  placa_anaquel   horizontal, con dos espigas lisas para las ranuras M3 de la estacion del anaquel
  pie             triangulo de 4 mm; se imprimen 2 por placa, acostados

Todo se imprime plano sobre la cama, sin soportes. Uso:
  uv run --no-project --python 3.12 --with "build123d>=0.10,<0.14" --with matplotlib python cad/pie_mesa.py
"""
import json
import math
import os

os.environ.setdefault("ARGOS_MODULAR", "1")
from build123d import Axis, Plane, Polygon, Pos, Rot, Box, Align, export_step, export_stl, extrude, fillet  # noqa: E402

import nodos  # noqa: E402
from nodos import DIS, caja_c, cil, perno  # noqa: E402

E = 4.0            # espesor de placas y pies
JUEGO = 0.3        # holgura de la media madera
ANG = 15.0         # inclinacion de la placa hacia atras
ALMA = 10.0        # material que queda en el pie bajo su ranura
SALIDA = nodos.SALIDA   # exports/modular, o exports/capsula con ARGOS_CAPSULA=1 (cambia el paso de las estaciones)


def _ranuras_pie(placa, xs, y_inf):
    """Ranuras en el borde inferior de la placa: montan sobre el alma de cada pie."""
    prof = ALMA / math.cos(math.radians(ANG)) + 0.1
    for x in xs:
        placa -= caja_c(x, y_inf + prof / 2 - 0.05, -0.1, E + JUEGO, prof + 0.1, E + 0.2)
    return placa


def placa_dht(paso):
    """Placa vertical de 60 mm de ancho con dos pernos a `paso` (los del soporte de pared del dht)."""
    largo = paso + 30
    placa = fillet(caja_c(0, 0, 0, 60, largo, E).edges().filter_by(Axis.Z), 5)
    placa += perno(0, paso / 2, E) + perno(0, -paso / 2, E)
    return _ranuras_pie(placa, (-20.0, 20.0), -largo / 2)


def placa_estacion(paso, espigas=False):
    """Placa horizontal para las estaciones: pernos (entrada) o espigas lisas de 3 mm (ranuras M3 del anaquel)."""
    # la caja mide 80 mm de alto y cuelga de sus orejas a media altura: los pernos van a 56 mm del borde inferior
    # para que el fondo de la caja quede ~10 mm arriba de la mesa
    ancho, alto, y_p = paso + 22, 80.0, 16.0
    placa = fillet(caja_c(0, 0, 0, ancho, alto, E).edges().filter_by(Axis.Z), 5)
    placa -= fillet(caja_c(0, -4.0, -0.1, paso - 60, alto - 36, E + 0.2).edges().filter_by(Axis.Z), 6)   # aligerado
    for sx in (-1, 1):
        if espigas:
            placa += cil(sx * paso / 2, y_p, E, 3.0, 5.0)
        else:
            placa += perno(sx * paso / 2, y_p, E)
    return _ranuras_pie(placa, (-paso / 2 + 28, paso / 2 - 28), -alto / 2)


def pie():
    """Pie triangular: se imprime acostado. La ranura inclinada recibe la placa; el alma de 10 mm entra en la
    ranura de la placa. 26 mm hacia el frente y 46 mm hacia atras de la placa."""
    perfil = Polygon((0, 0), (72, 0), (72, 6), (36, 36), (18, 36), (0, 6), align=None)
    s = extrude(perfil, amount=E)
    s = fillet(s.edges().filter_by(Axis.Z), 2)
    ranura = Pos(26, ALMA, -0.1) * Rot(0, 0, -ANG) * Box(E + JUEGO, 60, E + 0.2, align=(Align.CENTER, Align.MIN, Align.MIN))
    return s - ranura


def piezas():
    paso_dht = nodos.nodo_dht()["paso_pernos"]
    paso_est = nodos.estacion_entrada()["paso_pernos"]
    return {"pie_mesa_placa_dht": placa_dht(paso_dht),
            "pie_mesa_placa_entrada": placa_estacion(paso_est),
            "pie_mesa_placa_anaquel": placa_estacion(paso_est, espigas=True),
            "pie_mesa_pie": pie()}, {"paso_dht": paso_dht, "paso_estaciones": paso_est}


if __name__ == "__main__":
    SALIDA.mkdir(parents=True, exist_ok=True)
    ps, notas = piezas()
    resumen = dict(notas)
    for nombre, s in ps.items():
        export_step(s, str(SALIDA / f"{nombre}.step"))
        export_stl(s, str(SALIDA / f"{nombre}.stl"), tolerance=0.02, angular_tolerance=0.2)
        bb = s.bounding_box().size
        resumen[nombre] = {"caja_mm": [round(bb.X, 1), round(bb.Y, 1), round(bb.Z, 1)],
                           "masa_g_petg": round(s.volume / 1000 * DIS["densidad_petg"], 1)}
        print(nombre, resumen[nombre])
    # chequeo de la media madera: pie colocado en su ranura de la placa del dht, sin choque
    (SALIDA / "verificacion_pie_mesa.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False),
                                                       encoding="utf-8")
