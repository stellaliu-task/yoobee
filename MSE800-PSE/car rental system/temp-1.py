import sqlite3
import os

def add_returned_column(db_file="car_rental.db"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    abs_db_path = os.path.join(base_dir, db_file)
    conn = sqlite3.connect(abs_db_path)
    cursor = conn.cursor()

    # Check if the column already exists
    cursor.execute("PRAGMA table_info(orders)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'returned' not in columns:
        try:
            cursor.execute("ALTER TABLE orders ADD COLUMN returned INTEGER DEFAULT 0")
            conn.commit()
            print("✅ Successfully added 'returned' column to orders table.")
        except sqlite3.Error as e:
            print(f"❌ Error adding 'returned' column: {e}")
            conn.rollback()
    else:
        print("Column 'returned' already exists in orders table.")
    conn.close()

# Run this once:
if __name__ == "__main__":
    add_returned_column("car_rental.db")
