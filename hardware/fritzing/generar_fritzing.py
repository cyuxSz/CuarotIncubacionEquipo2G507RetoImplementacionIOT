"""Versión en Fritzing de los nodos (vista de protoboard y esquemático) generada desde layouts.py.

Es una versión para comparar con las figuras de protoboard.py y esquematicos.py; no las reemplaza.
Fritzing coloca el NodeMCU Amica en vista superior: con el USB hacia la columna 1 sus pines D0-D8
quedan del lado de las filas a-e de la protoboard de Fritzing, al revés que en layouts.py. Para que el
armado sea físicamente posible, las filas se reflejan (a↔j, b↔i, ...) y los rieles A_* pasan arriba.

Uso (desde la raíz):
    uv run --no-project --python 3.12 --with svgelements python hardware/fritzing/generar_fritzing.py [nodo_pir ...]
Requiere Fritzing (CD-548 o 1.0) en FRITZING_DIR; instala las partes de partes/ en la carpeta de usuario.
"""
import glob
import html
import re
import math
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "hardware" / "breadboard"))
sys.path.insert(0, str(AQUI))
import layouts  # noqa: E402
import geometria as geo  # noqa: E402

FZ = Path(os.environ.get("FRITZING_DIR") or (glob.glob("C:/Users/luedm/fz/app/forzip/fritzing-*") or ["."])[0])
CORE = FZ / "fritzing-parts"
PROPIAS = AQUI / "partes"
SALIDA = AQUI / "salida"
NODOS = ["nodo_dht", "nodo_luz", "nodo_pir", "nodo_puerta", "nodo_acel",
         "estacion_entrada", "estacion_anaquel"]
CAJAS = ["nodo_dht", "estacion_entrada", "estacion_anaquel"]


def carpeta_usuario():
    for base in [Path.home() / "OneDrive" / "Documents", Path.home() / "Documents"]:
        if (base / "Fritzing" / "parts").exists():
            return base / "Fritzing" / "parts"
    return Path.home() / "Documents" / "Fritzing" / "parts"


# clave: (fzp, carpeta svg, {pin de layouts: connector}, propiedades)
def _core(n):
    return CORE / "core" / n, CORE / "svg" / "core"


def _propia(n):
    return PROPIAS / n, PROPIAS / "svg"


AMICA_J = ["3V3", "GND", "TX", "RX", "D8", "D7", "D6", "D5", "GND", "3V3", "D4", "D3", "D2", "D1", "D0"]
AMICA_A = ["VIN", "GND", "RST", "EN", "3V3", "GND", "CLK", "SD0", "CMD", "SD1", "SD2", "SD3", "RSV", "RSV", "A0"]
PARTES = {
    "bb400": (*_core("Half_breadboard.fzp"), {}),
    "bb830": (*_core("breadboard2.fzp"), {}),
    "Entrada5V": (*_core("Camdenboss_CTB0158-2_5_08mm_pitch_90deg_terminals.fzp"), {"+": "connector0", "-": "connector1"}),
    "nodemcu": (*_propia("Amica_NodeMCU_DEVKIT_1.0.fzp"),
                {"3V3": "connector0", "GND": "connector1", "VIN": "connector29", "A0": "connector15",
                 **{p: f"connector{i}" for i, p in enumerate(AMICA_J) if p.startswith("D")}}),
    "R": (*_core("resistor.fzp"), {"1": "connector0", "2": "connector1"}),
    "C": (*_core("capacitor_electrolytic_medium.fzp"), {"+": "connector1", "-": "connector0"}),
    "Q": (*_core("sparkfun-discretesemi-transistor_npn-to92.fzp"), {"E": "connector0", "B": "connector1", "C": "connector2"}),
    "LED": (*_core("LED-generic-5mm.fzp"), {"A": "connector1", "K": "connector0"}),
    "Boton": (*_core("pushbutton_2_horizontal.fzp"), {"1": "connector0", "2": "connector1"}),
    "Buzzer": (*_core("sparkfun-electromechanical-buzzer-pth.fzp"), {"+": "connector0", "-": "connector1"}),
    "Reed": (*_core("reedSwitch_500mil.fzp"), {"1": "connector0", "2": "connector1"}),
    "LDR": (*_core("LDR_photocell_300mil.fzp"), {"1": "connector0", "2": "connector1"}),
    "DHT22": (*_propia("DHT22_Humidity_and_Temperature_Sensor__5a66c01a9adead9b6c488a2653070fb3_C9.fzp"),
              {"VCC": "connector1", "DATA": "connector2", "GND": "connector4"}),
    "PIR": (*_propia("PIR_sensor__723e9e78d3d1bdc76f4badecd521c4cb_6B.fzp"), {"VCC": "connector1", "OUT": "connector2", "GND": "connector3"}),
    "ADS1115": (*_propia("adafruit_b5f9951570be0e9678775cd7193acf99_1.fzp"),
                {"VDD": "connector19", "GND": "connector18", "SCL": "connector17", "SDA": "connector16", "ADDR": "connector15",
                 "ALRT": "connector14", "A0": "connector13", "A1": "connector12", "A2": "connector11", "A3": "connector10"}),
    "GY61": (*_propia("argos_gy61.fzp"), {"VCC": "connector0", "X": "connector1", "Y": "connector2", "Z": "connector3", "GND": "connector4"}),
    "OLED": (*_propia("argos_oled_242.fzp"), {"CS": "connector0", "DC": "connector1", "RES": "connector2", "SDA": "connector3", "SCL": "connector4",
                                                "VCC": "connector5", "GND": "connector6"}),
}
COLORES = {"rojo": "#cc1414", "negro": "#404040", "naranja": "#ef6100", "verde": "#2f9e44",
           "azul": "#1f5fbf", "cafe": "#8c3b00",
           "blanco-naranja": "#ffc99a", "blanco-verde": "#b9e8c4", "blanco-azul": "#a9c8f0", "blanco-cafe": "#d9b99b"}
