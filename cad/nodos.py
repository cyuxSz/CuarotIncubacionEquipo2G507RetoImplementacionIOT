"""Argos: carcasas parametricas de los nodos (build123d).

Uso (desde la raiz del proyecto):
    uv run --no-project --python 3.12 --with "build123d>=0.10,<0.14" --with matplotlib python cad/nodos.py [dht ...]

Por nodo:
  1. arma el gemelo digital (protoboard, NodeMCU, modulos, conectores Dupont) con las medidas de
     cad/medidas.json y la distribucion de hardware/breadboard/layouts.py;
  2. deriva la carcasa (base, tapa y piezas de montaje impresas) de esa envolvente;
  3. comprueba interferencias (volumen de interseccion = 0) y holguras;
  4. exporta STEP (ensamble, coordenadas del nodo) y STL (cada pieza en su orientacion de impresion)
     a cad/exports/ y un resumen en cad/exports/verificacion_<nodo>.json.

Ejes del nodo: x = ancho (derecha viendo el frente), y = alto (arriba), z = profundidad
(z = 0 espalda contra la pared, z = D frente). Unidades: mm.
"""
import json
import math
import os
import sys
from pathlib import Path

from build123d import (Align, Axis, Box, Circle, FontStyle, Cone, Cylinder, Compound, Plane, Pos, Polygon, Rectangle, RectangleRounded, Rot, SortBy, Text, chamfer,
                       export_step, export_stl, extrude, fillet)

RAIZ = Path(__file__).resolve().parent
# Variante modular (10-nov): protoboard con clips, tapa a presion sin tornillos, esquinas redondeadas.
# Se activa con --modular o ARGOS_MODULAR=1 y escribe en exports/modular/ (la version con tornillos queda intacta).
# Variante capsula (18-nov): las ESTACIONES con extremos semicirculares y sin orejas (cuelgan de ojos de cerradura
# en la espalda); la caja dht no cambia. Implica la modular. Se activa con --capsula o ARGOS_CAPSULA=1 y escribe
# en exports/capsula/. Cuerpo de ~201 x 80 mm: cabe derecho en una cama de 220 mm.
CAPSULA = os.environ.get("ARGOS_CAPSULA") == "1" or "--capsula" in sys.argv
MODULAR = CAPSULA or os.environ.get("ARGOS_MODULAR") == "1" or "--modular" in sys.argv
SALIDA = RAIZ / "exports" / ("capsula" if CAPSULA else "modular") if MODULAR else RAIZ / "exports"
sys.path.insert(0, str(RAIZ.parent / "hardware" / "breadboard"))
import layouts  # noqa: E402

MED = json.loads((RAIZ / "medidas.json").read_text(encoding="utf-8"))
C, MIN, MAX = Align.CENTER, Align.MIN, Align.MAX


def med(*ruta):
    d = MED
    for k in ruta:
        d = d[k]
    return d["valor"] if isinstance(d, dict) and "valor" in d else d


# ── parametros de diseno (los de componentes vienen de medidas.json) ─────────
DIS = dict(
    pared=med("impresion", "pared"),
    holgura=med("impresion", "holgura"),
    chaflan=med("impresion", "chaflan"),
    hundido=med("impresion", "texto_hundido"),
    ranura=med("impresion", "ranura_ventilacion"),
    holgura_min=med("impresion", "holgura_minima_modulos"),
    densidad_petg=1.27,                  # g/cm3
    ancho=80.0,                          # 76 del diseno no deja 2 mm entre protoboard y torretas
    tapa=2.5,                            # espesor de la tapa
    labio=(1.0, 2.0),                    # ancho y alto del labio de la tapa
    torreta_d=8.0, torreta_margen=6.2,   # del borde exterior al eje
    inserto_d=med("fijacion", "inserto_termico", "agujero"), inserto_prof=5.5, piloto_d=3.2,
    paso_m3=3.4, avellanado_d=6.6, torreta_tapa=3.0,
    oreja=(30.0, 14.0, 3.0),             # orejas de montaje en la espalda
    ojo_cabeza=med("fijacion", "ojo_cerradura", "cabeza"), ojo_ranura=med("fijacion", "ojo_cerradura", "ranura"),
    ojo_carrera=6.0,
    perno=(3.4, 3.4, 7.4),               # perno impreso: diametro del cuello, largo del cuello, cabeza
    anaquel_espesor=18.0,                # [POR CONFIRMAR] espesor del borde del anaquel
    dupont=(2.5, 14.0),                  # carcasa del conector macho: lado y alto sobre la protoboard
    # --- variante modular: todo nominal, se afina con el cupon cad/pruebas_clips.py ---
    radio=6.0,                           # radio de las esquinas verticales de la caja
    clip=dict(largo=22.0, raiz=4.0, esp=1.6, gancho=1.0, juego=0.15, sobre=0.1),   # clip de la protoboard
    broche=dict(alto=12.0, ancho=10.0, esp=1.4, aprieto=0.5, ranura=0.8),          # lengua de pared de la tapa
    grapa=dict(esp=1.6, ancho=8.0, aprieto=0.4),                                   # grapa de la OLED
)

PASO = layouts.PASO


class Gemelo:
    """Piezas compradas como bloques con medidas nominales."""

    def __init__(self):
        self.partes = {}   # nombre -> (solido, montado)

    def agregar(self, nombre, solido, montado=False):
        self.partes[nombre] = (solido, montado)


# ── ayudas geometricas ───────────────────────────────────────────────────────
def caja(x, y, z, dx, dy, dz):
    """Caja con esquina minima en (x, y, z)."""
    return Pos(x, y, z) * Box(dx, dy, dz, align=(MIN, MIN, MIN))


def caja_c(xc, yc, z0, dx, dy, dz):
    """Caja centrada en x, y; desde z0 hacia +z."""
    return Pos(xc, yc, z0) * Box(dx, dy, dz, align=(C, C, MIN))


def cil(xc, yc, z0, d, h):
    return Pos(xc, yc, z0) * Cylinder(d / 2, h, align=(C, C, MIN))


def ojo_cerradura(xc, y_entrada, z0, h, dir="y+"):
    """Entrada para la cabeza y ranura de ojo_carrera: hacia +y (dht) o hacia -x (estaciones, que se
    giran 90 grados y quedan con la ranura hacia abajo)."""
    r = DIS["ojo_ranura"]
    car = DIS["ojo_carrera"]
    if dir == "x-":
        return (cil(xc, y_entrada, z0, DIS["ojo_cabeza"], h)
                + caja_c(xc - car / 2, y_entrada, z0, car, r, h)
                + cil(xc - car, y_entrada, z0, r, h))
    return (cil(xc, y_entrada, z0, DIS["ojo_cabeza"], h)
            + caja_c(xc, y_entrada + car / 2, z0, r, car, h)
            + cil(xc, y_entrada + car, z0, r, h))


def gota_x(xc, yc, zc, d, largo):
    """Agujero horizontal a lo largo de x con techo en punta a 45 grados (se imprime sin soportes)."""
    r = d / 2
    rombo = Pos(xc, yc, zc) * Rot(45, 0, 0) * Box(largo, 2 * r, 2 * r)
    return Pos(xc, yc, zc) * Rot(0, 90, 0) * Cylinder(r, largo) + (rombo & caja_c(xc, yc, zc, largo, 4 * r, 2 * r))


def prisma_xz(pts, y0, largo):
    """Perfil dibujado en el plano XZ (x, z) y extruido de y0 a y0 + largo."""
    s = extrude(Plane.XZ * Polygon(*pts, align=None), amount=largo)
    return Pos(0, y0 - s.bounding_box().min.Y, 0) * s      # el sentido de extrusion depende del giro del perfil


def clip_piso(sx, x_borde, yc, z_sup, x_pared, p, gancho=None):
    """Clip de la protoboard: brazo vertical paralelo al borde largo, suelto del piso por una ranura pasante
    (se imprime desde la cama, con las fibras a lo largo del brazo) y gancho en V sobre el borde de la protoboard.
    Devuelve (suma, resta). sx = lado (+1 derecha); x_borde = semiancho de la protoboard; yc = centro del brazo."""
    c = DIS["clip"]
    g = c["gancho"] if gancho is None else gancho
    xi = x_borde + c["juego"]
    xo = xi + c["esp"]
    y0, y1 = yc - c["largo"] / 2, yc + c["largo"] / 2
    zb = z_sup + c["sobre"]
    ztop = zb + 2 * g + 0.4
    resta = caja_c(sx * (xi - 0.6 + xo + g + 0.4) / 2, (y0 + c["raiz"] + y1 + 0.8) / 2, -0.1,
                   xo + g + 0.4 - (xi - 0.6), y1 + 0.8 - (y0 + c["raiz"]), p + 0.2)
    brazo = caja_c(sx * (xi + xo) / 2, yc, 0, c["esp"], c["largo"], ztop)
    refuerzo = caja_c(sx * (xo + x_pared) / 2, y0 + c["raiz"] / 2, 0, x_pared - xo + 0.02, c["raiz"], ztop)
    # gancho en V: 45 grados por abajo (se imprime sin soportes; la protoboard sale jalandola) y por arriba (entrada)
    diente = prisma_xz([(sx * xi, zb), (sx * (xi - g), zb + g), (sx * (xi - g), zb + g + 0.4), (sx * xi, ztop)],
                       y1 - 7.0, 7.0)
    return brazo + refuerzo + diente, resta


def lengua_pared(sx, W, p, Db, yc, aprieto=None):
    """Lengua elastica cortada en la pared lateral (dos ranuras desde el borde) con un diente en V hacia adentro
    que entra en la muesca de la pestana de la tapa. Devuelve (suma, resta)."""
    b = DIS["broche"]
    ap = b["aprieto"] if aprieto is None else aprieto
    xi = W / 2 - p
    zr = Db - b["alto"]
    alivio = p - b["esp"]
    zc = Db - 3.5
    resta = caja_c(sx * (xi + alivio / 2 - 0.005), yc, zr, alivio + 0.01, b["ancho"], b["alto"] + 0.1)
    for dy in (-1, 1):
        resta += caja_c(sx * (W / 2 - p / 2), yc + dy * (b["ancho"] + b["ranura"]) / 2, zr, p + 1, b["ranura"],
                        b["alto"] + 0.1)
    # raiz sin esquinas vivas (ahi se concentra el esfuerzo al flexionar): cada ranura termina en un alivio
    # redondo de 1.6 mm y el escalon del adelgazamiento se cambia por una rampa (cartela) de 2:1
    for dy in (-1, 1):
        resta += (Pos(sx * (W / 2 - p / 2), yc + dy * (b["ancho"] + b["ranura"]) / 2, zr + 0.4)
                  * Rot(0, 90, 0) * Cylinder(0.8, p + 1))
    rampa = prisma_xz([(sx * xi, zr), (sx * (xi + alivio), zr), (sx * (xi + alivio), zr + 2 * alivio)],
                      yc - b["ancho"] / 2, b["ancho"])
    alto_d = alivio + DIS["holgura"] + ap     # del fondo del alivio a la punta
    diente = prisma_xz([(sx * (xi + alivio), zc - alto_d), (sx * (xi + alivio), zc + alto_d),
                        (sx * (xi + alivio - alto_d), zc)], yc - 4.0, 8.0)
    return diente + rampa, resta


