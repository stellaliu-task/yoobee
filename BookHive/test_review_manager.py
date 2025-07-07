import unittest
from unittest.mock import MagicMock
from review_manager import ReviewManager

class TestReviewManager(unittest.TestCase):
    def setUp(self):
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor
        self.review_manager = ReviewManager(self.mock_conn)

    def test_add_reply_commits(self):
        self.mock_cursor.lastrowid = 99
        result = self.review_manager.add_reply(1, 2, "Test reply")
        # Should insert and commit, and return new id
        self.assertEqual(result, 99)
        self.mock_conn.commit.assert_called()

    def test_add_reply_blank(self):
        # Blank content
        self.assertIsNone(self.review_manager.add_reply(1, 2, ""))
        self.assertIsNone(self.review_manager.add_reply(1, 2, "    "))
        self.mock_conn.commit.assert_not_called()

    def test_edit_reply_commits(self):
        self.mock_cursor.rowcount = 1
        result = self.review_manager.edit_reply(3, 1, "Edit content")
        self.assertTrue(result)
        self.mock_conn.commit.assert_called()

    def test_edit_reply_blank(self):
        self.assertFalse(self.review_manager.edit_reply(3, 1, ""))
        self.assertFalse(self.review_manager.edit_reply(3, 1, "   "))
        self.mock_conn.commit.assert_not_called()

    def test_hide_reply_commits(self):
        self.mock_cursor.rowcount = 1
        result = self.review_manager.hide_reply(5, 2)
        self.assertTrue(result)
        self.mock_conn.commit.assert_called()

    def test_restore_reply_commits(self):
        self.mock_cursor.rowcount = 1
        result = self.review_manager.restore_reply(7, 2)
        self.assertTrue(result)
        self.mock_conn.commit.assert_called()

    def test_get_replies_for_activity(self):
        fake_result = [(1, 2, "user2", "Nice!", "2024-01-02")]
        self.mock_cursor.execute.return_value.fetchall.return_value = fake_result
        result = self.review_manager.get_replies_for_activity(2)
        self.assertEqual(result, fake_result)
        self.mock_conn.commit.assert_not_called()

    def test_get_reply_by_id(self):
        fake_reply = (1, 2, "user2", "A reply", "2024-01-02")
        self.mock_cursor.execute.return_value.fetchone.return_value = fake_reply
        result = self.review_manager.get_reply_by_id(3)
        self.assertEqual(result, fake_reply)
        self.mock_conn.commit.assert_not_called()

if __name__ == "__main__":
    unittest.main()
