import unittest
from unittest.mock import patch, MagicMock
from baza import Database


class TestDatabase(unittest.TestCase):
    @patch("database.mysql.connector.connect")
    def setUp(self, mock_connect):

        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        mock_connect.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cursor

        self.db = Database(host="localhost", user="root", password="", database="test_db")

    def test_create_tables(self):
        self.mock_cursor.execute.assert_any_call("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                login VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)
        self.mock_cursor.execute.assert_any_call("""
            CREATE TABLE IF NOT EXISTS notatki (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tresc TEXT NOT NULL,
                user_id INT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def test_insert_user_success(self):
        self.mock_cursor.execute.side_effect = None
        result = self.db.insert_user("test_user", "test_password")
        self.assertTrue(result)
        self.mock_cursor.execute.assert_called_with(
            "INSERT INTO users (login, password) VALUES (%s, SHA2(%s, 256))",
            ("test_user", "test_password")
        )

    def test_insert_user_duplicate(self):
        self.mock_cursor.execute.side_effect = self.mock_conn.IntegrityError
        result = self.db.insert_user("existing_user", "test_password")
        self.assertFalse(result)

    def test_check_user_exists_true(self):
        self.mock_cursor.fetchone.return_value = (1,)
        result = self.db.check_user_exists("test_user")
        self.assertTrue(result)

    def test_check_user_exists_false(self):
        self.mock_cursor.fetchone.return_value = (0,)
        result = self.db.check_user_exists("non_existent_user")
        self.assertFalse(result)


    def test_insert_notatka(self):
        self.db.insert_notatka("Testowa notatka", 1)
        self.mock_cursor.execute.assert_called_with(
            "INSERT INTO notatki (tresc, user_id) VALUES (%s, %s)",
            ("Testowa notatka", 1)
        )

    def test_select_notatki_by_user(self):
        self.mock_cursor.fetchall.return_value = [(1, "Notatka1", 1, "2025-03-07 12:00:00")]
        result = self.db.select_notatki_by_user(1)
        self.assertEqual(result, [(1, "Notatka1", 1, "2025-03-07 12:00:00")])

    def test_delete_notatka(self):
        self.db.delete_notatka(5)
        self.mock_cursor.execute.assert_called_with(
            "DELETE FROM notatki WHERE id = %s", (5,)
        )

    def tearDown(self):
        self.db.close()
        self.mock_cursor.close.assert_called()
        self.mock_conn.close.assert_called()


unittest.main()