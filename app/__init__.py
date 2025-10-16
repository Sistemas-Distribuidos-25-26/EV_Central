from sys import argv
from socket import socket
from database import db
from gui import run
import threading

STX = b'\x02'
ETX = b'\x03'
EOT = b'\x04'
ENQ = b'\x05'
ACK = b'\x06'
NACK = b'\x15'

def calculate_lrc(data):
    lrc = 0
    for byte in data:
        lrc ^= byte
    return bytes([lrc])


def handle_monitor(connection):
    try:
        while True:
            enquiry = connection.recv(1)
            connection.send(ACK if enquiry == ENQ else NACK)
            while True:
                message = connection.recv(1024)
                if not message or message == EOT:
                    print("[ServerSocket] El cliente ha cortado la conexión")
                    return
                if message[0:1] != STX or ETX not in message:
                    connection.send(NACK)
                    break

                end = message.index(ETX)
                data = message[1:end]
                lrc = message[end+1:end+2]
                if lrc != calculate_lrc(data):
                    connection.send(NACK)
                else:
                    connection.send(ACK)
                    print(f"[ServerSocket] Recibido: {data.decode()}")
                    id, state = data.decode().split(',')
                    if not db.exists(id):
                        print(f"[ServerSocket] Alta de nuevo Charging Point {id}")
                        db.add_cp(id, 0, 0, "Nombre", 0, state)
    except ConnectionError:
        print("[ServerSocket] El cliente ha cortado la conexión")
        connection.close()


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
