import json
import sqlite3
from pathlib import Path

DB_FILE = "parsed_logs.db"
EXPORT_FOLDER = "exports"  # folder with multiple JSON files

def init_db():
    conn = sqlite3.connect(DB_FILE)
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
        timestamp TEXT,
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
    conn.commit()
    return conn

def flatten_message(msg, guild, channel):
    author = msg["author"]
    flat = {
        "message_id": msg["id"],
        "timestamp": msg["timestamp"],
        "content": msg.get("content", ""),
        "guild_id": guild.get("id", "unknown"),
        "guild_name": guild.get("name", "unknown"),
        "channel_id": channel.get("id", "unknown"),
        "channel_name": channel.get("name", "unknown"),
        "author_id": author["id"],
        "author_name": author["name"],
        "author_nickname": author.get("nickname")
    }
    roles = [{"message_id": msg["id"], "role_name": r["name"], "role_color": r["color"]} for r in author.get("roles", [])]
    return flat, roles

def insert_message(cur, flat, roles):
    cur.execute("""
        INSERT OR IGNORE INTO messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        flat["message_id"], flat["guild_id"], flat["guild_name"],
        flat["channel_id"], flat["channel_name"],
        flat["author_id"], flat["author_name"], flat["author_nickname"],
        flat["timestamp"], flat["content"]
    ))
    for role in roles:
        cur.execute("INSERT INTO roles VALUES (?, ?, ?)", (role["message_id"], role["role_name"], role["role_color"]))

def process_file(cur, file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Determine format: full metadata vs messages-only
    if isinstance(data, list):
        messages = data
        guild = {"id": "unknown", "name": "unknown"}
        channel = {"id": "unknown", "name": Path(file_path).stem}
    else:
        messages = data.get("messages", [])
        guild = data.get("guild", {"id": "unknown", "name": "unknown"})
        channel = data.get("channel", {"id": "unknown", "name": "unknown"})
    
    for msg in messages:
        author_name = msg["author"]["name"]
        if author_name.lower() == "rythm":  # skip this bot
            continue
        
        flat, roles = flatten_message(msg, guild, channel)
        insert_message(cur, flat, roles)

def main():
    conn = init_db()
    cur = conn.cursor()
    
    folder = Path(EXPORT_FOLDER)
    for file_path in folder.glob("*.json"):
        print(f"Processing {file_path.name} ...")
        process_file(cur, file_path)

    conn.commit()
    conn.close()
    print("✅ All files processed into database.")

if __name__ == "__main__":
    main()
