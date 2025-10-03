import sqlite3

class Database:

    def __init__(self, file: str):
        self.file = file
        try:
            with sqlite3.connect(self.file) as c:
                cursor = c.cursor()
                cursor.execute("""CREATE TABLE IF NOT EXISTS drivers (id INT PRIMARY KEY);""")
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS charging_points (id INT PRIMARY KEY, x REAL NOT NULL, y REAL NOT NULL, state TEXT NOT NULL);""")
                c.commit()
                print("Base de datos creada o restaurada")
                self.cursor = cursor

        except sqlite3.DatabaseError as e:
            self.cursor = None
            print(e)