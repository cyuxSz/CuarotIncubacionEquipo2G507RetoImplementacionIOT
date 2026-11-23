# Cables de la caja entrada

Estación de entrada (pir + puerta). Largos estimados desde la distancia entre orificios; los de pieza externa son supuestos (ajustar al armar).

**Letras de fila como vienen impresas en la protoboard y en la imagen de Fritzing**, con el USB de los NodeMCU hacia la izquierda: J arriba, A abajo. Rieles: arriba +5V (línea roja) y GND (línea azul); abajo GND (línea azul) y +3V3 (línea roja). Los 4 rieles son continuos de punta a punta.

| # | Tipo | De | A | Cable | Largo (cm) | Para qué |
|---|---|---|---|---|---|---|
| 1 | puente | J1 | riel de arriba +5V (línea roja), col. 1 | UTP naranja | 2.5 | [pir] VIN (5 V del USB) → riel 5V |
| 2 | puente | J2 | riel de arriba GND (línea azul), col. 2 | UTP café | 2.5 | [pir] GND → riel GND de arriba |
| 3 | puente | A1 | riel de abajo +3V3 (línea roja), col. 1 | UTP naranja | 2.5 | [pir] 3V3 → riel 3V3 |
| 4 | puente | A2 | riel de abajo GND (línea azul), col. 2 | UTP café | 2.5 | [pir] GND → riel GND de abajo |
| 5 | puente | A6 | C20 | UTP café | 6 | [pir] D7 → columna 20 (LED verde), por fuera de la fila A |
| 6 | puente | A5 | C22 | UTP blanco/naranja | 6.5 | [pir] D8 → columna 22 (LED rojo), por fuera de la fila A |
| 7 | puente | A8 | C27 | UTP blanco/café | 7 | [pir] D5 → columna 27 (OUT del PIR), por fuera de la fila A |
| 8 | puente | J34 | riel de arriba +5V (línea roja), col. 34 | UTP naranja | 2.5 | [puerta] VIN (5 V del USB) → riel 5V |
| 9 | puente | J35 | riel de arriba GND (línea azul), col. 35 | UTP café | 2.5 | [puerta] GND → riel GND de arriba |
| 10 | puente | A35 | riel de abajo GND (línea azul), col. 35 | UTP café | 2.5 | [puerta] GND → riel GND de abajo |
| 11 | puente | A39 | C53 | UTP café | 6 | [puerta] D7 → columna 53 (LED verde), por fuera de la fila A |
| 12 | puente | A38 | C55 | UTP blanco/naranja | 6.5 | [puerta] D8 → columna 55 (LED rojo), por fuera de la fila A |
| 13 | puente | A41 | C60 | UTP blanco/café | 7 | [puerta] D5 → columna 60 (reed), por fuera de la fila A |
| 14 | a pieza | pir_LED_V.A | J20 | UTP verde | 15 | Ánodo (pata larga) del LED verde, en la tapa |
| 15 | a pieza | pir_LED_V.K | riel de arriba GND (línea azul), col. 19 | UTP café | 15 | Cátodo (pata corta, lado plano) |
| 16 | a pieza | pir_LED_R.A | J22 | UTP naranja | 15 | Ánodo (pata larga) del LED rojo, en la tapa |
| 17 | a pieza | pir_LED_R.K | riel de arriba GND (línea azul), col. 23 | UTP café | 15 | Cátodo (pata corta, lado plano) |
| 18 | a pieza | pir_PIR.VCC | riel de arriba +5V (línea roja), col. 28 | UTP naranja | 25 | HC-SR501 en la tapa; pinout VCC-OUT-GND [verificar serigrafía] |
| 19 | a pieza | pir_PIR.OUT | E27 | UTP blanco/café | 25 |  |
| 20 | a pieza | pir_PIR.GND | riel de arriba GND (línea azul), col. 28 | UTP café | 25 |  |
| 21 | a pieza | puerta_LED_V.A | J53 | UTP verde | 15 | Ánodo (pata larga) del LED verde, en la tapa |
| 22 | a pieza | puerta_LED_V.K | riel de arriba GND (línea azul), col. 52 | UTP café | 15 | Cátodo (pata corta, lado plano) |
| 23 | a pieza | puerta_LED_R.A | J55 | UTP naranja | 15 | Ánodo (pata larga) del LED rojo, en la tapa |
| 24 | a pieza | puerta_LED_R.K | riel de arriba GND (línea azul), col. 56 | UTP café | 15 | Cátodo (pata corta, lado plano) |
| 25 | a pieza | puerta_Reed.1 | E60 | UTP blanco/café | 0 | Cable del MC-38 (≈ 30 cm) con terminal Dupont macho crimpado Usa el cable propio del MC-38: no se corta cable. |
| 26 | a pieza | puerta_Reed.2 | riel de abajo GND (línea azul), col. 60 | UTP café | 0 | Sin polaridad Usa el cable propio del MC-38: no se corta cable. |
| 27 | a pieza | Entrada5V.+ | riel de arriba +5V (línea roja), col. 32 | UTP naranja | 10 | Módulo de entrada USB-C a terminales (5 V de la fuente de la caja) |
| 28 | a pieza | Entrada5V.- | riel de arriba GND (línea azul), col. 32 | UTP café | 10 |  |

## Totales por cable

| Cable | Cantidad | Largo total (cm) |
|---|---|---|
| UTP blanco/café | 3 | 39 |
| UTP blanco/naranja | 2 | 13 |
| UTP café | 12 | 117 |
| UTP naranja | 7 | 72.5 |
| UTP verde | 2 | 30 |
| **Total** | **26** | **271.5** |
