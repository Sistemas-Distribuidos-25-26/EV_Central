from socket import socket
from database import db
import threading
import config

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
                    info = data.decode().split('#')
                    msgtype = info[0]
                    id = info[1]
                    state = info[2]
                    if not db.exists(id) and msgtype == 'A':
                        print(f"[ServerSocket] Alta de nuevo Charging Point {id}")
                        price = info[3]
                        db.add_cp(id, 0, 0, "Nombre", price, state)
                    if msgtype == 'S':
                        paired = info[3]
                        total_charged = info[4]
                        db.set_state(id, state, paired, total_charged)

    except ConnectionError:
        print("[ServerSocket] El cliente ha cortado la conexión")
        connection.close()


def run_server_socket() -> None :
    s = socket()
    s.bind(('', config.PORT))
    s.listen(5)
    print("[ServerSocket] Escuchando en el puerto " + str(config.PORT))
    while True:
        connection, addr = s.accept()
        thread = threading.Thread(target=handle_monitor, args=[connection], daemon=True)
        thread.start()