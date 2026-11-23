// Plantilla sin valores. Copiar a secrets.h (no versionado) y llenar ahi.
#pragma once

#define WIFI_SSID ""
#define WIFI_PASSWORD ""
#define MQTT_HOST ""   // broker del curso: "broker.hivemq.com" (puerto 1883, sin contrasena)
#define MQTT_PORT 1883
#define MQTT_PASSWORD ""
// API REST de ESTE nodo (servidor/LEEME.md), sin http:// ni https://
//  - Por el tunel de Cloudflare: API_HOST = "xxxx.trycloudflare.com" (el tunel de ESTE nodo), API_PORT = 443 (HTTPS)
//  - En la misma red que el servidor: API_HOST = IP del servidor, API_PORT segun el nodo:
//    dht 3001, luz 3002, pir 3003, puerta 3004, acel 3005
#define API_HOST ""
#define API_PORT 3001
#define API_KEY ""
