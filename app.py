from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_caching import Cache
import os
from pymongo.mongo_client import MongoClient
from pymongo import ASCENDING, DESCENDING
import certifi
import random
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow all origins (adjust for production)

# Configure caching
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})

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

    # Safely create indexes for players
    def ensure_index(collection, field, direction=ASCENDING):
        try:
            collection.create_index([(field, direction)])
        except Exception as e:
            # Ignore if index exists with different name
            if "IndexOptionsConflict" in str(e):
                print(f"⚠️ Index on '{field}' already exists, skipping.")
            else:
                raise e

    ensure_index(players_collection, "name")
    ensure_index(players_collection, "position")
    ensure_index(players_collection, "rating", DESCENDING)

    ensure_index(scouts_collection, "name")
    ensure_index(clubs_collection, "name")

    client.admin.command("ping")
    print("✅ Successfully connected to MongoDB Atlas")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    raise e

# -----------------------
# UTIL FUNCTIONS
# -----------------------
def generate_age():
    return random.randint(16, 38)  # footballer age

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

def transform_player(p):
    """Efficient player transformation function"""
    # --- Age ---
    age = p.get("age")
    if not age and p.get("Date"):
        try:
            year = int(str(p["Date"]).split("-")[0])
            age = datetime.now().year - year
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
        rating = float(rating) if rating else 0
    except (TypeError, ValueError):
        rating = 0  # Default to 0 for frontend

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

# -----------------------
# FLASK ROUTES
# -----------------------
@app.route("/")
def home():
    return "⚽ Players, Scouts & Clubs Flask App is running!"

# ==================================================
# PLAYERS ROUTES (OPTIMIZED)
# ==================================================
@app.route("/players", methods=["GET"])
@cache.cached(timeout=60, query_string=True)  # Cache for 60 seconds
def get_players():
    # Get query parameters with defaults
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    name_filter = request.args.get("name")
    position_filter = request.args.get("position")
    
    # Calculate skip value for pagination
    skip = (page - 1) * per_page

    # Build query
    query = {}
    if name_filter:
        query["name"] = {"$regex": name_filter, "$options": "i"}
    if position_filter:
        query["position"] = position_filter

    try:
        # Get total count for pagination info
        total_players = players_collection.count_documents(query)
        
        # Fetch only the required page of players
        raw_players_cursor = players_collection.find(query, {"_id": 0}).skip(skip).limit(per_page)
        
        # Use list comprehension for faster transformation
        players = [transform_player(p) for p in raw_players_cursor]

        return jsonify({
            "total_players": total_players,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_players + per_page - 1) // per_page,
            "players": players
        })
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@app.route("/players/<player_name>", methods=["GET"])
@cache.cached(timeout=300)  # Cache individual player for 5 minutes
def get_player(player_name):
    player = players_collection.find_one({"name": player_name}, {"_id": 0})
    if not player:
        return jsonify({"error": "Player not found"}), 404
    
    transformed_player = transform_player(player)
    return jsonify(transformed_player)

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
    
    # Clear cache for players list
    cache.delete_memoized(get_players)
    return jsonify({"message": "Player added successfully"}), 201

@app.route("/players/<player_name>", methods=["PUT"])
def update_player(player_name):
    data = request.json
    player = players_collection.find_one({"name": player_name})
    if not player:
        return jsonify({"error": "Player not found"}), 404
    players_collection.update_one({"name": player_name}, {"$set": data})
    
    # Clear relevant caches
    cache.delete_memoized(get_players)
    cache.delete_memoized(get_player, player_name)
    return jsonify({"message": "Player updated successfully"})

@app.route("/players/<player_name>", methods=["DELETE"])
def delete_player(player_name):
    player = players_collection.find_one({"name": player_name})
    if not player:
        return jsonify({"error": "Player not found"}), 404
    players_collection.delete_one({"name": player_name})
    
    # Clear relevant caches
    cache.delete_memoized(get_players)
    cache.delete_memoized(get_player, player_name)
    return jsonify({"message": f"{player_name} deleted successfully"})

