import sqlite3


def init_chat_db():
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            chat_id TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def init_payment_db():
    conn = sqlite3.connect("payments.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            amount REAL,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_payment(user_id, status="completed"):
    conn = sqlite3.connect("payments.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO payments (user_id, status)
        VALUES (?, ?)
    ''', (user_id, status))
    conn.commit()
    conn.close()

def has_paid(user_id):
    conn = sqlite3.connect("payments.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM payments
        WHERE user_id = ? AND status = "completed"
    ''', (user_id,))
    result = cursor.fetchone()[0]
    conn.close()
    return result > 0

def get_allowed_users_from_db():
    conn = sqlite3.connect('payments.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    user_ids = cursor.fetchall()
    allowed_users = [user_id[0] for user_id in user_ids]
    conn.close()
    return allowed_users

def get_payment_history(user_id):
    conn = sqlite3.connect("payments.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT payment_date, amount, status FROM payments
        WHERE user_id = ?
        ORDER BY payment_date ASC
    ''', (user_id,))
    history = cursor.fetchall()
    conn.close()
    return [{"payment_date": row[0], "amount": row[1], "status": row[2]} for row in history]

def save_message(user_id, chat_id, role, content):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO conversations (user_id, chat_id, role, content)
        VALUES (?, ?, ?, ?)
    ''', (user_id, chat_id, role, content))
    conn.commit()
    conn.close()

def get_chat_history(user_id, chat_id):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT role, content FROM conversations
        WHERE user_id = ? AND chat_id = ?
        ORDER BY timestamp ASC
    ''', (user_id, chat_id))
    history = cursor.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in history]

def clear_chat_history(user_id, chat_id):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM conversations
        WHERE user_id = ? AND chat_id = ?
    ''', (user_id, chat_id))
    conn.commit()
    conn.close()