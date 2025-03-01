import sqlite3
import threading
import logging


class StationDatabaseManager:
    def __init__(self, db_name='stations.db'):
        self.cursor = None
        self.db_name = db_name
        self.connection = None
        self.lock = threading.Lock()
        self.connect_db()
        self.create_station_db()

    def connect_db(self):
        self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
        self.connection.execute('PRAGMA journal_mode=WAL;')
        self.cursor = self.connection.cursor()

    def close_db(self):
        if self.connection:
            self.connection.close()

    def create_station_db(self):
        create_table_command = '''
            CREATE TABLE IF NOT EXISTS stations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL
            );
        '''
        self.execute_command(create_table_command)

    def execute_query(self, query, params=()):
        with self.lock:
            try:
                self.cursor.execute(query, params)
                result = self.cursor.fetchall()
                return result
            except sqlite3.Error as e:
                logging.error(f"Database query error: {e}")
                return []

    def execute_command(self, command, params=()):
        with self.lock:
            try:
                self.cursor.execute(command, params)
                self.connection.commit()
            except sqlite3.Error as e:
                logging.error(f"Database command error: {e}")
                self.connection.rollback()
