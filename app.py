from flask import Flask, redirect, request, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import json
from dotenv import load_dotenv

# Load your credentials from .env file
load_dotenv()

app = Flask(__name__)
COMMENTS_FILE = 'comments.json'

# Spotify login setup
sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="playlist-read-private"
)

def load_comments():
    if os.path.exists(COMMENTS_FILE):
        with open(COMMENTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_comments(data):
    with open(COMMENTS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route("/")
def index():
    auth_url = sp_oauth.get_authorize_url()
    return f'<a href="{auth_url}">Login to Spotify</a>'

@app.route("/callback")
def callback():
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    sp = spotipy.Spotify(auth=token_info['access_token'])

    playlist_id = "5hdA5T6opqq1X8d9uXwf7I"
    results = sp.playlist_items(playlist_id)
    tracks = results['items']
    comments = load_comments()

    output = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Our Collective Consciousness</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Quicksand&family=Playfair+Display:wght@700&family=UnifrakturCook:700&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Quicksand', sans-serif;
                background: url('https://images2.alphacoders.com/138/1386740.png') no-repeat center center fixed;
                background-size: cover;
                color: #ffffff;
            }
            .overlay {
                background-color: rgba(0, 0, 0, 0.2);
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
                font-family: 'UnifrakturCook', cursive;
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
        </style>
    </head>
    <body>
        <div class="overlay">
            <div class="container">
                <h1 class="mb-5 text-center">🌌 Our Collective Consciousness</h1>
    """

    for item in tracks:
        track = item['track']
        track_id = track['id']
        name = track['name']
        artist = track['artists'][0]['name']
        added = item['added_at'][:10]

        kai_comment = comments.get(track_id, {}).get("kai", "")
        vic_comment = comments.get(track_id, {}).get("victoria", "")

        output += f"""
        <div class="card mb-4 p-3 shadow-lg">
            <div class="row g-3">
                <div class="col-md-5">
                    <h5 class="card-title">{name}</h5>
                    <p class="card-text"><em>{artist}</em><br><small>Added on {added}</small></p>
                </div>
                <div class="col-md-7">
                    <div class="mb-3">
                        <label for="kai_{track_id}">Comment (Kai):</label>
                        <textarea id="kai_{track_id}" onblur="saveComment('{track_id}', 'kai')" placeholder="yap yap yap">{kai_comment}</textarea>
                    </div>
                    <div>
                        <label for="vic_{track_id}">Comment (Victoria):</label>
                        <textarea id="vic_{track_id}" onblur="saveComment('{track_id}', 'victoria')" placeholder="yap yap yap">{vic_comment}</textarea>
                    </div>
                </div>
            </div>
        </div>
        """

    output += """
    <script src='/static/script.js'></script>
    </body>
    </html>
    """

    return output

@app.route("/load_comments")
def get_comments():
    return jsonify(load_comments())

@app.route("/save_comment", methods=["POST"])
def save_comment():
    data = request.json
    track_id = data["track_id"]
    author = data["author"]
    text = data["text"]

    comments = load_comments()
    if track_id not in comments:
        comments[track_id] = {}
    comments[track_id][author] = text

    save_comments(comments)
    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
