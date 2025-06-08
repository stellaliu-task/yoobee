import hashlib
import secrets

class AdminManager:
    def __init__(self, conn):
        self.conn = conn

    def toggle_review_visibility(conn, review_id, show_state):
        cur = conn.cursor()
        cur.execute(
            "UPDATE reviews SET show_state = ? WHERE id = ?",
            (show_state, review_id)
        )
        conn.commit()
        return cur.rowcount > 0

    def get_all_orders(conn, start_date=None, end_date=None):
        sql = '''SELECT o.*, u.email as user_email, c.name as car_name, c.price, c.insurance_price
                FROM orders o 
                JOIN users u ON o.user_id = u.id
                JOIN cars c ON o.car_id = c.id'''
        params = []
        if start_date and end_date:
            sql += " WHERE o.start_datetime BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()

    
    def _verify_password(self, stored_hash, password):
        if not stored_hash or not password:
            return False
        try:
            salt, stored_key = stored_hash.split('$')
            new_key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            ).hex()
            return secrets.compare_digest(new_key, stored_key)
        except:
            return False