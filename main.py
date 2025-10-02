from sys import argv
from socket import socket

ARG_NUMBER = 0

if len(argv) < ARG_NUMBER:
    print("Uso: EV_Central [PUERTO] [IP Broker] [PUERTO Broker]")
    exit(-1)

PORT = int(argv[1])

def create_server_socket(port: int) -> socket :
    s = socket()
    s.bind(('', PORT))
    s.listen(5)
    print("Escuchando en el puerto " + str(port))
    return s


server = create_server_socket(PORT)
while True:
    connection, addr = server.accept()

    connection.close()
    break