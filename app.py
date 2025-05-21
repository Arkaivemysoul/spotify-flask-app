import sqlite3

DB_FILE = "comments.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def load_comments():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS comments (track_id TEXT, user TEXT, comment TEXT, PRIMARY KEY(track_id, user))")
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

def save_comment_to_db(track_id, author, text):
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
    cursor.execute("""
        INSERT INTO comments (track_id, user, comment)
        VALUES (?, ?, ?)
        ON CONFLICT(track_id, user) DO UPDATE SET comment=excluded.comment
    """, (track_id, author, text))
    conn.commit()
    conn.close()
    return True




