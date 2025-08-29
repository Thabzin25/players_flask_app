from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from pymongo.mongo_client import MongoClient
import certifi

app = Flask(__name__)
CORS(app)  # Allow all origins (adjust for production)

# -----------------------
# CONFIG
# -----------------------
MONGO_URI = os.getenv("MONGO_URI")  # Set in Render secrets
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

# Fetch all players with optional filters
@app.route("/players", methods=["GET"])
def get_players():
    name_filter = request.args.get("name")
    position_filter = request.args.get("position")
    query = {}
    if name_filter:
        query["name"] = {"$regex": name_filter, "$options": "i"}
    if position_filter:
        query["position"] = position_filter
    players = list(collection.find(query, {"_id": 0}))
    return jsonify(players)

# Fetch a single player
@app.route("/players/<player_name>", methods=["GET"])
def get_player(player_name):
    player = collection.find_one({"name": player_name}, {"_id": 0})
    if not player:
        return jsonify({"error": "Player not found"}), 404
    return jsonify(player)

# Add a new player
@app.route("/players", methods=["POST"])
def add_player():
    data = request.json
    if not data.get("name") or not data.get("age") or not data.get("position"):
        return jsonify({"error": "Name, age, and position are required"}), 400
    if collection.find_one({"name": data["name"]}):
        return jsonify({"error": "Player with this name already exists"}), 400
    collection.insert_one(data)
    return jsonify({"message": "Player added successfully"}), 201

# Update a player
@app.route("/players/<player_name>", methods=["PUT"])
def update_player(player_name):
    data = request.json
    player = collection.find_one({"name": player_name})
    if not player:
        return jsonify({"error": "Player not found"}), 404
    collection.update_one({"name": player_name}, {"$set": data})
    return jsonify({"message": "Player updated successfully"})

# Delete a player
@app.route("/players/<player_name>", methods=["DELETE"])
def delete_player(player_name):
    player = collection.find_one({"name": player_name})
    if not player:
        return jsonify({"error": "Player not found"}), 404
    collection.delete_one({"name": player_name})
    return jsonify({"message": f"{player_name} deleted successfully"})

# -----------------------
# PLAYER REPORTS (for charts)
# -----------------------
@app.route("/player-reports", methods=["GET"])
def player_reports():
    players = list(collection.find({}, {"_id": 0, "name": 1, "position": 1, "rating": 1}))
    
    # Sample ratings if not present
    for p in players:
        if "rating" not in p:
            p["rating"] = round(5 + 5 * os.urandom(1)[0]/255, 1)  # Random 5-10 rating
    
    # Count positions
    positions_count = {}
    for p in players:
        pos = p.get("position", "Unknown")
        positions_count[pos] = positions_count.get(pos, 0) + 1
    
    return jsonify({"players": players, "positions_count": positions_count})

# -----------------------
# RUN APP
# -----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
