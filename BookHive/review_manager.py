import sqlite3
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime

class ReviewManager:
    def __init__(self, db_conn: sqlite3.Connection):
        self.conn = db_conn

    def add_review(self, user_id: int, activity_id: int, content: str) -> Optional[int]:
        """Add a review to an activity.
        Returns the ID of the new review or None if failed."""
        if not content or not content.strip():
            return None
        
        try:
            with self.conn:
                cur = self.conn.cursor()
                cur.execute("""
                    INSERT INTO reviews (user_id, activity_id, content)
                    VALUES (?, ?, ?)
                """, (int(user_id), int(activity_id), content.strip()))
                return cur.lastrowid
        except (sqlite3.Error, ValueError) as e:
            print(f"Error adding review: {e}")
            return None

    def edit_review(self, review_id: int, user_id: int, content: str) -> bool:
        """Edit a user's own review. Returns True if successful."""
        if not content or not content.strip():
            return False
            
        try:
            with self.conn:
                cur = self.conn.cursor()
                cur.execute("""
                    UPDATE reviews 
                    SET content = ?, created_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND user_id = ?
                """, (content.strip(), int(review_id), int(user_id)))
                return cur.rowcount > 0
        except (sqlite3.Error, ValueError) as e:
            print(f"Error editing review: {e}")
            return False

    def delete_review(self, review_id: int, user_id: int) -> bool:
        """Delete a user's own review. Returns True if successful."""
        try:
            with self.conn:
                cur = self.conn.cursor()
                cur.execute("""
                    DELETE FROM reviews 
                    WHERE id = ? AND user_id = ?
                """, (int(review_id), int(user_id)))
                return cur.rowcount > 0
        except (sqlite3.Error, ValueError) as e:
            print(f"Error deleting review: {e}")
            return False

    def get_reviews_for_activity(self, activity_id: int) -> List[Tuple]:
        """Return all reviews for an activity with user info."""
        try:
            with self.conn:
                cur = self.conn.cursor()
                return cur.execute("""
                    SELECT r.id, r.user_id, u.username, r.content, r.created_at
                    FROM reviews r
                    JOIN users u ON r.user_id = u.id
                    WHERE r.activity_id = ?
                    ORDER BY r.created_at DESC
                """, (int(activity_id),)).fetchall()
        except (sqlite3.Error, ValueError) as e:
            print(f"Error fetching reviews: {e}")
            return []

    def get_review_by_id(self, review_id: int) -> Optional[Tuple]:
        """Fetch a specific review with user info."""
        try:
            with self.conn:
                cur = self.conn.cursor()
                return cur.execute("""
                    SELECT r.id, r.user_id, u.username, r.content, r.created_at
                    FROM reviews r
                    JOIN users u ON r.user_id = u.id
                    WHERE r.id = ?
                """, (int(review_id),)).fetchone()
        except (sqlite3.Error, ValueError) as e:
            print(f"Error fetching review: {e}")
            return None

    def get_user_reviews(self, user_id: int) -> List[Tuple]:
        """Return all reviews by a specific user."""
        try:
            with self.conn:
                cur = self.conn.cursor()
                return cur.execute("""
                    SELECT r.id, r.activity_id, a.name, r.content, r.created_at
                    FROM reviews r
                    JOIN activities a ON r.activity_id = a.id
                    WHERE r.user_id = ?
                    ORDER BY r.created_at DESC
                """, (int(user_id),)).fetchall()
        except (sqlite3.Error, ValueError) as e:
            print(f"Error fetching user reviews: {e}")
            return []