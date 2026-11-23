# Cables de la caja anaquel

Estación del anaquel (acel + luz). Largos estimados desde la distancia entre orificios; los de pieza externa son supuestos (ajustar al armar).

**Letras de fila como vienen impresas en la protoboard y en la imagen de Fritzing**, con el USB de los NodeMCU hacia la izquierda: J arriba, A abajo. Rieles: arriba +5V (línea roja) y GND (línea azul); abajo GND (línea azul) y +3V3 (línea roja). Los 4 rieles son continuos de punta a punta.

| # | Tipo | De | A | Cable | Largo (cm) | Para qué |
|---|---|---|---|---|---|---|
| 1 | puente | J1 | riel de arriba +5V (línea roja), col. 1 | UTP naranja | 2.5 | [acel] VIN (5 V del USB) → riel 5V |
| 2 | puente | J2 | riel de arriba GND (línea azul), col. 2 | UTP café | 2.5 | [acel] GND → riel GND de arriba |
| 3 | puente | A1 | riel de abajo +3V3 (línea roja), col. 1 | UTP naranja | 2.5 | [acel] 3V3 → riel 3V3 |
| 4 | puente | A2 | riel de abajo GND (línea azul), col. 2 | UTP café | 2.5 | [acel] GND → riel GND de abajo |
| 5 | puente | A6 | C19 | UTP café | 5.5 | [acel] D7 → columna 19 (LED verde), por fuera de la fila A |
| 6 | puente | A5 | C30 | UTP blanco/naranja | 8.5 | [acel] D8 → columna 30 (LED rojo), por fuera de la fila A |
| 7 | puente | A14 | C22 | UTP azul | 4.5 | [acel] D1/SCL → columna 22, por fuera de la fila A |
| 8 | puente | A13 | C23 | UTP verde | 5 | [acel] D2/SDA → columna 23, por fuera de la fila A |
| 9 | puente | E22 | F22 | UTP azul | 2.5 | [acel] SCL cruza el canal hacia el ADS1115 |
| 10 | puente | E23 | F23 | UTP verde | 2.5 | [acel] SDA cruza el canal hacia el ADS1115 |
| 11 | puente | F20 | E20 | UTP naranja | 2.5 | [acel] VDD del ADS1115 cruza el canal |
| 12 | puente | A20 | riel de abajo +3V3 (línea roja), col. 20 | UTP naranja | 2.5 | [acel] VDD del ADS1115 → riel 3V3 |
| 13 | puente | J21 | riel de arriba GND (línea azul), col. 21 | UTP café | 2.5 | [acel] GND del ADS1115 → riel GND |
| 14 | puente | J24 | riel de arriba GND (línea azul), col. 24 | UTP café | 2.5 | [acel] ADDR → GND (dirección 0x48) |
| 15 | puente | A25 | riel de abajo +3V3 (línea roja), col. 25 | UTP naranja | 2.5 | [acel] VCC del GY-61 → riel 3V3 |
| 16 | puente | A29 | riel de abajo GND (línea azul), col. 29 | UTP café | 2.5 | [acel] GND del GY-61 → riel GND |
| 17 | puente | E26 | F26 | UTP blanco/café | 2.5 | [acel] X del GY-61 → A0 del ADS1115 |
| 18 | puente | E27 | F27 | UTP blanco/azul | 2.5 | [acel] Y del GY-61 → A1 del ADS1115 |
| 19 | puente | E28 | F28 | UTP café | 2.5 | [acel] Z del GY-61 → A2 del ADS1115 |
| 20 | puente | J34 | riel de arriba +5V (línea roja), col. 34 | UTP naranja | 2.5 | [luz] VIN (5 V del USB) → riel 5V |
| 21 | puente | J35 | riel de arriba GND (línea azul), col. 35 | UTP café | 2.5 | [luz] GND → riel GND de arriba |
| 22 | puente | A35 | riel de abajo GND (línea azul), col. 35 | UTP café | 2.5 | [luz] GND → riel GND de abajo |
| 23 | puente | A39 | C53 | UTP café | 6 | [luz] D7 → columna 53 (LED verde), por fuera de la fila A |
| 24 | puente | A38 | C55 | UTP blanco/naranja | 6.5 | [luz] D8 → columna 55 (LED rojo), por fuera de la fila A |
| 25 | puente | J48 | I58 | UTP blanco/verde | 4.5 | [luz] A0 → columna 58 (divisor), por fuera de la fila J |
| 26 | puente | A43 | C59 | UTP naranja | 6.5 | [luz] 3V3 (pin 10 del lado D) → columna 59, para la LDR; no usa el riel 3V3 |
| 27 | a pieza | acel_LED_V.A | J19 | UTP verde | 15 | Ánodo del LED verde, en la tapa |
| 28 | a pieza | acel_LED_V.K | riel de arriba GND (línea azul), col. 18 | UTP café | 15 | Cátodo |
| 29 | a pieza | acel_LED_R.A | J30 | UTP naranja | 15 | Ánodo del LED rojo, en la tapa |
| 30 | a pieza | acel_LED_R.K | riel de arriba GND (línea azul), col. 30 | UTP café | 15 | Cátodo |
| 31 | a pieza | luz_LED_V.A | J53 | UTP verde | 15 | Ánodo (pata larga) del LED verde, en la tapa |
| 32 | a pieza | luz_LED_V.K | riel de arriba GND (línea azul), col. 52 | UTP café | 15 | Cátodo (pata corta, lado plano) |
| 33 | a pieza | luz_LED_R.A | J55 | UTP naranja | 15 | Ánodo (pata larga) del LED rojo, en la tapa |
| 34 | a pieza | luz_LED_R.K | riel de arriba GND (línea azul), col. 56 | UTP café | 15 | Cátodo (pata corta, lado plano) |
| 35 | a pieza | luz_LDR.1 | H58 | UTP blanco/verde | 100 | LDR en su capuchón remoto (junto a la lámpara); cable de 2 hilos con terminal Dupont macho crimpado |
| 36 | a pieza | luz_LDR.2 | E59 | UTP naranja | 100 | Sin polaridad. Va al 3V3 de su propia placa (columna 59) |
| 37 | a pieza | Entrada5V.+ | riel de arriba +5V (línea roja), col. 32 | UTP naranja | 10 | Módulo de entrada USB-C a terminales (5 V de la fuente de la caja) |
| 38 | a pieza | Entrada5V.- | riel de arriba GND (línea azul), col. 32 | UTP café | 10 |  |

## Totales por cable

| Cable | Cantidad | Largo total (cm) |
|---|---|---|
| UTP azul | 2 | 7 |
| UTP blanco/azul | 1 | 2.5 |
| UTP blanco/café | 1 | 2.5 |
| UTP blanco/naranja | 2 | 15 |
| UTP blanco/verde | 2 | 104.5 |
| UTP café | 15 | 101.5 |
| UTP naranja | 11 | 161.5 |
| UTP verde | 4 | 37.5 |
| **Total** | **38** | **432** |
