from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import os

app = Flask(__name__)

# -----------------------
# CONFIG
# -----------------------
MONGO_URI = os.environ.get("MONGO_URI")
CA_FILE = "rds-combined-ca-bundle.pem"

try:
    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsCAFile=CA_FILE,
        serverSelectionTimeoutMS=5000
    )
    db = client["Players"]
    collection = db["Players"]
    # test connection
    client.admin.command("ping")
    print("✅ Connected to MongoDB Atlas")
except ServerSelectionTimeoutError as e:
    print(f"❌ MongoDB connection failed: {e}")
    raise e

# -----------------------
# CRUD ENDPOINTS
# -----------------------

# GET all players
@app.route("/players", methods=["GET"])
def get_players():
    players = list(collection.find({}, {"_id": 0}))
    return jsonify(players), 200


# GET single player by name
@app.route("/players/<name>", methods=["GET"])
def get_player(name):
    player = collection.find_one({"name": name}, {"_id": 0})
    if not player:
        return jsonify({"error": "Player not found"}), 404
    return jsonify(player), 200


# CREATE new player
@app.route("/players", methods=["POST"])
def create_player():
    data = request.json
    if not data.get("name"):
        return jsonify({"error": "Missing 'name' field"}), 400

    collection.update_one({"name": data["name"]}, {"$set": data}, upsert=True)
    return jsonify({"message": "Player created/updated successfully"}), 201


# UPDATE existing player
@app.route("/players/<name>", methods=["PUT"])
def update_player(name):
    data = request.json
    result = collection.update_one({"name": name}, {"$set": data})
    if result.matched_count == 0:
        return jsonify({"error": "Player not found"}), 404
    return jsonify({"message": "Player updated successfully"}), 200


# DELETE player
@app.route("/players/<name>", methods=["DELETE"])
def delete_player(name):
    result = collection.delete_one({"name": name})
    if result.deleted_count == 0:
        return jsonify({"error": "Player not found"}), 404
    return jsonify({"message": "Player deleted successfully"}), 200


# -----------------------
# RUN APP
# -----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