def pestana_tapa(sx, W, p, Db, yc):
    """Pestana de la tapa que baja por dentro de la pared, con muesca en V para el diente de la lengua."""
    xo = W / 2 - p - DIS["holgura"]
    xin = xo - 3.0
    zc, zb = Db - 3.5, Db - 7.0
    # cartela de 1 mm a 45 grados en la raiz interior (union con la tapa): reparte el esfuerzo al abrir
    pts = [(xin - 1.0, Db + 0.2), (xo, Db + 0.2), (xo, zc + 0.85), (xo - 0.85, zc), (xo, zc - 0.85), (xo, zb + 1.0),
           (xo - 1.0, zb), (xin, zb), (xin, Db - 1.0)]
    return prisma_xz([(sx * x, z) for x, z in pts], yc - 4.5, 9.0)


def plano_frente(n, origen):
    """Plano del frente para texto legible: en las cajas horizontales (giro) el marco local esta girado."""
    xd = (0, -1, 0) if getattr(n, "giro", False) else (1, 0, 0)
    return Plane(origin=origen, x_dir=xd, z_dir=(0, 0, 1))


def texto(txt, alto, plano, profundidad):
    # negrita: el trazo de Arial normal a 4-5 mm mide ~0.45 mm y la pata de elefante lo cierra (el frente va en la
    # cama); en negrita queda en ~0.65-0.75 mm
    t = plano * Text(txt, font_size=alto, font="Arial", font_style=FontStyle.BOLD, align=(C, C))
    return extrude(t, amount=profundidad, both=True)


# ── protoboard ───────────────────────────────────────────────────────────────
class Protoboard:
    def __init__(self, y_borde_sup, z_espalda, columnas=30):
        clave = "protoboard_nodo_propuesta" if columnas == 30 else "protoboard_kit"
        self.largo, self.ancho, self.alto = med(clave, "dimensiones")
        self.y_sup = y_borde_sup
        self.y_inf = y_borde_sup - self.largo
        self.z0 = z_espalda
        self.z_sup = z_espalda + self.alto
        self.y_col1 = y_borde_sup - (self.largo - (columnas - 1) * PASO) / 2

    def xy(self, h):
        fila, col = layouts.orificio(h)
        return (layouts.FILA_X[fila] - 5.5) * PASO, self.y_col1 - (col - 1) * PASO

    def y_col(self, col):
        return self.y_col1 - (col - 1) * PASO

    def solido(self):
        return caja_c(0, (self.y_sup + self.y_inf) / 2, self.z0, self.ancho, self.largo, self.alto)


# ═════════════════════════════════════════════════════════════════════════════
#  Cuerpo comun de todos los nodos
# ═════════════════════════════════════════════════════════════════════════════
class Nodo:
    """Contexto de construccion: medidas derivadas, gemelo, base y tapa en curso."""


# ── grabados del frente: ojo de Argos e iconos por sensor (hundidos como el texto) ───────────
def _lente(ancho, alto):
    """Almendra: interseccion de dos circulos; ancho x alto totales."""
    a, h = ancho / 2, alto / 2
    rad = (a * a + h * h) / (2 * h)
    return (Pos(0, rad - h) * Circle(rad)) & (Pos(0, h - rad) * Circle(rad))


def _aro(d, trazo):
    return Circle(d / 2) - Circle(d / 2 - trazo)


def ojo_argos(ancho=14.0):
    """Ojo del logotipo de Argos (20-nov): almendra de 1.0 mm de trazo, pupila CUADRADA y tres rayos arriba.
    Regla de impresion (boquilla 0.4, frente contra la cama): lo hundido mide >= 1.0 mm y lo que queda en
    relieve entre dos hundidos >= 0.8 mm. Por eso mide 14 mm de ancho (con 11 la pupila tocaba los parpados) y
    los rayos van un poco mas cortos y pegados que en el logotipo. El conjunto baja 1.9 mm respecto al origen
    para que los rayos no lleguen a la ventana de la pantalla."""
    alto = ancho * 0.447
    pupila = alto - 2.0 - 1.7                      # deja 0.85 mm de relieve arriba y abajo
    fig = (_lente(ancho, alto) - _lente(ancho - 2.2, alto - 2.0)) + Rectangle(pupila, pupila)
    fig += Pos(0, alto / 2 + 1.07 + 1.0) * Rectangle(1.0, 2.0)
    for s in (-1, 1):
        fig += Pos(s * 0.213 * ancho, alto / 2 + 0.57 + 1.0) * Rot(0, 0, -s * 25) * Rectangle(1.0, 2.0)
    return Pos(0, -1.9) * fig


def icono(tipo, tam=7.0):
    """Icono 2D de ~`tam` mm de alto, centrado: dht, pir, puerta, acel o luz. Misma regla que el ojo: trazos
    hundidos >= 1.0 mm y relieves entre hundidos >= 0.8 mm (las cotas en mm fijos no se escalan con `tam`)."""
    s, tr = tam / 7.0, 1.0
    if tipo == "dht":      # termometro: tubo con bulbo (relieve interior de 1.2 mm)
        tubo = Pos(0, 1.0 * s) * RectangleRounded(3.2 * s, 5.0 * s, 1.55 * s)
        return (tubo - Pos(0, 1.0 * s) * RectangleRounded(3.2 * s - 2 * tr, 5.0 * s - 2 * tr, 0.55)
                ) + Pos(0, -2.0 * s) * Circle(1.75 * s)
    if tipo == "pir":      # persona: cabeza y torso, separados por 0.8 mm
        return Pos(0, 2.5 * s) * Circle(1.2 * s) + Pos(0, -1.5 * s) * RectangleRounded(3.6 * s, 4.0 * s, 1.2 * s)
    if tipo == "puerta":   # marco abierto por abajo y perilla (relieves de 0.8 mm o mas a cada lado de la perilla)
        marco = Rectangle(5.6 * s, 7.0 * s) - Pos(0, -tr / 2) * Rectangle(5.6 * s - 2 * tr, 7.0 * s - tr)
        return marco + Pos(0.45 * s, -0.3 * s) * Circle(0.55)
    if tipo == "acel":     # onda de vibracion: punto y dos arcos de 1.0 mm separados 0.8 mm
        fig = Circle(0.6)
        for r_in in (1.4, 3.2):
            fig += (Circle(r_in + tr) - Circle(r_in)) & Pos(0, 5) * Rectangle(20, 10)
        return Pos(0, -1.8) * fig
    if tipo == "luz":      # sol: disco y 8 rayos (0.9 mm entre disco y rayos; 0.88 mm entre rayos)
        fig = Circle(1.5 * s)
        for k in range(8):
            fig += Rot(0, 0, 45 * k) * Pos(3.0 * s, 0) * Rectangle(1.2 * s, tr)
        return fig
    raise KeyError(tipo)


def grabar(plano, figura, dx=0.0, dy=0.0):
    """Solido para restar: `figura` (2D) sobre `plano`, corrida (dx, dy) en el plano, hundida como el texto."""
    return extrude(plano * (Pos(dx, dy) * figura), amount=DIS["hundido"], both=True)


def persiana(xc, yc, ancho_x, r, z0, z1):
    """Ranura inclinada 45 grados en la tapa (persiana): por fuera (z1) queda mas abajo que por dentro (z0), asi
    no hay linea de vista recta hacia el sensor y el aire pasa. Se imprime sin soportes (paredes a 45 grados)."""
    dz = z1 - z0
    perfil = Plane.YZ * Polygon((yc - r / 2 + dz / 2 + 0.1, z0 - 0.1), (yc + r / 2 + dz / 2 + 0.1, z0 - 0.1),
                                (yc + r / 2 - dz / 2 - 0.1, z1 + 0.1), (yc - r / 2 - dz / 2 - 0.1, z1 + 0.1), align=None)
    return Pos(xc, 0, 0) * extrude(perfil, amount=ancho_x / 2, both=True)


