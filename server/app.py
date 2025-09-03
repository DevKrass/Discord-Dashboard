from flask import Flask, jsonify
from .queries import *

app = Flask(__name__, static_folder="public")

# --- API Routes ---
@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/api/top-users")
def api_top_users():
    return jsonify(get_top_users())

@app.route("/api/messages-per-channel")
def api_messages_per_channel():
    return jsonify(get_messages_per_channel())

@app.route("/api/flagged-users")
def api_flagged_users():
    return jsonify(get_flagged_messages())
