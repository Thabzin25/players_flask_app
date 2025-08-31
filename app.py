from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from pymongo.mongo_client import MongoClient
import certifi
import random

app = Flask(__name__)
CORS(app)  # Allow all origins (adjust for production)

# -----------------------
# CONFIG
# -----------------------
MONGO_URI = os.getenv("MONGO_URI")  # Set in Render secrets
DB_NAME = "Players"

# -----------------------
# CONNECT TO MONGO
# -----------------------
try:
    client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
    db = client[DB_NAME]

    # Collections
    players_collection = db["Players"]
    scouts_collection = db["Scouts"]
    clubs_collection = db["Clubs"]

    client.admin.command("ping")
    print("✅ Successfully connected to MongoDB Atlas")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    raise e

# -----------------------
# UTIL FUNCTIONS
# -----------------------
def generate_age():
    return random.randint(16, 40)  # footballer age

def generate_height():
    return random.randint(160, 200)  # cm

def generate_weight():
    return random.randint(55, 95)  # kg

def generate_experience():
    return random.randint(1, 25)  # scout years of experience

def generate_capacity():
    return random.randint(5000, 90000)  # stadium capacity

def generate_founded_year():
    return random.randint(1850, 2020)  # club foundation year

# -----------------------
# FLASK ROUTES
# -----------------------
@app.route("/")
def home():
    return "⚽ Players, Scouts & Clubs Flask App is running!"

# ==================================================
# PLAYERS ROUTES
# ==================================================
@app.route("/players", methods=["GET"])
def get_players():
    name_filter = request.args.get("name")
    position_filter = request.args.get("position")
    query = {}
    if name_filter:
        query["name"] = {"$regex": name_filter, "$options": "i"}
    if position_filter:
        query["position"] = position_filter
    raw_players = list(players_collection.find(query, {"_id": 0}))

    def transform_player(p):
        # --- Age ---
        age = p.get("age")
        if not age and p.get("Date"):
            try:
                year = int(str(p["Date"]).split("-")[0])
                age = 2025 - year
            except Exception:
                age = generate_age()
        elif not age:
            age = generate_age()

        # --- Height & Weight ---
        height = p.get("height") or generate_height()
        weight = p.get("weight") or generate_weight()

        # --- Position ---
        position = p.get("position", "N/A")

        # --- Rating ---
        rating = (
            p.get("rating") or
            p.get("Rating") or
            p.get("Original Rating") or
            p.get("Alternative Rating")
        )
        try:
            rating = float(rating)
        except (TypeError, ValueError):
            rating = "N/A"

        # --- Club & Nationality ---
        club = p.get("club") or p.get("Team Name") or "N/A"
        nationality = p.get("nationality", "N/A")
        notes = p.get("notes", "")

        return {
            "name": p.get("name", "N/A"),
            "age": age,
            "height": height,
            "weight": weight,
            "position": position,
            "rating": rating,
            "club": club,
            "nationality": nationality,
            "notes": notes
        }

    players = [transform_player(p) for p in raw_players]
    return jsonify(players)

@app.route("/players/<player_name>", methods=["GET"])
def get_player(player_name):
    player = players_collection.find_one({"name": player_name}, {"_id": 0})
    if not player:
        return jsonify({"error": "Player not found"}), 404
    return jsonify(player)

@app.route("/players", methods=["POST"])
def add_player():
    data = request.json
    if not data.get("name") or not data.get("position"):
        return jsonify({"error": "Name and position are required"}), 400
    if players_collection.find_one({"name": data["name"]}):
        return jsonify({"error": "Player with this name already exists"}), 400

    # Auto-generate if missing
    data.setdefault("age", generate_age())
    data.setdefault("height", generate_height())
    data.setdefault("weight", generate_weight())

    players_collection.insert_one(data)
    return jsonify({"message": "Player added successfully"}), 201

@app.route("/players/<player_name>", methods=["PUT"])
def update_player(player_name):
    data = request.json
    player = players_collection.find_one({"name": player_name})
    if not player:
        return jsonify({"error": "Player not found"}), 404
    players_collection.update_one({"name": player_name}, {"$set": data})
    return jsonify({"message": "Player updated successfully"})

@app.route("/players/<player_name>", methods=["DELETE"])
def delete_player(player_name):
    player = players_collection.find_one({"name": player_name})
    if not player:
        return jsonify({"error": "Player not found"}), 404
    players_collection.delete_one({"name": player_name})
    return jsonify({"message": f"{player_name} deleted successfully"})

