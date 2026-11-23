"""Prueba P-COM: broker local temporal + simulador + suscriptor. Solo PC."""
import asyncio, json, subprocess, sys, threading, time, os
from amqtt.broker import Broker
import paho.mqtt.client as mqtt
PUERTO = 18830
RAIZ = sys.argv[1]; LOG = sys.argv[2]
cfg = {"listeners": {"default": {"type": "tcp", "bind": f"127.0.0.1:{PUERTO}"}}, "plugins": {"amqtt.plugins.authentication.AnonymousAuthPlugin": {"allow_anonymous": True}}}
NODOS = ("dht", "luz", "pir", "puerta", "acel")
async def _b():
    b = Broker(cfg); await b.start(); await asyncio.sleep(3600)
def broker():
    asyncio.run(_b())
threading.Thread(target=broker, daemon=True).start(); time.sleep(3)
f = open(LOG, "w", encoding="utf-8")
def msg(c, u, m):
    f.write(f"{time.strftime('%H:%M:%S')} {m.topic} {'(ret) ' if m.retain else ''}{m.payload.decode()}\n"); f.flush()
s = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="monitor")
s.on_message = msg; s.connect("127.0.0.1", PUERTO); s.subscribe("invernadero/#", qos=1); s.loop_start()
env = dict(os.environ, MQTT_HOST="127.0.0.1", MQTT_PORT=str(PUERTO), **{f"MQTT_PASSWORD_{n.upper()}": "prueba-" + n for n in NODOS})
p = subprocess.Popen([sys.executable, "-u", os.path.join(RAIZ, "simulador", "simulador_nodos.py"), "--rapido", "--escenario", "calor"],
                     env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
time.sleep(20)
cmd = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="n8n-prueba"); cmd.connect("127.0.0.1", PUERTO)
cmd.publish("invernadero/cmd/alarma", "on"); time.sleep(40)
p.terminate(); out = p.communicate(timeout=10)[0]
f.write("---- salida del simulador ----\n" + out); f.close()
