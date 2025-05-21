from flask import Flask, jsonify, request, render_template
import json
import sqlite3

app = Flask(__name__)

DB_FILE = "comments.db"
TRACKS_FILE = "tracks.json"

# Database connection
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# Load comments from DB
def load_comments():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            track_id TEXT,
            user TEXT,
            comment TEXT,
            PRIMARY KEY(track_id, user)
        )
    """)
    rows = cursor.execute("SELECT * FROM comments").fetchall()
    conn.close()

    comments = {}
    for row in rows:
        track_id = row["track_id"]
        user = row["user"]
        text = row["comment"]
        if track_id not in comments:
            comments[track_id] = {}
        comments[track_id][user] = text
    return comments

# Save new or updated comment
def save_comment_to_db(track_id, author, text):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO comments (track_id, user, comment)
        VALUES (?, ?, ?)
        ON CONFLICT(track_id, user) DO UPDATE SET comment=excluded.comment
    """, (track_id, author, text))
    conn.commit()
    conn.close()
    return True

# Load playlist from JSON
def load_tracks():
    with open(TRACKS_FILE, "r") as f:
        return json.load(f)["tracks"][::-1]  # newest first

# Homepage
@app.route("/")
def index():
    tracks = load_tracks()
    comments = load_comments()
    return render_template("index.html", tracks=tracks, comments=comments)

# Save comment endpoint
@app.route("/save_comment", methods=["POST"])
def save_comment():
    data = request.get_json()
    track_id = data.get("track_id")
    author = data.get("author")
    text = data.get("text")

    success = save_comment_to_db(track_id, author, text)
    return jsonify({"status": "success" if success else "error"})

# Load all comments (API endpoint)
@app.route("/load_comments")
def get_comments():
    return jsonify(load_comments())

# Run the app locally
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)




