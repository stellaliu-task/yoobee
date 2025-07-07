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
        self.conn.commit()

    def hide_book(self, book_id):
        self.execute("UPDATE books SET is_deleted = 1 WHERE id = ?", (book_id,))
        self.conn.commit()

    def restore_book(self, book_id):
        self.execute("UPDATE books SET is_deleted = 0 WHERE id = ?", (book_id,))
        self.conn.commit()

    def restore_review(self, review_id):
        self.execute("UPDATE reviews SET is_deleted = 0 WHERE id = ?", (review_id,))
        self.conn.commit()

    def add_theme(self, title, is_hidden=False):
        self.execute("INSERT INTO themes (title, is_hidden) VALUES (?, ?)",(title, int(is_hidden)))
        self.conn.commit()
        
    def set_theme_visibility(self, theme_id, hide=True):
        self.execute("UPDATE themes SET is_hidden = ? WHERE id = ?",(int(hide), theme_id))
        self.conn.commit()


    def add_book_to_theme(self, theme_id, book_id):
        self.execute("INSERT OR IGNORE INTO theme_books (theme_id, book_id) VALUES (?, ?)",(theme_id, book_id))
        self.conn.commit()

    def get_visible_themes(self):
        return self.execute(
            "SELECT id, title FROM themes WHERE is_hidden = 0"
        ).fetchall()
    
    def get_theme_books(self, theme_id):
        return self.execute(
            """
            SELECT b.* FROM books b
            JOIN theme_books tb ON b.id = tb.book_id
            WHERE tb.theme_id = ? AND b.is_deleted = 0
            """, (theme_id,)
        ).fetchall()