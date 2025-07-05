import sqlite3
import hashlib
import secrets

class UserManager:
    def __init__(self, db_conn):
        self.conn = db_conn

    def hash_password(self, password):
        """Generate a salted hash for password storage."""
        salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        return f"{salt}${key}"

    def verify_password(self, stored_hash, password):
        """Verify user password against stored hash."""
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
        """Register a new user."""
        cur = self.conn.cursor()
        # Check for duplicate username or email
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
        """Log in user by username or email and password."""
        cur = self.conn.cursor()
        user = cur.execute(
            "SELECT id, password_hash, is_deleted FROM users WHERE (username=? OR email=?)",
            (username_or_email, username_or_email)
        ).fetchone()
        if not user or user[2]:  # User does not exist or is soft-deleted
            return None
        user_id, password_hash, _ = user
        if self.verify_password(password_hash, password):
            return user_id
        return None

    def get_user_by_id(self, user_id):
        """Get user info (excluding password hash)."""
        cur = self.conn.cursor()
        return cur.execute(
            "SELECT id, username, email, created_at FROM users WHERE id=? AND is_deleted=0",
            (user_id,)
        ).fetchone()

    def soft_delete_user(self, user_id):
        """Soft-delete (hide) a user."""
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE users SET is_deleted=1 WHERE id=? AND is_deleted=0",
            (user_id,)
        )
        self.conn.commit()
        return cur.rowcount > 0

    def restore_user(self, user_id):
        """Restore a soft-deleted user."""
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE users SET is_deleted=0 WHERE id=? AND is_deleted=1",
            (user_id,)
        )
        self.conn.commit()
        return cur.rowcount > 0

    def update_user(self, user_id, username=None, email=None, password=None):
        """Update user profile fields (only those provided)."""
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
            sql = f"UPDATE users SET {', '.join(updates)} WHERE id=? AND is_deleted=0"
            cur.execute(sql, params)
            self.conn.commit()
            return True
        return False