# color del diseno (layouts.py) -> hilo real de UTP / cable solido que se va a tener
UTP = {"morado": "blanco-naranja", "amarillo": "blanco-verde", "gris": "blanco-azul", "blanco": "blanco-cafe"}
ESPEJO = dict(zip("abcdefghij", "JIHGFEDCBA"))
RIELES = {"A_5V": "Y", "A_GND": "Z", "J_3V3": "W", "J_GND": "X"}  # siguen las lineas impresas: roja = +, azul = GND

_cache = {}


def geometria(clave, vista):
    if (clave, vista) not in _cache:
        fzp, svg, _ = PARTES[clave]
        _cache[clave, vista] = geo.conectores(fzp, svg, vista)
    return _cache[clave, vista]


def module_id(clave):
    import re
    return re.search(r'moduleId="([^"]*)"', PARTES[clave][0].read_text(encoding="utf-8", errors="ignore"))[1]


PREFIJOS = re.compile(r"^(acel|luz_rele|luz|pir|puerta|dht)_")


def color_real(c):
    return UTP.get(c, c)


def estilo_cable(c):
    """(color, rayado): los hilos blanco/color del UTP se dibujan del color de su par con bandas blancas, para
    distinguirlos del hilo de color solido."""
    real = color_real(c)
    if real.startswith("blanco-"):
        return COLORES.get(real.split("-", 1)[1], "#404040"), 1
    return COLORES.get(real, "#404040"), 0


def tipo_de(nombre):
    """Dispositivo de layouts -> clave de PARTES."""
    nombre = PREFIJOS.sub("", nombre)
    if nombre.startswith("LED"):
        return "LED"
    if nombre.startswith("NodeMCU"):
        return "nodemcu"
    return nombre if nombre in PARTES else nombre[0]


# ── transformaciones (rotación alrededor del centro, como Fritzing) ──
def matriz(ang, w, h):
    c, s = round(math.cos(math.radians(ang))), round(math.sin(math.radians(ang)))
    cx, cy = w / 2, h / 2
    return c, s, -s, c, cx - (c * cx - s * cy), cy - (s * cx + c * cy)


def aplicar(m, x, y):
    m11, m12, m21, m22, m31, m32 = m
    return m11 * x + m21 * y + m31, m12 * x + m22 * y + m32


def invertir(m, x, y):
    m11, m12, m21, m22, m31, m32 = m
    x, y = x - m31, y - m32
    return m11 * x + m12 * y, m21 * x + m22 * y  # rotaciones: inversa = transpuesta


