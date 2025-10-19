from sys import argv
import config
from kafka_consumer import receive_requests
from database import db
from gui import run
import threading
from serversocket import run_server_socket

if len(argv) < 4:
    print("Uso: EV_Central [PUERTO] [IP Broker] [PUERTO Broker]")
    exit(-1)

config.PORT = int(argv[1])
config.BROKER_IP = argv[2]
config.BROKER_PORT = int(argv[3])

socket_thread = threading.Thread(target=run_server_socket, daemon=True)
socket_thread.start()

requests_thread = threading.Thread(target=receive_requests, daemon=True)
requests_thread.start()

run()
