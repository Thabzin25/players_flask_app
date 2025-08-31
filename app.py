from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from pymongo.mongo_client import MongoClient
import certifi
from datetime import datetime
import hashlib
import random
import urllib.parse

app = Flask(__name__)
CORS(app)  # Allow all origins (adjust for production)

# -----------------------
# CONFIG
# -----------------------
MONGO_URI = os.getenv("MONGO_URI")  # Set in Render secrets or environment
DB_NAME = os.getenv("DB_NAME", "Players")
PLAYERS_COLLECTION = os.getenv("PLAYERS_COLLECTION", "Players")
SCOUTS_COLLECTION = os.getenv("SCOUTS_COLLECTION", "Scouts")

# -----------------------
# CONNECT TO MONGO
# -----------------------
try:
    client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
    db = client[DB_NAME]
    players_coll = db[PLAYERS_COLLECTION]
    scouts_coll = db[SCOUTS_COLLECTION]
    client.admin.command("ping")
    print("✅ Successfully connected to MongoDB Atlas")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    raise e

# -----------------------
# HELPERS
# -----------------------

def parse_birthdate_to_age(value):
    """Try to parse a birthdate-like value to an integer age.
    Accepts: YYYY-MM-DD, YYYY/MM/DD, DD-MM-YYYY, timestamps, year only, datetime objects, etc.
    Returns int age or None if can't parse.
    """
    if value is None:
        return None

    # If it's already a number and looks like a realistic age, return it
    try:
        if isinstance(value, (int, float)):
            v = int(value)
            if 8 <= v <= 60:  # plausible age range for footballers
                return v
            # if v looks like a year (e.g. 1999 or 03 meaning 2003), convert
            if 1900 <= v <= datetime.now().year:
                return datetime.now().year - v
            if 0 < v < 100:  # 2-digit year
                # assume 1900s if > 30 else 2000s
                full_year = (1900 if v > 30 else 2000) + v
                return datetime.now().year - full_year
    except Exception:
        pass

    s = str(value).strip()
    # Try ISO formats and common separators
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y",
        "%d %b %Y",
        "%d %B %Y",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(s, fmt)
            return datetime.now().year - dt.year
        except Exception:
            pass

    # Sometimes value can be like '1999-08-01T00:00:00.000Z' or pandas.Timestamp
    try:
        # Remove timezone/Z
        s2 = s.split("T")[0]
        year = int(s2.split("-")[0])
        if 1900 <= year <= datetime.now().year:
            return datetime.now().year - year
    except Exception:
        pass

    # Last resort: try to extract any 4-digit year
    import re

    m = re.search(r"(19|20)\d{2}", s)
    if m:
        year = int(m.group(0))
        return datetime.now().year - year

    return None


def get_team_from_record(record):
    # look through keys to find common team/club fields (case-insensitive)
    for(k, v) in record.items():
        if not isinstance(k, str):
            continue
        lk = k.lower()
        if any(tok in lk for tok in ("team", "club", "squad", "team name", "club name")):
            if v:
                return v
    # common fallback keys
    return record.get("club") or record.get("Team Name") or record.get("team") or "N/A"


def get_rating_from_record(record):
    for key in ("rating", "Rating", "Original Rating", "Alternative Rating", "overall", "ovr"):
        if key in record and record.get(key) not in (None, "", "N/A"):
            try:
                return float(record[key])
            except Exception:
                try:
                    return float(str(record[key]).strip())
                except Exception:
                    return None
    return None


def deterministic_height_weight(name, position=None):
    """Return realistic (height_cm, weight_kg) generated deterministically from name and position.
    """
    if not name:
        name = "unknown"
    seed = int(hashlib.md5(name.encode("utf-8")).hexdigest()[:8], 16)
    rnd = random.Random(seed)

    pos = (position or "").lower()
    # Base ranges by position
    if "goal" in pos or "gk" in pos or "keeper" in pos:
        height = rnd.randint(185, 200)
        weight = rnd.randint(80, 95)
    elif "def" in pos or "centre" in pos or "cb" in pos:
        height = rnd.randint(180, 195)
        weight = rnd.randint(75, 92)
    elif "mid" in pos or "cm" in pos or "dm" in pos or "am" in pos:
        height = rnd.randint(170, 188)
        weight = rnd.randint(68, 85)
    elif "wing" in pos or "fw" in pos or "st" in pos or "att" in pos or "forward" in pos:
        height = rnd.randint(168, 193)
        weight = rnd.randint(65, 88)
    else:
        # unknown position: general footballer
        height = rnd.randint(168, 195)
        weight = rnd.randint(65, 92)

    return height, weight


