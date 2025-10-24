import sqlite3
from threading import Lock

db_lock = Lock()

CREATE_TABLE_CP = """
    CREATE TABLE IF NOT EXISTS charging_points (
        id VARCHAR(5) PRIMARY KEY,
        x REAL NOT NULL,
        y REAL NOT NULL,
        name VARCHAR(32) NOT NULL,
        price REAL,
        state VARCHAR(12) NOT NULL,
        paired VARCHAR(8),
        total_charged REAL
    );
"""

CREATE_TABLE_REQUESTS = """
    CREATE TABLE IF NOT EXISTS requests (
        start_date DATETIME NOT NULL,
        driver_id  VARCHAR(5) NOT NULL,
        cp      VARCHAR(5) NOT NULL,
        PRIMARY KEY (start_date, driver_id, cp)
    );
"""


class Database:

    def __init__(self, file: str):
        self.file = file
        try:
            with sqlite3.connect(self.file, check_same_thread=False) as c:
                self.c = c
                cursor = c.cursor()
                cursor.execute(CREATE_TABLE_CP)
                cursor.execute(CREATE_TABLE_REQUESTS)
                c.commit()
                print("[DB] Base de datos creada o restaurada")
                self.cursor = cursor

        except sqlite3.DatabaseError as e:
            self.cursor = None
            print(e)

    def add_cp(self, id: str, x: float, y: float, name: str, price: float, state: str) -> None:
        with db_lock:
            if self.cursor is None: return
            try:
                self.cursor.execute(f"INSERT INTO charging_points (id,x,y,name,price,state) VALUES ('{id}',{x},{y},'{name}',{price},'{state}');")
                self.c.commit()
                print(f"[DB] Añadido un nuevo CP ({id}, {x}, {y}, {name}, {price}, {state})")
            except:
                return

    def get_cps(self) -> list:
        with db_lock:
            if self.cursor is None: return []
            self.cursor.execute("SELECT * FROM charging_points")
            rows = self.cursor.fetchall()
            return rows

    def get_cp(self, cp_id: str):
        with db_lock:
            if self.cursor is None: return None
            self.cursor.execute(f"SELECT * FROM charging_points WHERE id='{cp_id}'")
            rows = self.cursor.fetchall()
            return rows[0]
    
    def set_state(self, id: str, state: str) -> None:
        with db_lock:
            if self.cursor is None: return
            self.cursor.execute(f"UPDATE charging_points SET state='{state}' WHERE id='{id}'")

    def set_transaction(self, id: str, paired: str, total_charged: float):
        with db_lock:
            if self.cursor is None: return
            self.cursor.execute(f"UPDATE charging_points SET paired='{paired}', total_charged={total_charged} WHERE id='{id}'")

    def clear_transaction(self, id: str):
        with db_lock:
            if self.cursor is None: return
            self.cursor.execute(f"UPDATE charging_points SET paired=NULL, total_charged=NULL WHERE id='{id}'")

    def disconnect_all(self):
        with db_lock:
            if self.cursor is None: return
            self.cursor.execute(f"UPDATE charging_points SET state='DESCONECTADO'")

    def exists(self, id: str) -> bool:
        with db_lock:
            if self.cursor is None: return False
            self.cursor.execute(f"SELECT * FROM charging_points WHERE id='{id}'")
            rows = self.cursor.fetchall()
            return False if not rows else True

    def add_request(self, start_datetime: str, driver_id: str, cp: str):
        with db_lock:
            if self.cursor is None: return
            try:
                self.cursor.execute(f"INSERT INTO requests (start_date, driver_id, cp) VALUES ('{start_datetime}','{driver_id}', '{cp}');")
                self.c.commit()
                print(f"[DB] Añadida nueva request ({start_datetime},{driver_id},{cp})")
            except:
                return

    def get_requests(self) -> list:
        with db_lock:
            if self.cursor is None: return
            self.cursor.execute("SELECT * FROM requests")
            rows = self.cursor.fetchall()
            return rows

    def delete_request(self, timestamp, driver, cp):
        with db_lock:
            if self.cursor is None: return
            try:
                self.cursor.execute(f"DELETE FROM requests WHERE start_date='{timestamp}' AND driver_id='{driver}' AND cp='{cp}';")
                self.c.commit()
                print(f"[DB] Eliminada la request ({timestamp},{driver},{cp})")
            except Exception as e:
                print(e)
                return

db = Database("database.db")
db.disconnect_all()