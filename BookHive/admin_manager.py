import hashlib
import secrets

class AdminManager:
    def __init__(self, conn):
        self.conn = conn
    
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
        except Exception:
            return False
        
    def is_admin(self, user_id):
        result = self.execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,))
        return result.fetchone() is not None
    
    def search_users(self, term):
        term = f"%{term}%"
        return self.execute("""
            SELECT id, username, email FROM users
            WHERE username LIKE ? OR email LIKE ?
        """, (term, term)).fetchall()
    
    def get_user_books(self, user_id):
        return self.execute("""
            SELECT b.*, GROUP_CONCAT(t.name) AS tags
            FROM books b
            LEFT JOIN book_tags bt ON b.id = bt.book_id
            LEFT JOIN tags t ON bt.tag_id = t.id
            WHERE b.user_id = ?
            GROUP BY b.id
        """, (user_id,)).fetchall()
    
    def get_all_activities(self):
        return self.execute("""
            SELECT a.*, u.username
            FROM activities a
            JOIN users u ON a.user_id = u.id
            ORDER BY a.created_at DESC
        """).fetchall()
    def hide_review(self, review_id):
        self.execute("UPDATE reviews SET is_deleted = 1 WHERE id = ?", (review_id,))

    def hide_book(self, book_id):
        self.execute("UPDATE books SET is_deleted = 1 WHERE id = ?", (book_id,))

    def restore_book(self, book_id):
        self.execute("UPDATE books SET is_deleted = 0 WHERE id = ?", (book_id,))

    def restore_review(self, review_id):
        self.execute("UPDATE reviews SET is_deleted = 0 WHERE id = ?", (review_id,))