import sqlite3

class LikesManager:
    def __init__(self, db_conn):
        self.conn = db_conn

    def add_like(self, user_id, activity_id):
        """Add a like for a given activity by a user. Only one like per user/activity."""
        cur = self.conn.cursor()
        row = cur.execute("""
            SELECT 1 FROM likes WHERE user_id=? AND activity_id=?
        """, (user_id, activity_id)).fetchone()
        if row:
            return False  # Already liked
        cur.execute("""
            INSERT INTO likes (user_id, activity_id) VALUES (?, ?)
        """, (user_id, activity_id))
        self.conn.commit()
        return True

    def remove_like(self, user_id, activity_id):
        """Hard delete a user's like from an activity."""
        cur = self.conn.cursor()
        cur.execute("""
            DELETE FROM likes WHERE user_id=? AND activity_id=?
        """, (user_id, activity_id))
        self.conn.commit()
        return cur.rowcount > 0

    def has_liked(self, user_id, activity_id):
        """Check if the user has liked a particular activity."""
        cur = self.conn.cursor()
        row = cur.execute("""
            SELECT 1 FROM likes WHERE user_id=? AND activity_id=?
        """, (user_id, activity_id)).fetchone()
        return bool(row)

    def count_likes(self, activity_id):
        """Return the number of likes for a given activity."""
        cur = self.conn.cursor()
        row = cur.execute("""
            SELECT COUNT(*) FROM likes WHERE activity_id=?
        """, (activity_id,)).fetchone()
        return row[0] if row else 0

    def get_likes_for_activity(self, activity_id):
        """Return all likes for an activity, including user info."""
        cur = self.conn.cursor()
        return cur.execute("""
            SELECT l.id, l.user_id, u.username, l.created_at
            FROM likes l
            JOIN users u ON l.user_id = u.id
            WHERE l.activity_id=?
            ORDER BY l.created_at
        """, (activity_id,)).fetchall()

    def get_liked_activities_by_user(self, user_id):
        """Return list of activity_ids liked by a user."""
        cur = self.conn.cursor()
        rows = cur.execute("""
            SELECT activity_id FROM likes WHERE user_id=?
        """, (user_id,)).fetchall()
        return [row[0] for row in rows]
