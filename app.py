import os
import sys
import json
from datetime import datetime, timezone
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# -----------------------
# CONFIG
# -----------------------
# Load MongoDB URI from environment variable
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    print("❌ Error: MONGO_URI environment variable not set.")
    sys.exit(1)

PLAYERS_JSON = r"C:\Users\Thabi\OneDrive\Desktop\Scrapers\players_stats.json"
DB_NAME = "Players"
COLLECTION_NAME = "Players"

# -----------------------
# CONNECT TO MONGO
# -----------------------
try:
    client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # test connection
    client.admin.command("ping")
    print("✅ Successfully connected to MongoDB Atlas")

except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    sys.exit(1)

# -----------------------
# LOAD JSON FILE
# -----------------------
if not os.path.exists(PLAYERS_JSON):
    print(f"⚠️ File not found: {PLAYERS_JSON}")
    sys.exit(1)

try:
    with open(PLAYERS_JSON, "r", encoding="utf-8") as f:
        players = json.load(f)

    if not isinstance(players, list):
        raise ValueError("JSON file must contain a list of player objects")

except Exception as e:
    print(f"❌ Error reading JSON: {e}")
    sys.exit(1)

# -----------------------
# NORMALIZE PLAYER NAMES
# -----------------------
for player in players:
    if "name" not in player:
        if "Player Name" in player:
            player["name"] = player.pop("Player Name")
        else:
            print("⚠️ Skipping record missing both 'name' and 'Player Name':", player)
            continue

# -----------------------
# INSERT OR UPDATE PLAYERS
# -----------------------
inserted, updated = 0, 0

for player in players:
    player["imported_at"] = datetime.now(timezone.utc)  # timezone-aware UTC

    try:
        result = collection.update_one(
            {"name": player["name"]},  # match by player name
            {"$set": player},          # update or insert all fields
            upsert=True
        )
        if result.upserted
