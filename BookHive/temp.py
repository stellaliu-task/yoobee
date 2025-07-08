from database import Database
import os

# Initialize the database explicitly
db = Database()

# Verify the file was created
print(f"Database file exists: {os.path.exists(db.db_file)}")

# Test a query
with db.conn as conn:
    conn.execute("INSERT INTO test (id) VALUES (1)")
    result = conn.execute("SELECT * FROM test").fetchall()
    print("Query results:", result)