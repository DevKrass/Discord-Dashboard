import sqlite3

DB_FILE = "discord_logs.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # --- Messages table ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        message_id TEXT PRIMARY KEY,
        guild_id TEXT,
        guild_name TEXT,
        channel_id TEXT,
        channel_name TEXT,
        author_id TEXT,
        author_name TEXT,
        author_nickname TEXT,
        timestamp TEXT,
        content TEXT
    )
    """)

    # --- Roles table ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS roles (
        message_id TEXT,
        role_name TEXT,
        role_color TEXT
    )
    """)

    # --- Flagged words table ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS flagged_words (
        word TEXT PRIMARY KEY
    )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
