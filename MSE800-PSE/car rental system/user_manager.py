import sqlite3
import hashlib
import secrets
from datetime import datetime
from database import Database

class UserManager:
    def __init__(self, conn):
        self.conn = conn

    def _hash_password(self, password, salt=None):
        if salt is None:
            salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return f"{salt}${key.hex()}"

    def signup(self, email, password):
        if not email or not password:
            raise ValueError("Email and password are required")

        if self.get_user_by_email(email):
            raise ValueError("Email already registered")

        # Hash password
        hashed_pw = self._hash_password(password)

        sql = '''INSERT INTO users(
                    email, 
                    password_hash)
                 VALUES(?,?)'''
        
        try:
            cur = self.conn.cursor()
            cur.execute(sql, (email, hashed_pw))
            self.conn.commit()
            return cur.lastrowid
        except sqlite3.Error as e:
            self.conn.rollback()
            raise ValueError(f"Database error: {str(e)}")

    def update_profile(self, user_id, profile_data):
        allowed_fields = {
            'first_name',
            'last_name',
            'phone_number',
            'card_number',
            'driver_licence_number',
            'driver_licence_country',
            'licence_expiry_date'
        }
        
        updates = []
        params = []
        
        for field, value in profile_data.items():
            if field in allowed_fields and value is not None:
                # Validate date format if provided
                if field == 'licence_expiry_date':
                    try:
                        datetime.strptime(value, '%Y-%m-%d')
                    except ValueError:
                        raise ValueError("Licence expiry must be in YYYY-MM-DD format")
                
                updates.append(f"{field} = ?")
                params.append(value)
        
        if not updates:
            return False  # No valid updates

        sql = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        params.append(user_id)

        try:
            cur = self.conn.cursor()
            cur.execute(sql, params)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise ValueError(f"Database error: {str(e)}")

    def login(self, email, password):
        user = self.get_user_by_email(email)
        if not user:
            return None

        # Verify password
        salt, stored_key = user['password_hash'].split('$')
        new_key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()

        if secrets.compare_digest(new_key, stored_key):
            return {k: user[k] for k in user.keys() if k != 'password_hash'}
        return None

    def get_user_by_email(self, email):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        row = cur.fetchone()
        if row:
            columns = [col[0] for col in cur.description]
            return dict(zip(columns, row))
        return None

    
    def get_user_profile(self, user_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
        row = cur.fetchone()
        if row:
            columns = [col[0] for col in cur.description]
            profile = dict(zip(columns, row))
            profile.pop('password_hash', None)  # Remove sensitive data
            return profile
        return None