def profile_picture_url_for_name(name):
    # Use DiceBear's avatars (SVG) — no key required and deterministic per name
    name_safe = urllib.parse.quote_plus(name)
    # styles: initials, identicon, adventure, icons, etc. Choose identicon for variety
    return f"https://avatars.dicebear.com/api/identicon/{name_safe}.svg"

# -----------------------
# TRANSFORM PLAYER RECORD
# -----------------------

def transform_player(p):
    # Name
    name = p.get("name") or p.get("Name") or p.get("player_name") or "N/A"

    # Age: prefer existing 'age' field if plausible; else parse known date fields
    age = None
    for key in ("age", "Age"):
        if key in p and p[key] not in (None, "", "N/A"):
            try:
                age_candidate = int(p[key])
                if 8 <= age_candidate <= 60:
                    age = age_candidate
                    break
            except Exception:
                pass

    if age is None:
        # try a variety of possible date fields
        for date_key in ("Date", "DOB", "Date of Birth", "birthdate", "Birthdate", "birth_date"):
            if date_key in p and p[date_key]:
                age = parse_birthdate_to_age(p[date_key])
                if age is not None:
                    break

    # As a final fallback, try parsing any field that looks date-like
    if age is None:
        age = parse_birthdate_to_age(p.get("date") or p.get("birth") or p.get("birth_date") or None)

    if age is None:
        age = "N/A"

    # Position
    position = p.get("position") or p.get("Position") or p.get("pos") or "N/A"

    # Rating
    rating = get_rating_from_record(p)
    if rating is None:
        # if there's an 'overall' or 'ovr' field fallback done above; otherwise create a stable pseudo-rating
        seed = int(hashlib.md5((name or "").encode("utf-8")).hexdigest()[:8], 16)
        rnd = random.Random(seed)
        rating = round(5 + rnd.random() * 5, 1)  # 5.0 - 10.0

    # Club / Team
    club = get_team_from_record(p)

    # Nationality
    nationality = p.get("nationality") or p.get("Nationality") or p.get("Country") or "N/A"

    # Notes
    notes = p.get("notes") or p.get("Notes") or ""

    # Height & weight (generate if missing)
    height = p.get("height") or p.get("Height")
    weight = p.get("weight") or p.get("Weight")
    if not height or not weight:
        h, w = deterministic_height_weight(name or club or "unknown", position)
        height = height or h
        weight = weight or w

    # Profile picture — generate a deterministic placeholder if missing
    profile_picture = p.get("profile_picture") or p.get("avatar") or profile_picture_url_for_name(name)

    return {
        "name": name,
        "age": age,
        "position": position,
        "rating": rating,
        "club": club,
        "nationality": nationality,
        "notes": notes,
        "height_cm": height,
        "weight_kg": weight,
        "profile_picture": profile_picture,
    }

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
        query["position"] = {"$regex": position_filter, "$options": "i"}

    raw_players = list(players_coll.find(query, {"_id": 0}))
    players = [transform_player(p) for p in raw_players]
    return jsonify(players)

# Fetch a single player (case-insensitive match)
@app.route("/players/<player_name>", methods=["GET"])
def get_player(player_name):
    player = players_coll.find_one({"name": {"$regex": f"^{player_name}$", "$options": "i"}}, {"_id": 0})
    if not player:
        return jsonify({"error": "Player not found"}), 404
    return jsonify(transform_player(player))

# Add a new player
@app.route("/players", methods=["POST"])
def add_player():
    data = request.json or {}
    # allow adding with name + (age or DOB or Date)
    if not data.get("name"):
        return jsonify({"error": "Name is required"}), 400

    # check duplicate (case-insensitive)
    if players_coll.find_one({"name": {"$regex": f"^{data['name']}$", "$options": "i"}}):
        return jsonify({"error": "Player with this name already exists"}), 400

    # if age missing but DOB present attempt to calculate
    if not data.get("age"):
        age_calc = parse_birthdate_to_age(data.get("DOB") or data.get("Date") or data.get("birthdate"))
        if age_calc:
            data["age"] = age_calc

    # Generate height/weight/profile_picture if not provided
    if not data.get("height") or not data.get("weight"):
        h, w = deterministic_height_weight(data.get("name"), data.get("position"))
        data.setdefault("height", h)
        data.setdefault("weight", w)

    if not data.get("profile_picture"):
        data["profile_picture"] = profile_picture_url_for_name(data.get("name"))

    players_coll.insert_one(data)
    return jsonify({"message": "Player added successfully"}), 201

