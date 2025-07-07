import unittest
from unittest.mock import MagicMock
from likes_manager import LikesManager

class TestLikesManager(unittest.TestCase):
    def setUp(self):
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor
        self.likes_manager = LikesManager(self.mock_conn)

    def assertSQLCalledSubstring(self, substring, params):
        found = any(
            substring in str(call[0][0]) and call[0][1] == params
            for call in self.mock_cursor.execute.call_args_list
        )
        self.assertTrue(found, f"{substring} with {params} was not called")

    def test_add_like_insert(self):
        self.mock_cursor.execute.return_value.fetchone.return_value = None
        result = self.likes_manager.add_like(1, 10)
        self.assertSQLCalledSubstring(
            "INSERT INTO likes (user_id, activity_id) VALUES (?, ?)", (1, 10)
        )
        self.mock_conn.commit.assert_called()
        self.assertTrue(result)

    def test_add_like_duplicate(self):
        self.mock_cursor.execute.return_value.fetchone.return_value = (5, 0)
        result = self.likes_manager.add_like(2, 30)
        self.assertFalse(result)
        self.mock_conn.commit.assert_not_called()

    def test_remove_like_noupdate(self):
        self.mock_cursor.rowcount = 0
        result = self.likes_manager.remove_like(3, 12)
        self.assertFalse(result)
        self.mock_conn.commit.assert_called()

    def test_has_liked_true(self):
        self.mock_cursor.execute.return_value.fetchone.return_value = (1,)
        self.assertTrue(self.likes_manager.has_liked(4, 100))

    def test_has_liked_false(self):
        self.mock_cursor.execute.return_value.fetchone.return_value = None
        self.assertFalse(self.likes_manager.has_liked(4, 101))

    def test_count_likes_some(self):
        self.mock_cursor.execute.return_value.fetchone.return_value = (7,)
        self.assertEqual(self.likes_manager.count_likes(42), 7)

    def test_count_likes_none(self):
        self.mock_cursor.execute.return_value.fetchone.return_value = (0,)
        self.assertEqual(self.likes_manager.count_likes(43), 0)

    def test_count_likes_row_none(self):
        self.mock_cursor.execute.return_value.fetchone.return_value = None
        self.assertEqual(self.likes_manager.count_likes(99), 0)

    def test_get_likes_for_activity(self):
        fake_result = [(1, 2, "testuser", "2024-01-01")]
        self.mock_cursor.execute.return_value.fetchall.return_value = fake_result
        result = self.likes_manager.get_likes_for_activity(21)
        self.assertEqual(result, fake_result)

    def test_get_liked_activities_by_user(self):
        self.mock_cursor.execute.return_value.fetchall.return_value = [(5,), (7,), (8,)]
        result = self.likes_manager.get_liked_activities_by_user(6)
        self.assertEqual(result, [5, 7, 8])

if __name__ == "__main__":
    unittest.main()
