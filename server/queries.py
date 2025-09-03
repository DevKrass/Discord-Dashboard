import psycopg2
import os

# --- DB Connection ---
def connect_db():
    return psycopg2.connect(os.environ["DATABASE_URL"])

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
    flagged_words = get_flagged_words()
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT author_name, content FROM messages")

    counts = {}
    for author, content in cur.fetchall():
        if content:
            lower_content = content.lower()
            for word in flagged_words:
                if word.lower() in lower_content:
                    counts[author] = counts.get(author, 0) + 1
                    break

    conn.close()
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [{"author": u, "count": c} for u, c in sorted_counts[:limit]]