class Boceto:
    def __init__(self):
        self.inst = []      # dicts de instancias
        self.indice = 5000
        self.huecos = {}    # agujeros de la protoboard ocupados
        self.titulos = {}

    def nuevo(self, clave, titulo, props=None):
        self.indice += 1
        d = dict(clave=clave, idx=self.indice, titulo=titulo, props=props or {}, vistas={})
        self.inst.append(d)
        return d

    @staticmethod
    def vista(inst, nombre, x, y, ang=0, w=0, h=0, z=2.5):
        inst["vistas"][nombre] = dict(x=x, y=y, ang=ang, w=w, h=h, z=z, con={})
        return inst["vistas"][nombre]

    @staticmethod
    def unir(a, ca, b, cb, vista, capa_a, capa_b):
        a["vistas"][vista]["con"].setdefault(ca, {"geo": None, "leg": None, "con": []})["con"].append((cb, b["idx"], capa_b))
        b["vistas"][vista]["con"].setdefault(cb, {"geo": None, "leg": None, "con": []})["con"].append((ca, a["idx"], capa_a))

    # ── XML ──
    def xml(self, titulo):
        out = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<module fritzingVersion="0.9.4" icon=".png">',
               ' <views>',
               '  <view name="breadboardView" backgroundColor="#ffffff" gridSize="0.1in" showGrid="1" alignToGrid="1" viewFromBelow="0"/>',
               '  <view name="schematicView" backgroundColor="#ffffff" gridSize="0.1in" showGrid="1" alignToGrid="1" viewFromBelow="0"/>',
               '  <view name="pcbView" backgroundColor="#333333" gridSize="0.05in" showGrid="1" alignToGrid="1" viewFromBelow="0"/>',
               ' </views>', ' <instances>']
        capas = {"breadboardView": "breadboard", "schematicView": "schematic", "pcbView": "copper0"}
        for d in self.inst:
            clave = d["clave"]
            if clave in ("wire", "wire_sch"):
                out.append(self._xml_cable(d))
                continue
            if clave in ("NetLabelModuleID", "LeftNetLabelModuleID"):
                ruta = ":/resources/parts/core/netlabel.fzp"
                mid = clave
            else:
                ruta = PARTES[clave][0].as_posix()
                mid = module_id(clave)
            out.append(f'  <instance moduleIdRef="{mid}" modelIndex="{d["idx"]}" path="{html.escape(ruta)}">')
            for k, v in d["props"].items():
                out.append(f'   <property name="{k}" value="{html.escape(v)}"/>')
            out.append(f'   <title>{html.escape(d["titulo"])}</title>')
            out.append('   <views>')
            for vista, v in d["vistas"].items():
                capa = "breadboardbreadboard" if clave.startswith("bb") else capas[vista]
                out.append(f'    <{vista} layer="{capa}">')
                g = f'     <geometry z="{v["z"]}" x="{v["x"]:.4f}" y="{v["y"]:.4f}"'
                if v["ang"]:
                    m = matriz(v["ang"], v["w"], v["h"])
                    g += (f'>\n      <transform m11="{m[0]}" m12="{m[1]}" m13="0" m21="{m[2]}" m22="{m[3]}" m23="0" '
                          f'm31="{m[4]:.4f}" m32="{m[5]:.4f}" m33="1"/>\n     </geometry>')
                else:
                    g += "/>"
                out.append(g)
                if v.get("titulo"):
                    tx, ty, claves = v["titulo"]
                    out.append(f'     <titleGeometry visible="true" x="{tx:.4f}" y="{ty:.4f}" z="{v["z"] + 3}" '
                               f'xOffset="{tx - v["x"]:.4f}" yOffset="{ty - v["y"]:.4f}" textColor="#000000" fontSize="5">')
                    out += [f'      <displayKey key="{k}"/>' for k in claves]
                    out.append('     </titleGeometry>')
                if v["con"]:
                    out.append('     <connectors>')
                    for cid, c in v["con"].items():
                        out.append(f'      <connector connectorId="{cid}" layer="{capa}">')
                        gx, gy = c["geo"] or (0, 0)
                        out.append(f'       <geometry x="{gx:.4f}" y="{gy:.4f}"/>')
                        if c["leg"]:
                            dx, dy = c["leg"]
                            out.append(f'       <leg><point x="0" y="0"/><bezier/><point x="{dx:.4f}" y="{dy:.4f}"/><bezier/></leg>')
                        out.append('       <connects>')
                        for cb, idx, capa_b in c["con"]:
                            out.append(f'        <connect connectorId="{cb}" modelIndex="{idx}" layer="{capa_b}"/>')
                        out.append('       </connects>')
                        out.append('      </connector>')
                    out.append('     </connectors>')
                out.append(f'    </{vista}>')
            out.append('   </views>')
            out.append('  </instance>')
        out += [' </instances>', f' <title>{html.escape(titulo)}</title>', '</module>', '']
        return "\n".join(out)

    def _xml_cable(self, d):
        bb = d["clave"] == "wire"
        vista, capa, flags = ("breadboardView", "breadboardWire", 64) if bb else ("schematicView", "schematicTrace", 128)
        v = d["vistas"][vista]
        s = [f'  <instance moduleIdRef="WireModuleID" modelIndex="{d["idx"]}" path=":/resources/parts/core/wire.fzp">',
             f'   <title>{d["titulo"]}</title>', '   <views>', f'    <{vista} layer="{capa}">',
             f'     <geometry z="{v["z"]}" x="{v["x"]:.4f}" y="{v["y"]:.4f}" x1="0" y1="0" x2="{v["x2"]:.4f}" y2="{v["y2"]:.4f}" wireFlags="{flags}"/>',
             f'     <wireExtras mils="{22.2222 if bb else 9.7222}" color="{d.get("color", "#404040")}" opacity="1" banded="{d.get("banded", 0)}"/>',
             '     <connectors>']
        for cid in ("connector0", "connector1"):
            s.append(f'      <connector connectorId="{cid}" layer="{capa}">\n       <geometry x="0" y="0"/>\n       <connects>')
            for cb, idx, capa_b in v["con"].get(cid, {"con": []})["con"]:
                s.append(f'        <connect connectorId="{cb}" modelIndex="{idx}" layer="{capa_b}"/>')
            s.append('       </connects>\n      </connector>')
        s += ['     </connectors>', f'    </{vista}>', '   </views>', '  </instance>']
        return "\n".join(s)


