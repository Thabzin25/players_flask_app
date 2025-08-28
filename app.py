from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime
import os

# -----------------------
# CONFIG
# -----------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://thabzin25_db_user:MEjbEk05d0Ks3Muv@players.khmqi7k.mongodb.net/?retryWrites=true&w=majority")
DB_NAME = "Players"
COLLECTION_NAME = "Players"

# -----------------------
# CONNECT TO MONGO
# -----------------------
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    client.admin.command("ping")
    print("✅ Connected to MongoDB Atlas")
except ConnectionFailure as e:
    print(f"❌ MongoDB connection failed: {e}")
    exit(1)

# -----------------------
# FLASK APP
# -----------------------
app = Flask(__name__)

# -----------------------
# READ ENDPOINTS
# -----------------------
@app.route("/")
def home():
    return "Players API is running!"

@app.route("/query_players", methods=["GET"])
def query_players():
    """
    Query players by name. Case-insensitive.
    Example: /query_players?name=Relebohile
    """
    name = request.args.get("name", "").strip()
    if not name:
        return jsonify({"error": "Please provide a player name using ?name=<player_name>"}), 400

    results = list(collection.find({"name": {"$regex": f"^{name}", "$options": "i"}}, {"_id": 0}))
    if not results:
        return jsonify({"message": "No players found"}), 404

    return jsonify(results)

@app.route("/all_players", methods=["GET"])
def all_players():
    results = list(collection.find({}, {"_id": 0}))
    return jsonify(results)

@app.route("/count_players", methods=["GET"])
def count_players():
    count = collection.count_documents({})
    return jsonify({"total_players": count})

# -----------------------
# CREATE / UPDATE ENDPOINT
# -----------------------
@app.route("/add_or_update_player", methods=["POST"])
def add_or_update_player():
    """
    Add a new player or update existing one.
    Expected JSON body:
    {
        "name": "Player Name",
        "position": "CM",
        "team": "Ipswich",
        "age": 22,
        ...
    }
    """
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "JSON body must include 'name' field"}), 400

    data["imported_at"] = datetime.utcnow()

    try:
        result = collection.update_one(
            {"name": data["name"]},  # match by name
            {"$set": data},
            upsert=True
        )
        if result.upserted_id:
            return jsonify({"message": f"Player '{data['name']}' added"}), 201
        else:
            return jsonify({"message": f"Player '{data['name']}' updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------
# DELETE ENDPOINT
# -----------------------
@app.route("/delete_player", methods=["DELETE"])
def delete_player():
    """
    Delete a player by name.
    Example: /delete_player?name=Relebohile
    """
    name = request.args.get("name", "").strip()
    if not name:
        return jsonify({"error": "Please provide a player name using ?name=<player_name>"}), 400

    result = collection.delete_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
    if result.deleted_count == 0:
        return jsonify({"message": "No player found to delete"}), 404
    return jsonify({"message": f"Player '{name}' deleted"}), 200

# -----------------------
# RUN APP
# -----------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
