C = {
 "Caja": ["idCaja", "descripcion", "ubicacion", "   area", "   punto_montaje"],
 "Responsable": ["idResponsable", "nombre"],
 "Nodo": ["idNodo", "descripcion"],
 "estadoNodo": ["idNodo", "estado", "ultimo_reporte", "reset_reason", "uptime_s", "rssi"],
 "Sensor": ["idSensor", "modelo"],
 "Evento": ["idEvento", "tipo", "magnitud", "fuera_horario", "fecha_hora"],
 "Medicion": ["idMedicion", "valor", "fecha_hora"],
 "parametro": ["idParametro", "nombre", "unidad"],
 "Umbral": ["idUmbral", "minimo", "maximo", "histeresis", "persistencia", "activa_buzzer"],
 "alerta": ["idAlerta", "tipo", "valor", "ts_inicio", "ts_fin", " / estado", " / duracion"],
 "notificacion": ["idAlerta", "canal", "enviada", "ts_envio"],
 "actuador": ["idActuador", "tipo"],
 "accionControl": ["idAccion", "origen", "comando", "duracion_s", "fecha_hora"],
 "Configuracion": ["clave", "valor"],
}
R = [  # a, b, etiqueta, mult_a, mult_b
 ("Caja", "Nodo", "aloja", "1", "1..2"),
 ("Responsable", "Nodo", "responde de", "1", "1..*"),
 ("Nodo", "estadoNodo", "reporta", "1", "1"),
 ("Nodo", "Sensor", "tiene", "1", "1..*"),
 ("Sensor", "Evento", "registra", "1", "0..*"),
 ("Sensor", "Medicion", "produce", "1", "0..*"),
 ("parametro", "Medicion", "describe", "1", "0..*"),
 ("parametro", "Umbral", "evalua", "1", "0..*"),
 ("Sensor", "Umbral", "se compara con", "1", "0..*"),
 ("Nodo", "alerta", "genera", "1", "0..*"),
 ("Umbral", "alerta", "rige", "0..1", "0..*"),
 ("alerta", "notificacion", "notifica por", "1", "1..*"),
 ("Nodo", "actuador", "posee", "1", "1..2"),
 ("actuador", "accionControl", "ejecuta", "1", "0..*"),
 ("alerta", "accionControl", "dispara", "0..1", "0..*"),
]
def lab(n, at):
    filas = "".join(f'<TR><TD ALIGN="LEFT" BALIGN="LEFT">{"-" + a if not a.startswith("   ") else "&nbsp;&nbsp;&nbsp;-" + a.strip()}</TD></TR>' for a in at)
    return (f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3" BGCOLOR="#7ccdf4" COLOR="black">'
            f'<TR><TD SIDES="B" BORDER="1"><B>{n}</B></TD></TR>{filas}<TR><TD> </TD></TR></TABLE>>')
o = ['graph G {', 'graph [layout=neato, splines=line, overlap=true, fontname="Arial", pad=0.2];',
     'node [shape=plain, fontname="Arial", fontsize=13];', 'edge [fontname="Arial", fontsize=12, labeldistance=1.8, labelangle=35];']
for n, at in C.items(): o.append(f'"{n}" [label={lab(n, at)}];')
for a, b, e, ma, mb in R:
    o.append(f'"{a}" -- "{b}" [label="  {e}  ", taillabel="{ma}", headlabel="{mb}"];')
P = {"Configuracion": (9.4, 12.6), "Responsable": (1.6, 12.2), "Caja": (5.4, 12.0), "estadoNodo": (1.8, 9.4), "Nodo": (5.4, 8.9),
     "Evento": (9.4, 10.6), "Sensor": (9.4, 7.6), "actuador": (1.6, 6.6), "alerta": (5.4, 5.2),
     "accionControl": (1.6, 3.9), "Medicion": (9.4, 4.4), "notificacion": (1.6, 0.8), "Umbral": (5.4, 1.0),
     "parametro": (9.4, 0.9)}
for n,(x,y) in P.items(): o.append(f'"{n}" [pos="{x},{y}!"];')
o.append('}')
open("fig/uml.dot", "w", encoding="utf-8").write("\n".join(o))
