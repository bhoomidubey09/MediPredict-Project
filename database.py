import sqlite3
import bcrypt

DB_NAME = "users.db"


def connect_db():
    return sqlite3.connect(DB_NAME)


# CREATE TABLES
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            symptoms TEXT,
            disease TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# PASSWORD HASHING
def hash_password(password):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(password, hashed):
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed.encode("utf-8")
    )


# REGISTER USER
def register_user(username, password):

    hashed_pw = hash_password(password)

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username,password) VALUES (?,?)",
            (username, hashed_pw)
        )

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


# LOGIN USER
def login_user(username, password):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT username,password FROM users WHERE username=?",
        (username,)
    )

    user = cursor.fetchone()

    conn.close()

    if user is None:
        return None

    db_username, db_password = user

    if verify_password(password, db_password):
        return db_username

    return None


# SAVE HISTORY
def save_history(username, symptoms, disease):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO history (username,symptoms,disease) VALUES (?,?,?)",
        (username, symptoms, disease)
    )

    conn.commit()
    conn.close()


# GET HISTORY
def get_history(username):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT date,symptoms,disease
        FROM history
        WHERE username=?
        ORDER BY date DESC
        """,
        (username,)
    )

    data = cursor.fetchall()

    conn.close()

    return data


if __name__ == "__main__":
    create_tables()