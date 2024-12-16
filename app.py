from flask import Flask
import os

app = Flask(__name__)

PORT = int(os.environ.get("PORT", 5000))

@app.route("/")
def home():
    return "Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
