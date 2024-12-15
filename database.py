import sqlite3

# Initialize database connection
def init_db():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()

    # Create users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            name TEXT NOT NULL,
            phone_number TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Add user to the database
def add_user(name, phone_number, user_id):
    try:
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO users (user_id, name, phone_number)
            VALUES (?, ?, ?)
        ''', (user_id, name, phone_number))

        conn.commit()
    except sqlite3.IntegrityError:
        print(f"User with ID {user_id} already exists in the database.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

# Check if user exists in the database
def user_exists(user_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 1 FROM users WHERE user_id = ?
    ''', (user_id,))

    exists = cursor.fetchone() is not None
    conn.close()

    return exists

# Retrieve user details from the database
def get_user(user_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT name, phone_number FROM users WHERE user_id = ?
    ''', (user_id,))

    user = cursor.fetchone()
    conn.close()

    if user:
        return {"name": user[0], "phone_number": user[1]}
    else:
        return None

def check_user(user_id):
    connection = sqlite3.connect("bot_database.db")
    sql = connection.cursor()
    checker = sql.execute("SELECT * FROM users WHERE user_id=?;",
                          (user_id, )).fetchone()
    if checker:
        return True
    elif not checker:
        return False


# Initialize the database
init_db()
