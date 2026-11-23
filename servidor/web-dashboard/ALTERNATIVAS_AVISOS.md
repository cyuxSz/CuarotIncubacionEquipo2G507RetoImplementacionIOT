# Avisos de Argos: alternativas a la API de WhatsApp de Meta

De: Iván Acosta · 22-nov-2026 · Para decidir en equipo

**Situación.** n8n ya lee los avisos graves del central (`GET /api/notificaciones/pendientes`) y solo falta el canal por el que salen. CallMeBot (WhatsApp gratis) no acepta registros nuevos, y la WhatsApp Cloud API de Meta pide una cuenta de empresa verificada para salir del modo de prueba.

Esto no cambia nada del dashboard ni del central: solo cambia el nodo de envío dentro del flujo de n8n. Los precios, límites y requisitos de cada servicio son de memoria y pueden haber cambiado: **cada opción está marcada `[POR CONFIRMAR]` y hay que revisar su página oficial antes de elegir.**

## Recomendación: Telegram

| | |
|---|---|
| Qué es | Bot de Telegram que escribe en un grupo del equipo y de los encargados |
| Costo | Gratis |
| Verificación | Ninguna: no pide empresa ni número verificado |
| Trabajo | Unos 15 min. El flujo `servidor/n8n/avisos_graves.json` ya trae la rama de Telegram |
| Pasos | Crear el bot con @BotFather (da el token), meterlo a un grupo, sacar el `chat_id` del grupo y llenar el nodo Configuracion de n8n |
| Contra | Los encargados tienen que instalar Telegram y entrar al grupo |

Es la única opción que ya está escrita, que no depende de aprobaciones de terceros y que el propio `PARA_CLAUDE.md` recomienda.

## Si tiene que ser WhatsApp

| Opción | Cómo funciona | Contras | Estado |
|---|---|---|---|
| **Sandbox de WhatsApp de Twilio** | Cuenta de prueba de Twilio; cada destinatario manda un mensaje «join …» al número del sandbox y a partir de ahí recibe avisos. n8n tiene nodo de Twilio | Es un entorno de pruebas: el número es compartido, cada persona debe unirse a mano y la unión caduca a los pocos días si no se renueva; el crédito de prueba se acaba | `[POR CONFIRMAR]` vigencia de la unión, crédito y límites |
| **Meta Cloud API en modo prueba** | Sin verificar la empresa se puede mandar a un máximo de 5 números registrados a mano, con el número de prueba de Meta | Token temporal de 24 h (o uno permanente con usuario del sistema); solo plantillas aprobadas fuera de la ventana de 24 h | `[POR CONFIRMAR]` si el modo prueba sigue permitiendo 5 destinatarios sin verificación |
| **Pasarelas no oficiales** (se conectan a WhatsApp Web con un número propio) | Un servicio o programa mantiene una sesión de WhatsApp Web y n8n le pide mandar mensajes por HTTP | Van contra las condiciones de WhatsApp: el número puede quedar bloqueado. Varias piden instalar software en el servidor, que es justo lo que no se quiere | No recomendada para la entrega |
| **Esperar a CallMeBot** | El flujo `avisos_whatsapp.json` ya está importado | No se sabe cuándo vuelve a aceptar registros | `[POR CONFIRMAR]` revisando su página |

## Otros canales sin verificación

| Opción | Cómo funciona | Contras |
|---|---|---|
| **Correo** | Nodo de correo de n8n (SMTP) a una lista de destinatarios | Menos inmediato que un mensaje; con Gmail hace falta una contraseña de aplicación `[POR CONFIRMAR]` |
| **ntfy** | n8n hace un `POST` a un tema y la app de ntfy en el celular muestra la notificación | En el servicio público, cualquiera que adivine el nombre del tema puede leerlo: usar un nombre largo y aleatorio. Hay que instalar la app `[POR CONFIRMAR]` límites del servicio gratuito |
| **Discord** | Webhook de un canal; n8n hace un `POST` | Solo sirve si los encargados usan Discord |

## Qué propone Iván

1. **Telegram como canal principal**, para tener avisos funcionando hoy y probarlos antes de la Expo.
2. Si el encargado del invernadero pide WhatsApp sí o sí, probar el **sandbox de Twilio** como segundo canal para la demostración, sabiendo que es temporal.
3. No usar pasarelas no oficiales ni instalar nada extra en el servidor.

Recordatorio del `servidor/LEEME.md`: el central crea una notificación por cada canal (telegram y whatsapp). Las de un canal que no se use se quedan pendientes y dejan de salir a las 24 h, sin estorbar. Y el flujo de n8n con valores llenos (tokens, `chat_id`) **no se exporta a git**.
