import time
from kafka_producer import create_ticket

import config
from kafka import KafkaConsumer
from json import loads
from database import db

consumer = None

try:
    print(f"[KafkaConsumer] Intentando conectar con Kafka ({config.BROKER_IP}:{config.BROKER_PORT})...")
    consumer = KafkaConsumer(
        "requests", "orders", "transactions",
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
            topic = message.topic
            data = message.value
            if topic == "requests":
                timestamp = data.get("timestamp")
                driver_id = data.get("driver")
                cp = data.get("cp")
                db.add_request(timestamp, driver_id, cp)
            elif topic == "orders":
                print("SE HA RECIBIDO UNA ORDEN")
                ordertype = data.get("type")
                source = data.get("from")
                destination = data.get("to")
                if ordertype == "stop":
                    cp = db.get_cp(source)
                    paired = cp[6]
                    total_charged = cp[7]
                    price = cp[4]
                    create_ticket(price, total_charged, paired)
                    db.clear_transaction(source)
            elif topic == "transactions":
                print("TRANSACCION RECIBIDA")
                cp = data.get("cp")
                paired = data.get("paired")
                total_charged = data.get("total_charged")
                db.set_transaction(cp, paired, total_charged)
        time.sleep(1)