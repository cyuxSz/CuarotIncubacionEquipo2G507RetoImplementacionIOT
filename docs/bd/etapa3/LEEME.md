# Etapa 3: base de datos, API REST e indicadores

Probado el 13-nov-2026 en MySQL local: el script corre sin errores y se puede repetir, los datos de prueba cargan y las 15 consultas dan resultados.

**Cambios.** 11-nov: cada integrante entrega su propia API REST para su nodo (`servidor/api-rest/`); Luis pasa al nodo `dht` y José María al `pir`. 13-nov: el script del equipo es la versión `Argos_V2` (sin ENUM ni CHECK), con la base renombrada a `argos`; `docs/bd/esquema.sql` queda solo para el servidor integrado con Docker.

## Archivos

| Archivo | Para qué |
|---|---|
| `ScriptCreacionBaseDatos_iot_Equipo2.sql` | Crea la base `argos` con sus 14 tablas y datos fijos. El mismo para todo el equipo |
| `datos_prueba_Equipo2.sql` | Tres días de datos inventados (terminan en el momento en que lo corres). Va después del script |
| `indicadores_<nodo>.sql` | Tres indicadores por nodo |

## Cómo se usa

- **Paquete para el equipo:** `python docs/entregables/etapa3/armar_paquete.py` crea `entregas/paquete_equipo2/` y su `.zip`, con instrucciones (`LEEME.md`) y `preparar_entrega.js`, que arma la carpeta de entrega de cada integrante con su matrícula.
- **Entrega del nodo `dht`:** `docs/entregables/etapa3/generar.py` (carpeta de entrega, PDF de indicadores y documento técnico).
- **API de un nodo:** `servidor/api-rest/LEEME.md`.

## Frecuencia de registro (para el video)

- `dht`: cada 30 s. Es un buen equilibrio entre detectar a tiempo (una alerta se abre en 90 s, con 3 lecturas) y no llenar la BD: son unas 5,800 filas al día. Las mediciones de más de 90 días se purgan solas.
- `luz`: toma una muestra cada 5 s y manda el promedio cada 60 s. La luz cambia poco, y el promedio filtra sombras momentáneas.
- `pir`, `puerta` y `acel`: solo cuando pasa algo (un evento). Además mandan un latido cada 60 s para que se sepa que siguen vivos.
- Actuadores: cada vez que el LED rojo se prende o se apaga, y cuando se silencia el buzzer con el botón. Las acciones del buzzer que ordena una alerta las registra el servidor.
