import unittest
from unittest.mock import MagicMock
from books_manager import BooksManager

class TestBooksManager(unittest.TestCase):
    def setUp(self):
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor
        self.books_manager = BooksManager(self.mock_conn)
        # Patch get_or_create_tag to always return 1
        self.books_manager.get_or_create_tag = MagicMock(return_value=1)
        self.mock_cursor.lastrowid = 123  # fake book id

    def test_add_book_commits(self):
        self.books_manager.add_book(
            1, "Book Title", "Author", "Description", "Catalog", b"imgbytes", "want_to_read", ["tag1", "tag2"]
        )
        self.mock_conn.commit.assert_called()

    def test_edit_book_commits(self):
        # Should commit if any fields are provided
        self.books_manager.edit_book(
            5, 1, title="New Title", author="New Author"
        )
        self.mock_conn.commit.assert_called()

    def test_hide_book_commits(self):
        self.mock_cursor.rowcount = 1
        result = self.books_manager.hide_book(3, 1)
        self.mock_conn.commit.assert_called()
        self.assertTrue(result)

    def test_restore_book_commits(self):
        self.mock_cursor.rowcount = 1
        result = self.books_manager.restore_book(4, 1)
        self.mock_conn.commit.assert_called()
        self.assertTrue(result)

    def test_set_reading_status_commits(self):
        self.mock_cursor.rowcount = 1
        result = self.books_manager.set_reading_status(2, 1, "reading")
        self.mock_conn.commit.assert_called()
        self.assertTrue(result)

    def test_add_tag_to_book_commits(self):
        # Simulate book found
        self.mock_cursor.execute.return_value.fetchone.side_effect = [(123,), (1,)]
        result = self.books_manager.add_tag_to_book(5, 1, "NewTag")
        self.mock_conn.commit.assert_called()
        self.assertTrue(result)

    def test_remove_tag_from_book_commits(self):
        # Simulate book and tag found
        self.mock_cursor.execute.return_value.fetchone.side_effect = [(123,), (1,)]
        result = self.books_manager.remove_tag_from_book(5, 1, "OldTag")
        self.mock_conn.commit.assert_called()
        self.assertTrue(result)

    def test_get_books_by_user_no_commit(self):
        self.books_manager.get_books_by_user(1)
        self.mock_conn.commit.assert_not_called()

    def test_get_book_by_id_no_commit(self):
        self.books_manager.get_book_by_id(1, 1)
        self.mock_conn.commit.assert_not_called()

    def test_get_tags_for_book_no_commit(self):
        self.books_manager.get_tags_for_book(1, 1)
        self.mock_conn.commit.assert_not_called()

if __name__ == "__main__":
    unittest.main()
