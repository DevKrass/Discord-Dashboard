import discord
import sqlite3
import os

DB_FILE = "bot_logs.db"

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # required for roles

client = discord.Client(intents=intents)

# --- Database helpers ---
def connect_db():
    return sqlite3.connect(DB_FILE)

def insert_message(message):
    conn = connect_db()
    cur = conn.cursor()

    # Insert message
    cur.execute("""
        INSERT OR IGNORE INTO messages (
            message_id, guild_id, guild_name, channel_id, channel_name,
            author_id, author_name, author_nickname, timestamp, content
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(message.id),
        str(message.guild.id),
        message.guild.name,
        str(message.channel.id),
        message.channel.name,
        str(message.author.id),
        message.author.name,
        getattr(message.author, "nick", None),
        str(message.created_at),
        message.content
    ))

    # Insert roles
    if isinstance(message.author, discord.Member):
        for role in message.author.roles:
            cur.execute("""
                INSERT INTO roles (message_id, role_name, role_color)
                VALUES (?, ?, ?)
            """, (str(message.id), role.name, str(role.color)))

    conn.commit()
    conn.close()

# --- Event: new messages ---
@client.event
async def on_message(message):
    if message.author.bot:
        return  # skip bot messages if desired
    insert_message(message)

# --- Optional: fetch historical messages on startup ---
async def fetch_history():
    for guild in client.guilds:
        for channel in guild.text_channels:
            try:
                async for msg in channel.history(limit=None):
                    insert_message(msg)
            except Exception as e:
                print(f"Skipped {channel.name}: {e}")

@client.event
async def on_ready():
    print(f"Bot logged in as {client.user}")
    # Optional: Uncomment to fetch history
    # await fetch_history()


client.run(os.environ["DISCORD_BOT_TOKEN"])