def comun(nombre, lay_nombre, camara=0.0, orejas="vertical", y_marca=None, y_led_desde_arriba=14.0,
          leds=((None, None),), giro=False, led_x=0.0, broches=None, iconos=()):
    """Gemelo de la protoboard + caja base/tapa compartida por todas las cajas.

    camara: alto interior de una camara inferior aislada (solo dht); 0 = sin camara.
    orejas: "vertical" (ojos de cerradura arriba y abajo), "laterales" (ranuras M3, montaje rigido),
    "llave_x" / "rigidas_x" (cajas horizontales: orejas en los extremos con ranura hacia abajo / ranura M3).
    giro: la caja se modela vertical y al final se gira 90 grados para quedar horizontal (menos alto).
    led_x: posicion de los LED a lo ancho del marco local (en cajas giradas queda a media altura).
    leds: un par verde/rojo por NodeMCU: (columna de la protoboard o None = arriba, etiqueta hundida).
    Con 2 NodeMCU (estaciones) la protoboard es la MB-102 de 830 puntos y la energia entra por un
    modulo USB-C en la pared izquierda.
    broches (solo variante modular): alturas y de las lenguas de pared que retienen la tapa.
    """
    n = Nodo()
    n.giro = giro
    n.nombre = nombre
    p, hg, W = DIS["pared"], DIS["holgura"], DIS["ancho"]
    n.p, n.hg, n.W = p, hg, W
    lay = layouts.LAYOUTS[lay_nombre]
    n.lay = lay
    # --- distribucion vertical (desde el piso) ---
    sep = DIS["holgura_min"]
    n.camara = camara
    if camara:
        n.aire = 3.0
        n.y_pared1 = p + camara
        n.y_pared2 = n.y_pared1 + 2 + n.aire
        y_pb_inf = n.y_pared2 + 2 + sep
    else:
        y_pb_inf = p + sep
    columnas = layouts.columnas(lay)
    n.estacion = estacion = columnas > 30
    n.capsula = cap = CAPSULA and estacion
    pb_largo = med("protoboard_nodo_propuesta" if not estacion else "protoboard_kit", "dimensiones")[0]
    if cap:
        # extremos semicirculares: las esquinas de la protoboard (y sus guias) deben caber dentro del arco interior
        ri_cap = W / 2 - p
        medio = med("protoboard_kit", "dimensiones")[1] / 2 + hg + 1.3
        margen = ri_cap - math.sqrt(ri_cap ** 2 - medio ** 2) + 2.0
        y_pb_inf = p + margen
        orejas = "capsula_rigida" if orejas == "rigidas_x" else "capsula"
        y_led_desde_arriba = W / 2 - 2.0      # el primer par de LED baja hasta donde el arco ya deja ancho
    y_pb_sup = y_pb_inf + pb_largo
    n.H = H = (y_pb_sup + margen + p) if cap else (y_pb_sup + med("nodemcu", "vuelo_usb") + sep + 0.1 + p)
    n.Db = Db = 38.0                   # profundidad de la base (z del plano de particion)
    n.t = t = DIS["tapa"]
    n.D = D = Db + t
    n.y_pb_inf = y_pb_inf

    pb = n.pb = Protoboard(y_pb_sup, p, columnas)
    g = n.g = Gemelo()
    g.agregar("protoboard", pb.solido(), montado=True)

    # NodeMCU Amica: PCB a 2.5 mm sobre la protoboard; bloque total 13 mm (nominal)
    nm_l, nm_a, _ = med("nodemcu", "pcb")
    nm_alto = med("nodemcu", "alto_sobre_protoboard")
    c = layouts.NODEMCU_CUERPO
    for m in layouts.placas(lay):
        y_usb = pb.y_col(m["col0"]) - c["borde_usb"] * PASO
        y_ant = pb.y_col(m["col0"]) - (c["borde_antena"] - 1) * PASO
        g.agregar(m["nombre"].lower(), caja_c(0, (y_usb + y_ant) / 2, pb.z_sup, nm_a, y_usb - y_ant, nm_alto))
    y_usb = pb.y_col(1) - c["borde_usb"] * PASO
    n.y_antena = pb.y_col(1) - (c["borde_antena"] - 1) * PASO
    # centro del micro-USB: separacion de la PCB + espesor de la PCB + medio conector
    n.z_usb = z_usb = (pb.z_sup + med("nodemcu", "separacion_pcb_protoboard") + med("nodemcu", "pcb")[2]
                       + med("nodemcu", "conector_usb_cuerpo")[2] / 2)
    capuchon = med("nodemcu", "cable_usb_capuchon")  # ancho, largo, alto [POR CONFIRMAR]
    usb_cuerpo = (capuchon[0], capuchon[2])
    # 18-nov: las tres cajas reciben la energia por el modulo USB-C (adaptadores de 5 V / 3 A con cable USB-C);
    # el micro-USB del techo queda solo para flashear, asi que ya no se modela un cable fijo ahi.

    # componentes en la protoboard
    for comp in lay["componentes"]:
        pts = [pb.xy(h) for h in comp["pines"].values()]
        xs = [q[0] for q in pts]
        ys = [q[1] for q in pts]
        if comp["tipo"] == "C":
            g.agregar(comp["ref"], cil(sum(xs) / 2, sum(ys) / 2, pb.z_sup, *med("c1", "cuerpo")))
        elif comp["tipo"] == "Q":
            q = med("q1_to92", "cuerpo")
            if q[0] == q[1]:   # lata metalica TO-18 (redonda), centrada sobre la base
                g.agregar(comp["ref"], cil(sum(xs) / 3, sum(ys) / 3, pb.z_sup, q[0], q[2]))
            else:              # TO-92 de plastico
                g.agregar(comp["ref"], caja_c(sum(xs) / 3 + 1.2, sum(ys) / 3, pb.z_sup, *q))
        elif comp["tipo"] == "M":
            # modulo de pie sobre su tira de pines: base plastica + PCB + componentes (cara +x)
            largo, alto = med(comp["ref"].split("_")[-1].lower(), "pcb")
            xm, ym = xs[0], (min(ys) + max(ys)) / 2
            g.agregar(comp["ref"] + "_tira", caja_c(xm, ym, pb.z_sup, 2.5, len(pts) * PASO, 2.5), montado=True)
            g.agregar(comp["ref"], caja_c(xm, ym, pb.z_sup + 2.5, 1.6, largo, alto)
                      + caja_c(xm + comp.get("lado", 1) * (0.8 + 1.25), ym, pb.z_sup + 2.5, 2.5, largo - 2, alto - 3),
                      montado=True)
            n.modulos = getattr(n, "modulos", []) + [(comp["ref"], xm, ym, largo, pb.z_sup + 2.5 + alto)]
        else:
            (xa, ya), (xb, yb) = pts
            de_pie = "pie" in comp.get("nota", "")   # layouts.py lo indica en la nota ("De pie ...")
            largo = math.hypot(xb - xa, yb - ya)
            ang = math.degrees(math.atan2(yb - ya, xb - xa))
            ancho_r, alto_acostada, alto_pie = med("resistencia", "cuerpo")
            # el cuerpo real es redondo (2.9-3.0 medido): en columnas vecinas roza al Dupont de al lado y las patas
            # ceden. El gemelo se limita a menos de un paso para que el chequeo no marque ese roce como choque.
            ancho_r = min(ancho_r, 2 * (PASO - DIS["dupont"][0] / 2) - 0.1)
            g.agregar(comp["ref"], Pos((xa + xb) / 2, (ya + yb) / 2, pb.z_sup) * Rot(0, 0, ang) *
                      Box(largo, ancho_r, alto_pie if de_pie else alto_acostada, align=(C, C, MIN)))

    # conectores Dupont macho de los cables externos
    lado, alto = DIS["dupont"]
    if getattr(layouts, "SOLO_UTP", False):   # 19-nov: los cables son hilo de UTP sin carcasa Dupont
        lado = 1.2
    for e in lay["externos"]:
        x, y = pb.xy(e["orificio"])
        g.agregar(f"dupont_{e['disp']}_{e['pin']}", caja_c(x, y, pb.z_sup, lado, lado, alto))

    # LED 5 mm en la tapa: 1.5 mm fuera del frente, ceja de 5.8 mm contra el collar
    led_largo, led_fuera = 8.6, 1.5
    n.led_paso = led_paso = med("led", "paso_verde_rojo")
    n.pares_led = [(H - y_led_desde_arriba if col is None else pb.y_col(col), etiqueta) for col, etiqueta in leds]
    n.y_led = n.pares_led[0][0]
    z_led0 = D + led_fuera - led_largo

    def pos_leds(y):
        """((x, y) del verde, (x, y) del rojo) en el marco local."""
        if giro:
            return (led_x, y + led_paso / 2), (led_x, y - led_paso / 2)
        return (-led_paso / 2 + led_x, y), (led_paso / 2 + led_x, y)
    n.pos_leds = pos_leds
    for k, (y_led, _) in enumerate(n.pares_led):
        suf = "" if k == 0 else f"_{k + 1}"
        for nom, (xl, yl) in zip(("led_verde", "led_rojo"), pos_leds(y_led)):
            g.agregar(nom + suf, cil(xl, yl, z_led0, med("led", "diametro"), led_largo) + cil(xl, yl, z_led0, 5.8, 1.0),
                      montado=True)
            g.agregar(nom + suf + "_patas", caja_c(xl, yl, z_led0 - 4.0, 3.0, 3.0, 4.0), montado=True)
    n.collar = collar = Db - (z_led0 + 1.0)
    # modulo de entrada USB-C de pie contra la pared izquierda, conector hacia afuera [medidas POR CONFIRMAR].
    # Desde el 18-nov tambien en la caja dht (las tres fuentes son adaptadores con cable USB-C).
    n.y_entrada = y_ent = (H - W / 2 - 16.0) if cap else (H - 34.0)   # capsula: en la parte recta de la pared
    g.agregar("entrada_5v", caja(-W / 2 + p + 0.3, y_ent - 7, 5.0, 4.5, 14, 12), montado=True)

    # ═════ BASE ═════
    ch = DIS["chaflan"]
    R = (W / 2 - 0.05) if cap else DIS["radio"]
    if MODULAR:
        base = Pos(0, H / 2, 0) * extrude(RectangleRounded(W, H, R), amount=Db)
        base = chamfer(base.edges().group_by(Axis.Z)[0], ch)
        base -= Pos(0, H / 2, p) * extrude(RectangleRounded(W - 2 * p, H - 2 * p, R - p), amount=Db)
    else:
        base = Box(W, H, Db, align=(C, MIN, MIN))
        base = chamfer(base.edges().filter_by(Axis.Z), ch)
        base = chamfer(base.edges().group_by(Axis.Z)[0], ch)
        base -= caja_c(0, H / 2, p, W - 2 * p, H - 2 * p, Db)

    # torretas con inserto (la tapa trae su propia torreta de 3 mm)
    xt = W / 2 - DIS["torreta_margen"]
    yt = (DIS["torreta_margen"], H - DIS["torreta_margen"])
    z_torre = Db - DIS["torreta_tapa"]
    n.torretas = torretas = [] if MODULAR else [(sx * xt, y) for sx in (-1, 1) for y in yt]
    for x, y in torretas:
        base += cil(x, y, p, DIS["torreta_d"], z_torre - p)
        base -= cil(x, y, z_torre - DIS["inserto_prof"], DIS["inserto_d"], DIS["inserto_prof"] + 0.01)
        base -= cil(x, y, z_torre - DIS["inserto_prof"] - 3, DIS["piloto_d"], 3.01)

    r = DIS["ranura"]
    if camara:
        # doble pared con camara de aire y paso de cable; la camara de aire respira por los costados
        for y0 in (n.y_pared1, n.y_pared2):
            base += caja(-W / 2 + p, y0, p, W - 2 * p, 2, Db - p)
        base -= caja_c(-W / 2 + p + 5, (n.y_pared1 + n.y_pared2 + 2) / 2, p + 14, 5,
                       n.y_pared2 + 2 - n.y_pared1 + 0.2, 6)
        for sx in (-1, 1):
            base -= caja_c(sx * (W / 2 - p / 2), n.y_pared1 + 2 + n.aire / 2, 6, p + 1, 2.0, Db - 12)

    # guias de esquina de la protoboard (ajuste con holgura)
    xg = pb.ancho / 2 + hg
    for sx in (-1, 1):
        for y, sy in ((pb.y_inf - hg, -1), (pb.y_sup + hg, 1)):
            base += caja_c(sx * (xg + 0.6), y - sy * 3, p, 1.2, 6, 2.5)
            base += caja_c(sx * (xg - 3 + 0.6), y + sy * 0.6, p, 6, 1.2, 2.5)

    if MODULAR:
        # clips de la protoboard (en diagonal; lejos de la silica y del modulo USB-C) y lenguas de la tapa
        if estacion:
            n.clips = [(-1, pb.y_inf + 25), (-1, pb.y_sup - 60), (1, pb.y_inf + 58), (1, pb.y_sup - 25)]
        else:
            n.clips = [(-1, pb.y_inf + 30), (1, pb.y_sup - 22)]   # el izquierdo libra los Dupont del buzzer (dht)
        for sx, yc in n.clips:
            suma, resta = clip_piso(sx, pb.ancho / 2, yc, pb.z_sup, W / 2 - p, p)
            base = base - resta + suma
        n.broches = broches or ((W / 2 + 4.0, H / 2, H - W / 2 - 4.0) if cap else
                                (30.0, H / 2, H - 30.0) if estacion else (H * 0.40, H - 14.0))
        for sx in (-1, 1):
            for yc in n.broches:
                suma, resta = lengua_pared(sx, W, p, Db, yc)
                base = base - resta + suma

    # compartimento de silica: costilla perforada junto a la pared derecha
    y_sil = (y_pb_inf + 12, y_pb_inf + 42)
    x_cost = pb.ancho / 2 + hg + 3.0
    base += caja(x_cost, y_sil[0], p, 1.2, y_sil[1] - y_sil[0], 26)
    for y in (y_sil[0] + 7, y_sil[0] + 15, y_sil[0] + 23):
        base -= caja_c(x_cost + 0.6, y, p + 4, 2, r, 18)

    # ventilas de la bahia (lado largo en z: puentes de 1.6 mm al imprimir)
    y_vent = max(y_pb_inf + 12, W / 2 + 12.0) if cap else y_pb_inf + 12   # capsula: en la parte recta
    for y in (y_vent, y_vent + 5):                         # entrada baja por los costados
        for sx in (-1, 1):
            base -= caja_c(sx * (W / 2 - p / 2), y, 8, p + 1, r, Db - 16)
    if cap:                                                # capsula: la salida alta tambien va por los costados
        for y in (H - W / 2 - 12.0, H - W / 2 - 17.0):
            base -= caja_c(W / 2 - p / 2, y, 8, p + 1, r, Db - 16)     # solo el derecho: el izquierdo tiene el USB-C
    else:
        for x in (12, 17, 22):                             # salida alta por el techo
            for sx in (-1, 1):
                base -= caja_c(sx * x, H - p / 2, 8, r, p + 1, Db - 16)
    # paso del micro-USB por el techo (alimentacion en el dht; solo flasheo en las estaciones)
    usb_hueco = (usb_cuerpo[0] + 1.5, usb_cuerpo[1] + 2.0)
    base -= caja_c(0, H - p / 2, z_usb - usb_hueco[1] / 2, usb_hueco[0], p + 1, usb_hueco[1])
    # hueco del cable USB-C en la pared izquierda + guia que sostiene el modulo (las tres cajas)
    base -= caja_c(-W / 2 + p / 2, n.y_entrada, 11.0 - 4.5, p + 1, 13.0, 9.0)
    base += caja(-W / 2 + p + 0.3 + 4.5 + hg, n.y_entrada - 9, p, 1.2, 18, 16)

    # orejas de montaje
    ow, oh, oe = DIS["oreja"]
    n.orejas = orejas
    if orejas == "capsula":
        # sin orejas: dos ojos de cerradura en la espalda, en el hueco de cada extremo redondo. Un refuerzo interior
        # iguala el largo del cuello del perno; la ranura baja hacia -x (abajo al girar), como en "llave_x".
        cuello = DIS["perno"][1]
        y_ojos = (9.0, H - 9.0)
        for y_o in y_ojos:
            base += caja_c(-1.0, y_o, p, 18.0, 12.0, cuello - p)
            base -= ojo_cerradura(3.0, y_o, -0.1, cuello + 0.2, dir="x-")
        n.paso_pernos = y_ojos[1] - y_ojos[0]
    elif orejas == "capsula_rigida":
        # estacion del anaquel: fijacion rigida (el acelerometro no debe tener juego). En el hueco de cada extremo,
        # un agujero M3 (tornillo desde adentro) y dos ranuras para pasar un cincho que abrace el poste del anaquel.
        for y_o in (9.0, H - 9.0):
            base -= cil(0, y_o, -0.1, DIS["paso_m3"], p + 0.2)
            for sx in (-1, 1):
                base -= caja_c(sx * 9.0, y_o, -0.1, 2.0, 5.0, p + 0.2)
        n.paso_pernos = 0.0   # sin pernos: los dos agujeros M3 quedan a H - 18 mm entre si
    elif orejas == "vertical":
        sup = caja_c(0, H - p + (oh + p) / 2, 0, ow, oh + p, oe)
        sup = fillet(sup.edges().filter_by(Axis.Z).group_by(Axis.Y)[-1], 4)
        inf = caja_c(0, (p - oh) / 2, 0, ow, oh + p, oe)
        inf = fillet(inf.edges().filter_by(Axis.Z).group_by(Axis.Y)[0], 4)
        base += sup + inf
        y_ojo_sup, y_ojo_inf = H + 4.0, -10.0
        base -= ojo_cerradura(0, y_ojo_sup, -0.1, oe + 0.2)
        base -= ojo_cerradura(0, y_ojo_inf, -0.1, oe + 0.2)
        for sx in (-1, 1):  # cincho del cable USB
            base -= caja_c(sx * 10.5, H + 7.0, -0.1, 3.5, r, oe + 0.2)
        n.paso_pernos = y_ojo_sup - y_ojo_inf
    elif orejas in ("llave_x", "rigidas_x"):
        # cajas horizontales: orejas en los extremos (arriba/abajo del marco local); al girar quedan a los lados
        sup = caja_c(0, H - p + (oh + p) / 2, 0, ow, oh + p, oe)
        sup = fillet(sup.edges().filter_by(Axis.Z).group_by(Axis.Y)[-1], 4)
        inf = caja_c(0, (p - oh) / 2, 0, ow, oh + p, oe)
        inf = fillet(inf.edges().filter_by(Axis.Z).group_by(Axis.Y)[0], 4)
        base += sup + inf
        y_ojo_sup, y_ojo_inf = H + 3.0, -9.0
        if orejas == "llave_x":
            x_ojo = ow / 2 - 9.0    # entrada a la derecha; la ranura baja hacia -x (abajo al girar)
            base -= ojo_cerradura(x_ojo, y_ojo_sup, -0.1, oe + 0.2, dir="x-")
            base -= ojo_cerradura(x_ojo, y_ojo_inf, -0.1, oe + 0.2, dir="x-")
            n.paso_pernos = y_ojo_sup - y_ojo_inf
        else:
            for y_o in (y_ojo_sup, y_ojo_inf):   # ranura M3 de 10 mm (ajuste vertical al girar)
                base -= (caja_c(0, y_o, -0.1, 10.0, DIS["paso_m3"], oe + 0.2)
                         + cil(-5.0, y_o, -0.1, DIS["paso_m3"], oe + 0.2)
                         + cil(5.0, y_o, -0.1, DIS["paso_m3"], oe + 0.2))
            n.paso_pernos = 0.0
    else:
        # orejas laterales con ranura vertical para M3 o cincho: fijacion rigida (sin espuma)
        for sx in (-1, 1):
            o = caja_c(sx * (W / 2 + oh / 2 - p), H / 2, 0, oh + p, ow + 10, oe)
            o = fillet(o.edges().filter_by(Axis.Z).group_by(Axis.X)[-1 if sx > 0 else 0], 4)
            base += o
            base -= caja_c(sx * (W / 2 + oh / 2 - 1), H / 2, -0.1, 3.4, 8.0, oe + 0.2)
            base -= cil(sx * (W / 2 + oh / 2 - 1), H / 2 - 4, -0.1, 3.4, oe + 0.2)
            base -= cil(sx * (W / 2 + oh / 2 - 1), H / 2 + 4, -0.1, 3.4, oe + 0.2)
        n.paso_pernos = 0.0

    # identificacion hundida en el costado derecho
    plano_der = Plane(origin=(W / 2, y_pb_inf + 50, Db / 2), x_dir=(0, 0, -1), z_dir=(1, 0, 0))
    try:
        base -= texto(nombre.upper(), 5.0, plano_der, DIS["hundido"])
    except Exception as err:  # fuente no disponible: se omite el texto
        print("aviso: texto lateral omitido:", err)

    # ═════ TAPA ═════
    contorno = RectangleRounded(W, H, R) if MODULAR else chamfer(Rectangle(W, H).vertices(), ch)
    tapa = Pos(0, H / 2, Db) * extrude(contorno, amount=t)
    tapa = chamfer(tapa.edges().group_by(Axis.Z)[-1], 1.2)
    lw, lh = DIS["labio"]
    wi, hi = W - 2 * p - 2 * hg, H - 2 * p - 2 * hg
    if MODULAR:
        tapa = chamfer(tapa.edges().group_by(Axis.Z)[0], 0.6)   # linea de sombra entre tapa y base
        ri = R - p - hg
        labio = (Pos(0, H / 2, Db - lh) * extrude(RectangleRounded(wi, hi, ri), amount=lh)
                 - Pos(0, H / 2, Db - lh - 0.1) * extrude(RectangleRounded(wi - 2 * lw, hi - 2 * lw, ri - lw),
                                                          amount=lh + 0.2))
        for sx in (-1, 1):
            for yc in n.broches:
                tapa += pestana_tapa(sx, W, p, Db, yc)
    else:
        labio = (caja_c(0, H / 2, Db - lh, wi, hi, lh)
                 - caja_c(0, H / 2, Db - lh - 0.1, wi - 2 * lw, hi - 2 * lw, lh + 0.2))
    if camara:
        labio -= caja(-W / 2, n.y_pared1 - hg, Db - lh - 0.1, W, n.y_pared2 + 2 - n.y_pared1 + 2 * hg, lh + 0.2)
    for x, y in torretas:
        labio -= caja_c(x, y, Db - lh - 0.1, 12.0, 12.0, lh + 0.2)  # corte recto: sin puntas delgadas
    tapa += labio
    for x, y in torretas:
        tapa += cil(x, y, Db - DIS["torreta_tapa"], DIS["torreta_d"], DIS["torreta_tapa"])
        tapa -= cil(x, y, Db - DIS["torreta_tapa"] - 0.1, DIS["paso_m3"], DIS["torreta_tapa"] + t + 0.2)
        # avellanado a 90 grados para M3 cabeza plana (ISO 10642): imprime boca abajo sin soportes
        tapa -= Pos(x, y, D - (DIS["avellanado_d"] - DIS["paso_m3"]) / 2) * Cone(
            DIS["paso_m3"] / 2, DIS["avellanado_d"] / 2 + 0.05, (DIS["avellanado_d"] - DIS["paso_m3"]) / 2 + 0.05,
            align=(C, C, MIN))
    # LED: agujero y collar que detiene la ceja; en estaciones, el nombre del sensor junto a cada par
    for y_led, etiqueta in n.pares_led:
        for xl, yl in pos_leds(y_led):
            tapa += cil(xl, yl, Db - collar, 8.4, collar)
            tapa -= cil(xl, yl, Db - collar - 0.1, med("led", "agujero"), collar + t + 0.2)
        if etiqueta:
            ancho_txt = len(etiqueta) * 3.3
            if giro:     # a la derecha del par (al girar): -y local
                c_txt = (led_x, y_led - led_paso / 2 - 4.2 - 3.0 - ancho_txt / 2)
            else:        # a la derecha del par
                c_txt = (led_x + led_paso / 2 + 4.2 + 3.0 + ancho_txt / 2, y_led)
            try:
                tapa -= texto(etiqueta, 4.5, plano_frente(n, (c_txt[0], c_txt[1], D)), DIS["hundido"])
            except Exception as err:
                print("aviso: rotulo de LED omitido:", err)
    # icono del sensor junto a cada par de LED: despues del rotulo (estaciones) o a la derecha del par (dht)
    for (y_led, etiqueta), tipo in zip(n.pares_led, iconos):
        if not tipo:
            continue
        lejos = led_paso / 2 + 4.2 + 3.0 + (len(etiqueta) * 3.3 + 3.0 if etiqueta else 0.0) + 3.5
        c_ic = (led_x, y_led - lejos) if giro else (led_x + lejos, y_led)
        if giro and y_led - lejos - 4.0 < p + 4.0:   # no cabe despues del rotulo (fin de la caja): va debajo de el
            c_ic = (led_x - 10.0, y_led - led_paso / 2 - 4.2 - 3.0 - len(etiqueta) * 3.3 / 2)
        tapa -= grabar(plano_frente(n, (c_ic[0], c_ic[1], D)), icono(tipo))
    # marca hundida, con el ojo de Argos a su izquierda
    if y_marca is not None:
        try:
            tapa -= texto("Argos", 4.2, Plane(origin=(0, y_marca, D), z_dir=(0, 0, 1)), DIS["hundido"])
            tapa -= grabar(Plane(origin=(0, y_marca, D), z_dir=(0, 0, 1)), ojo_argos(), dx=-15.0)
        except Exception as err:
            print("aviso: marca omitida:", err)

    n.base, n.tapa = base, tapa
    n.extras = {}
    n.notas = {"z_usb": z_usb, "collar_led": collar}
    n.orientacion = {"base": "espalda en la cama", "tapa": "frente en la cama"}
    return n


