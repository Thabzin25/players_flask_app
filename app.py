from flask import Flask, jsonify, request
import os
from pymongo.mongo_client import MongoClient
import certifi

app = Flask(__name__)

# -----------------------
# CONFIG
# -----------------------
MONGO_URI = os.getenv("MONGO_URI")  # Set in Render or local environment
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

# GET all players with optional search/filter and pagination
@app.route("/players", methods=["GET"])
def get_players():
    search = request.args.get("search", "")
    position = request.args.get("position", "")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))

    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"club": {"$regex": search, "$options": "i"}},
            {"position": {"$regex": search, "$options": "i"}}
        ]
    if position:
        query["position"] = position

    total_players = collection.count_documents(query)
    players = list(
        collection.find(query, {"_id": 0})
                  .skip((page - 1) * limit)
                  .limit(limit)
    )

    return jsonify({
        "players": players,
        "page": page,
        "pages": (total_players + limit - 1) // limit,
        "total": total_players
    })

# GET single player
@app.route("/players/<player_name>", methods=["GET"])
def get_player(player_name):
    player = collection.find_one({"name": player_name}, {"_id": 0})
    if not player:
        return jsonify({"error": "Player not found"}), 404
    return jsonify(player)

# ADD new player
@app.route("/players", methods=["POST"])
def add_player():
    data = request.json
    if not data.get("name"):
        return jsonify({"error": "Player name is required"}), 400
    if collection.find_one({"name": data["name"]}):
        return jsonify({"error": "Player already exists"}), 400
    collection.insert_one(data)
    return jsonify({"message": "Player added successfully"}), 201

# UPDATE player
@app.route("/players/<player_name>", methods=["PUT"])
def update_player(player_name):
    data = request.json
    result = collection.update_one({"name": player_name}, {"$set": data})
    if result.matched_count == 0:
        return jsonify({"error": "Player not found"}), 404
    return jsonify({"message": "Player updated successfully"})

# DELETE player
@app.route("/players/<player_name>", methods=["DELETE"])
def delete_player(player_name):
    result = collection.delete_one({"name": player_name})
    if result.deleted_count == 0:
        return jsonify({"error": "Player not found"}), 404
    return jsonify({"message": "Player deleted successfully"})

# SCRAPE players (trigger scraper backend)
@app.route("/scrape-players", methods=["POST"])
def scrape_players():
    data = request.json
    league = data.get("league")
    position = data.get("position")

    # TODO: Integrate your scraper logic here
    # Example:
    # new_players = scraper.fetch_players(league=league, position=position)
    # for player in new_players:
    #     collection.update_one({"name": player["name"]}, {"$set": player}, upsert=True)

    return jsonify({"message": "Scraping completed successfully"})

# -----------------------
# RUN APP
# -----------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
