from flask import Flask, jsonify, request
import os
from pymongo.mongo_client import MongoClient
import certifi
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS so frontend can call backend

# -----------------------
# CONFIG
# -----------------------
MONGO_URI = os.getenv("MONGO_URI")  # Set in Render Environment Variables
DB_NAME = "Players"
COLLECTION_NAME = "Players"

# -----------------------
# CONNECT TO MONGO
# -----------------------
try:
    client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    client.admin.command("ping")
    print("✅ Connected to MongoDB Atlas")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    raise e

# -----------------------
# ROUTES
# -----------------------

@app.route("/")
def home():
    return "Players Flask App is running!"

# GET all players
@app.route("/players", methods=["GET"])
def get_players():
    players = list(collection.find({}, {"_id": 0}))
    return jsonify(players)

# GET single player
@app.route("/players/<player_name>", methods=["GET"])
def get_player(player_name):
    player = collection.find_one({"name": player_name}, {"_id": 0})
    if not player:
        return jsonify({"error": "Player not found"}), 404
    return jsonify(player)

# POST - Add new player
@app.route("/players", methods=["POST"])
def add_player():
    data = request.get_json()
    if not data.get("name"):
        return jsonify({"error": "Player name is required"}), 400
    if collection.find_one({"name": data["name"]}):
        return jsonify({"error": "Player already exists"}), 400
    collection.insert_one(data)
    return jsonify({"message": "Player added successfully"}), 201

# PUT - Update player
@app.route("/players/<player_name>", methods=["PUT"])
def update_player(player_name):
    data = request.get_json()
    result = collection.update_one({"name": player_name}, {"$set": data})
    if result.matched_count == 0:
        return jsonify({"error": "Player not found"}), 404
    return jsonify({"message": "Player updated successfully"})

# DELETE - Delete player
@app.route("/players/<player_name>", methods=["DELETE"])
def delete_player(player_name):
    result = collection.delete_one({"name": player_name})
    if result.deleted_count == 0:
        return jsonify({"error": "Player not found"}), 404
    return jsonify({"message": f"{player_name} deleted successfully"})

# SEARCH - server-side search
@app.route("/players/search", methods=["GET"])
def search_players():
    name = request.args.get("name", "")
    position = request.args.get("position", "")
    club = request.args.get("club", "")

    query = {}
    if name: query["name"] = {"$regex": name, "$options": "i"}
    if position: query["position"] = position
    if club: query["club"] = {"$regex": club, "$options": "i"}

    players = list(collection.find(query, {"_id": 0}))
    return jsonify(players)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
