from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

DB_FILE = "comments.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def load_comments():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            track_id TEXT,
            user TEXT,
            comment TEXT,
            PRIMARY KEY(track_id, user)
        )
    """)
    rows = conn.execute("SELECT * FROM comments").fetchall()
    conn.close()
    comments = {}
    for row in rows:
        tid = row["track_id"]
        if tid not in comments:
            comments[tid] = {}
        comments[tid][row["user"]] = row["comment"]
    return comments

def save_comment_to_db(track_id, user, comment):
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO comments (track_id, user, comment)
        VALUES (?, ?, ?)
        ON CONFLICT(track_id, user) DO UPDATE SET comment=excluded.comment
    """, (track_id, user, comment))
    conn.commit()
    conn.close()

@app.route("/", methods=["GET"])
def index():
    tracks = [
        {"name": "Track One", "artist": "Artist A"},
        {"name": "Track Two", "artist": "Artist B"}
    ]
    comments = load_comments()
    return render_template("index.html", tracks=tracks, comments=comments)

@app.route("/save_comment", methods=["POST"])
def save_comment():
    track_id = request.form["track_id"]
    kai_comment = request.form.get("kai_comment", "")
    victoria_comment = request.form.get("victoria_comment", "")
    if kai_comment:
        save_comment_to_db(track_id, "kai", kai_comment)
    if victoria_comment:
        save_comment_to_db(track_id, "victoria", victoria_comment)
    return redirect("/")
