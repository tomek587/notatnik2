import mysql.connector
from mysql.connector import Error
import configparser


class Database:
    def __init__(self, host, user, password, database):
        try:
            self.conn = mysql.connector.connect(host=host, user=user, password=password)
            self.cursor = self.conn.cursor()

            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}`")
            self.cursor.close()
            self.conn.close()

            self.conn = mysql.connector.connect(host=host, user=user, password=password, database=database)
            self.cursor = self.conn.cursor()

            self.create_tables()

        except Error as error:
            print(f"Błąd przy tworzeniu bazy lub połączeniu: {error}")
            self.conn = None
            self.cursor = None

    def create_tables(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    login VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS notatki (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    tresc TEXT NOT NULL,
                    user_id INT,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()
        except Error as error:
            print(f"Błąd przy tworzeniu tabel: {error}")

    def check_user(self, login, password):
        query = "SELECT * FROM users WHERE login = %s AND password = SHA2(%s, 256)"
        self.cursor.execute(query, (login, password))
        result = self.cursor.fetchone()

        if result:
            return result
        else:
            return None

    def check_user_exists(self, login):
        query = "SELECT COUNT(*) FROM users WHERE login = %s"
        self.cursor.execute(query, (login,))
        result = self.cursor.fetchone()

        if result:
            count = result[0]
        else:
            count = 0

        return count > 0

    def insert_user(self, login, password):
        try:
            query = "INSERT INTO users (login, password) VALUES (%s, SHA2(%s, 256))"
            self.cursor.execute(query, (login, password))
            self.conn.commit()
            return True
        except mysql.connector.IntegrityError:
            return False

    def get_user_id(self, login):
        query = "SELECT id FROM users WHERE login = %s"
        self.cursor.execute(query, (login,))
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    def select_notatki_by_user(self, user_id):
        query = "SELECT * FROM notatki WHERE user_id = %s"
        self.cursor.execute(query, (user_id,))
        return self.cursor.fetchall()

    def insert_notatka(self, tresc, user_id):
        query = "INSERT INTO notatki (tresc, user_id) VALUES (%s, %s)"
        self.cursor.execute(query, (tresc, user_id))
        self.conn.commit()

    def delete_notatka(self, notatka_id):
        query = "DELETE FROM notatki WHERE id = %s"
        self.cursor.execute(query, (notatka_id,))
        self.conn.commit()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


config = configparser.ConfigParser()
config.read("config.ini")

host = config["baza"]["host"]
user = config["baza"]["user"]
password = config["baza"]["password"]
database = config["baza"]["dbname"]

baza = Database(host=host, user=user, password=password, database=database)