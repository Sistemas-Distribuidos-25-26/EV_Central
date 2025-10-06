from sys import argv
from socket import socket
from database import Database
from gui import run
import threading

def run_server_socket() -> None :
    s = socket()
    s.bind(('', PORT))
    s.listen(5)
    print("Escuchando en el puerto " + str(PORT))
    while True:
        connection, addr = s.accept()

        connection.close()
        break

if len(argv) < 4:
    print("Uso: EV_Central [PUERTO] [IP Broker] [PUERTO Broker]")
    exit(-1)

PORT = int(argv[1])

socket_thread = threading.Thread(target=run_server_socket)
socket_thread.daemon = True
socket_thread.start()

db = Database("database.db")
run()