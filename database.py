# import os
# import bcrypt
# import mysql.connector
# from dotenv import load_dotenv

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# env_path = os.path.join(BASE_DIR, ".env")

# load_dotenv(env_path)

# DB_CONFIG = {
#     "host": os.getenv("DB_HOST"),
#     "user": os.getenv("DB_USER"),
#     "password": os.getenv("DB_PASSWORD"),
#     "database": os.getenv("DB_NAME")
# }

# if not all(DB_CONFIG.values()):
#     raise RuntimeError(
#         "Database environment variables are missing."
#     )


# # CONNECT DATABASE
# def connect_db():
#     # print("DB_CONFIG =", DB_CONFIG)
#     return mysql.connector.connect(**DB_CONFIG)



# # CREATE TABLES
# def create_tables():
#     conn = connect_db()
#     cursor = conn.cursor()

#     # USERS TABLE
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             username VARCHAR(100) UNIQUE,
#             password VARCHAR(255)
#         )
#     """)

#     # HISTORY TABLE
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS history (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             username VARCHAR(100),
#             symptoms TEXT,
#             disease VARCHAR(100),
#             date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     """)

#     conn.commit()
#     cursor.close()
#     conn.close()


# # REGISTER USER
# def register_user(username, password):
#     hashed_pw = hash_password(password)

#     conn = connect_db()
#     cursor = conn.cursor()

#     try:
#         cursor.execute(
#             "INSERT INTO users (username, password) VALUES (%s, %s)",
#             (username, hashed_pw)
#         )
#         conn.commit()
#         return True
#     # except:
#     #     return False
#     except mysql.connector.Error as e:
#         print(f"Registration error: {e}")
#         return False
#     finally:
#         cursor.close()
#         conn.close()


# # LOGIN USER
# def login_user(username, password):
#     conn = connect_db()
#     cursor = conn.cursor()

#     try:
#         cursor.execute(
#             "SELECT username, password FROM users WHERE username = %s",
#             (username,)
#         )

#         user = cursor.fetchone()

#         if user is None:
#             return None

#         db_username, db_password = user

#         if verify_password(password, db_password):
#             return db_username

#         return None

#     finally:
#         cursor.close()
#         conn.close()


# def hash_password(password: str) -> str:
#     return bcrypt.hashpw(
#         password.encode("utf-8"),
#         bcrypt.gensalt()
#     ).decode("utf-8")


# def verify_password(password: str, hashed: str) -> bool:
#     return bcrypt.checkpw(
#         password.encode("utf-8"),
#         hashed.encode("utf-8")
#     )




# # SAVE HISTORY
# def save_history(username, symptoms, disease):
#     conn = None
#     cursor = None

#     try:
#         conn = connect_db()
#         cursor = conn.cursor()

#         cursor.execute(
#             "INSERT INTO history (username, symptoms, disease) VALUES (%s, %s, %s)",
#              (username, symptoms, disease)
#         )

#         conn.commit()

#     except mysql.connector.Error as e:
#         print(f"Save history error: {e}")

#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()


# # GET HISTORY
# def get_history(username):
#     conn = None
#     cursor = None

#     try:
#         conn = connect_db()
#         cursor = conn.cursor()

#         cursor.execute(
#             "SELECT date, symptoms, disease FROM history WHERE username=%s ORDER BY date DESC",
#              (username,)
#         )

#         return cursor.fetchall()
    
#     except mysql.connector.Error as e:
#         print(f"History error: {e}")
#         return []

#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()


# if __name__ == "__main__":
#     create_tables()
#     print("Database connected and tables created!")


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