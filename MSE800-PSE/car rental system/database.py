import sqlite3
import os
import threading

class Database:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_file="car_rental.db"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
                cls._instance._local = threading.local()
        return cls._instance

    def __init__(self, db_file="car_rental.db"):
        if getattr(self, '_initialized', False):
            return
        # Always use an absolute path based on this file's location
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_db_path = os.path.join(base_dir, db_file)
        self.db_file = abs_db_path
        self._initialized = True

    @property
    def conn(self):
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_file)
            self._local.conn.row_factory = sqlite3.Row
            self.create_tables()
        return self._local.conn
    
    #def close(self):
    #    self.conn.close()

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,   
                email TEXT NOT NULL UNIQUE,
                phone_number VARCHAR(15),
                password_hash VARCHAR(255) NOT NULL,
                card_number VARCHAR(20),
                driver_licence_number VARCHAR(25),
                driver_licence_country TEXT,
                licence_expiry_date DATE
            )
        ''')

        # Admin table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL
            )
        ''')

        # Cars table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                picture BLOB NOT NULL,
                fuel_type VARCHAR(10) CHECK (fuel_type IN ('gas', 'electric', 'diesel', 'hybrid')) NOT NULL,
                gear_type VARCHAR(10) CHECK (gear_type IN ('automatic', 'manual')) NOT NULL,
                seats INTEGER NOT NULL CHECK (seats > 0),
                location TEXT NOT NULL,
                available_datetime DATETIME NOT NULL,
                price REAL NOT NULL CHECK (price > 0),
                insurance_price REAL NOT NULL CHECK (insurance_price >= 0)
            )
        ''')

        # Orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_datetime DATETIME NOT NULL,
                end_datetime DATETIME NOT NULL CHECK (end_datetime > start_datetime),
                user_id INTEGER NOT NULL,
                car_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(car_id) REFERENCES cars(id)
            )
        ''')

        # Reviews table (changed ranking to 1-10)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submit_datetime DATETIME NOT NULL,
                user_id INTEGER NOT NULL,
                car_id INTEGER NOT NULL,
                ranking INTEGER CHECK (ranking BETWEEN 1 AND 10),
                review_content TEXT NOT NULL,
                show_state BOOLEAN NOT NULL DEFAULT TRUE,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(car_id) REFERENCES cars(id)
            )
        ''')

        # try to use indexes
        #cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        #cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)')
        #cursor.execute('CREATE INDEX IF NOT EXISTS idx_reviews_car_id ON reviews(car_id)')

        self.conn.commit()

    def close(self):
        if hasattr(self._local, 'conn'):
            self._local.conn.close()
            del self._local.conn

    def get_cursor(self):
        return self.conn.cursor()