def cerrar(n, con_soportes=True):
    piezas = {"base": n.base, "tapa": n.tapa}
    if "embolo_boton" in n.extras:
        piezas["embolo_boton"] = n.extras["embolo_boton"]
    montaje = {k: v for k, v in n.extras.items() if k != "embolo_boton"}   # piezas sueltas: no se chocan con la caja
    if con_soportes and n.orejas == "vertical":
        montaje["soporte_pared"], montaje["soporte_anaquel"] = soportes(n.paso_pernos)
        n.orientacion["soporte_pared"] = "espalda en la cama"
        n.orientacion["soporte_anaquel"] = "de canto (perfil del gancho en la cama)"
    elif con_soportes and n.orejas in ("llave_x", "capsula"):
        montaje["soporte_pared"] = soportes_llave()
        n.orientacion["soporte_pared"] = "espalda en la cama (2 tacos)"
    g, W, H = n.g, n.W, n.H
    torretas = n.torretas
    if n.giro:   # de vertical (marco local) a horizontal: x = largo, y = alto, quedando y desde 0
        def girar(s):
            return Pos(H / 2, W / 2, 0) * Rot(0, 0, 90) * s
        piezas["base"], piezas["tapa"] = girar(piezas["base"]), girar(piezas["tapa"])
        g2 = Gemelo()
        for nom, (s_, montado) in g.partes.items():
            g2.agregar(nom, girar(s_), montado)
        torretas = [(H / 2 - y, W / 2 + x) for x, y in torretas]
        g, W, H = g2, H, W
    return dict(nodo=n.nombre, H=H, W=W, D=n.D, Db=n.Db, gemelo=g, piezas=piezas, montaje=montaje,
                orientacion=n.orientacion, paso_pernos=n.paso_pernos, notas=n.notas,
                torretas=torretas,        # ejes de los 4 tornillos de la tapa (x, y), ya girados
                y_pb_inf=n.y_pb_inf)      # borde inferior de la protoboard (marco local, antes de girar)


