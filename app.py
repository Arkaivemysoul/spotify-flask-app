from flask import Flask, jsonify, request
import requests
import csv
import json
import os
import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

app = Flask(__name__)
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
COMMENTS_SHEET_NAME = os.getenv("COMMENTS_SHEET_NAME", "comments")

# Set up Google Sheets API access
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

def fetch_playlist():
    try:
        sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("tracks")
        data = sheet.get_all_records()
        return {"tracks": data}
    except Exception as e:
        return {"error": str(e)}

def load_comments():
    try:
        sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet(COMMENTS_SHEET_NAME)
        rows = sheet.get_all_records()
        comments = {}
        for row in rows:
            track_id = row["track_id"]
            author = row["author"]
            text = row["text"]
            if track_id not in comments:
                comments[track_id] = {}
            comments[track_id][author] = text
        return comments
    except Exception as e:
        print("Error loading comments:", e)
        return {}

def save_comment_to_sheet(track_id, author, text):
    try:
        sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet(COMMENTS_SHEET_NAME)
        headers = sheet.row_values(1)
        if headers != ['track_id', 'author', 'text']:
            print("Header mismatch or missing, aborting write.")
            return False
        sheet.append_row([track_id, author, text])
        return True
    except Exception as e:
        print("Error saving comment to Google Sheet:", e)
        return False

@app.route("/", methods=["GET"])
def index():
    playlist = fetch_playlist()
    if not playlist or "tracks" not in playlist:
        return f"Failed to load playlist. Response: {json.dumps(playlist, indent=2)}"

    tracks = playlist["tracks"]
    comments = load_comments()

    output = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Our Collective Consciousness</title>
        <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'>
        <link href='https://fonts.googleapis.com/css2?family=Quicksand&family=Playfair+Display:wght@700&family=Cinzel:wght@700&display=swap' rel='stylesheet'>
        <style>
            body {
                font-family: 'Quicksand', sans-serif;
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
                background-color: rgba(0, 0, 0, 0.5);
                min-height: 100vh;
                padding: 2rem;
            }
            .card {
                background-color: rgba(30, 30, 30, 0.2) !important;
                border: none;
                color: #ffffff;
                backdrop-filter: blur(4px);
            }
            .card-title {
                font-family: 'Cinzel', serif;
                font-size: 1.6rem;
                font-weight: 700;
                text-shadow: 0 0 4px rgba(0, 0, 0, 0.6);
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
                font-family: 'Century Schoolbook', Georgia, serif;
                font-size: 1rem;
                resize: vertical;
                min-height: 100px;
            }
            @media only screen and (max-width: 768px) {
                body {
                    background-image: url('https://i.imgur.com/E4kkNq6.jpeg');
                    background-size: cover;
                    background-repeat: no-repeat;
                    background-position: center center;
                    background-attachment: scroll;
                    min-height: 100vh;
                    background-color: #000;
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
                        <label for='kai_{track_id}'>Comment (Kai):</label>
                        <textarea id='kai_{track_id}' onblur="saveComment('{track_id}', 'kai')" placeholder='yap yap yap'>{kai_comment}</textarea>
                    </div>
                    <div>
                        <label for='vic_{track_id}'>Comment (Victoria):</label>
                        <textarea id='vic_{track_id}' onblur="saveComment('{track_id}', 'victoria')" placeholder='yap yap yap'>{vic_comment}</textarea>
                    </div>
                </div>
            </div>
        </div>
        """

    output += """
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

    success = save_comment_to_sheet(track_id, author, text)
    if success:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error"})

@app.route("/load_comments")
def get_comments():
    return jsonify(load_comments())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)


