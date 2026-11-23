-- ScriptCreacionBaseDatos_iot_Equipo2.sql. Argos (G507, TC1004B), Etapa 3. Base de datos "argos", 14 tablas.
-- Script unico del Equipo 2 (version Argos_V2). Cada integrante lo ejecuta en su MySQL local (DBeaver: Alt+X).
-- Borra y vuelve a crear la base "argos", asi que se puede ejecutar varias veces.
-- Cambio del 11-nov: Luis Mendoza pasa al nodo dht (id_responsable 1) y Jose Maria Garcia al nodo pir (id_responsable 5).
-- Los datos de prueba van aparte: datos_prueba_Equipo2.sql (se corre despues de este).

DROP DATABASE IF EXISTS argos;
CREATE DATABASE argos;
USE argos;


-- Caja: gabinete físico donde se alojan los nodos
CREATE TABLE Caja (
  id_caja       VARCHAR(10) NOT NULL,
  descripcion   VARCHAR(60) NOT NULL,
  area          VARCHAR(40) NOT NULL DEFAULT 'Cuarto de incubación',
  punto_montaje VARCHAR(40) NULL,
  PRIMARY KEY (id_caja)
);

-- Responsable: integrante del equipo a cargo de uno o más nodos
CREATE TABLE Responsable (
  id_responsable INT NOT NULL AUTO_INCREMENT,
  nombre         VARCHAR(60) NOT NULL UNIQUE,
  PRIMARY KEY (id_responsable)
);

-- Nodo: microcontrolador NodeMCU conectado por MQTT
CREATE TABLE Nodo (
  id_nodo        VARCHAR(10) NOT NULL,
  id_caja        VARCHAR(10) NOT NULL,
  descripcion    VARCHAR(60) NOT NULL,
  id_responsable INT NOT NULL,
  PRIMARY KEY (id_nodo),
  FOREIGN KEY (id_caja) REFERENCES Caja (id_caja),
  FOREIGN KEY (id_responsable) REFERENCES Responsable (id_responsable)
);

-- Sensor: dispositivos conectados a cada nodo
CREATE TABLE Sensor (
  id_sensor INT NOT NULL AUTO_INCREMENT,
  id_nodo   VARCHAR(10) NOT NULL,
  modelo    VARCHAR(40) NOT NULL,
  PRIMARY KEY (id_sensor),
  FOREIGN KEY (id_nodo) REFERENCES Nodo (id_nodo)
);

-- Parametro: catálogo de variables medidas y su unidad
CREATE TABLE Parametro (
  id_parametro INT NOT NULL AUTO_INCREMENT,
  nombre       VARCHAR(30) NOT NULL UNIQUE,
  unidad       VARCHAR(10) NOT NULL,
  PRIMARY KEY (id_parametro)
);

-- Medicion: registro histórico de lecturas de los sensores
CREATE TABLE Medicion (
  id_medicion  INT NOT NULL AUTO_INCREMENT,
  id_sensor    INT NOT NULL,
  id_parametro INT NOT NULL,
  valor        DECIMAL(8,2) NOT NULL,
  fecha_hora   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_medicion),
  FOREIGN KEY (id_sensor) REFERENCES Sensor (id_sensor),
  FOREIGN KEY (id_parametro) REFERENCES Parametro (id_parametro)
);

-- Evento: sucesos puntuales detectados (movimiento, golpes, puerta)
CREATE TABLE Evento (
  id_evento        INT NOT NULL AUTO_INCREMENT,
  id_sensor        INT NOT NULL,
  tipo             VARCHAR(25) NOT NULL,
  magnitud         DECIMAL(8,2) NULL,
  fuera_de_horario BOOLEAN NOT NULL DEFAULT FALSE,
  fecha_hora       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_evento),
  FOREIGN KEY (id_sensor) REFERENCES Sensor (id_sensor)
);

-- Umbral: rangos permitidos por sensor y parámetro
CREATE TABLE Umbral (
  id_umbral     INT NOT NULL AUTO_INCREMENT,
  id_sensor     INT NOT NULL,
  id_parametro  INT NOT NULL,
  minimo        DECIMAL(8,2) NOT NULL,
  maximo        DECIMAL(8,2) NOT NULL,
  histeresis    DECIMAL(8,2) NOT NULL DEFAULT 0,
  persistencia  INT NOT NULL DEFAULT 3,
  activa_buzzer BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (id_umbral),
  UNIQUE (id_sensor, id_parametro),
  FOREIGN KEY (id_sensor) REFERENCES Sensor (id_sensor),
  FOREIGN KEY (id_parametro) REFERENCES Parametro (id_parametro)
);

-- Alerta: incidencias generadas al salir de un umbral o detectar evento
CREATE TABLE Alerta (
  id_alerta INT NOT NULL AUTO_INCREMENT,
  id_nodo   VARCHAR(10) NOT NULL,
  id_umbral INT NULL,
  tipo      VARCHAR(30) NOT NULL,
  valor     DECIMAL(8,2) NULL,
  ts_inicio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ts_fin    DATETIME NULL,
  PRIMARY KEY (id_alerta),
  FOREIGN KEY (id_nodo) REFERENCES Nodo (id_nodo),
  FOREIGN KEY (id_umbral) REFERENCES Umbral (id_umbral)
);