def entrada_cable(n, lado, y, z, r=2.6):
    """Agujero en gota (techo a 45 grados, sin soportes) en una pared lateral + 2 ranuras de cincho."""
    W, p, r_s = n.W, n.p, DIS["ranura"]
    x = lado * (W / 2 - p / 2)
    n.base -= gota_x(x, y, z, 2 * r, p + 1)
    for dy in (-6, 6):
        n.base -= caja_c(x, y + dy, z - 6, p + 1, r_s, 3.5)


def huella_mc38(cuerpo, alto):
    """Contorno del porta (bolsillo + paredes + orejas con ranuras) extruido a `alto`; sirve para el porta y las calzas.
    Ejes: x = largo del MC-38, +y = cara que mira al otro cuerpo, z = 0 en la cama."""
    P = med("mc38", "porta")
    hg, pared = DIS["holgura"], DIS["pared"]
    ix, iy = cuerpo[0] + 2 * hg, cuerpo[1] + 2 * hg
    ox, oy, yc = ix + 2 * pared, iy + pared + P["pared_frente"], (P["pared_frente"] - pared) / 2
    L = P["oreja_largo"]
    pieza = fillet(caja_c(0, yc, 0, ox + 2 * L, oy, alto).edges().filter_by(Axis.Z), 3)
    for sx in (-1, 1):  # ranuras a lo largo de y: ajuste fino del gap
        xr, rl, rw = sx * (ox / 2 + L / 2), P["ranura_largo"], P["ranura_ancho"]
        pieza -= caja_c(xr, yc, -0.1, rw, rl - rw, alto + 0.2)
        for dy in (-1, 1):
            pieza -= cil(xr, yc + dy * (rl - rw) / 2, -0.1, rw, alto + 0.2)
    return pieza, ix, iy, ox, oy, yc


def porta_mc38(cuerpo, rotulo, cable):
    """Porta del cuerpo del MC-38 (sensor o iman): bolsillo abierto arriba con chaflan de entrada y 4 topes de
    retencion, pared delgada (cara lisa) hacia el otro cuerpo, muesca V de centrado en la espalda, orejas con
    ranuras (tornillo de cabeza plana 3.5 mm o cinta VHB debajo). Se imprime con el piso en la cama."""
    P = med("mc38", "porta")
    hg, pared = DIS["holgura"], DIS["pared"]
    bx, by, bz = cuerpo
    zt = P["piso"] + bz + 0.2 + 1.65                       # el cuerpo queda abajo de los topes (sin rozarlos)
    pieza, ix, iy, ox, oy, yc = huella_mc38(cuerpo, P["oreja_alto"])
    caja_p = fillet(caja_c(0, yc, 0, ox, oy, zt).edges().filter_by(Axis.Z), 2)
    pieza += caja_p
    pieza -= caja_c(0, 0, P["piso"], ix, iy, zt)
    ch = P["chaflan_entrada"]                               # chaflan de entrada (piramide truncada)
    pieza -= Pos(0, 0, zt - ch) * extrude(Rectangle(ix, iy), amount=ch + 0.01, taper=-45)
    r, ret = 0.8, P["retencion"]                            # topes: medio cilindro que sobresale `ret`
    for sy in (-1, 1):
        for sx in (-1, 1):
            pieza += Pos(sx * bx / 4, sy * (iy / 2 + r - ret), zt - 0.9) * Rot(0, 90, 0) * Cylinder(r, 4.0)
    # muesca V de centrado en la ESPALDA (la pared delgada del frente no da para una muesca); 1 mm de hondo
    pieza -= Pos(0, -(iy / 2 + pared), 0) * Rot(0, 0, 45) * Box(1.42, 1.42, 3 * zt, align=(C, C, C))
    if cable:                                               # salida del cable en el extremo +x, abierta arriba
        pieza -= caja_c(ix / 2 + pared / 2, 0, P["piso"] + 1.0, pared + 1, 4.0, zt)
    try:
        pieza -= texto(rotulo, 4.0, Plane(origin=(-9.0, -(iy / 2 + pared), zt / 2 + 0.6), x_dir=(-1, 0, 0),
                                          z_dir=(0, -1, 0)), DIS["hundido"])
    except Exception as err:
        print("aviso: rotulo omitido:", err)
    return pieza


def portas_mc38(n):
    """Porta-sensor (marco) y porta-iman (hoja) del MC-38 y calzas de 2 y 4 mm con las mismas ranuras."""
    cs = med("mc38", "cuerpo_sensor")
    ci = med("mc38", "cuerpo_iman") or cs
    n.extras["porta_sensor"] = Pos(80, 0, 0) * porta_mc38(cs, "REED", cable=True)
    n.extras["porta_iman"] = Pos(130, 0, 0) * porta_mc38(ci, "IMAN", cable=False)
    n.orientacion["porta_sensor"] = n.orientacion["porta_iman"] = "piso en la cama"
    for e in (2.0, 4.0):
        n.extras[f"calza_{int(e)}mm"] = Pos(80, -40 - 15 * e, 0) * huella_mc38(cs, e)[0]
        n.orientacion[f"calza_{int(e)}mm"] = "plana"
    n.notas["mc38_paredes_en_el_gap_mm"] = 2 * med("mc38", "porta")["pared_frente"]


def agregar_accesorio(n, acc, lugares):
    """Suma las piezas de un accesorio a las piezas sueltas del nodo, cada una en su lugar de la cama."""
    for nombre, (x, y) in lugares.items():
        n.extras[nombre] = Pos(x, y, 0) * acc["piezas"][nombre]
    n.orientacion.update(acc["orientacion"])
    n.notas.update(acc["notas"])


def capuchon_ldr(hg=None):
    """Capuchon remoto de la LDR (fase 1, 20-oct): cuerpo NEGRO opaco y disco difusor aparte (PETG blanco).

    Eje optico = +z (z = 0 espalda, por donde sale el cable). De atras hacia adelante:
      cola en U con tunel para cincho (alivio del cable) | alojamiento de la LDR | ventana (diafragma) |
      asiento del difusor | visera que limita la luz lateral.
    Oreja con agujero M3 horizontal: pivota en la horquilla de `soporte_ldr` para apuntar a la lampara.
    Se imprime con la espalda en la cama: todos los huecos abren hacia arriba (sin soportes).
    Devuelve {"piezas": capuchon_ldr, difusor_ldr y soporte_ldr en su origen, "orientacion", "notas"};
    para armarlo: sobre_horquilla(), ldr_en_capuchon() y difusor_en_asiento()."""
    c = med("ldr", "capuchon")
    hg = DIS["holgura"] if hg is None else hg
    d_ldr, d_cab = med("ldr", "cabeza_diametro"), med("ldr", "cable_diametro")
    De, cola = c["diametro_exterior"], c["cola"]
    z_ven = cola + c["alojamiento_ldr"]                    # inicio de la ventana
    z_dif = z_ven + c["espesor_ventana"]                   # asiento del difusor
    H = z_dif + c["difusor_espesor"] + 0.1 + c["visera"]
    d_aloj = max(d_ldr, d_cab) + 2 * hg
    d_asiento = c["difusor_diametro"] + hg                 # ajuste justo: una gota de pegamento lo fija
    # cola abierta hacia +y para tender el cable; la rampa a 45 grados evita el voladizo sobre la cola
    rampa = extrude(Plane.YZ * Polygon((0, -0.1), (0, cola + 3), (cola + 3.1, -0.1), (De, -0.1), align=None),
                    amount=De / 2 + 1, both=True)
    cuerpo = cil(0, 0, 0, De, H) - (rampa & caja_c(0, De / 2, -0.1, De + 1, De, cola + 3.2))
    h_cono = (d_aloj - c["ventana"]) / 2                    # asiento conico a 45 grados: tope de la LDR, sin techo plano
    cuerpo -= cil(0, 0, -0.1, d_aloj, z_ven - h_cono + 0.1)                              # cable y LDR
    cuerpo -= Pos(0, 0, z_ven - h_cono) * Cone(d_aloj / 2, c["ventana"] / 2, h_cono, align=(C, C, MIN))
    cuerpo -= cil(0, 0, z_ven - 0.1, c["ventana"], c["espesor_ventana"] + 0.2)           # ventana / diafragma
    cuerpo -= cil(0, 0, z_dif, d_asiento, H - z_dif + 0.1)                               # asiento + visera
    cuerpo -= caja_c(0, -(d_aloj / 2 + 0.8 + 0.8), 2.0, De + 1, 1.6, 3.0)               # tunel del cincho (piso de 0.8)
    # oreja de pivote hacia -y, desde la cama; agujero M3 a lo largo de x
    oreja = caja_c(0, -(De / 2 + 4.5), 0, 4.0, 13.0, 12.0)   # entra 2 mm en el cuerpo: un solo solido
    oreja = fillet(oreja.edges().filter_by(Axis.X).group_by(Axis.Z)[-1], 1.5)
    cuerpo += oreja
    cuerpo -= gota_x(0, -(De / 2 + 7.0), 7.0, DIS["paso_m3"], 10)
    try:  # chaflan del borde exterior de la visera
        cuerpo = chamfer(cuerpo.edges().group_by(Axis.Z)[-1].sort_by(SortBy.RADIUS)[-1], 0.8)
    except Exception as err:
        print("aviso: chaflan de la visera omitido:", err)
    difusor = cil(0, 0, 0, c["difusor_diametro"], c["difusor_espesor"])
    # horquilla: placa con 2 agujeros (tornillo o cincho) y dos orejas con M3; tuerca del otro lado
    e, gap, ore = 3.0, 4.0 + 2 * hg, 3.0
    sop = fillet(caja_c(0, 0, 0, 34, 18, e).edges().filter_by(Axis.Z), 4)
    for sx in (-1, 1):
        ear = caja_c(sx * (gap / 2 + ore / 2), 0, e, ore, 9.0, 13.0)
        ear = fillet(ear.edges().filter_by(Axis.X).group_by(Axis.Z)[-1], 3.0)
        sop += ear
    sop -= gota_x(0, 0, e + 9.5, DIS["paso_m3"], 20)
    for x in (-12.0, 12.0):
        sop -= cil(x, 0, -0.1, 4.0, e + 0.2)                                   # tornillo 3.5 o cincho
        sop -= Pos(x, 0, e - 2.0) * Cone(2.0, 4.0, 2.1, align=(C, C, MIN))      # avellanado
    ang = math.degrees(math.atan((d_asiento / 2) / (c["visera"] + 0.1)))   # desde el centro del difusor
    return {"piezas": {"capuchon_ldr": cuerpo, "difusor_ldr": difusor, "soporte_ldr": sop},
            "orientacion": {"capuchon_ldr": "espalda (cola) en la cama; PETG negro",
                            "difusor_ldr": "plano; PETG blanco o natural, 100 % relleno (lineas concentricas)",
                            "soporte_ldr": "placa en la cama; PETG negro"},
            "notas": {"ldr_ventana_mm": c["ventana"], "ldr_difusor_mm": c["difusor_espesor"],
                      "ldr_semiangulo_visera_grados": ang, "ldr_largo_capuchon_mm": H}}


