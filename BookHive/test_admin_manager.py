import unittest
from unittest.mock import MagicMock
from admin_manager import AdminManager

class TestAdminManager(unittest.TestCase):
    def setUp(self):
        # Mock the database connection and cursor
        self.mock_conn = MagicMock()
        self.admin_manager = AdminManager(self.mock_conn)
        self.admin_manager.execute = MagicMock()
    
    def test_is_admin_true(self):
        self.admin_manager.execute.return_value.fetchone.return_value = (1,)
        self.assertTrue(self.admin_manager.is_admin(2))
    
    def test_is_admin_false(self):
        self.admin_manager.execute.return_value.fetchone.return_value = None
        self.assertFalse(self.admin_manager.is_admin(3))
    
    def test_search_users(self):
        expected = [(1, 'alice', 'alice@mail.com')]
        self.admin_manager.execute.return_value.fetchall.return_value = expected
        result = self.admin_manager.search_users("alice")
        self.assertEqual(result, expected)

    def test_get_user_books(self):
        expected = [(1, 'Book Title', 'Tag1,Tag2')]
        self.admin_manager.execute.return_value.fetchall.return_value = expected
        result = self.admin_manager.get_user_books(1)
        self.assertEqual(result, expected)
    
    def test_hide_book(self):
        self.admin_manager.hide_book(10)
        self.admin_manager.execute.assert_called_with("UPDATE books SET is_deleted = 1 WHERE id = ?", (10,))
        self.mock_conn.commit.assert_called_once()

    def test_restore_book(self):
        self.admin_manager.restore_book(11)
        self.admin_manager.execute.assert_called_with("UPDATE books SET is_deleted = 0 WHERE id = ?", (11,))
        self.mock_conn.commit.assert_called_once()

    def test_hide_review(self):
        self.admin_manager.hide_review(12)
        self.admin_manager.execute.assert_called_with("UPDATE reviews SET is_deleted = 1 WHERE id = ?", (12,))

    def test_restore_review(self):
        self.admin_manager.restore_review(13)
        self.admin_manager.execute.assert_called_with("UPDATE reviews SET is_deleted = 0 WHERE id = ?", (13,))

    def test_add_theme(self):
        # Simulate adding a theme (doesn't need to return, just check call)
        self.theme_manager.add_theme(self.mock_db, "Test Theme", False)
        self.theme_manager.execute.assert_called_with(
            "INSERT INTO themes (title, is_hidden) VALUES (?, ?)",
            ("Test Theme", 0)
        )
        self.mock_db.commit.assert_called_once()

    def test_set_theme_visibility(self):
        # Hide theme
        self.theme_manager.set_theme_visibility(self.mock_db, 1, True)
        self.theme_manager.execute.assert_called_with(
            "UPDATE themes SET is_hidden = ? WHERE id = ?",
            (1, 1)
        )
        self.mock_db.commit.assert_called_once()
        # Show theme
        self.theme_manager.set_theme_visibility(self.mock_db, 2, False)
        self.theme_manager.execute.assert_called_with(
            "UPDATE themes SET is_hidden = ? WHERE id = ?",
            (0, 2)
        )

    def test_add_book_to_theme(self):
        self.theme_manager.add_book_to_theme(self.mock_db, 1, 42)
        self.theme_manager.execute.assert_called_with(
            "INSERT OR IGNORE INTO theme_books (theme_id, book_id) VALUES (?, ?)",
            (1, 42)
        )
        self.mock_db.commit.assert_called_once()
    
    def test_get_visible_themes(self):
        expected = [(1, "Theme A"), (2, "Theme B")]
        self.theme_manager.execute.return_value.fetchall.return_value = expected
        result = self.theme_manager.get_visible_themes(self.mock_db)
        self.theme_manager.execute.assert_called_with(
            "SELECT id, title FROM themes WHERE is_hidden = 0"
        )
        self.assertEqual(result, expected)

    def test_get_theme_books(self):
        expected = [{"id": 5, "title": "Book 1"}]
        self.theme_manager.execute.return_value.fetchall.return_value = expected
        result = self.theme_manager.get_theme_books(self.mock_db, 1)
        self.theme_manager.execute.assert_called_with(
            """
        SELECT b.* FROM books b
        JOIN theme_books tb ON b.id = tb.book_id
        WHERE tb.theme_id = ? AND b.is_deleted = 0
        """, (1,)
        )
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
