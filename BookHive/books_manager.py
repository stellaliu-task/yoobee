import sqlite3

class BooksManager:
    def __init__(self, db_conn):
        self.conn = db_conn

    def add_book(self, user_id, title, author, description, catalog, cover_picture, status, tags):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO books (user_id, title, author, description, catalog, cover_picture, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, title, author, description, catalog, cover_picture, status)
        )
        book_id = cur.lastrowid
        for tag in tags:
            tag_id = self.get_or_create_tag(tag)
            cur.execute(
                "INSERT OR IGNORE INTO book_tags (book_id, tag_id) VALUES (?, ?)",
                (book_id, tag_id)
            )
        self.conn.commit()
        return book_id

    def edit_book(self, book_id, user_id, title=None, author=None, description=None, catalog=None, status=None, cover_picture=None): 
        cur = self.conn.cursor()
        updates = []
        params = []
        if title is not None:
            updates.append("title=?")
            params.append(title)
        if author is not None:
            updates.append("author=?")
            params.append(author)
        if description is not None:
            updates.append("description=?")
            params.append(description)
        if catalog is not None:
            updates.append("catalog=?")
            params.append(catalog)
        if status is not None:
            updates.append("status=?")
            params.append(status)
        if cover_picture is not None:
            updates.append("cover_picture=?")
            params.append(cover_picture)
        if updates:
            params += [book_id, user_id]
            sql = f"UPDATE books SET {', '.join(updates)} WHERE id=? AND user_id=? AND (is_deleted IS NULL OR is_deleted=0)"
            cur.execute(sql, params)
            self.conn.commit()
            return True
        return False


    def hide_book(self, book_id, user_id):
        """User soft deletes (hides) their own book."""
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE books SET is_deleted=1 WHERE id=? AND user_id=? AND is_deleted=0",
            (book_id, user_id)
        )
        self.conn.commit()
        return cur.rowcount > 0

    def restore_book(self, book_id, user_id):
        """User restores their own hidden book."""
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE books SET is_deleted=0 WHERE id=? AND user_id=? AND is_deleted=1",
            (book_id, user_id)
        )
        self.conn.commit()
        return cur.rowcount > 0

    def get_books_by_user(self, user_id, status=None, tag=None, catalog=None):
        """List a user's own books, filterable by status, tag, or catalog."""
        cur = self.conn.cursor()
        sql = """
            SELECT b.*, GROUP_CONCAT(t.name) as tags
            FROM books b
            LEFT JOIN book_tags bt ON b.id = bt.book_id
            LEFT JOIN tags t ON bt.tag_id = t.id
            WHERE b.user_id=? AND b.is_deleted=0
        """
        params = [user_id]
        if status:
            sql += " AND b.status=?"
            params.append(status)
        if catalog:
            sql += " AND b.catalog=?"
            params.append(catalog)
        if tag:
            sql += """
                AND EXISTS (
                    SELECT 1 FROM book_tags bt2
                    JOIN tags t2 ON bt2.tag_id = t2.id
                    WHERE bt2.book_id = b.id AND t2.name = ?
                )
            """
            params.append(tag)
        sql += " GROUP BY b.id"
        cur.execute(sql, params)
        return cur.fetchall()

    def set_reading_status(self, book_id, user_id, status):
        """Change reading status of a user's book."""
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE books SET status=? WHERE id=? AND user_id=? AND is_deleted=0",
            (status, book_id, user_id)
        )
        self.conn.commit()
        return cur.rowcount > 0

    def add_tag_to_book(self, book_id, user_id, tag_name):
        """Assign a tag to a user's book."""
        cur = self.conn.cursor()
        # Ensure book is owned by user and not deleted
        book = cur.execute("SELECT id FROM books WHERE id=? AND user_id=? AND is_deleted=0", (book_id, user_id)).fetchone()
        if not book:
            return False
        cur.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
        tag_id = cur.execute("SELECT id FROM tags WHERE name = ?", (tag_name,)).fetchone()[0]
        cur.execute("INSERT OR IGNORE INTO book_tags (book_id, tag_id) VALUES (?, ?)", (book_id, tag_id))
        self.conn.commit()
        return True

    def remove_tag_from_book(self, book_id, user_id, tag_name):
        """Remove a tag from a user's book."""
        cur = self.conn.cursor()
        # Ensure book is owned by user and not deleted
        book = cur.execute("SELECT id FROM books WHERE id=? AND user_id=? AND is_deleted=0", (book_id, user_id)).fetchone()
        if not book:
            return False
        tag = cur.execute("SELECT id FROM tags WHERE name = ?", (tag_name,)).fetchone()
        if not tag:
            return False
        tag_id = tag[0]
        cur.execute("DELETE FROM book_tags WHERE book_id=? AND tag_id=?", (book_id, tag_id))
        self.conn.commit()
        return True

    def get_book_by_id(self, book_id, user_id):
        """Fetch all info (including tags) for a user's book."""
        cur = self.conn.cursor()
        book = cur.execute("""
            SELECT * FROM books WHERE id=? AND user_id=? AND is_deleted=0
        """, (book_id, user_id)).fetchone()
        if not book:
            return None
        tags = self.get_tags_for_book(book_id, user_id)
        return (book, tags)

    def get_tags_for_book(self, book_id, user_id):
        """List all tags for a user's book."""
        cur = self.conn.cursor()
        tags = cur.execute("""
            SELECT t.name FROM tags t
            JOIN book_tags bt ON bt.tag_id = t.id
            JOIN books b ON bt.book_id = b.id
            WHERE b.id=? AND b.user_id=? AND b.is_deleted=0
        """, (book_id, user_id)).fetchall()
        return [t[0] for t in tags]