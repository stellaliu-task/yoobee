import unittest
from unittest.mock import MagicMock
from admin_manager import AdminManager

class TestAdminManager(unittest.TestCase):
    def setUp(self):
        # Mock the database connection and cursor
        self.mock_conn = MagicMock()
        self.admin_manager = AdminManager(self.mock_conn)
        self.admin_manager.execute = MagicMock()
        self.mock_conn.commit = MagicMock()
    
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

if __name__ == '__main__':
    unittest.main()
