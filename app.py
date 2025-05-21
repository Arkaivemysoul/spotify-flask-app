from flask import Flask, jsonify, request
from db import load_comments, save_comment_to_db

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({"message": "It works!"})

@app.route("/load_comments")
def get_comments():
    return jsonify(load_comments())

@app.route("/save_comment", methods=["POST"])
def save_comment():
    data = request.get_json()
    track_id = data.get("track_id")
    author = data.get("author")
    text = data.get("text")
    if save_comment_to_db(track_id, author, text):
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

if __name__ == "__main__":
    app.run(debug=True)





