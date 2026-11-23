-- Argos: esquema MySQL 8 (InnoDB, UTC). 14 tablas. Version 3 (11-nov-2026).
-- Une el esquema de la Etapa 2 v2 (docs/bd/etapa2_software_v2.md) con la revision de Jose Maria Garcia
-- (indices de consulta, nombres de llaves, ON DELETE CASCADE). Script de entrega: docs/bd/etapa3/.
-- Todas las fechas y horas se guardan en UTC (Monterrey = UTC-6).

SET time_zone = '+00:00';
CREATE DATABASE IF NOT EXISTS argos CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE argos;

-- ---------------------------------------------------------------------
-- Caja: gabinete impreso con su fuente de 5 V (dht, entrada, anaquel)
-- ---------------------------------------------------------------------
CREATE TABLE Caja (
  id_caja        VARCHAR(10)  NOT NULL,
  descripcion    VARCHAR(60)  NOT NULL,
  area           VARCHAR(40)  NOT NULL DEFAULT 'Cuarto de incubación',
  punto_montaje  VARCHAR(40)  NULL,
  PRIMARY KEY (id_caja)
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- Responsable: integrante del equipo que atiende uno o mas nodos
-- ---------------------------------------------------------------------
CREATE TABLE Responsable (
  id_responsable INT          NOT NULL AUTO_INCREMENT,
  nombre         VARCHAR(60)  NOT NULL,
  PRIMARY KEY (id_responsable),
  UNIQUE KEY uq_responsable_nombre (nombre)
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- Nodo: cada NodeMCU (dispositivo IoT). El id es el mismo del topic MQTT
-- y el que usa cada API REST para identificar de donde viene el dato.
-- ---------------------------------------------------------------------
CREATE TABLE Nodo (
  id_nodo        VARCHAR(10)  NOT NULL,
  id_caja        VARCHAR(10)  NOT NULL,
  descripcion    VARCHAR(60)  NOT NULL,
  id_responsable INT          NOT NULL,
  PRIMARY KEY (id_nodo),
  CONSTRAINT fk_nodo_caja        FOREIGN KEY (id_caja) REFERENCES Caja (id_caja),
  CONSTRAINT fk_nodo_responsable FOREIGN KEY (id_responsable) REFERENCES Responsable (id_responsable)
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- Sensor: el sensor fisico conectado a un nodo
-- ---------------------------------------------------------------------
CREATE TABLE Sensor (
  id_sensor      INT          NOT NULL AUTO_INCREMENT,
  id_nodo        VARCHAR(10)  NOT NULL,
  modelo         VARCHAR(40)  NOT NULL,
  PRIMARY KEY (id_sensor),
  CONSTRAINT fk_sensor_nodo FOREIGN KEY (id_nodo) REFERENCES Nodo (id_nodo)
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- Parametro: catalogo de magnitudes con su unidad (temperatura, humedad, luz)
-- ---------------------------------------------------------------------
CREATE TABLE Parametro (
  id_parametro   INT          NOT NULL AUTO_INCREMENT,
  nombre         VARCHAR(30)  NOT NULL,
  unidad         VARCHAR(10)  NOT NULL,
  PRIMARY KEY (id_parametro),
  UNIQUE KEY uq_parametro_nombre (nombre)
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- Medicion: una fila por lectura. Un mismo sensor puede medir varios
-- parametros (el DHT22 mide temperatura y humedad), por eso la medicion
-- apunta al sensor Y al parametro. Se purga a los 90 dias (RNF03).
-- ---------------------------------------------------------------------
CREATE TABLE Medicion (
  id_medicion    BIGINT       NOT NULL AUTO_INCREMENT,
  id_sensor      INT          NOT NULL,
  id_parametro   INT          NOT NULL,
  valor          DECIMAL(8,2) NOT NULL,
  fecha_hora     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_medicion),
  KEY idx_medicion_consulta (id_sensor, id_parametro, fecha_hora),  -- historial de un sensor
  KEY idx_medicion_fecha (fecha_hora),                              -- purga
  CONSTRAINT fk_medicion_sensor    FOREIGN KEY (id_sensor) REFERENCES Sensor (id_sensor),
  CONSTRAINT fk_medicion_parametro FOREIGN KEY (id_parametro) REFERENCES Parametro (id_parametro)
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- Evento: sucesos puntuales (no son valores continuos)
-- ---------------------------------------------------------------------
CREATE TABLE Evento (
  id_evento        BIGINT       NOT NULL AUTO_INCREMENT,
  id_sensor        INT          NOT NULL,
  tipo             ENUM('movimiento','golpe','puerta_abierta','puerta_cerrada','sensor_error') NOT NULL,
  magnitud         DECIMAL(8,2) NULL,                    -- solo golpe (g)
  fuera_de_horario BOOLEAN      NOT NULL DEFAULT FALSE,
  fecha_hora       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_evento),
  KEY idx_evento_consulta (id_sensor, fecha_hora),
  KEY idx_evento_tipo_fecha (tipo, fecha_hora),
  CONSTRAINT fk_evento_sensor FOREIGN KEY (id_sensor) REFERENCES Sensor (id_sensor)
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- Umbral: el rango permitido de UN parametro de UN sensor.
--
-- Por que un sensor puede tener varios umbrales: porque un sensor puede medir
-- varios parametros y cada uno tiene su propio rango. El DHT22 tiene dos filas:
-- temperatura (22 a 28 C) y humedad (40 a 60 %). La llave unica
-- (id_sensor, id_parametro) impide que haya mas de un umbral por parametro.
--
-- minimo y maximo van en la MISMA fila (no son dos umbrales).
-- histeresis: margen para CERRAR la alerta. Se abre al pasar de 28 C, pero se
--   cierra hasta bajar de 27.5 C (28 - 0.5). Sin ese margen, una lectura que
--   oscila entre 27.9 y 28.1 abriria y cerraria alertas sin parar.
-- persistencia: lecturas seguidas fuera de rango para ABRIR la alerta (3), para
--   que una sola lectura mala no dispare el aviso.
-- ---------------------------------------------------------------------
CREATE TABLE Umbral (
  id_umbral      INT              NOT NULL AUTO_INCREMENT,
  id_sensor      INT              NOT NULL,
  id_parametro   INT              NOT NULL,
  minimo         DECIMAL(8,2)     NOT NULL,
  maximo         DECIMAL(8,2)     NOT NULL,
  histeresis     DECIMAL(8,2)     NOT NULL DEFAULT 0,
  persistencia   TINYINT UNSIGNED NOT NULL DEFAULT 3,
  activa_buzzer  BOOLEAN          NOT NULL DEFAULT FALSE,
  PRIMARY KEY (id_umbral),
  UNIQUE KEY uq_umbral_sensor_parametro (id_sensor, id_parametro),
  CONSTRAINT ck_umbral_rango CHECK (maximo > minimo),
  CONSTRAINT fk_umbral_sensor    FOREIGN KEY (id_sensor) REFERENCES Sensor (id_sensor),
  CONSTRAINT fk_umbral_parametro FOREIGN KEY (id_parametro) REFERENCES Parametro (id_parametro)
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- Alerta: episodio con inicio y fin (activa mientras ts_fin sea NULL).
-- activa_clave + UNIQUE implementa RN5: no puede haber dos alertas activas
-- del mismo nodo y tipo (los NULL no chocan en el UNIQUE).
-- tipo: temperatura, humedad, luz, golpe, puerta_abierta,
--       movimiento_fuera_de_horario, nodo_sin_reporte, sensor_falla
-- ---------------------------------------------------------------------
CREATE TABLE Alerta (
  id_alerta      BIGINT       NOT NULL AUTO_INCREMENT,
  id_nodo        VARCHAR(10)  NOT NULL,
  id_umbral      INT          NULL,           -- solo las alertas que salen de un umbral (T y HR)
  tipo           VARCHAR(30)  NOT NULL,
  valor          DECIMAL(8,2) NULL,
  ts_inicio      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ts_fin         DATETIME     NULL,
  activa_clave   TINYINT      GENERATED ALWAYS AS (IF(ts_fin IS NULL, 1, NULL)) STORED,
  PRIMARY KEY (id_alerta),
  UNIQUE KEY uq_alerta_activa (id_nodo, tipo, activa_clave),
  KEY idx_alerta_nodo_inicio (id_nodo, ts_inicio),
  CONSTRAINT ck_alerta_fechas CHECK (ts_fin IS NULL OR ts_fin >= ts_inicio),
  CONSTRAINT fk_alerta_nodo   FOREIGN KEY (id_nodo) REFERENCES Nodo (id_nodo),
  CONSTRAINT fk_alerta_umbral FOREIGN KEY (id_umbral) REFERENCES Umbral (id_umbral)
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- Notificacion: aviso de una alerta por un canal
-- ---------------------------------------------------------------------
CREATE TABLE Notificacion (
  id_alerta      BIGINT       NOT NULL,
  canal          ENUM('whatsapp','telegram') NOT NULL,
  enviada        BOOLEAN      NOT NULL DEFAULT FALSE,
  ts_envio       DATETIME     NULL,
  PRIMARY KEY (id_alerta, canal),
  CONSTRAINT fk_notificacion_alerta FOREIGN KEY (id_alerta) REFERENCES Alerta (id_alerta) ON DELETE CASCADE
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- Actuador: LED rojo de cada nodo y buzzer del nodo dht
-- ---------------------------------------------------------------------
CREATE TABLE Actuador (
  id_actuador    INT          NOT NULL AUTO_INCREMENT,
  id_nodo        VARCHAR(10)  NOT NULL,
  tipo           ENUM('buzzer','led_rojo') NOT NULL,
  PRIMARY KEY (id_actuador),
  UNIQUE KEY uq_actuador_nodo_tipo (id_nodo, tipo),
  CONSTRAINT fk_actuador_nodo FOREIGN KEY (id_nodo) REFERENCES Nodo (id_nodo)
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- AccionControl: evento de actuacion (cada vez que un actuador se prende o apaga).
-- origen: alerta (lo ordeno una alerta), local (lo decidio el nodo), manual (boton).
-- id_alerta no usa ON DELETE SET NULL porque MySQL no permite acciones
-- referenciales sobre columnas usadas en un CHECK.
-- ---------------------------------------------------------------------
CREATE TABLE AccionControl (
  id_accion      BIGINT            NOT NULL AUTO_INCREMENT,
  id_actuador    INT               NOT NULL,
  id_alerta      BIGINT            NULL,
  origen         ENUM('alerta','local','manual') NOT NULL,
  comando        ENUM('on','off')  NOT NULL,
  duracion_s     SMALLINT UNSIGNED NULL,       -- encendidos de duracion fija (LED 5 s); NULL = hasta un off
  fecha_hora     DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_accion),
  KEY idx_accion_actuador_fecha (id_actuador, fecha_hora),
  CONSTRAINT ck_accion_origen CHECK ((origen = 'alerta') = (id_alerta IS NOT NULL)),
  CONSTRAINT fk_accion_actuador FOREIGN KEY (id_actuador) REFERENCES Actuador (id_actuador),
  CONSTRAINT fk_accion_alerta   FOREIGN KEY (id_alerta) REFERENCES Alerta (id_alerta)
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- EstadoNodo: relacion 1:1 con Nodo (se actualiza en cada reporte)
-- ---------------------------------------------------------------------
CREATE TABLE EstadoNodo (
  id_nodo        VARCHAR(10)  NOT NULL,
  estado         ENUM('online','offline') NOT NULL DEFAULT 'offline',
  ultimo_reporte DATETIME     NULL,
  reset_reason   VARCHAR(60)  NULL,
  uptime_s       INT UNSIGNED NULL,
  rssi           SMALLINT     NULL,
  PRIMARY KEY (id_nodo),
  CONSTRAINT fk_estadonodo_nodo FOREIGN KEY (id_nodo) REFERENCES Nodo (id_nodo) ON DELETE CASCADE
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- Configuracion: pares clave-valor (no se relaciona con otras tablas)
-- ---------------------------------------------------------------------
CREATE TABLE Configuracion (
  clave          VARCHAR(40)  NOT NULL,
  valor          VARCHAR(60)  NOT NULL,
  PRIMARY KEY (clave)
) ENGINE = InnoDB;

-- RNF03: purga diaria de mediciones con mas de 90 dias (requiere event_scheduler = ON)
CREATE EVENT IF NOT EXISTS purga_mediciones
  ON SCHEDULE EVERY 1 DAY
  DO DELETE FROM Medicion WHERE fecha_hora < UTC_TIMESTAMP() - INTERVAL 90 DAY;

-- ── datos fijos del cuarto ─────────────────────────────────────────────────
INSERT INTO Caja (id_caja, descripcion, area, punto_montaje) VALUES
  ('dht',     'Nodo de temperatura y humedad (caja propia)', 'Cuarto de incubación', 'Anaquel, a la altura de los frascos'),
  ('entrada', 'Estación de entrada: pir + puerta',           'Cuarto de incubación', 'Pared junto a la puerta'),
  ('anaquel', 'Estación del anaquel: acel + luz',            'Cuarto de incubación', 'Anaquel');

INSERT INTO Responsable (nombre) VALUES
  ('Luis Mendoza'), ('Arianna Téllez'), ('José María García'), ('Iván Acosta'), ('Mía Nieto');

-- Reparto de la Etapa 3 (11-nov): cada integrante desarrolla el circuito y la API REST de su nodo.
INSERT INTO Nodo (id_nodo, id_caja, descripcion, id_responsable) VALUES
  ('dht',    'dht',     'Temperatura y humedad',    (SELECT id_responsable FROM Responsable WHERE nombre = 'Luis Mendoza')),
  ('luz',    'anaquel', 'Luz / fotoperiodo',        (SELECT id_responsable FROM Responsable WHERE nombre = 'Arianna Téllez')),
  ('pir',    'entrada', 'Movimiento / accesos',     (SELECT id_responsable FROM Responsable WHERE nombre = 'José María García')),
  ('puerta', 'entrada', 'Puerta abierta o cerrada', (SELECT id_responsable FROM Responsable WHERE nombre = 'Iván Acosta')),
  ('acel',   'anaquel', 'Golpes / vibración',       (SELECT id_responsable FROM Responsable WHERE nombre = 'Mía Nieto'));

INSERT INTO Sensor (id_nodo, modelo) VALUES
  ('dht', 'DHT22'), ('luz', 'LDR (modelo POR CONFIRMAR)'), ('pir', 'HC-SR501'),
  ('puerta', 'Reed MC-38'), ('acel', 'GY-61 (ADXL335) + ADS1115');

INSERT INTO Parametro (nombre, unidad) VALUES ('temperatura', 'C'), ('humedad', '%'), ('luz', 'adc');

-- Umbrales del DHT22: uno por parametro (22-28 C y 40-60 % HR), 3 lecturas seguidas, con histeresis.
INSERT INTO Umbral (id_sensor, id_parametro, minimo, maximo, histeresis, persistencia, activa_buzzer) VALUES
  ((SELECT id_sensor FROM Sensor WHERE id_nodo = 'dht'), (SELECT id_parametro FROM Parametro WHERE nombre = 'temperatura'), 22, 28, 0.5, 3, TRUE),
  ((SELECT id_sensor FROM Sensor WHERE id_nodo = 'dht'), (SELECT id_parametro FROM Parametro WHERE nombre = 'humedad'),     40, 60, 2.0, 3, TRUE);

INSERT INTO Actuador (id_nodo, tipo) VALUES
  ('dht', 'buzzer'), ('dht', 'led_rojo'), ('luz', 'led_rojo'), ('pir', 'led_rojo'),
  ('puerta', 'led_rojo'), ('acel', 'led_rojo');

INSERT INTO EstadoNodo (id_nodo) VALUES ('dht'), ('luz'), ('pir'), ('puerta'), ('acel');

INSERT INTO Configuracion (clave, valor) VALUES
  ('horario_lamparas', 'POR CONFIRMAR'),   -- fotoperiodo: lo definen los encargados
  ('horario_acceso_inicio', '08:00'),      -- acceso al cuarto: L-V 8:00-17:00 (hora de Monterrey)
  ('horario_acceso_fin', '17:00'),
  ('umbral_golpe_g', '0.5'),               -- igual que el firmware; calibrar en sitio
  ('umbral_luz_adc', '300'),               -- igual que el firmware; calibrar con docs/prueba_ldr.md
  ('puerta_abierta_max_s', '120'),
  ('retencion_mediciones_dias', '90');
