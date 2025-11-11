from sys import argv
import config

if len(argv) < 4:
    print("Uso: EV_Central [PUERTO] [IP Broker] [PUERTO Broker]")
    exit(-1)

config.PORT = int(argv[1])
config.BROKER_IP = argv[2]
config.BROKER_PORT = int(argv[3])

from kafka_consumer import receive_requests, setup_consumer
from kafka_producer import resolve_requests, setup_producer
from database import db
import threading
from serversocket import run_server_socket
from api import run_api

socket_thread = threading.Thread(target=run_server_socket, daemon=True)
socket_thread.start()

requests_thread = threading.Thread(target=receive_requests, daemon=True)
requests_thread.start()

orders_thread = threading.Thread(target=resolve_requests, daemon=True)
orders_thread.start()

run_api()