def sobre_horquilla(ang=0.0):
    """Lleva el capuchon a su horquilla: pivote del capuchon (y = -(De/2 + 7), z = 7) sobre el de la horquilla
    (z = 12.5), eje optico hacia +y, girado `ang` grados alrededor del tornillo."""
    De = med("ldr", "capuchon")["diametro_exterior"]
    return Pos(0, 0, 12.5) * Rot(ang, 0, 0) * Rot(90, 0, 0) * Pos(0, De / 2 + 7.0, -7.0)


def ldr_en_capuchon(largo_cable):
    """Gemelo de la LDR (cabeza apoyada en el cono de 45 grados) y su cable, en el marco del capuchon."""
    c = med("ldr", "capuchon")
    alto, z_top = med("ldr", "cabeza_alto"), c["cola"] + c["alojamiento_ldr"] - 0.3
    return {"ldr": cil(0, 0, z_top - alto, med("ldr", "cabeza_diametro"), alto),
            "cable": cil(0, 0, -largo_cable, med("ldr", "cable_diametro"), z_top - alto + largo_cable)}


def difusor_en_asiento(difusor):
    c = med("ldr", "capuchon")
    return Pos(0, 0, c["cola"] + c["alojamiento_ldr"] + c["espesor_ventana"]) * difusor


def pir_en_tapa(n, y_pines):
    """HC-SR501 en la tapa (gemelo, agujero del domo y marco de la PCB); el borde con los pines en y_pines."""
    g, Db, t, hg = n.g, n.Db, n.t, n.hg
    px, py = med("hc_sr501", "pcb")
    domo_d, domo_h = med("hc_sr501", "domo_diametro"), med("hc_sr501", "domo_alto")
    cy = y_pines + py / 2 - 1.5
    g.agregar("pir_pcb", caja_c(0, cy, Db - 1.6, px, py, 1.6), montado=True)
    g.agregar("pir_domo", cil(0, cy, Db, domo_d, domo_h), montado=True)
    g.agregar("pir_componentes", caja_c(0, cy + 1.5, Db - 1.6 - 8.0, px - 4, py - 6, 8.0), montado=True)
    g.agregar("pir_dupont", caja_c(0, y_pines, Db - 1.6 - 6.0 - 14.0, 8.0, 2.6, 20.0), montado=True)
    n.tapa -= cil(0, cy, Db - 0.1, domo_d + 2 * hg + 0.4, t + 0.2)
    marco = caja_c(0, cy, Db - 3.0, px + 2 * hg + 2.4, py + 2 * hg + 2.4, 3.0) - \
        caja_c(0, cy, Db - 3.1, px + 2 * hg, py + 2 * hg, 3.2)
    marco -= caja_c(0, cy - py / 2, Db - 3.1, 12, 4, 3.2)   # salida de los pines
    n.tapa += marco
    n.notas["y_domo"] = cy


def costillas_modulos(n):
    """Costilla con ranura en la tapa que atrapa el borde superior de cada PCB de pie (no vibran por separado)."""
    for ref, xm, ym, largo, z_top in n.modulos:
        clave = ref.split("_")[-1].lower()
        if MED[clave]["pcb"].get("fuente") != "medido":
            # la costilla muerde 2 mm exactos del borde de la placa: sin la medida real no se modela (el modulo
            # queda libre dentro de la caja, que tiene altura de sobra) y se avisa
            print(f"aviso: {clave} sin medir -> tapa sin costilla para ese modulo")
            continue
        z_rib = z_top - 2.0                                # la ranura muerde 2 mm de PCB
        costilla = caja_c(xm, ym, z_rib, 1.6 + 2 * n.hg + 2.4, largo - 4, n.Db - z_rib)
        costilla -= caja_c(xm, ym, z_rib - 0.1, 1.6 + 2 * n.hg, largo + 1, 2.1)
        n.tapa += costilla


