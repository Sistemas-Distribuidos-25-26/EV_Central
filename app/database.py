import sqlite3

CREATE_TABLE_CP = """
    CREATE TABLE IF NOT EXISTS charging_points (
        id VARCHAR(5) PRIMARY KEY,
        x REAL NOT NULL,
        y REAL NOT NULL,
        name VARCHAR(32) NOT NULL,
        price REAL,
        state VARCHAR(12) NOT NULL
    );
"""


class Database:

    def __init__(self, file: str):
        self.file = file
        try:
            with sqlite3.connect(self.file, check_same_thread=False) as c:
                self.c = c
                cursor = c.cursor()
                cursor.execute("""CREATE TABLE IF NOT EXISTS drivers (id INT PRIMARY KEY);""")
                cursor.execute(CREATE_TABLE_CP)
                c.commit()
                print("[DB] Base de datos creada o restaurada")
                self.cursor = cursor

        except sqlite3.DatabaseError as e:
            self.cursor = None
            print(e)

    def add_cp(self, id: str, x: float, y: float, name: str, price: float, state: str) -> None:
        if self.cursor is None: return
        self.cursor.execute(f"INSERT INTO charging_points (id,x,y,name,price,state) VALUES ('{id}',{x},{y},'{name}',{price},'{state}');") 
        self.c.commit()
        print(f"[DB] Añadido un nuevo CP ({id}, {x}, {y}, {name}, {price}, {state})")

    def get_cps(self) -> list:
        if self.cursor is None: return
        self.cursor.execute("SELECT * FROM charging_points")
        rows = self.cursor.fetchall()
        return rows
    
    def set_state(self, id: str, state: str) -> None:
        if self.cursor is None: return

    def exists(self, id: str) -> bool:
        if self.cursor is None: return False
        self.cursor.execute(f"SELECT * FROM charging_points WHERE id='{id}'")
        rows = self.cursor.fetchall()
        return False if not rows else True

db = Database("database.db")