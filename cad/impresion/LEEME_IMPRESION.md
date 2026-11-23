# Argos: qué imprimir (generado el 20-nov-2026)

Todos los STL ya vienen **acostados en la posición de impresión**: se abren en Creality Print y se imprimen sin girarlos y **sin soportes**. Material: PETG. Revisión automática: 0 interferencias en las tres cajas.

Los gramos son del modelo macizo equivalente; el laminador dará menos según el relleno.

## Orden recomendado

1. **`0_cupon_de_prueba`** (unos gramos). Prueba el encaje a presión, el agujero del LED y el texto con SU impresora y SU filamento. Si la tapa del cupón no entra o queda floja, avisen antes de imprimir una caja.
2. **`1_caja_dht`**, que es la que ya están armando.
3. **`2_estacion_entrada`** y **`3_estacion_anaquel`**.

## 1. Caja dht (80 × 166.5 × 40.5 mm con orejas)

| Archivo | Cantidad | Cómo va en la cama | Gramos |
|---|---|---|---|
| `nodo_dht_base.stl` | 1 | Espalda en la cama | 84 |
| `nodo_dht_tapa.stl` | 1 | Frente en la cama (es la cara que se ve: primera capa lenta) | 32 |
| `nodo_dht_grapa_oled_IMPRIMIR_2.stl` | **2** | De canto, como viene | 1 c/u |
| `nodo_dht_embolo_boton.stl` | 1 | Ceja en la cama | 0.1 |
| `nodo_dht_soporte_pared.stl` **o** `nodo_dht_soporte_anaquel.stl` | 1 | Como viene | 27 o 35 |

Solo uno de los dos soportes: el de pared si la caja va atornillada a la pared, el de anaquel si cuelga del borde del anaquel (supone un borde de 18 mm de espesor, sin confirmar).

**Lo que se debe saber de esta caja:**
- La abertura de la pantalla mide **60.4 × 36.9 mm**: es la medida interior de la pantalla que tomó Iván (62.37 × 38.92 mm) menos 1 mm de ceja por lado, así que deja ver todo el vidrio. Su posición a lo alto se estimó de una foto; la ceja absorbe hasta 1 mm de diferencia.
- La pantalla entra con la **cinta naranja hacia abajo** y la tira de 7 pines del lado **izquierdo** viendo la caja de frente. Se detiene con las 2 grapas, que cruzan de arriba abajo.
- La pantalla casi llena el ancho interior: queda a 0.4 mm de cada pared. Si su placa mide más de 72.5 mm, hay que lijar el marco.
- El botón queda al ras de su cuna: fíjenlo con un punto de pegamento. El émbolo impreso va entre el botón y la tapa.

## 2. Estación de entrada (201.7 × 80 × 40.5 mm)

| Archivo | Cantidad | Cómo va en la cama | Gramos |
|---|---|---|---|
| `nodo_entrada_base.stl` | 1 | Espalda en la cama | 84 |
| `nodo_entrada_tapa.stl` | 1 | Frente en la cama | 48 |
| `nodo_entrada_soporte_pared.stl` | 1 (trae los 2 tacos) | Espalda en la cama | 14 |
| `nodo_entrada_porta_sensor.stl` | 1 | Piso en la cama | 4 |
| `nodo_entrada_porta_iman.stl` | 1 | Piso en la cama | 5 |
| `nodo_entrada_calza_2mm.stl` y `calza_4mm.stl` | Solo si hacen falta | Planas | 2 y 4 |

Las calzas sirven para alinear el sensor de puerta con el imán si el marco y la puerta no quedan al mismo nivel.

Sin medir: el alto del sensor de movimiento por detrás (se supuso 12 mm).

## 3. Estación del anaquel (201.7 × 80 × 40.5 mm)

| Archivo | Cantidad | Cómo va en la cama | Material | Gramos |
|---|---|---|---|---|
| `nodo_anaquel_base.stl` | 1 | Espalda en la cama | PETG | 84 |
| `nodo_anaquel_tapa.stl` | 1 | Frente en la cama | PETG | 49 |
| `nodo_anaquel_capuchon_ldr.stl` | 1 | Cola en la cama | **PETG negro** | 5 |
| `nodo_anaquel_soporte_ldr.stl` | 1 | Placa en la cama | PETG negro | 3 |
| `nodo_anaquel_difusor_ldr.stl` | 1 | Plano, relleno 100 % | **PETG blanco o natural** | 0.1 |

Si el PETG que tienen no es negro, el capuchón de la fotorresistencia hay que pintarlo o forrarlo por fuera: debe ser opaco.

La tapa **no lleva costillas** para el acelerómetro y el convertidor, porque sus medidas son aproximadas. Los dos quedan sostenidos solo por sus pines en la protoboard.

## Cama

Las estaciones miden 201.7 mm de largo: caben derechas en una cama de 220 mm. Céntrenlas y revisen que el borde ("brim") no se salga.

Total aproximado de las tres cajas con sus accesorios: unos 450 g de PETG.