@app.route("/player-reports", methods=["GET"])
def player_reports():
    players = list(players_collection.find({}, {"_id": 0, "name": 1, "position": 1, "rating": 1}))
    for p in players:
        if "rating" not in p:
            p["rating"] = round(5 + 5 * os.urandom(1)[0]/255, 1)

    positions_count = {}
    for p in players:
        pos = p.get("position", "Unknown")
        positions_count[pos] = positions_count.get(pos, 0) + 1

    return jsonify({"players": players, "positions_count": positions_count})

# ==================================================
# SCOUTS ROUTES
# ==================================================
@app.route("/scouts", methods=["GET"])
def get_scouts():
    scouts = list(scouts_collection.find({}, {"_id": 0}))
    for s in scouts:
        s["experience"] = s.get("experience", generate_experience())
    return jsonify(scouts)

@app.route("/scouts/<scout_name>", methods=["GET"])
def get_scout(scout_name):
    scout = scouts_collection.find_one({"name": scout_name}, {"_id": 0})
    if not scout:
        return jsonify({"error": "Scout not found"}), 404
    scout["experience"] = scout.get("experience", generate_experience())
    return jsonify(scout)

@app.route("/scouts", methods=["POST"])
def add_scout():
    data = request.json
    if not data.get("name") or not data.get("region"):
        return jsonify({"error": "Scout name and region are required"}), 400
    if scouts_collection.find_one({"name": data["name"]}):
        return jsonify({"error": "Scout with this name already exists"}), 400

    data.setdefault("experience", generate_experience())
    scouts_collection.insert_one(data)
    return jsonify({"message": "Scout added successfully"}), 201

@app.route("/scouts/<scout_name>", methods=["PUT"])
def update_scout(scout_name):
    data = request.json
    scout = scouts_collection.find_one({"name": scout_name})
    if not scout:
        return jsonify({"error": "Scout not found"}), 404
    scouts_collection.update_one({"name": scout_name}, {"$set": data})
    return jsonify({"message": "Scout updated successfully"})

@app.route("/scouts/<scout_name>", methods=["DELETE"])
def delete_scout(scout_name):
    scout = scouts_collection.find_one({"name": scout_name})
    if not scout:
        return jsonify({"error": "Scout not found"}), 404
    scouts_collection.delete_one({"name": scout_name})
    return jsonify({"message": f"{scout_name} deleted successfully"})

# ==================================================
# CLUBS ROUTES
# ==================================================
@app.route("/clubs", methods=["GET"])
def get_clubs():
    clubs = list(clubs_collection.find({}, {"_id": 0}))
    for c in clubs:
        c["capacity"] = c.get("capacity", generate_capacity())
        c["founded"] = c.get("founded", generate_founded_year())
    return jsonify(clubs)

@app.route("/clubs/<club_name>", methods=["GET"])
def get_club(club_name):
    club = clubs_collection.find_one({"name": club_name}, {"_id": 0})
    if not club:
        return jsonify({"error": "Club not found"}), 404
    club["capacity"] = club.get("capacity", generate_capacity())
    club["founded"] = club.get("founded", generate_founded_year())
    return jsonify(club)

@app.route("/clubs", methods=["POST"])
def add_club():
    data = request.json
    if not data.get("name") or not data.get("league"):
        return jsonify({"error": "Club name and league are required"}), 400
    if clubs_collection.find_one({"name": data["name"]}):
        return jsonify({"error": "Club with this name already exists"}), 400

    data.setdefault("capacity", generate_capacity())
    data.setdefault("founded", generate_founded_year())

    clubs_collection.insert_one(data)
    return jsonify({"message": "Club added successfully"}), 201

@app.route("/clubs/<club_name>", methods=["PUT"])
def update_club(club_name):
    data = request.json
    club = clubs_collection.find_one({"name": club_name})
    if not club:
        return jsonify({"error": "Club not found"}), 404
    clubs_collection.update_one({"name": club_name}, {"$set": data})
    return jsonify({"message": "Club updated successfully"})

@app.route("/clubs/<club_name>", methods=["DELETE"])
def delete_club(club_name):
    club = clubs_collection.find_one({"name": club_name})
    if not club:
        return jsonify({"error": "Club not found"}), 404
    clubs_collection.delete_one({"name": club_name})
    return jsonify({"message": f"{club_name} deleted successfully"})

# -----------------------
# RUN APP
# -----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
