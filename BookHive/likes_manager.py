class LikeManager():   
    def __init__(self, conn):
        self.conn = conn

    def add_like(self, user_id, activity_id):
        # Check if already liked (but soft-deleted)
        result = self.execute("""
        if result := self.execute(
            SELECT id, is_deleted FROM likes
            WHERE user_id = ? AND activity_id = ?
        """, (user_id, activity_id)).fetchone()

        if result:
            like_id, is_deleted = result
            if is_deleted:
                # Reactivate the previously deleted like
                self.execute("UPDATE likes SET is_deleted = 0 WHERE id = ?", (like_id,))
            else:
                # Already liked and active
                return {"message": "Already liked"}, 400
        else:
            # Insert a new like
            self.execute("""
                INSERT INTO likes (user_id, activity_id)
                VALUES (?, ?)
            """, (user_id, activity_id))
        
        self.commit()
        return {"message": "Like added successfully"}, 201

    def get_likes_for_activity(self, activity_id):
        return self.execute("""
            SELECT l.id, l.user_id, u.username, l.created_at
            FROM likes l
            JOIN users u ON l.user_id = u.id
            WHERE l.activity_id = ? AND l.is_deleted = 0
            ORDER BY l.created_at
        """, (activity_id,)).fetchall()