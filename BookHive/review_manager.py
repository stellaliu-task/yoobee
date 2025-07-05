import sqlite3

class ReviewManager:
    def __init__(self, db_conn):
        self.conn = db_conn

    def add_reply(self, user_id, activity_id, content):
        """Add a reply (comment) to an activity."""
        if not content or not content.strip():
            return None  # Reject blank reply
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO replies (user_id, activity_id, content)
            VALUES (?, ?, ?)
        """, (user_id, activity_id, content.strip()))
        self.conn.commit()
        return cur.lastrowid

    def edit_reply(self, reply_id, user_id, content):
        """Edit a user's own reply."""
        if not content or not content.strip():
            return False
        cur = self.conn.cursor()
        cur.execute("""
            UPDATE replies SET content=? WHERE id=? AND user_id=? AND is_deleted=0
        """, (content.strip(), reply_id, user_id))
        self.conn.commit()
        return cur.rowcount > 0

    def hide_reply(self, reply_id, user_id):
        """User soft-deletes (hides) their own reply."""
        cur = self.conn.cursor()
        cur.execute("""
            UPDATE replies SET is_deleted=1 WHERE id=? AND user_id=? AND is_deleted=0
        """, (reply_id, user_id))
        self.conn.commit()
        return cur.rowcount > 0

    def restore_reply(self, reply_id, user_id):
        """User restores their own soft-deleted reply."""
        cur = self.conn.cursor()
        cur.execute("""
            UPDATE replies SET is_deleted=0 WHERE id=? AND user_id=? AND is_deleted=1
        """, (reply_id, user_id))
        self.conn.commit()
        return cur.rowcount > 0

    def get_replies_for_activity(self, activity_id):
        """Return all non-deleted replies for an activity, with user info."""
        cur = self.conn.cursor()
        return cur.execute("""
            SELECT r.id, r.user_id, u.username, r.content, r.created_at
            FROM replies r
            JOIN users u ON r.user_id = u.id
            WHERE r.activity_id=? AND r.is_deleted=0
            ORDER BY r.created_at
        """, (activity_id,)).fetchall()

    def get_reply_by_id(self, reply_id):
        """Fetch a specific reply with user info (if not deleted)."""
        cur = self.conn.cursor()
        return cur.execute("""
            SELECT r.id, r.user_id, u.username, r.content, r.created_at
            FROM replies r
            JOIN users u ON r.user_id = u.id
            WHERE r.id=? AND r.is_deleted=0
        """, (reply_id,)).fetchone()
