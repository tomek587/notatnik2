import time
import random
import string
from database import Database
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

host = config["baza"]["host"]
user = config["baza"]["user"]
password = config["baza"]["password"]
database = config["baza"]["dbname"]

db = Database(host=host, user=user, password=password, database=database)


def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def test_insert_users(n=100):
    start = time.time()
    success = 0
    for _ in range(n):
        login = random_string()
        passwd = random_string()
        if db.insert_user(login, passwd):
            success += 1
    end = time.time()
    print(f"Wstawiono {success}/{n} użytkowników w {end - start:.2f} s")


def test_insert_notes(n=100):
    login = random_string()
    passwd = random_string()
    db.insert_user(login, passwd)
    user_id = db.get_user_id(login)

    start = time.time()
    for _ in range(n):
        content = random_string(50)
        db.insert_notatka(content, user_id)
    end = time.time()
    print(f"Wstawiono {n} notatek w {end - start:.2f} s")


def test_select_notes(user_id):
    start = time.time()
    notes = db.select_notatki_by_user(user_id)
    end = time.time()
    print(f"Pobrano {len(notes)} notatek w {end - start:.4f} s")


def test_delete_notes(user_id):
    notes = db.select_notatki_by_user(user_id)
    start = time.time()
    for note in notes:
        db.delete_notatka(note[0])
    end = time.time()
    print(f"Usunięto {len(notes)} notatek w {end - start:.2f} s")


if _name_ == "_main_":
    print("Test: Insert users")
    test_insert_users(100)

    print("\nTest: Insert notes")
    test_insert_notes(200)

    user_id = db.get_user_id(login)
    print("\nTest: Select notes")
    test_select_notes(user_id)

    print("\nTest: Delete notes")
    test_delete_notes(user_id)

    db.close()