from flask import Flask, jsonify, request
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)

# -----------------------
# CONFIG
# -----------------------
MONGO_URI = os.getenv("MONGO_URI")  # set this in Render or your local environment
DB_NAME = "Players"
COLLECTION_NAME = "Players"

# -----------------------
# CONNECT TO MONGO
# -----------------------
try:
    client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    client.admin.command("ping")
    print("✅ Successfully connected to MongoDB Atlas")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    raise e

# -----------------------
# FLASK ROUTES
# -----------------------
@app.route("/")
def home():
    return "Players Flask App is running!"

@app.route("/players", methods=["GET"])
def get_players():
    # Optional query param to filter by player name
    name_filter = request.args.get("name")
    query = {"name": name_filter} if name_filter else {}
    players = list(collection.find(query, {"_id": 0}))  # hide MongoDB _id
    return jsonify(players)

@app.route("/players/<player_name>", methods=["GET"])
def get_player(player_name):
    player = collection.find_one({"name": player_name}, {"_id": 0})
    if not player:
        return jsonify({"error": "Player not found"}), 404
    return jsonify(player)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