# ── vista de protoboard ──
def hueco(nombre, bb_con):
    """Orificio de layouts ('a20', 'A_5V:3') -> id del conector de la protoboard de Fritzing (filas reflejadas)."""
    fila, col = layouts.orificio(nombre)
    if fila in RIELES:
        letra = RIELES[fila]
        x_obj = bb_con[f"pin{col}A"]["x"]
        candidatos = [k for k in bb_con if k.startswith("pin") and k.endswith(letra) and k[3:-1].isdigit()]
        return min(candidatos, key=lambda k: abs(bb_con[k]["x"] - x_obj))
    return f"pin{col}{ESPEJO[fila]}"


def protoboard(b, lay):
    clave_bb = "bb830" if len(layouts.placas(lay)) > 1 else "bb400"
    _, _, bb_con = geometria(clave_bb, "breadboard")
    bb = b.nuevo(clave_bb, "Protoboard 830 puntos" if clave_bb == "bb830" else "Protoboard 400 puntos")
    b.vista(bb, "breadboardView", 0, 0, z=1.0)
    usados = {}

    def orificio(nombre):
        k = hueco(nombre, bb_con)
        if ":" in nombre and k in usados:  # riel ocupado: el libre más cercano de la misma tira
            letra = k[-1]
            libres = [c for c in bb_con if c.endswith(letra) and c.startswith("pin") and c[3:-1].isdigit() and c not in usados]
            k = min(libres, key=lambda c: abs(bb_con[c]["x"] - bb_con[k]["x"]))
        usados[k] = nombre
        return k, (bb_con[k]["x"], bb_con[k]["y"])

    insts = {}

    def fija(clave, titulo, pines, props=None):
        """Parte de patas rígidas clavada en la protoboard: busca el giro que cae en los orificios."""
        w, h, con = geometria(clave, "breadboard")
        obj = {cid: orificio(o) for cid, o in pines.items()}
        mejor = None
        for ang in (0, 90, 180, 270):
            m = matriz(ang, w, h)
            pts = {cid: aplicar(m, con[cid]["x"], con[cid]["y"]) for cid in obj}
            tx = sum(obj[c][1][0] - pts[c][0] for c in obj) / len(obj)
            ty = sum(obj[c][1][1] - pts[c][1] for c in obj) / len(obj)
            err = max(math.hypot(pts[c][0] + tx - obj[c][1][0], pts[c][1] + ty - obj[c][1][1]) for c in obj)
            if mejor is None or err < mejor[0]:
                mejor = (err, ang, tx, ty)
        err, ang, tx, ty = mejor
        if err > 3:
            print(f"  aviso: {titulo} queda a {err:.1f} px de sus orificios")
        d = b.nuevo(clave, titulo, props)
        b.vista(d, "breadboardView", tx, ty, ang, w, h, z=2.6)
        for cid, (k, _) in obj.items():
            b.unir(d, cid, bb, k, "breadboardView", "breadboard", "breadboardbreadboard")
        return d

    def con_patas(clave, titulo, pines, props=None, afuera=0.0):
        """Parte de patas flexibles (resistencia, capacitor): cuerpo entre los orificios y patas estiradas."""
        w, h, con = geometria(clave, "breadboard")
        obj = {cid: orificio(o) for cid, o in pines.items()}
        (c0, (_, p0)), (c1, (_, p1)) = list(obj.items())
        vertical = abs(p1[1] - p0[1]) > abs(p1[0] - p0[0])
        ang = 90 if vertical and clave == "R" else 0
        mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 - afuera
        x, y = mx - w / 2, my - h / 2
        d = b.nuevo(clave, titulo, props)
        b.vista(d, "breadboardView", x, y, ang, w, h, z=2.7)
        m = matriz(ang, w, h)
        for cid, (k, p) in obj.items():
            bx, by = con[cid]["base"]
            lx, ly = invertir(m, p[0] - x, p[1] - y)
            d["vistas"]["breadboardView"]["con"].setdefault(cid, {"geo": None, "leg": None, "con": []})
            d["vistas"]["breadboardView"]["con"][cid].update(geo=(bx, by), leg=(lx - bx, ly - by))
            b.unir(d, cid, bb, k, "breadboardView", "breadboard", "breadboardbreadboard")
        return d

    # NodeMCU
    for placa in layouts.placas(lay):
        col0 = placa["col0"]
        pines = {}
        for i, p in enumerate(AMICA_J):
            pines[f"connector{i}"] = f"i{col0 + i}"
        for k in range(15):
            pines[f"connector{29 - k}"] = f"b{col0 + k}"
        nombre_placa = placa["nombre"]
        insts[nombre_placa] = fija("nodemcu", nombre_placa.replace("NodeMCU_", "NodeMCU "), pines)

    for c in lay["componentes"]:
        clave = tipo_de(c["ref"]) if c["tipo"] == "M" else c["tipo"]
        mapa = PARTES[clave][2]
        pines = {mapa[p]: o for p, o in c["pines"].items()}
        if c["tipo"] == "R":
            insts[c["ref"]] = con_patas("R", c["ref"], pines, {"resistance": c["valor"].replace(" ", "")})
        elif c["tipo"] == "C":
            insts[c["ref"]] = con_patas("C", c["ref"], pines, {"capacitance": "220µF", "voltage": "16V"}, afuera=22)
        else:
            insts[c["ref"]] = fija(clave, c["ref"], pines)

    # dispositivos fuera de la protoboard, conectados con cable
    externos = {}
    for e in lay["externos"]:
        externos.setdefault(e["disp"], []).append(e)
    _, alto_bb = geometria(clave_bb, "breadboard")[0:2]
    cables = 0

    def tender(puntos, color, ini, fin):
        """Cable por tramos rectos: ini / fin = (instancia, conector, capa) de cada extremo."""
        nonlocal cables
        hexa, rayado = estilo_cable(color)
        anterior = None
        for i in range(len(puntos) - 1):
            (xa, ya), (xb, yb) = puntos[i], puntos[i + 1]
            cables += 1
            cab = b.nuevo("wire", f"Wire{cables}")
            cab["color"], cab["banded"] = hexa, rayado
            v = b.vista(cab, "breadboardView", xa, ya, z=3.5)
            v.update(x2=xb - xa, y2=yb - ya)
            if i == 0:
                b.unir(cab, "connector0", ini[0], ini[1], "breadboardView", "breadboardWire", ini[2])
            else:
                b.unir(cab, "connector0", anterior, "connector1", "breadboardView", "breadboardWire", "breadboardWire")
            if i == len(puntos) - 2:
                b.unir(cab, "connector1", fin[0], fin[1], "breadboardView", "breadboardWire", fin[2])
            anterior = cab

    def x_medio(lista):
        return sum(bb_con[hueco(e["orificio"], bb_con)]["x"] for e in lista) / len(lista)

    def lado_de(lista):
        ym = sum(bb_con[hueco(e["orificio"], bb_con)]["y"] for e in lista) / len(lista)
        return "arriba" if ym < alto_bb / 2 else "abajo"

    # Cada cable a una pieza externa baja recto, corre por SU carril (ninguno se encima) y entra recto al orificio.
    # El hueco entre las piezas y la protoboard crece con el numero de cables de ese lado.
    PASO_CARRIL = 5.0
    n_lado = {"arriba": 0, "abajo": 0}
    for lista in externos.values():
        n_lado[lado_de(lista)] += len(lista)
    cursor = {"arriba": -(26.0 + PASO_CARRIL * n_lado["arriba"]), "abajo": alto_bb + 26.0 + PASO_CARRIL * n_lado["abajo"]}
    x_lado = {"arriba": 0.0, "abajo": 0.0}
    carril_ext = {"arriba": 0, "abajo": 0}
    for disp, lista in sorted(externos.items(), key=lambda kv: x_medio(kv[1])):
        clave = tipo_de(disp)
        w, h, con = geometria(clave, "breadboard")
        mapa = PARTES[clave][2]
        objs = [(mapa[e["pin"]], orificio(e["orificio"]), e["color"]) for e in lista]
        xm = sum(p[0] for _, (_, p), _ in objs) / len(objs)
        lado = lado_de(lista)
        # las piezas de abajo se giran 180 grados si sus patas quedan del lado lejano a la protoboard
        ym_pines = sum(con[cid]["y"] for cid, _, _ in objs) / len(objs)
        ang = 180 if (lado == "abajo" and ym_pines > h / 2) or (lado == "arriba" and ym_pines < h / 2 - 1) else 0
        m = matriz(ang, w, h)
        x = max(xm - w / 2, x_lado[lado])
        y = cursor[lado] - h if lado == "arriba" else cursor[lado]
        x_lado[lado] = x + w + 18
        props = {}
        if clave == "LED":
            props = {"color": "Green (570nm)" if disp.endswith("V") else "Red (633nm)"}
        d = b.nuevo(clave, disp, props)
        b.vista(d, "breadboardView", x, y, ang, w, h, z=2.8)
        for cid, (k, p), color in sorted(objs, key=lambda o: o[1][1][0]):
            lx, ly = aplicar(m, con[cid]["x"], con[cid]["y"])
            px, py = x + lx, y + ly
            if "base" in con[cid]:
                bx, by = con[cid]["base"]
                d["vistas"]["breadboardView"]["con"].setdefault(cid, {"geo": None, "leg": None, "con": []})
                d["vistas"]["breadboardView"]["con"][cid].update(geo=(bx, by), leg=(con[cid]["x"] - bx, con[cid]["y"] - by))
            if abs(p[0] - px) < 2.5:
                puntos = [(px, py), p]
            else:
                carril_ext[lado] += 1
                yl = (-10.0 - PASO_CARRIL * carril_ext[lado]) if lado == "arriba" else \
                    (alto_bb + 10.0 + PASO_CARRIL * carril_ext[lado])
                puntos = [(px, py), (px, yl), (p[0], yl), p]
            tender(puntos, color, (d, cid, "breadboard"), (bb, k, "breadboardbreadboard"))
        insts[disp] = d

    # puentes: los largos van por un carril junto a la fila A (abajo) o J (arriba), no encima del NodeMCU
    y_a, y_j = bb_con["pin1A"]["y"], bb_con["pin1J"]["y"]
    carriles = {"abajo": 0, "arriba": 0}
    for p in sorted(lay["puentes"], key=lambda p: p.get("carril", 0)):
        (k0, p0), (k1, p1) = orificio(p["de"]), orificio(p["a"])
        if abs(p1[0] - p0[0]) > 20 and ":" not in p["de"] + p["a"]:
            lado = "abajo" if p0[1] > (y_a + y_j) / 2 else "arriba"
            carriles[lado] += 1
            yc = y_a + 3 + 2.6 * carriles[lado] if lado == "abajo" else y_j - 3 - 2.6 * carriles[lado]
            puntos = [p0, (p0[0], yc), (p1[0], yc), p1]
        else:
            puntos = [p0, p1]
        tender(puntos, p["color"], (bb, k0, "breadboardbreadboard"), (bb, k1, "breadboardbreadboard"))
    return insts