# Update a player
@app.route("/players/<player_name>", methods=["PUT"])
def update_player(player_name):
    data = request.json or {}
    player = players_coll.find_one({"name": {"$regex": f"^{player_name}$", "$options": "i"}})
    if not player:
        return jsonify({"error": "Player not found"}), 404
    players_coll.update_one({"_id": player["_id"]}, {"$set": data})
    return jsonify({"message": "Player updated successfully"})

# Delete a player
@app.route("/players/<player_name>", methods=["DELETE"])
def delete_player(player_name):
    player = players_coll.find_one({"name": {"$regex": f"^{player_name}$", "$options": "i"}})
    if not player:
        return jsonify({"error": "Player not found"}), 404
    players_coll.delete_one({"_id": player["_id"]})
    return jsonify({"message": f"{player_name} deleted successfully"})

# -----------------------
# SCOUTS: store and manage scouts
# -----------------------
@app.route("/scouts", methods=["GET"])
def get_scouts():
    scouts = list(scouts_coll.find({}, {"_id": 0}))
    return jsonify(scouts)

@app.route("/scouts/<scout_name>", methods=["GET"])
def get_scout(scout_name):
    scout = scouts_coll.find_one({"name": {"$regex": f"^{scout_name}$", "$options": "i"}}, {"_id": 0})
    if not scout:
        return jsonify({"error": "Scout not found"}), 404
    return jsonify(scout)

@app.route("/scouts", methods=["POST"])
def add_scout():
    data = request.json or {}
    if not data.get("name"):
        return jsonify({"error": "Scout name required"}), 400
    # generate profile picture if missing
    if not data.get("profile_picture"):
        data["profile_picture"] = profile_picture_url_for_name(data.get("name"))
    # default experience years
    data.setdefault("experience_years", 1)
    scouts_coll.insert_one(data)
    return jsonify({"message": "Scout added"}), 201

@app.route("/scouts/<scout_name>", methods=["PUT"])
def update_scout(scout_name):
    data = request.json or {}
    scout = scouts_coll.find_one({"name": {"$regex": f"^{scout_name}$", "$options": "i"}})
    if not scout:
        return jsonify({"error": "Scout not found"}), 404
    scouts_coll.update_one({"_id": scout["_id"]}, {"$set": data})
    return jsonify({"message": "Scout updated"})

@app.route("/scouts/<scout_name>", methods=["DELETE"])
def delete_scout(scout_name):
    scout = scouts_coll.find_one({"name": {"$regex": f"^{scout_name}$", "$options": "i"}})
    if not scout:
        return jsonify({"error": "Scout not found"}), 404
    scouts_coll.delete_one({"_id": scout["_id"]})
    return jsonify({"message": "Scout deleted"})

# -----------------------
# PLAYER REPORTS (for charts)
# -----------------------
@app.route("/player-reports", methods=["GET"])
def player_reports():
    players = list(players_coll.find({}, {"_id": 0, "name": 1, "position": 1, "rating": 1, "height": 1, "weight": 1}))

    # Fill missing ratings deterministically
    for p in players:
        if "rating" not in p or p.get("rating") in (None, "", "N/A"):
            seed = int(hashlib.md5((p.get("name") or "").encode("utf-8")).hexdigest()[:8], 16)
            rnd = random.Random(seed)
            p["rating"] = round(5 + rnd.random() * 5, 1)

        if "height" not in p or not p.get("height"):
            h, _ = deterministic_height_weight(p.get("name"), p.get("position"))
            p["height"] = h
        if "weight" not in p or not p.get("weight"):
            _, w = deterministic_height_weight(p.get("name"), p.get("position"))
            p["weight"] = w

    # Count positions
    positions_count = {}
    for p in players:
        pos = p.get("position", "Unknown")
        positions_count[pos] = positions_count.get(pos, 0) + 1

    return jsonify({"players": players, "positions_count": positions_count})

