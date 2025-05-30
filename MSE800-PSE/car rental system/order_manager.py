import sqlite3
from datetime import datetime
from database import Database

class OrderManager:
    def __init__(self, conn):
        self.conn = conn

    def create_order(self, order_data):
        # Check car availability first
        conflict_check = '''
        SELECT id FROM orders 
        WHERE car_id = ? AND ? < end_datetime AND ? > start_datetime
        '''
        cur = self.conn.cursor()
        cur.execute(conflict_check, (
            order_data['car_id'],
            order_data['end_datetime'],
            order_data['start_datetime']
        ))
        if cur.fetchone():
            raise ValueError("Car not available for selected dates")
        
        # Modified to ensure created_at is set
        sql = '''INSERT INTO orders(start_datetime, end_datetime, user_id, car_id, created_at)
                VALUES(?,?,?,?,datetime('now'))'''  # Explicitly set current timestamp
        cur.execute(sql, (
            order_data['start_datetime'],
            order_data['end_datetime'],
            order_data['user_id'],
            order_data['car_id']
        ))
        self.conn.commit()
        return cur.lastrowid

    def get_user_orders(self, user_id):
        sql = '''SELECT o.*, c.name as car_name, c.fuel_type, c.gear_type, c.seats, 
                        c.location, c.price, c.insurance_price
                FROM orders o 
                JOIN cars c ON o.car_id = c.id
                WHERE o.user_id = ?
                ORDER BY o.created_at DESC''' 
        cur = self.conn.cursor()
        cur.execute(sql, (user_id,))
        return cur.fetchall()