from pymongo import MongoClient
import json
import os

# -----------------------
# CONFIG
# -----------------------
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "Players"
COLLECTION_NAME = "Players"
PLAYERS_JSON = r"C:\Users\Thabi\OneDrive\Desktop\Scrapers\players_stats.json"

# -----------------------
# CONNECT TO MONGO
# -----------------------
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# -----------------------
# FUNCTIONS
# -----------------------

def import_players_from_json():
    """Import scraped players from JSON into MongoDB."""
    if not os.path.exists(PLAYERS_JSON):
        print(f"âš ï¸ File not found: {PLAYERS_JSON}")
        return

    with open(PLAYERS_JSON, "r", encoding="utf-8") as f:
        players = json.load(f)

    if not players:
        print("âš ï¸ No players found in JSON.")
        return

    # Insert players (ignore duplicates using upsert)
    for player in players:
        collection.update_one(
            {"name": player.get("name")},  # match by name
            {"$set": player},              # update fields
            upsert=True                    # insert if not exists
        )

    print(f"âœ… Imported {len(players)} players into MongoDB.")


def export_players_to_json():
    """Export all players from MongoDB into JSON file."""
    players = list(collection.find({}, {"_id": 0}))  # remove MongoDB _id
    if not players:
        print("âš ï¸ No records in MongoDB.")
        return

    with open(PLAYERS_JSON, "w", encoding="utf-8") as f:
        json.dump(players, f, indent=4, ensure_ascii=False)

    print(f"âœ… Exported {len(players)} players to {PLAYERS_JSON}")


def show_stats():
    """Show quick database stats."""
    count = collection.count_documents({})
    print(f"ðŸ“¦ {count} players in {DB_NAME}.{COLLECTION_NAME}")


# -----------------------
# MAIN MENU
# -----------------------
if __name__ == "__main__":
    while True:
        print("\n=== PlayersDB Main Menu ===")
        print("1. Import players from JSON â†’ MongoDB")
        print("2. Export players from MongoDB â†’ JSON")
        print("3. Show database stats")
        print("4. Exit")

        choice = input("Enter choice (1-4): ").strip()

        if choice == "1":
            import_players_from_json()
        elif choice == "2":
            export_players_to_json()
        elif choice == "3":
            show_stats()
        elif choice == "4":
            print("ðŸ‘‹ Exiting...")
            break
        else:
            print("âŒ Invalid choice. Try again.")