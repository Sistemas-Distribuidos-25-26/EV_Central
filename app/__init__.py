from sys import argv
from socket import socket
from database import db
from gui import run
import threading

def handle_monitor(connection):
    while True:
        message = connection.recv(1024).decode()
        if not message:
            print("[ServerSocket] El cliente ha cortado la conexión")
            break
        print(f"[ServerSocket] Recibido: {message}")
        id, state = message.split(',')
        if not db.exists(id):
            print(f"[ServerSocket] Alta de nuevo Charging Point {id}")
            db.add_cp(id, 0, 0, "Nombre", 0, state)

def run_server_socket() -> None :
    s = socket()
    s.bind(('', PORT))
    s.listen(5)
    print("Socket escuchando en el puerto " + str(PORT))
    while True:
        connection, addr = s.accept()
        thread = threading.Thread(target=handle_monitor, args=[connection], daemon=True)
        thread.start()

if len(argv) < 4:
    print("Uso: EV_Central [PUERTO] [IP Broker] [PUERTO Broker]")
    exit(-1)

PORT = int(argv[1])
BROKER_IP = argv[2]
BROKER_PORT = int(argv[3])

socket_thread = threading.Thread(target=run_server_socket, daemon=True)
socket_thread.start()

try:
    db.add_cp("ALC01", 0, 0, "Universidad", 0.34, "ACTIVE")
except:
    pass
finally:
    print(db.get_cps())

run()
