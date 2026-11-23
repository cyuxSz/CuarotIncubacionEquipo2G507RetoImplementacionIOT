# Cables de la caja dht

dht (con OLED 2.42"). Largos estimados desde la distancia entre orificios; los de pieza externa son supuestos (ajustar al armar).

**Letras de fila como vienen impresas en la protoboard y en la imagen de Fritzing**, con el USB de los NodeMCU hacia la izquierda: J arriba, A abajo. Rieles: arriba +5V (línea roja) y GND (línea azul); abajo GND (línea azul) y +3V3 (línea roja). Los 4 rieles son continuos de punta a punta.

| # | Tipo | De | A | Cable | Largo (cm) | Para qué |
|---|---|---|---|---|---|---|
| 1 | puente | J1 | riel de arriba +5V (línea roja), col. 1 | UTP naranja | 2.5 | VIN (5 V del USB) → riel 5V |
| 2 | puente | J2 | riel de arriba GND (línea azul), col. 2 | UTP café | 2.5 | GND → riel GND de arriba |
| 3 | puente | A1 | riel de abajo +3V3 (línea roja), col. 1 | UTP naranja | 2.5 | 3V3 → riel 3V3 |
| 4 | puente | A2 | riel de abajo GND (línea azul), col. 2 | UTP café | 2.5 | GND → riel GND de abajo |
| 5 | puente | A6 | C20 | UTP café | 6 | D7 → columna 20 (LED verde), por fuera de la fila A |
| 6 | puente | A5 | C22 | UTP blanco/naranja | 6.5 | D8 → columna 22 (LED rojo), por fuera de la fila A |
| 7 | puente | A8 | C27 | UTP blanco/café | 7 | D5 → columna 27 (R3 hacia la base de Q1), por fuera de la fila A |
| 8 | puente | J26 | riel de arriba GND (línea azul), col. 26 | UTP café | 2.5 | Emisor de Q1 → GND |
| 9 | puente | A7 | C21 | UTP blanco/azul | 6 | D6 → columna 21 (botón), por fuera de la fila A |
| 10 | puente | A11 | C24 | UTP blanco/verde | 5.5 | D4 → columna 24 (DATA del DHT22), por fuera de la fila A |
| 11 | puente | A13 | C23 | UTP verde | 5 | D2/SDA → columna 23 (OLED), por fuera de la fila A |
| 12 | puente | A14 | C25 | UTP azul | 5 | D1/SCL → columna 25 (OLED), por fuera de la fila A |
| 13 | a pieza | LED_V.A | J20 | UTP verde | 15 | Ánodo (pata larga) del LED verde, en la tapa |
| 14 | a pieza | LED_V.K | riel de arriba GND (línea azul), col. 19 | UTP café | 15 | Cátodo (pata corta, lado plano) |
| 15 | a pieza | LED_R.A | J22 | UTP naranja | 15 | Ánodo (pata larga) del LED rojo, en la tapa |
| 16 | a pieza | LED_R.K | riel de arriba GND (línea azul), col. 23 | UTP café | 15 | Cátodo (pata corta, lado plano) |
| 17 | a pieza | Boton.1 | A21 | UTP blanco/azul | 15 | Botón de silencio/pantalla (en la tapa) |
| 18 | a pieza | Boton.2 | riel de abajo GND (línea azul), col. 7 | UTP café | 15 |  |
| 19 | a pieza | DHT22.VCC | riel de abajo +3V3 (línea roja), col. 26 | UTP naranja | 20 | Cámara inferior: cable más largo. Columna 26 para no chocar con R1 de pie |
| 20 | a pieza | DHT22.DATA | E24 | UTP blanco/verde | 20 |  |
| 21 | a pieza | DHT22.GND | riel de abajo GND (línea azul), col. 27 | UTP café | 20 | Dos columnas a la derecha de VCC para no chocar con R1 de pie |
| 22 | a pieza | Buzzer.+ | riel de arriba +5V (línea roja), col. 28 | UTP naranja | 15 | Buzzer suelto (sin placa): la pata marcada + (o la más larga) al riel 5V |
| 23 | a pieza | Buzzer.- | G28 | UTP blanco/café | 15 | Al colector de Q1 (conmutación del lado bajo). En G28 y no en J28: la lata metálica del 2N2222 (TO-18) no deja espacio junto a la fila J |
| 24 | a pieza | Entrada5V.+ | riel de arriba +5V (línea roja), col. 10 | UTP naranja | 10 | Módulo de entrada USB-C a terminales (5 V de la fuente de la caja) |
| 25 | a pieza | Entrada5V.- | riel de arriba GND (línea azul), col. 10 | UTP café | 10 |  |
| 26 | a pieza | OLED.VCC | riel de abajo +3V3 (línea roja), col. 12 | UTP naranja | 20 | El módulo dice VCC=5V: se prueba primero a 3V3 para que ninguna señal pase de 3.3 V |
| 27 | a pieza | OLED.GND | riel de abajo GND (línea azul), col. 12 | UTP café | 20 |  |
| 28 | a pieza | OLED.SCL | E25 | UTP azul | 20 | Reloj. D1 llega por el puente A14 → C25 |
| 29 | a pieza | OLED.SDA | E23 | UTP verde | 20 | Datos. D2 llega por el puente A13 → C23 |
| 30 | a pieza | OLED.DC | A12 | UTP blanco/verde | 20 | Dato/comando, directo al orificio libre junto al pin D3 |
| 31 | a pieza | OLED.RES | A15 | UTP blanco/azul | 20 | Reinicio de la pantalla, directo al orificio libre junto al pin D0 |
| 32 | a pieza | OLED.CS | riel de abajo GND (línea azul), col. 14 | UTP café | 20 | Selección: fija a GND (es el único dispositivo SPI) |

## Totales por cable

| Cable | Cantidad | Largo total (cm) |
|---|---|---|
| UTP azul | 2 | 25 |
| UTP blanco/azul | 3 | 41 |
| UTP blanco/café | 2 | 22 |
| UTP blanco/naranja | 1 | 6.5 |
| UTP blanco/verde | 3 | 45.5 |
| UTP café | 11 | 128.5 |
| UTP naranja | 7 | 85 |
| UTP verde | 3 | 40 |
| **Total** | **32** | **393.5** |