# ── vista esquemática: cada pin con un tramo corto y una etiqueta de red ──
def esquematico(b, lay, insts):
    redes = {}
    for red, miembros in lay["redes"].items():
        for m in miembros:
            disp, pin = m.split(".", 1)
            redes.setdefault(disp, {})[pin] = red
    placas = [k for k in insts if k.startswith("NodeMCU")]
    orden = placas + [k for k in insts if k not in placas]
    x_col, y_col, ancho_col = 0.0, 0.0, 0.0
    etiquetas = 0
    for n, disp in enumerate(orden):
        d = insts[disp]
        clave = d["clave"]
        w, h, con = geometria(clave, "schematic")
        if n == len(placas):
            x_col, y_col = ancho_col + 170, 0.0
            ancho_col = 0.0
        elif n > len(placas) and y_col + h > 520:
            x_col, y_col = x_col + ancho_col + 190, 0.0
            ancho_col = 0.0
        x, y = x_col, y_col
        ancho_col = max(ancho_col, w)
        y_col += h + 95
        v = b.vista(d, "schematicView", x, y, 0, w, h, z=2.5)
        v["titulo"] = (x + w + 4, y - 2, [""] + [k for k in ("resistance", "capacitance", "color") if k in d["props"]])
        mapa = PARTES[clave][2]
        pines = []
        for pin, red in redes.get(disp, {}).items():
            cid = mapa.get(pin)
            if cid is None or cid not in con:
                print(f"  aviso: {disp}.{pin} sin conector en el esquemático")
                continue
            tx, ty = con[cid]["x"], con[cid]["y"]
            dist = {"izq": tx, "der": w - tx, "arr": ty, "aba": h - ty}
            pines.append((pin, red, cid, tx, ty, min(dist, key=dist.get)))
        # dos pines juntos arriba o abajo (buzzer): etiquetas hacia afuera, a la izquierda y a la derecha
        for lado_v in ("arr", "aba"):
            grupo = sorted([p for p in pines if p[5] == lado_v], key=lambda p: p[3])
            if len(grupo) == 2 and abs(grupo[1][3] - grupo[0][3]) < 30:
                pines = [p for p in pines if p not in grupo] + [grupo[0][:5] + (lado_v + "_izq",), grupo[1][:5] + (lado_v + "_der",)]
        for pin, red, cid, tx, ty, lado in pines:
            giro = lado.split("_")[1] if "_" in lado else None
            lado = lado.split("_")[0]
            dx, dy = {"izq": (-1, 0), "der": (1, 0), "arr": (0, -1), "aba": (0, 1)}[lado]
            px, py = x + tx, y + ty
            ex, ey = px + dx * 27, py + dy * 27
            etiquetas += 1
            izquierda = lado == "izq" or giro == "izq"
            lab = b.nuevo("LeftNetLabelModuleID" if izquierda else "NetLabelModuleID", f"netlabel{etiquetas}", {"label": red})
            ancho_lab = 7 + 5.2 * len(red)
            lx = ex - ancho_lab if izquierda else ex
            ly = ey - 4.5
            if giro:
                lx = ex - ancho_lab if izquierda else ex
                ly = ey - 4.5
            elif lado in ("arr", "aba"):
                lx = ex - ancho_lab / 2
                ly = ey - 9 if lado == "arr" else ey
            b.vista(lab, "schematicView", lx, ly, z=2.6)
            etiquetas += 1
            cab = b.nuevo("wire_sch", f"Wire{1000 + etiquetas}")
            cab["color"] = "#404040"
            cv = b.vista(cab, "schematicView", px, py, z=3.5)
            cv.update(x2=ex - px, y2=ey - py)
            b.unir(cab, "connector0", d, cid, "schematicView", "schematicTrace", "schematic")
            b.unir(cab, "connector1", lab, "connector0", "schematicView", "schematicTrace", "schematic")


