import os.path
import sqlite3

from flask import abort


def create_db():
    try:
        connection = sqlite3.connect('database.db')
        with open('schema.sql') as f:
            connection.executescript(f.read())
    except Exception as err:
        print(f"Connection error {err}")


def get_db_connection():
    try:
        if not os.path.isfile("database.db"):
            create_db()
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as err:
        print(err)


def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


def make_db_record(dictionary: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    for key, value in dictionary.items():
        cur.execute("INSERT INTO posts (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
    conn.close()

