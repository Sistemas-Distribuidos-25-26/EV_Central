import time

from more_itertools.more import consumer

import config
from kafka import KafkaConsumer
from json import loads
from database import db

consumer = None

try:
    print(f"[KafkaConsumer] Intentando conectar con Kafka ({config.BROKER_IP}:{config.BROKER_PORT})...")
    consumer = KafkaConsumer(
        'requests',
        bootstrap_servers=[f"{config.BROKER_IP}:{config.BROKER_PORT}"],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda m: loads(m.decode('utf-8'))
    )
    print("[KafkaConsumer] Conectado a Kafka")
except:
    print("[KafkaConsumer] Error al conectar con Kafka")

def receive_requests():
    while True:
        if not consumer:
            print("[KafkaConsumer] Error al conectar con Kafka")
            time.sleep(5)
            continue
        for message in consumer:
            print("[KafkaConsumer] Nueva request")
            data = message.value
            timestamp = data.get("timestamp")
            driver_id = data.get("driver")
            cp = data.get("cp")
            db.add_request(timestamp, driver_id, cp)
        time.sleep(1)