-- Notificacion: envío de alertas por WhatsApp o Telegram
CREATE TABLE Notificacion (
  id_alerta INT NOT NULL,
  canal     VARCHAR(20) NOT NULL,
  enviada   BOOLEAN NOT NULL DEFAULT FALSE,
  ts_envio  DATETIME NULL,
  PRIMARY KEY (id_alerta, canal),
  FOREIGN KEY (id_alerta) REFERENCES Alerta (id_alerta)
);

-- Actuador: componentes de salida (LED rojo y buzzer)
CREATE TABLE Actuador (
  id_actuador INT NOT NULL AUTO_INCREMENT,
  id_nodo     VARCHAR(10) NOT NULL,
  tipo        VARCHAR(20) NOT NULL,
  PRIMARY KEY (id_actuador),
  UNIQUE (id_nodo, tipo),
  FOREIGN KEY (id_nodo) REFERENCES Nodo (id_nodo)
);

-- AccionControl: historial de encendido y apagado de actuadores
CREATE TABLE AccionControl (
  id_accion   INT NOT NULL AUTO_INCREMENT,
  id_actuador INT NOT NULL,
  id_alerta   INT NULL,
  origen      VARCHAR(20) NOT NULL,
  comando     VARCHAR(10) NOT NULL,
  duracion_s  INT NULL,
  fecha_hora  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_accion),
  FOREIGN KEY (id_actuador) REFERENCES Actuador (id_actuador),
  FOREIGN KEY (id_alerta) REFERENCES Alerta (id_alerta)
);

-- EstadoNodo: estado de conexión actual de cada nodo (relación 1:1)
CREATE TABLE EstadoNodo (
  id_nodo        VARCHAR(10) NOT NULL,
  estado         VARCHAR(15) NOT NULL DEFAULT 'offline',
  ultimo_reporte DATETIME NULL,
  reset_reason   VARCHAR(60) NULL,
  uptime_s       INT NULL,
  rssi           INT NULL,
  PRIMARY KEY (id_nodo),
  FOREIGN KEY (id_nodo) REFERENCES Nodo (id_nodo)
);

-- Configuracion: parámetros generales del sistema
CREATE TABLE Configuracion (
  clave VARCHAR(40) NOT NULL,
  valor VARCHAR(60) NOT NULL,
  PRIMARY KEY (clave)
);

-- =====================================================================
-- DATOS INICIALES

INSERT INTO Caja (id_caja, descripcion, area, punto_montaje) VALUES
  ('dht',     'Nodo dht (temperatura y humedad)', 'Cuarto de incubación', 'Por definir'),
  ('entrada', 'Nodos pir y puerta',               'Cuarto de incubación', 'Entrada'),
  ('anaquel', 'Nodos acel y luz',                 'Cuarto de incubación', 'Anaquel');

INSERT INTO Responsable (nombre) VALUES
  ('Luis Mendoza'),
  ('Arianna Téllez'),
  ('Mía Nieto'),
  ('Iván Acosta'),
  ('José María García');

INSERT INTO Nodo (id_nodo, id_caja, descripcion, id_responsable) VALUES
  ('dht',    'dht',     'Temperatura y humedad',    1),
  ('luz',    'anaquel', 'Luz / fotoperiodo',        2),
  ('pir',    'entrada', 'Movimiento / accesos',     5),
  ('puerta', 'entrada', 'Puerta abierta o cerrada', 4),
  ('acel',   'anaquel', 'Golpes / vibración',       3);

INSERT INTO Sensor (id_nodo, modelo) VALUES
  ('dht',    'DHT22'),
  ('luz',    'Fotorresistencia'),
  ('pir',    'HC-SR501'),
  ('puerta', 'MC-38'),
  ('acel',   'GY-61 (ADXL335) + ADS1115');

INSERT INTO Parametro (nombre, unidad) VALUES
  ('temperatura', '°C'),
  ('humedad',     '%'),
  ('luz',         'ADC');

INSERT INTO Actuador (id_nodo, tipo) VALUES
  ('dht',    'led_rojo'),
  ('dht',    'buzzer'),
  ('luz',    'led_rojo'),
  ('pir',    'led_rojo'),
  ('puerta', 'led_rojo'),
  ('acel',   'led_rojo');

INSERT INTO EstadoNodo (id_nodo) VALUES
  ('dht'), ('luz'), ('pir'), ('puerta'), ('acel');

INSERT INTO Umbral (id_sensor, id_parametro, minimo, maximo, histeresis, persistencia, activa_buzzer) VALUES
  (1, 1, 22.00, 28.00, 0.50, 3, TRUE),
  (1, 2, 40.00, 60.00, 2.00, 3, TRUE);

INSERT INTO Configuracion (clave, valor) VALUES
  ('horario_lamparas_inicio', '06:00'),
  ('horario_lamparas_fin',    '22:00'),
  ('horario_acceso_inicio',   '08:00'),
  ('horario_acceso_fin',      '18:00'),
  ('umbral_golpe',            '1.50'),
  ('umbral_luz',              '300'),
  ('puerta_max_abierta_s',    '120');