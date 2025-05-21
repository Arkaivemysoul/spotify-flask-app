from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)
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

@app.route("/", methods=["GET"])
def index():
    tracks = [
        {"name": "Track One", "artist": "Artist A"},
        {"name": "Track Two", "artist": "Artist B"}
    ]
    comments = load_comments()

    output = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Our Collective Consciousness</title>
        <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'>
        <link href='https://fonts.googleapis.com/css2?family=Cinzel:wght@700&display=swap' rel='stylesheet'>
        <style>
            body {
                font-family: 'Cinzel', serif;
                background-image: url('https://images2.alphacoders.com/138/1386740.png');
                background-size: cover;
                background-repeat: no-repeat;
                background-position: center center;
                background-attachment: fixed;
                background-color: #000000;
                min-height: 100vh;
                color: #ffffff;
            }
            .overlay {
                background-color: rgba(0, 0, 0, 0.75);
                min-height: 100vh;
                padding: 2rem;
            }
            .card {
                background-color: rgba(30, 30, 30, 0.6) !important;
                border: none;
                color: #ffffff;
                backdrop-filter: blur(4px);
            }
            .card-title {
                font-size: 1.6rem;
                font-weight: 700;
                text-shadow: 0 0 6px rgba(0, 0, 0, 0.7);
            }
            label, .card-text, h1, p {
                color: #ffffff;
                text-shadow: 0 0 4px rgba(0, 0, 0, 0.6);
            }
            textarea {
                width: 100%;
                padding: 12px;
                border-radius: 6px;
                border: none;
                background-color: #f8f9fa;
                color: #000;
                font-size: 1rem;
                resize: vertical;
                min-height: 100px;
            }
            @media only screen and (max-width: 768px) {
                body {
                    background-image: url('https://i.imgur.com/E4kkNq6.jpeg');
                    background-attachment: scroll;
                }
            }
        </style>
    </head>
    <body>
        <div class='overlay'>
            <div class='container'>
                <h1 class='mb-5 text-center'>🌌 Our Collective Consciousness</h1>
    """

    for track in tracks:
        name = track.get('name', 'Unknown')
        track_id = name.lower().strip().replace(' ', '_')
        artist = track.get('artist', 'Unknown')

        kai_comment = comments.get(track_id, {}).get("kai", "")
        vic_comment = comments.get(track_id, {}).get("victoria", "")

        output += f"""
        <div class='card mb-4 p-3 shadow-lg'>
            <div class='row g-3'>
                <div class='col-md-5'>
                    <h5 class='card-title'>{name}</h5>
                    <p class='card-text'><em>{artist}</em></p>
                </div>
                <div class='col-md-7'>
                    <div class='mb-3'>
                        <label for='kai_{track_id}'>Kai's Comment:</label>
                        <textarea id='kai_{track_id}' onblur="saveComment('{track_id}', 'kai')" placeholder='yap yap yap'>{kai_comment}</textarea>
                    </div>
                    <div>
                        <label for='vic_{track_id}'>Victoria's Comment:</label>
                        <textarea id='vic_{track_id}' onblur="saveComment('{track_id}', 'victoria')" placeholder='yap yap yap'>{vic_comment}</textarea>
                    </div>
                </div>
            </div>
        </div>
        """

    output += """
            </div>
        </div>
        <script>
        async function saveComment(trackId, author) {
            const text = document.getElementById(`${author}_${trackId}`).value;
            const res = await fetch('/save_comment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ track_id: trackId, author, text })
            });
            const result = await res.json();
            if (result.status !== 'success') alert('Failed to save comment');
        }
        </script>
    </body>
    </html>
    """
    return output

@app.route("/save_comment", methods=["POST"])
def save_comment():
    data = request.get_json()
    track_id = data.get("track_id")
    author = data.get("author")
    text = data.get("text")

    success = save_comment_to_db(track_id, author, text)
    if success:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error"})

@app.route("/load_comments")
def get_comments():
    return jsonify(load_comments())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)