@app.route("/player-reports", methods=["GET"])
@cache.cached(timeout=300)  # Cache reports for 5 minutes
def player_reports():
    # Use aggregation for faster processing
    pipeline = [
        {"$group": {
            "_id": "$position",
            "count": {"$sum": 1},
            "avg_rating": {"$avg": "$rating"}
        }},
        {"$project": {
            "position": "$_id",
            "count": 1,
            "avg_rating": {"$round": ["$avg_rating", 1]},
            "_id": 0
        }}
    ]
    
    positions_stats = list(players_collection.aggregate(pipeline))
    
    # Get top 10 players by rating
    top_players = list(players_collection.find(
        {}, 
        {"_id": 0, "name": 1, "position": 1, "rating": 1}
    ).sort("rating", -1).limit(10))
    
    # Ensure ratings are numbers
    for p in top_players:
        if "rating" not in p:
            p["rating"] = round(5 + 5 * random.random(), 1)
        elif isinstance(p["rating"], str):
            try:
                p["rating"] = float(p["rating"])
            except ValueError:
                p["rating"] = round(5 + 5 * random.random(), 1)

    return jsonify({
        "positions_stats": positions_stats,
        "top_players": top_players
    })

# ==================================================
# SCOUTS ROUTES
# ==================================================
@app.route("/scouts", methods=["GET"])
@cache.cached(timeout=300)
def get_scouts():
    scouts = list(scouts_collection.find({}, {"_id": 0}))
    for s in scouts:
        s["experience"] = s.get("experience", generate_experience())
    return jsonify(scouts)

@app.route("/scouts/<scout_name>", methods=["GET"])
@cache.cached(timeout=300)
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
    
    # Clear scouts cache
    cache.delete_memoized(get_scouts)
    return jsonify({"message": "Scout added successfully"}), 201

@app.route("/scouts/<scout_name>", methods=["PUT"])
def update_scout(scout_name):
    data = request.json
    scout = scouts_collection.find_one({"name": scout_name})
    if not scout:
        return jsonify({"error": "Scout not found"}), 404
    scouts_collection.update_one({"name": scout_name}, {"$set": data})
    
    # Clear relevant caches
    cache.delete_memoized(get_scouts)
    cache.delete_memoized(get_scout, scout_name)
    return jsonify({"message": "Scout updated successfully"})

@app.route("/scouts/<scout_name>", methods=["DELETE"])
def delete_scout(scout_name):
    scout = scouts_collection.find_one({"name": scout_name})
    if not scout:
        return jsonify({"error": "Scout not found"}), 404
    scouts_collection.delete_one({"name": scout_name})
    
    # Clear relevant caches
    cache.delete_memoized(get_scouts)
    cache.delete_memoized(get_scout, scout_name)
    return jsonify({"message": f"{scout_name} deleted successfully"})

# ==================================================
# CLUBS ROUTES
# ==================================================
@app.route("/clubs", methods=["GET"])
@cache.cached(timeout=300)
def get_clubs():
    clubs = list(clubs_collection.find({}, {"_id": 0}))
    for c in clubs:
        c["capacity"] = c.get("capacity", generate_capacity())
        c["founded"] = c.get("founded", generate_founded_year())
    return jsonify(clubs)

@app.route("/clubs/<club_name>", methods=["GET"])
@cache.cached(timeout=300)
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
    
    # Clear clubs cache
    cache.delete_memoized(get_clubs)
    return jsonify({"message": "Club added successfully"}), 201

@app.route("/clubs/<club_name>", methods=["PUT"])
def update_club(club_name):
    data = request.json
    club = clubs_collection.find_one({"name": club_name})
    if not club:
        return jsonify({"error": "Club not found"}), 404
    clubs_collection.update_one({"name": club_name}, {"$set": data})
    
    # Clear relevant caches
    cache.delete_memoized(get_clubs)
    cache.delete_memoized(get_club, club_name)
    return jsonify({"message": "Club updated successfully"})

@app.route("/clubs/<club_name>", methods=["DELETE"])
def delete_club(club_name):
    club = clubs_collection.find_one({"name": club_name})
    if not club:
        return jsonify({"error": "Club not found"}), 404
    clubs_collection.delete_one({"name": club_name})
    
    # Clear relevant caches
    cache.delete_memoized(get_clubs)
    cache.delete_memoized(get_club, club_name)
    return jsonify({"message": f"{club_name} deleted successfully"})

# -----------------------
# RUN APP
# -----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, threaded=True)