def pcb_por_defecto(b):
    for i, d in enumerate(b.inst):
        if d["clave"] not in ("wire", "wire_sch", "NetLabelModuleID", "LeftNetLabelModuleID", "bb400", "bb830"):
            b.vista(d, "pcbView", (i % 6) * 120.0, (i // 6) * 120.0, z=5.5)


def instalar_partes():
    """Copia partes/ a la carpeta de partes de usuario de Fritzing (la usa el modo -svg)."""
    dest = carpeta_usuario()
    (dest / "user").mkdir(parents=True, exist_ok=True)
    for f in PROPIAS.glob("*.fzp"):
        shutil.copy2(f, dest / "user" / f.name)
    for vista in ("breadboard", "schematic", "pcb", "icon"):
        (dest / "svg" / "user" / vista).mkdir(parents=True, exist_ok=True)
        for f in (PROPIAS / "svg" / vista).glob("*.svg"):
            shutil.copy2(f, dest / "svg" / "user" / vista / f.name)


def empacar(nombre, xml):
    """.fzz con las partes que no son de la biblioteca base (part.* y svg.<vista>.*), como lo guarda Fritzing."""
    SALIDA.mkdir(exist_ok=True)
    ruta = SALIDA / f"{nombre}.fzz"
    with zipfile.ZipFile(ruta, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"{nombre}.fz", xml)
        for f in PROPIAS.glob("*.fzp"):
            if f.stem.split("_")[0] in xml or f.stem in xml or module_id_de(f) in xml:
                z.write(f, "part." + f.name)
                for vista in ("breadboard", "schematic", "pcb", "icon"):
                    for s in (PROPIAS / "svg" / vista).glob("*.svg"):
                        if s.name in f.read_text(encoding="utf-8", errors="ignore"):
                            z.write(s, f"svg.{vista}.{s.name}")
    return ruta


def module_id_de(f):
    import re
    m = re.search(r'moduleId="([^"]*)"', f.read_text(encoding="utf-8", errors="ignore"))
    return f'moduleIdRef="{m[1]}"' if m else "\0"


PASOS = {1: "placas, energía y capacitores", 2: "resistencias y puentes", 3: "módulos y transistor",
         4: "cables a las piezas de la tapa"}


def lay_paso(lay, paso):
    """Distribucion recortada a lo que ya esta puesto al terminar ese paso del armado (para las imagenes por paso)."""
    def es_energia(p):
        return ":" in p["de"] + p["a"] and p["nota"].split("] ")[-1].startswith(("VIN", "GND →", "3V3 →"))
    comps = [c for c in lay["componentes"]
             if c["tipo"] == "C" or (paso >= 2 and c["tipo"] == "R") or (paso >= 3 and c["tipo"] in ("M", "Q"))]
    puentes = [p for p in lay["puentes"] if paso >= 2 or es_energia(p)]
    return dict(lay, componentes=comps, puentes=puentes, externos=lay["externos"] if paso >= 4 else [])


def generar(nombre, paso=None, parte=None):
    lay = layouts.LAYOUTS[nombre]
    b = Boceto()
    if parte:  # todo lo clavado (pasos 1 a 3) y SOLO los cables de una pieza externa: el paso 4, pieza por pieza
        i, clave, titulo, disps = parte
        protoboard(b, dict(lay_paso(lay, 3), externos=[e for e in lay["externos"] if e["disp"] in disps]))
        return empacar(f"{nombre}_parte{i}_{clave}", b.xml(f"Argos · {nombre} · paso 4, parte {i}: {titulo}"))
    if paso:   # solo la vista de protoboard, recortada al paso
        protoboard(b, lay_paso(lay, paso))
        return empacar(f"{nombre}_paso{paso}", b.xml(f"Argos · {nombre} · paso {paso}: {PASOS[paso]}"))
    insts = protoboard(b, lay)
    esquematico(b, lay, insts)
    pcb_por_defecto(b)
    xml = b.xml(f"Argos · {nombre}")
    return empacar(nombre, xml)


def exportar():
    """Fritzing -svg exporta las tres vistas de cada .fzz de la carpeta."""
    # En lotes de 8: con una carpeta de mas de ~10 archivos, Fritzing CD-548 se cierra solo (0xC0000005).
    import tempfile
    exe = FZ / "Fritzing.exe"
    fzz = sorted(SALIDA.glob("*.fzz"))
    for i in range(0, len(fzz), 8):
        with tempfile.TemporaryDirectory() as t:
            for f in fzz[i:i + 8]:
                shutil.copy2(f, t)
            subprocess.run([str(exe), "-svg", t], check=True, timeout=600)
            for s in Path(t).glob("*.svg"):
                shutil.copy2(s, SALIDA)


if __name__ == "__main__":
    por_pasos = "--pasos" in sys.argv        # ademas, 4 imagenes por caja: una por paso del armado
    nombres = [a for a in sys.argv[1:] if not a.startswith("--")] or NODOS
    instalar_partes()
    for n in nombres:
        print("ok", generar(n).name)
        if por_pasos and n in CAJAS:
            for paso in PASOS:
                print("ok", generar(n, paso).name)
        if "--partes" in sys.argv and n in CAJAS:   # ademas, una imagen por pieza externa
            import lista_cables
            for i, (clave, titulo, disps) in enumerate(lista_cables.piezas(layouts.LAYOUTS[n]), 1):
                print("ok", generar(n, parte=(i, clave, titulo, disps)).name)
    if (FZ / "Fritzing.exe").exists():
        exportar()
        print("svg exportados en", SALIDA)
