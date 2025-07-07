import unittest
from unittest.mock import MagicMock, patch
from user_manager import UserManager

class TestUserManager(unittest.TestCase):
    def setUp(self):
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor
        self.user_manager = UserManager(self.mock_conn)

    def test_hash_and_verify_password(self):
        password = "testpass123"
        hashed = self.user_manager.hash_password(password)
        self.assertIn('$', hashed)
        self.assertTrue(self.user_manager.verify_password(hashed, password))
        self.assertFalse(self.user_manager.verify_password(hashed, "wrongpass"))

    def test_register_user_success(self):
        self.mock_cursor.execute.return_value.fetchone.return_value = None  # No duplicate
        self.mock_cursor.lastrowid = 12
        with patch.object(self.user_manager, 'hash_password', return_value='salt$hash') as mock_hash:
            result = self.user_manager.register_user("user1", "mail@test.com", "pass123")
        self.assertEqual(result, 12)
        self.mock_conn.commit.assert_called()

    def test_register_user_duplicate(self):
        self.mock_cursor.execute.return_value.fetchone.return_value = (7,)
        result = self.user_manager.register_user("user1", "mail@test.com", "pass123")
        self.assertIsNone(result)
        self.mock_conn.commit.assert_not_called()

    def test_authenticate_user_success(self):
        # Patch verify_password to always True for this test
        user_row = (15, "salt$hash", 0)
        self.mock_cursor.execute.return_value.fetchone.return_value = user_row
        with patch.object(self.user_manager, 'verify_password', return_value=True):
            result = self.user_manager.authenticate_user("user1", "pass123")
        self.assertEqual(result, 15)

    def test_authenticate_user_fail_deleted(self):
        user_row = (15, "salt$hash", 1)
        self.mock_cursor.execute.return_value.fetchone.return_value = user_row
        with patch.object(self.user_manager, 'verify_password', return_value=True):
            result = self.user_manager.authenticate_user("user1", "pass123")
        self.assertIsNone(result)

    def test_authenticate_user_fail_password(self):
        user_row = (15, "salt$hash", 0)
        self.mock_cursor.execute.return_value.fetchone.return_value = user_row
        with patch.object(self.user_manager, 'verify_password', return_value=False):
            result = self.user_manager.authenticate_user("user1", "pass123")
        self.assertIsNone(result)

    def test_get_user_by_id(self):
        fake_user = (15, "user1", "mail@test.com", "2024-01-01")
        self.mock_cursor.execute.return_value.fetchone.return_value = fake_user
        result = self.user_manager.get_user_by_id(15)
        self.assertEqual(result, fake_user)
        self.mock_conn.commit.assert_not_called()

    def test_soft_delete_user_commits(self):
        self.mock_cursor.rowcount = 1
        result = self.user_manager.soft_delete_user(15)
        self.assertTrue(result)
        self.mock_conn.commit.assert_called()

    def test_restore_user_commits(self):
        self.mock_cursor.rowcount = 1
        result = self.user_manager.restore_user(15)
        self.assertTrue(result)
        self.mock_conn.commit.assert_called()

    def test_update_user_all_fields(self):
        # Provide username, email, password
        with patch.object(self.user_manager, 'hash_password', return_value='salt$hash'):
            result = self.user_manager.update_user(15, username="newu", email="newmail", password="pw")
        self.assertTrue(result)
        self.mock_conn.commit.assert_called()

    def test_update_user_none(self):
        result = self.user_manager.update_user(15)
        self.assertFalse(result)
        self.mock_conn.commit.assert_not_called()

if __name__ == "__main__":
    unittest.main()
