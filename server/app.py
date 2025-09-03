from flask import Flask, jsonify
import psycopg2
import os

app = Flask(__name__)

# --- DB Connection ---
def connect_db():
    return psycopg2.connect(os.environ["DATABASE_URL"])

# --- DB Initialization ---
def init_db():
    conn = connect_db()
    cur = conn.cursor()
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
        timestamp TIMESTAMP,
        content TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS roles (
        message_id TEXT,
        role_name TEXT,
        role_color TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS flagged_words (
        word TEXT PRIMARY KEY
    )
    """)
    conn.commit()
    conn.close()

# --- Queries ---
def get_flagged_words():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT word FROM flagged_words")
    words = [row[0] for row in cur.fetchall()]
    conn.close()
    return words

def get_top_users(limit=10):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT author_name, COUNT(*) as message_count
        FROM messages
        GROUP BY author_id, author_name
        ORDER BY message_count DESC
        LIMIT %s
    """, (limit,))
    results = [{"author": row[0], "count": row[1]} for row in cur.fetchall()]
    conn.close()
    return results

def get_messages_per_channel():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT channel_name, COUNT(*) as message_count
        FROM messages
        GROUP BY channel_id, channel_name
        ORDER BY message_count DESC
    """)
    results = [{"channel": row[0], "count": row[1]} for row in cur.fetchall()]
    conn.close()
    return results

def get_flagged_messages(limit=10):
    FLAGGED_WORDS = get_flagged_words()
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT author_name, content FROM messages")

    counts = {}
    for author, content in cur.fetchall():
        if content:
            lower_content = content.lower()
            for word in FLAGGED_WORDS:
                if word.lower() in lower_content:
                    counts[author] = counts.get(author, 0) + 1
                    break

    conn.close()
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [{"author": u, "count": c} for u, c in sorted_counts[:limit]]

# --- API Routes ---
@app.route("/api/top-users")
def api_top_users():
    return jsonify(get_top_users())

@app.route("/api/messages-per-channel")
def api_messages_per_channel():
    return jsonify(get_messages_per_channel())

@app.route("/api/flagged-users")
def api_flagged_users():
    return jsonify(get_flagged_messages())

# --- Start ---
if __name__ == "__main__":
    init_db()
