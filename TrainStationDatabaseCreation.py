import sqlite3

class StationDatabaseManager:
    def __init__(self, db_name='stations.db'):
        self.db_name = db_name
        self.create_station_db()

    def create_station_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stations (
            id INTEGER PRIMARY KEY,
            name TEXT,
            latitude REAL,
            longitude REAL);
        ''')

        conn.commit()
        conn.close()

    def execute_query(self, query, params=()):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        return result

    def execute_command(self, command, params=()):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(command, params)
        conn.commit()
        conn.close()
