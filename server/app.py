from flask import Flask, jsonify, send_from_directory
from queries import *  # absolute import
import os

app = Flask(__name__, static_folder="../client/build")

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

# --- Serve React frontend ---
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")
