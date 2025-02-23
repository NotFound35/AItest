import sqlite3

# Инициализация базы данных
def init_db():
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

# Сохранение сообщения в БД
def save_message(user_id, chat_id, role, content):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO conversations (user_id, chat_id, role, content)
        VALUES (?, ?, ?, ?)
    ''', (user_id, chat_id, role, content))
    conn.commit()
    conn.close()

# Получение истории чата
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

# Очистка истории чата
def clear_chat_history(user_id, chat_id):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM conversations
        WHERE user_id = ? AND chat_id = ?
    ''', (user_id, chat_id))
    conn.commit()
    conn.close()