# -----------------------
# UTILITY: generate missing physical stats for all players
# -----------------------
@app.route("/generate-player-profiles", methods=["POST"])
def generate_player_profiles():
    updated = 0
    for p in players_coll.find({}):
        name = p.get("name") or p.get("Name")
        position = p.get("position") or p.get("Position")
        h, w = deterministic_height_weight(name or "unknown", position)
        updates = {}
        if not p.get("height"):
            updates["height"] = h
        if not p.get("weight"):
            updates["weight"] = w
        if not p.get("profile_picture"):
            updates["profile_picture"] = profile_picture_url_for_name(name or "unknown")
        if updates:
            players_coll.update_one({"_id": p["_id"]}, {"$set": updates})
            updated += 1
    return jsonify({"message": "Profiles generated/updated", "updated": updated})

# -----------------------
# RUN APP
# -----------------------

# -----------------------
# RADAR (pentagon) GRAPH ENDPOINTS
# -----------------------
import io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Response


def get_attributes_for_radar(p):
    """Return 5 attribute values (0-10) for radar: Pace, Shooting, Passing, Dribbling, Defending.
    If attributes are present in the record use them; otherwise generate deterministic values from the name.
    """
    keys = ['pace', 'shooting', 'passing', 'dribbling', 'defending']
    attrs = {}
    for k in keys:
        val = None
        # try possible key variants
        for key in (k, k.capitalize(), k.upper()):
            if key in p and p[key] not in (None, '', 'N/A'):
                try:
                    val = float(p[key])
                    break
                except Exception:
                    pass
        attrs[k] = None if val is None else max(0.0, min(10.0, val))

    # generate deterministic values for missing ones
    if any(v is None for v in attrs.values()):
        seed = int(hashlib.md5((p.get('name') or '').encode('utf-8')).hexdigest()[:8], 16)
        rnd = random.Random(seed)
        for k in keys:
            if attrs[k] is None:
                attrs[k] = round(4 + rnd.random() * 6, 1)  # 4.0 - 10.0 range

    return [attrs[k] for k in keys]


@app.route('/player-reports/<player_name>/radar', methods=['GET'])
def player_radar(player_name):
    """Return a PNG image of a pentagon radar chart for the named player.
    Use case-insensitive name match. Front-end can embed this URL as an <img> source.
    """
    player = players_coll.find_one({"name": {"$regex": f"^{player_name}$", "$options": "i"}}, {"_id": 0})
    if not player:
        return jsonify({"error": "Player not found"}), 404

    values = get_attributes_for_radar(player)
    labels = ['Pace', 'Shooting', 'Passing', 'Dribbling', 'Defending']

    # prepare data for radar (close the polygon)
    N = len(values)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    values_closed = values + values[:1]
    angles_closed = angles + angles[:1]

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, polar=True)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    ax.plot(angles_closed, values_closed)
    ax.fill(angles_closed, values_closed, alpha=0.25)

    ax.set_thetagrids(np.degrees(angles), labels)
    ax.set_ylim(0, 10)
    ax.set_title(player.get('name', ''))

    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return Response(buf.getvalue(), mimetype='image/png')


# Update /player-reports to include radar image URL for each player
@app.route('/player-reports', methods=['GET'])
def player_reports():
    players = list(players_coll.find({}, {"_id": 0, "name": 1, "position": 1, "rating": 1, "height": 1, "weight": 1}))

    # Fill missing ratings deterministically and attach radar URL
    for p in players:
        if 'rating' not in p or p.get('rating') in (None, '', 'N/A'):
            seed = int(hashlib.md5((p.get('name') or '').encode('utf-8')).hexdigest()[:8], 16)
            rnd = random.Random(seed)
            p['rating'] = round(5 + rnd.random() * 5, 1)

        # ensure height and weight exist
        if 'height' not in p or not p.get('height'):
            h, _ = deterministic_height_weight(p.get('name'), p.get('position'))
            p['height'] = h
        if 'weight' not in p or not p.get('weight'):
            _, w = deterministic_height_weight(p.get('name'), p.get('position'))
            p['weight'] = w

        # attach radar image URL (front-end can fetch this)
        p['radar_url'] = f"/player-reports/{urllib.parse.quote_plus(p.get('name', ''))}/radar"

    # Count positions
    positions_count = {}
    for p in players:
        pos = p.get('position', 'Unknown')
        positions_count[pos] = positions_count.get(pos, 0) + 1

    return jsonify({"players": players, "positions_count": positions_count})


# -----------------------
# RUN APP
# -----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