# ═════════════════════════════════════════════════════════════════════════════
#  Nodo dht: camara aislada para el DHT22, OLED, boton y buzzer
# ═════════════════════════════════════════════════════════════════════════════
def nodo_dht(lay_nombre="nodo_dht"):
    n = comun("dht", lay_nombre, camara=40.0, y_marca=71.0, iconos=("dht",))
    p, hg, g, Db, D, t, r = n.p, n.hg, n.g, n.Db, n.D, n.t, DIS["ranura"]

    # DHT22 real (18-nov): modulo AM2302 con placa de 36.3 mm y 3 pines rectos por el borde. Con sus Dupont
    # hembra mide ~50 mm y no cabe de pie en la camara (40 mm), asi que va ACOSTADO a lo ancho, rejilla al frente.
    # De derecha a izquierda: cuerpo blanco | resto de la placa | pines + Dupont, que salen hacia el paso de cable.
    dx, dy, dz = med("dht22", "cuerpo")                 # ancho, largo y grueso del cuerpo blanco
    _, m_largo, m_grueso = med("dht22", "modulo_pcb")   # largo total con placa y grueso total
    dup, pcb_e = 14.0, m_grueso - dz
    pw = med("dht22", "placa")[0]                       # ancho real de la placa morada (19-nov)
    x_der, yc, z_dht = 22.0, p + n.camara / 2, p + 8.0
    x_izq = x_der - m_largo
    g.agregar("dht22_pcb", caja(x_izq, yc - dx / 2, z_dht, m_largo, dx, pcb_e), montado=True)
    g.agregar("dht22", caja(x_der - dy, yc - dx / 2, z_dht + pcb_e, dy, dx, dz), montado=True)
    g.agregar("dht22_dupont", caja(x_izq - dup, yc - 4.0, z_dht - 0.5, dup, 8.0, 2.6), montado=True)
    # cuna: dos rieles bajo los bordes de la placa (libran las soldaduras), dos guias laterales y un tope
    for sy in (-1, 1):
        n.base += caja(x_izq + 1, yc + sy * (pw / 2 - 1.0) - 0.8, p, m_largo - 2, 1.6, z_dht - p)
        n.base += caja(x_izq + 1, yc + sy * (dx / 2 + hg + 0.6) - 0.6, p, m_largo - 2, 1.2,
                       z_dht - p + m_grueso * 0.6)
    n.base += caja(x_der + hg, yc - dx / 2, p, 1.2, dx, z_dht - p + m_grueso * 0.6)
    # poste de la tapa: al cerrar, detiene el modulo por la parte lisa del cuerpo (junto a la placa)
    z_poste = z_dht + m_grueso + 0.3
    n.tapa += cil(0.0, yc, z_poste, 3.6, Db - z_poste)      # x = 0: detras del parteluz de las persianas
    # ventilas de la camara: costados y piso (entrada y salida del aire)
    for y in (14, 19, 24, 29, 34):
        for sx in (-1, 1):
            n.base -= caja_c(sx * (n.W / 2 - p / 2), y, 8, p + 1, r, Db - 16)
    for x in (-16, -8, 0, 8, 16):
        n.base -= caja_c(x, p / 2, 8, r, p + 1, Db - 16)
    # frente: persianas a 45 grados (caseta meteorologica) en dos campos con un parteluz al centro.
    # Dejan pasar el aire y tapan la luz y el calor radiante directo de las lamparas.
    for y in (11.0, 16.0, 21.0, 26.0, 31.0):
        for sx in (-1, 1):
            n.tapa -= persiana(sx * 14.0, y, 24.0, r, Db, D)

    # OLED 2.42" real (modulo ZJY_M242, medido el 19-nov): placa de 72.2 x 42.7 mm, la tira de 7 pines en un lado
    # CORTO y la cinta de la pantalla hacia abajo. Casi llena el ancho interior (76 mm): el marco lleva las
    # paredes laterales delgadas y las grapas cruzan a lo ALTO (a lo ancho ya no caben).
    ox, oy, oz = med("oled", "modulo_2p42")
    vent = med("oled", "ventana_2p42")                  # [estimada de foto] deja ver todo el vidrio util
    y_oled = 74.0                                       # entre los dos pares de broches de la tapa
    yc_o = y_oled + oy / 2
    g.agregar("oled", caja_c(0, yc_o, Db - oz, ox, oy, oz), montado=True)
    g.agregar("oled_pines", caja_c(-ox / 2 + 3.0, yc_o, Db - oz - 9.0, 2.6, 18.0, 9.0), montado=True)
    y_ventana = y_oled + med("oled", "ventana_centro_desde_borde_cinta")
    n.tapa -= caja_c(0, y_ventana, Db - 0.1, vent[0], vent[1], t + 0.2)
    try:  # chaflan del borde de la ventana (angulo de vision)
        n.tapa = chamfer(n.tapa.edges().filter_by_position(Axis.Z, D - 0.01, D + 0.01)
                         .filter_by_position(Axis.Y, y_ventana - vent[1] / 2 - 0.1, y_ventana + vent[1] / 2 + 0.1)
                         .filter_by_position(Axis.X, -vent[0] / 2 - 0.1, vent[0] / 2 + 0.1), 1.0)
    except Exception as err:
        print("aviso: chaflan de ventana omitido:", err)
    mi = (ox + 2 * hg, oy + 2 * hg)
    px_m, py_m = 0.9, 1.2                               # pared del marco: a los lados queda a 0.4 mm de la caja
    marco = caja_c(0, yc_o, Db - oz, mi[0] + 2 * px_m, mi[1] + 2 * py_m, oz) -         caja_c(0, yc_o, Db - oz - 0.1, mi[0], mi[1], oz + 0.2)
    marco -= caja_c(0, y_oled - hg - py_m / 2, Db - oz - 0.1, 26, py_m + 0.4, oz + 0.2)   # paso de la cinta
    if MODULAR:
        # dos grapas sueltas (se imprimen de canto) que cruzan la espalda de la OLED de arriba abajo y muerden
        # muescas de las paredes superior e inferior del marco. Se modelan a lo largo de x y se giran 90 grados.
        gr = DIS["grapa"]
        my, zg = mi[1] / 2 + py_m, Db - 2.0
        z_b = Db - oz - 0.2 - gr["esp"]
        d = 0.15 + gr["aprieto"]
        grapa_l = caja_c(0, 0, z_b, 2 * (my + 0.15 + 1.4), gr["ancho"], gr["esp"])
        muesca_l = None
        for s in (-1, 1):
            grapa_l += caja_c(s * (my + 0.15 + 0.7), 0, z_b, 1.4, gr["ancho"], Db - 1.0 - z_b)
            grapa_l += prisma_xz([(s * (my + 0.15), zg - d - 0.1), (s * (my + 0.15), zg + d + 0.1),
                                  (s * (my + 0.15 - d), zg)], -gr["ancho"] / 2, gr["ancho"])
            m = prisma_xz([(s * my, zg - 0.7), (s * my, zg + 0.7), (s * (my - 0.6), zg)],
                          -gr["ancho"] / 2 - 1, gr["ancho"] + 2)
            muesca_l = m if muesca_l is None else muesca_l + m
        for xg_o in (-22.0, 22.0):
            T = Pos(xg_o, yc_o, 0) * Rot(0, 0, 90)
            marco -= T * muesca_l
            n.extras["grapa_oled"] = T * grapa_l          # el archivo trae UNA: se imprimen 2 iguales
        n.orientacion["grapa_oled"] = "de canto (perfil en U sobre la cama); IMPRIMIR 2"
    n.tapa += marco

    # boton tactil 6x6 de 2 patas (medido el 19-nov: 6.05 de lado, 4.77 de alto con vastago) con embolo impreso
    # (ceja de 1 mm entre el vastago y la tapa). El cuerpo queda al ras de la cuna: se fija con un punto de pegamento.
    bx, by = 0.0, 62.0
    b_lado = med("boton_kit", "cuerpo")[0]
    b_alto = med("boton_kit", "alto_total")
    cuna, prof = b_lado + 2 * hg, 1.0 + b_alto
    g.agregar("boton", caja_c(bx, by, Db - prof, b_lado, b_lado, b_alto), montado=True)
    g.agregar("boton_dupont", caja_c(bx, by, Db - prof - 10.0, 6.5, 6.5, 10.0), montado=True)
    n.tapa -= cil(bx, by, Db - 0.1, 4.4, t + 0.2)
    n.tapa += caja_c(bx, by, Db - prof, cuna + 2.4, cuna + 2.4, prof) -         caja_c(bx, by, Db - prof - 0.1, cuna, cuna, prof + 0.2)
    embolo = cil(bx, by, Db - 1.0, 6.2, 1.0) + cil(bx, by, Db, 4.0, t + 1.0)
    n.extras["embolo_boton"] = chamfer(embolo.edges().group_by(Axis.Z)[-1], 0.5)
    n.orientacion["embolo_boton"] = "ceja en la cama"

    # buzzer SUELTO (sin placa KY-012, medido el 18-nov): cilindro contra la tapa dentro de un collar partido en
    # 3 dedos con un diente cada uno; entra a presion y los dientes lo detienen por atras. Sus 2 patas llevan
    # Dupont hembra hacia la espalda.
    zx, zy = -20.0, 60.0
    d_buz = med("buzzer_ky012", "diametro_buzzer")
    h_buz = med("buzzer_ky012", "alto")
    paso_buz = med("buzzer_ky012", "paso_pines")
    g.agregar("buzzer", cil(zx, zy, Db - h_buz, d_buz, h_buz), montado=True)
    for sx in (-1, 1):
        g.agregar(f"buzzer_dupont_{'+' if sx > 0 else '-'}",
                  caja_c(zx + sx * paso_buz / 2, zy, Db - h_buz - 14.0, 2.6, 2.6, 14.0), montado=True)
    h_col, d_in = h_buz + 1.4, d_buz + 2 * hg
    collar_b = cil(zx, zy, Db - h_col, d_in + 2.4, h_col) - cil(zx, zy, Db - h_col - 0.1, d_in, h_col + 0.2)
    for ang in (30, 150, 270):            # 3 ranuras: dejan 3 dedos elasticos en los ultimos 7 mm
        collar_b -= Pos(zx, zy, Db - h_col - 0.1) * Rot(0, 0, ang) * Box(d_in, 1.4, 6.4, align=(MIN, C, MIN))
        # fondo redondo (r = 0.7): la raiz de cada dedo ya no termina en esquina viva
        collar_b -= Pos(zx, zy, Db - h_col + 6.3) * Rot(0, 0, ang) * Pos(d_in / 2, 0, 0) * \
            Cylinder(0.7, d_in, rotation=(0, 90, 0))
    for ang in (90, 210, 330):            # diente al centro de cada dedo, justo detras del buzzer (0.35 de mordida)
        collar_b += Pos(zx, zy, Db - h_buz - 0.75) * Rot(0, 0, ang) * Pos(d_in / 2 + 0.45, 0, 0) * \
            Cylinder(0.8, 3.0, rotation=(90, 0, 0))
    n.tapa += collar_b
    for ang in range(0, 360, 60):
        n.tapa -= cil(zx + 3.5 * math.cos(math.radians(ang)), zy + 3.5 * math.sin(math.radians(ang)),
                      Db - 0.1, 1.8, t + 0.2)
    n.tapa -= cil(zx, zy, Db - 0.1, 1.8, t + 0.2)
    n.notas["y_ventana_oled"] = y_ventana
    return cerrar(n)


# ═════════════════════════════════════════════════════════════════════════════
#  Nodo luz: fotorresistencia tras un difusor impreso de 0.6 mm (PETG blanco)
# ═════════════════════════════════════════════════════════════════════════════
def nodo_luz():
    n = comun("luz", "nodo_luz", y_marca=None)
    g, Db, D, t = n.g, n.Db, n.D, n.t
    d_ldr = med("ldr", "cabeza_diametro")
    piel = 0.6                                  # difusor: la propia tapa adelgazada
    lx, ly = 0.0, 30.0
    g.agregar("ldr", cil(lx, ly, Db - 2.0, d_ldr, 2.0), montado=True)
    # tubo que aloja la LDR y la aisla de la luz de los LED propios; los Dupont quedan detras del tubo
    tubo_l = 6.0
    g.agregar("ldr_dupont", caja_c(lx, ly, Db - tubo_l - 14.0, 5.2, 2.6, 14.0), montado=True)
    n.tapa += cil(lx, ly, Db - tubo_l, d_ldr + 0.6 + 2.4, tubo_l) - cil(lx, ly, Db - tubo_l - 0.1, d_ldr + 0.6, tubo_l + 0.1)
    n.tapa -= cil(lx, ly, Db - 0.1, d_ldr + 0.6, t - piel + 0.1)  # bolsillo hasta dejar la piel (sin escalon)
    try:
        n.tapa -= texto("Argos", 4.2, Plane(origin=(0, ly + 14, D), z_dir=(0, 0, 1)), DIS["hundido"])
    except Exception as err:
        print("aviso: marca omitida:", err)
    n.notas["difusor_mm"] = piel
    return cerrar(n)


# ═════════════════════════════════════════════════════════════════════════════
#  Nodo pir: HC-SR501 con el domo saliendo por el frente
# ═════════════════════════════════════════════════════════════════════════════
def nodo_pir():
    n = comun("pir", "nodo_pir", y_marca=12.0)
    pir_en_tapa(n, n.pb.y_col(21))   # el borde con los pines a la altura de la columna 21 (sin NodeMCU debajo)
    n.notas["postes_m2_entre_centros"] = med("hc_sr501", "agujeros_entre_centros")
    return cerrar(n)


# ═════════════════════════════════════════════════════════════════════════════
#  Nodo puerta: caja en la pared junto al marco; el MC-38 va fuera con guias impresas
# ═════════════════════════════════════════════════════════════════════════════
def nodo_puerta():
    n = comun("puerta", "nodo_puerta", y_marca=40.0)
    entrada_cable(n, -1, n.y_pb_inf + 40, n.Db / 2)   # cable del MC-38 por el costado izquierdo, abajo
    portas_mc38(n)
    n.notas["mc38_supuesto"] = 1.0
    return cerrar(n)


# ═════════════════════════════════════════════════════════════════════════════
#  Nodo acel: modulos de pie en la protoboard, sujetos por costillas de la tapa
# ═════════════════════════════════════════════════════════════════════════════
def nodo_acel():
    n = comun("acel", "nodo_acel", orejas="laterales", y_marca=12.0)
    D = n.D
    costillas_modulos(n)
    # ejes del GY-61 marcados en el frente (flechas hundidas) [orientacion POR CONFIRMAR al armar]
    try:
        n.tapa -= texto("X", 5.0, Plane(origin=(14, 30, D), z_dir=(0, 0, 1)), DIS["hundido"])
        n.tapa -= texto("Y", 5.0, Plane(origin=(0, 44, D), z_dir=(0, 0, 1)), DIS["hundido"])
    except Exception as err:
        print("aviso: ejes omitidos:", err)
    n.tapa -= caja_c(5, 30, D - DIS["hundido"], 8, 1.0, 1)       # flecha X
    n.tapa -= caja_c(0, 36, D - DIS["hundido"], 1.0, 8, 1)       # flecha Y
    return cerrar(n, con_soportes=False)


# ═════════════════════════════════════════════════════════════════════════════
#  Estacion de entrada: pir (arriba) + puerta (abajo) en una MB-102, una caja y una fuente
# ═════════════════════════════════════════════════════════════════════════════
def estacion_entrada():
    n = comun("entrada", "estacion_entrada", y_marca=None, orejas="llave_x", giro=True, led_x=20.0,
              leds=((None, "PIR"), (50, "PUERTA")), iconos=("pir", "puerta"))
    Db, pb = n.Db, n.pb
    pir_en_tapa(n, pb.y_col(21))   # HC-SR501 en la tapa, frente al nodo pir (mitad superior)
    try:
        n.tapa -= texto("Argos", 4.2, plano_frente(n, (-20.0, n.H / 2, n.D)), DIS["hundido"])
        n.tapa -= grabar(plano_frente(n, (-20.0, n.H / 2, n.D)), ojo_argos(), dx=-15.0)
    except Exception as err:
        print("aviso: marca omitida:", err)
    # cable del MC-38 por la pared izquierda del marco local (abajo al girar), a la altura del nodo puerta
    entrada_cable(n, -1, pb.y_col(52), Db / 2)   # lejos de las ventilas bajas
    portas_mc38(n)
    return cerrar(n)


