from sys import argv
from socket import socket
import sqlite3 as sqlite
from gui import run

def create_database(filename: str):
    try:
        with sqlite.connect(filename) as c:
            cursor = c.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS drivers (id INT PRIMARY KEY);""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS charging_points (id INT PRIMARY KEY, x REAL NOT NULL, y REAL NOT NULL, state TEXT NOT NULL);""")
            c.commit()
            print("Base de datos creada o restaurada")
            return cursor

    except sqlite.DatabaseError as e:
        print(e)

def create_server_socket(port: int) -> socket :
    s = socket()
    s.bind(('', PORT))
    s.listen(5)
    print("Escuchando en el puerto " + str(port))
    return s



if len(argv) < 4:
    print("Uso: EV_Central [PUERTO] [IP Broker] [PUERTO Broker]")
    exit(-1)

run()
PORT = int(argv[1])
create_database("database.db")
server = create_server_socket(PORT)
while True:
    connection, addr = server.accept()

    connection.close()
    break