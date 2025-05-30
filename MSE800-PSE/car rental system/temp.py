
import sqlite3
import threading

class Database:
    _instance = None
    _lock = threading.Lock()
    def __init__(self, db_file="car_rental.db"):
        if getattr(self, '_initialized', False):
            return
            
        self.db_file = db_file
        self._initialized = True
        
        try:
            cursor = self.conn.cursor()
            
            # Check if the column exists first
            cursor.execute("PRAGMA table_info(orders)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'created_at' not in columns:
                # First add the column without DEFAULT
                cursor.execute('ALTER TABLE orders ADD COLUMN created_at DATETIME')
                
                # Then update existing rows with current timestamp
                cursor.execute('UPDATE orders SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL')
                
                # Finally modify the column to have DEFAULT
                # SQLite doesn't support modifying columns directly, so we need to:
                # 1. Create a new table
                # 2. Copy data
                # 3. Drop old table
                # 4. Rename new table
                cursor.executescript('''
                    BEGIN TRANSACTION;
                    CREATE TABLE orders_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        start_datetime DATETIME NOT NULL,
                        end_datetime DATETIME NOT NULL CHECK (end_datetime > start_datetime),
                        user_id INTEGER NOT NULL,
                        car_id INTEGER NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users(id),
                        FOREIGN KEY(car_id) REFERENCES cars(id)
                    );
                    INSERT INTO orders_new SELECT * FROM orders;
                    DROP TABLE orders;
                    ALTER TABLE orders_new RENAME TO orders;
                    COMMIT;
                ''')
                
                self.conn.commit()
                print("Successfully added created_at column to orders table")
        except sqlite3.Error as e:
            print(f"Error adding created_at column: {e}")
            self.conn.rollback()