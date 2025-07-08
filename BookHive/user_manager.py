import sqlite3
import hashlib
import secrets

class UserManager:
    def __init__(self, db_conn):
        self.conn = db_conn

    def hash_password(self, password):
        salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        return f"{salt}${key}"

    def verify_password(self, stored_hash, password):
        try:
            salt, stored_key = stored_hash.split('$')
            new_key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            ).hex()
            return secrets.compare_digest(new_key, stored_key)
        except Exception:
            return False

    def register_user(self, username, email, password):
        cur = self.conn.cursor()
        row = cur.execute(
            "SELECT id FROM users WHERE username=? OR email=?",
            (username, email)
        ).fetchone()
        if row:
            return None  # Username or email exists
        password_hash = self.hash_password(password)
        cur.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        self.conn.commit()
        return cur.lastrowid

    def authenticate_user(self, username_or_email, password):
        cur = self.conn.cursor()
        user = cur.execute(
            "SELECT id, password_hash FROM users WHERE (username=? OR email=?)",
            (username_or_email, username_or_email)
        ).fetchone()
        if not user:
            return None
        user_id, password_hash = user
        if self.verify_password(password_hash, password):
            return user_id
        return None

    def get_user_by_id(self, user_id):
        cur = self.conn.cursor()
        return cur.execute(
            "SELECT id, username, email, created_at FROM users WHERE id=?",
            (user_id,)
        ).fetchone()

    def delete_user(self, user_id):
        """Hard-delete user from the system."""
        cur = self.conn.cursor()
        cur.execute(
            "DELETE FROM users WHERE id=?",
            (user_id,)
        )
        self.conn.commit()
        return cur.rowcount > 0

    def update_user(self, user_id, username=None, email=None, password=None):
        cur = self.conn.cursor()
        updates = []
        params = []
        if username:
            updates.append("username=?")
            params.append(username)
        if email:
            updates.append("email=?")
            params.append(email)
        if password:
            updates.append("password_hash=?")
            params.append(self.hash_password(password))
        if updates:
            params.append(user_id)
            sql = f"UPDATE users SET {', '.join(updates)} WHERE id=?"
            cur.execute(sql, params)
            self.conn.commit()
            return True
        return False