# ═════════════════════════════════════════════════════════════════════════════
#  Estacion del anaquel: acel (arriba) + luz (abajo), rigida al anaquel; LDR remota con capuchon
# ═════════════════════════════════════════════════════════════════════════════
def estacion_anaquel(reles=False):
    """reles=True: submodulo opcional del fotoperiodo (estacion_anaquel_rele), con salida del cable de senal."""
    n = comun("anaquel_rele" if reles else "anaquel", "estacion_anaquel_rele" if reles else "estacion_anaquel",
              orejas="rigidas_x", giro=True, led_x=20.0, y_marca=None, leds=((None, "ACEL"), (50, "LUZ")),
              iconos=("acel", "luz"))
    Db, D, pb = n.Db, n.D, n.pb
    costillas_modulos(n)
    # ejes del GY-61 hundidos en el frente [orientacion POR CONFIRMAR al armar]: flecha X (a lo largo de x local,
    # vertical al girar) y flecha Y (a lo largo de y local, horizontal), con sus letras
    y0 = n.modulos[0][2] + 20.0
    try:
        n.tapa -= texto("X", 5.0, plano_frente(n, (14.0, y0, D)), DIS["hundido"])
        n.tapa -= texto("Y", 5.0, plano_frente(n, (0.0, y0 + 14.0, D)), DIS["hundido"])
        n.tapa -= texto("Argos", 4.2, plano_frente(n, (-20.0, n.H / 2, D)), DIS["hundido"])
        n.tapa -= grabar(plano_frente(n, (-20.0, n.H / 2, D)), ojo_argos(), dx=-15.0)
    except Exception as err:
        print("aviso: texto omitido:", err)
    n.tapa -= caja_c(5.0, y0, D - DIS["hundido"], 10.0, 1.0, 1)         # flecha X
    n.tapa -= caja_c(0.0, y0 + 5.0, D - DIS["hundido"], 1.0, 10.0, 1)   # flecha Y
    # cable de la LDR por la pared izquierda, a la altura del nodo luz
    entrada_cable(n, -1, pb.y_col(52), Db / 2)   # lejos de las ventilas bajas
    if reles:   # cable de senal de 6 hilos hacia la caja de potencia, por la misma pared, arriba del de la LDR
        entrada_cable(n, -1, pb.y_col(47), Db / 2, r=3.2)
    agregar_accesorio(n, capuchon_ldr(n.hg), {"capuchon_ldr": (-120, 0), "difusor_ldr": (-120, 40),
                                               "soporte_ldr": (-120, -40)})
    return cerrar(n, con_soportes=False)


def perno(x, y, z0):
    """Perno impreso: cuello + cabeza conica a 45 grados (sin soportes) + disco."""
    cd, cl, hd = DIS["perno"]
    cono_h = (hd - cd) / 2
    return (cil(x, y, z0, cd, cl)
            + Pos(x, y, z0 + cl) * Cone(cd / 2, hd / 2, cono_h, align=(C, C, MIN))
            + cil(x, y, z0 + cl + cono_h, hd, 1.0))


def soportes(paso):
    """Placa de pared y gancho de anaquel con los mismos dos pernos (separacion = paso)."""
    e = 4.0
    largo = paso + 22
    placa = caja_c(0, 0, 0, 30, largo, e)
    placa = fillet(placa.edges().filter_by(Axis.Z), 5)
    pared = placa + perno(0, paso / 2, e) + perno(0, -paso / 2, e)
    # dos tornillos 3.5 mm avellanados (o tiras adhesivas removibles en la espalda)
    for y in (paso / 2 - 22, -paso / 2 + 22):
        pared -= cil(0, y, -0.1, 4.0, e + 0.2)
        pared -= Pos(0, y, e - 2.5) * Cone(2.0, 4.6, 2.6, align=(C, C, MIN))
    # pinza de anaquel en C: brazos por arriba y por abajo de la repisa (espesor anaquel_espesor)
    t_an = DIS["anaquel_espesor"] + 2 * DIS["holgura"]
    brazo = 25.0
    anaquel = caja_c(0, 0, 0, 30, largo, e)
    arriba = caja(-15, largo / 2 - e, -brazo, 30, e, brazo + e)
    abajo = caja(-15, largo / 2 - 2 * e - t_an, -brazo, 30, e, brazo + e)
    anaquel = anaquel + arriba + abajo + perno(0, paso / 2, e) + perno(0, -paso / 2, e)
    return pared, anaquel


def soportes_llave():
    """Dos tacos de pared (para cajas horizontales) con un perno cada uno. No hace falta medir la distancia:
    se cuelga la caja de los dos tacos, se marcan los agujeros con ella y se atornillan."""
    e = 4.0
    taco = caja_c(0, 0, 0, 30, 46, e)
    taco = fillet(taco.edges().filter_by(Axis.Z), 5)
    taco += perno(0, 0, e)
    for y in (-17.0, 17.0):
        taco -= cil(0, y, -0.1, 4.0, e + 0.2)
        taco -= Pos(0, y, e - 2.5) * Cone(2.0, 4.6, 2.6, align=(C, C, MIN))
    return Compound(children=[Pos(-20, 0, 0) * taco, Pos(20, 0, 0) * taco])


# ── verificacion ─────────────────────────────────────────────────────────────
def verificar(n):
    g = n["gemelo"]
    piezas = {**n["piezas"]}
    res = {"interferencias": [], "holguras": [], "volumenes": {}}
    nombres = list(g.partes)
    # gemelo contra carcasa
    for nom in nombres:
        s, montado = g.partes[nom]
        dmin = 1e9
        for pn, ps in piezas.items():
            v = (s & ps).volume
            if v > 1e-3:
                res["interferencias"].append({"a": nom, "b": pn, "volumen_mm3": round(v, 3)})
            dmin = min(dmin, s.distance_to(ps))
        res["holguras"].append({"parte": nom, "montado": montado, "min_mm": round(dmin, 2),
                                "ok": montado or dmin >= DIS["holgura_min"] - 1e-6})
    # gemelo contra gemelo
    for i, a in enumerate(nombres):
        for b in nombres[i + 1:]:
            v = (g.partes[a][0] & g.partes[b][0]).volume
            if v > 1e-3:
                res["interferencias"].append({"a": a, "b": b, "volumen_mm3": round(v, 3)})
    # piezas de carcasa entre si (base, tapa, embolo)
    pn = list(piezas)
    for i, a in enumerate(pn):
        for b in pn[i + 1:]:
            v = (piezas[a] & piezas[b]).volume
            if v > 1e-3:
                res["interferencias"].append({"a": a, "b": b, "volumen_mm3": round(v, 3)})
    for nom, s in {**piezas, **n["montaje"]}.items():
        vol = s.volume
        res["volumenes"][nom] = {"volumen_cm3": round(vol / 1000, 2),
                                 "masa_g_petg": round(vol / 1000 * DIS["densidad_petg"], 1),
                                 "caja_mm": [round(d, 1) for d in s.bounding_box().size]}
    return res


def a_cama(nombre, s):
    """Orienta una pieza para imprimir: z = 0 sobre la cama."""
    if nombre == "tapa":
        s = Rot(180, 0, 0) * s
    elif nombre == "soporte_anaquel":
        s = Rot(0, 90, 0) * s
    elif nombre.startswith("grapa"):   # de canto: el perfil en U queda sobre la cama
        bb = s.bounding_box()
        s = (Rot(0, 90, 0) if bb.size.Y > bb.size.X else Rot(90, 0, 0)) * s
    bb = s.bounding_box()
    return Pos(-bb.center().X, -bb.center().Y, -bb.min.Z) * s


def exportar(n, res):
    SALIDA.mkdir(parents=True, exist_ok=True)
    nodo = n["nodo"]
    todas = {**n["piezas"], **n["montaje"]}
    (SALIDA / "impresion").mkdir(exist_ok=True)
    for nombre, s in todas.items():
        export_step(s, str(SALIDA / f"nodo_{nodo}_{nombre}.step"))
        export_step(a_cama(nombre, s), str(SALIDA / "impresion" / f"nodo_{nodo}_{nombre}.step"))
        export_stl(a_cama(nombre, s), str(SALIDA / f"nodo_{nodo}_{nombre}.stl"), tolerance=0.02,
                   angular_tolerance=0.2)
    gem = Compound(children=[s for s, _ in n["gemelo"].partes.values()])
    export_step(gem, str(SALIDA / f"nodo_{nodo}_gemelo.step"))
    # copias giradas (y del nodo -> z) para visores que usan z hacia arriba
    (SALIDA / "vista").mkdir(exist_ok=True)
    for nombre, s in {**n["piezas"], "gemelo": gem, **n["montaje"]}.items():
        export_step(Rot(90, 0, 0) * s, str(SALIDA / "vista" / f"nodo_{nodo}_{nombre}.step"))
    ens = Compound(children=[n["piezas"][k] for k in ("base", "tapa", "embolo_boton") if k in n["piezas"]] + [gem])
    export_step(ens, str(SALIDA / f"nodo_{nodo}_ensamble.step"))
    resumen = {"nodo": nodo, "envolvente_mm": [round(n["W"], 1), round(n["H"], 1), round(n["D"], 1)],
               "envolvente_con_orejas_mm": [round(v, 1) for v in
                                            Compound(children=[n["piezas"]["base"], n["piezas"]["tapa"]]).bounding_box().size],
               "paso_pernos_mm": round(n["paso_pernos"], 1), "orientacion": n["orientacion"],
               "notas": {k: round(v, 2) for k, v in n["notas"].items()}, **res}
    (SALIDA / f"verificacion_{nodo}.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False),
                                                       encoding="utf-8")
    return resumen


NODOS = {"dht": nodo_dht, "entrada": estacion_entrada, "anaquel": estacion_anaquel}
assert set(NODOS) == set(layouts.CAJAS), "las cajas de CAD no coinciden con layouts.CAJAS"
# Nodos sueltos (reemplazados por las estaciones el 19-oct): se pueden regenerar con su nombre.
SUELTOS = {"luz": nodo_luz, "pir": nodo_pir, "puerta": nodo_puerta, "acel": nodo_acel,
           "anaquel_rele": lambda: estacion_anaquel(reles=True)}   # submodulo opcional del fotoperiodo


def main(lista):
    falla = False
    lista = [a for a in lista if not a.startswith("--")]
    if MODULAR:
        import vistas
        vistas.RENDERS = RAIZ / "renders" / ("capsula" if CAPSULA else "modular")
        vistas.RENDERS.mkdir(parents=True, exist_ok=True)
    for nodo in lista or NODOS:
        n = {**NODOS, **SUELTOS}[nodo]()
        res = verificar(n)
        r = exportar(n, res)
        import vistas
        vistas.dibujar(n)
        malas = [h for h in res["holguras"] if not h["ok"]]
        print(f"{nodo}: envolvente {r['envolvente_mm']} mm; interferencias {len(res['interferencias'])}; "
              f"holguras < {DIS['holgura_min']} mm {len(malas)}")
        for i in res["interferencias"]:
            print("   interferencia", i)
        for h in malas:
            print("   holgura", h)
        falla |= bool(res["interferencias"] or malas)
    sys.exit(1 if falla else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
