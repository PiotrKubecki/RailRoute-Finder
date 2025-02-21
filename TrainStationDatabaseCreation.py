import sqlite3
import threading
import logging

class StationDatabaseManager:
    """Class to manage SQLite database interactions for station data."""

    def __init__(self, db_name='stations.db'):
        self.db_name = db_name
        self.connection = None
        self.lock = threading.Lock()
        self.connect_db()
        self.create_station_db()

    def connect_db(self):
        """Establishes a connection to the SQLite database."""
        self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
        self.connection.execute('PRAGMA journal_mode=WAL;')  # Improves concurrency
        self.cursor = self.connection.cursor()

    def close_db(self):
        """Closes the connection to the SQLite database."""
        if self.connection:
            self.connection.close()

    def create_station_db(self):
        """Creates the stations table if it doesn't exist."""
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
        """Executes a SELECT query and returns the results."""
        with self.lock:
            try:
                self.cursor.execute(query, params)
                result = self.cursor.fetchall()
                return result
            except sqlite3.Error as e:
                logging.error(f"Database query error: {e}")
                return []

    def execute_command(self, command, params=()):
        """Executes an INSERT, UPDATE, or DELETE command."""
        with self.lock:
            try:
                self.cursor.execute(command, params)
                self.connection.commit()
            except sqlite3.Error as e:
                logging.error(f"Database command error: {e}")
                self.connection.rollback()
