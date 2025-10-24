import time
from kafka import KafkaProducer
from database import db
import json

producer = None
try:
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
except:
    producer = None


def create_ticket(price: float, total_charged: float, paired: str):
    total_price = price * total_charged
    ticket = f"-----TICKET-----\nPrecio: {price}€/kWh\nConsumición: {total_charged}kWh\nTOTAL: {total_price:.2f}€\n-----------------"
    if producer is None: return
    producer.send("tickets", ticket)
    producer.flush()
    producer.send("notifications", {
        "type": "completed",
        "target": "",
        "destination": paired
    })
    producer.flush()

def send_notification(notiftype, target, dest):
    global producer
    producer.send("notifications", {
        "type": notiftype,
        "target": target,
        "destination": dest
    })
    producer.flush()

def resolve_requests():
    global producer

    while True:
        if not producer:
            time.sleep(5)
            continue

        requests = db.get_requests()
        if not requests:
            time.sleep(5)
            continue
        for req in requests:
            target = req[2]
            print(f"[KafkaProducer] Resolviendo request ({target},{req[1]})")
            if not db.exists(target):
                send_notification("unknown-cp",target,req[1])
                db.delete_request(req[0],req[1],req[2])
                continue
            cp = db.get_cp(target)
            state = cp[5]
            if state == "SUMINISTRANDO":
                send_notification("in-use",target,req[1])
                db.delete_request(req[0], req[1], req[2])
                continue
            if state == "FUERA DE SERVICIO":
                send_notification("out-of-order", target,req[1])
                db.delete_request(req[0], req[1], req[2])
                continue
            if state == "K.O.":
                send_notification("broken", target, req[1])
                db.delete_request(req[0], req[1], req[2])
                continue
            if state == "DESCONECTADO":
                send_notification("unavailable", target, req[1])
                db.delete_request(req[0], req[1], req[2])
                continue
            producer.send("orders", {
                "type": "prepare",
                "from": target,
                "to": req[1]
            })
            producer.flush()
            db.delete_request(req[0], req[1], req[2])
        time.sleep(1)
