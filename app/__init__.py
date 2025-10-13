from sys import argv
from socket import socket
from database import Database
from gui import run
import threading

def run_server_socket() -> None :
    s = socket()
    s.bind(('', PORT))
    s.listen(5)
    print("Socket escuchando en el puerto " + str(PORT))
    while True:
        connection, addr = s.accept()

        state = connection.recv()

        connection.close()
        break

if len(argv) < 4:
    print("Uso: EV_Central [PUERTO] [IP Broker] [PUERTO Broker]")
    exit(-1)

PORT = int(argv[1])
BROKER_IP = argv[2]
BROKER_PORT = int(argv[3])

socket_thread = threading.Thread(target=run_server_socket)
socket_thread.daemon = True
socket_thread.start()

gui_thread = threading.Thread(target=run)
gui_thread.daemon = True
gui_thread.start()


db = Database("database.db")
db.add_cp("ALC01", 0, 0, "Universidad", 0.34, "ACTIVE")
print(db.get_cps())
