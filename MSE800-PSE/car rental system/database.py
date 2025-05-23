import sqlite3

def create_connection():
    conn = sqlite3.connect("car_rental.db")
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone_number CHAR(10) NOT NULL,
            password_hash VARCHAR(255) NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            picture BLOB NOT NULL,
            fuel_type VARCHAR(10) CHECK (fuel_type IN ('gas', 'electric', 'diesel', 'hybrid')) NOT NULL,
            gear_type VARCHAR(10) CHECK (gear_type IN ('automatic','manual') NOT NULL,
            seats INTEGER NOT NULL,
            location TEXT NOT NULL,
            available_datetime DATETIME NOT NULL
            price REAL NOT NULL,
            ranking INTEGER 
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
        )
    ''')
    conn.commit()
    conn.close()
