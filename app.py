from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_caching import Cache
import os
from pymongo.mongo_client import MongoClient
from pymongo import ASCENDING, DESCENDING
import certifi
import random
from datetime import datetime, timedelta
from bson import ObjectId

app = Flask(__name__)
CORS(app)

# Configure caching
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})

# -----------------------
# CONFIG
# -----------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")  # Default to local MongoDB
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
    statuses_collection = db["Statuses"]

    # Create indexes
    scouts_collection.create_index([("name", ASCENDING)])
    scouts_collection.create_index([("region", ASCENDING)])
    statuses_collection.create_index([("statusId", ASCENDING)])

    client.admin.command("ping")
    print("✅ Successfully connected to MongoDB")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    raise e

# -----------------------
# UTIL FUNCTIONS
# -----------------------
def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable format"""
    if not doc:
        return None
        
    doc = doc.copy()
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

def parse_experience(exp_str):
    """Parse experience string to years (e.g., '3 years' -> 3)"""
    if not exp_str:
        return 0
    try:
        return int(exp_str.split()[0])
    except:
        return 0

def parse_success_rate(rate_str):
    """Parse success rate string to number (e.g., '65 percent' -> 65)"""
    if not rate_str:
        return 0
    try:
        return int(rate_str.split()[0])
    except:
        return 0

def map_experience_to_level(years):
    """Map years of experience to experience level"""
    if years < 2:
        return "Junior"
    elif years < 5:
        return "Mid-level"
    else:
        return "Senior"

# -----------------------
# STATUSES ROUTES
# -----------------------
@app.route("/api/statuses", methods=["GET"])
def get_statuses():
    try:
        # Create default statuses if they don't exist
        if statuses_collection.count_documents({}) == 0:
            default_statuses = [
                {"statusId": 1, "description": "Active"},
                {"statusId": 2, "description": "Inactive"},
                {"statusId": 3, "description": "Pending"}
            ]
            statuses_collection.insert_many(default_statuses)
        
        statuses = list(statuses_collection.find({}, {"_id": 0}))
        return jsonify(statuses)
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# -----------------------
# SCOUTS ROUTES
# -----------------------
@app.route("/api/scouts", methods=["GET"])
def get_scouts():
    try:
        scouts = list(scouts_collection.find({}))
        
        # Transform the data to match frontend expectations
        transformed_scouts = []
        for scout in scouts:
            # Handle field name variations
            name = scout.get("Scout_name") or scout.get("name", "Unknown")
            region = scout.get("Region") or scout.get("region", "Unknown")
            contact_info = scout.get("Contact Info") or scout.get("contactInfo", "")
            
            # Parse experience and success rate
            experience_str = scout.get("Experience") or scout.get("experienceLevel", "0 years")
            players_found_str = scout.get("Players_found") or scout.get("players_found", "0")
            success_rate_str = scout.get("Success Rate") or scout.get("success_rate", "0 percent")
            
            # Convert to proper formats
            experience_years = parse_experience(experience_str)
            experience_level = map_experience_to_level(experience_years)
            
            try:
                players_found = int(players_found_str)
            except:
                players_found = 0
                
            success_rate = parse_success_rate(success_rate_str)
            
            # Get status
            status = scout.get("Status") or scout.get("status", "Unknown")
            
            # Create transformed scout object
            transformed_scout = {
                "scoutId": str(scout.get("_id")),
                "name": name,
                "region": region,
                "contactInfo": contact_info,
                "status": status,
                "experienceLevel": experience_level,
                "players_found": players_found,
                "success_rate": success_rate
            }
            
            # Add statusId if available
            if "statusId" in scout:
                transformed_scout["statusId"] = scout["statusId"]
                
            transformed_scouts.append(transformed_scout)
        
        return jsonify(transformed_scouts)
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route("/api/scouts/<scout_id>", methods=["GET"])
def get_scout(scout_id):
    try:
        scout = scouts_collection.find_one({"_id": ObjectId(scout_id)})
        if not scout:
            return jsonify({"error": "Scout not found"}), 404
            
        # Transform the data (similar to get_scouts)
        name = scout.get("Scout_name") or scout.get("name", "Unknown")
        region = scout.get("Region") or scout.get("region", "Unknown")
        contact_info = scout.get("Contact Info") or scout.get("contactInfo", "")
        
        experience_str = scout.get("Experience") or scout.get("experienceLevel", "0 years")
        players_found_str = scout.get("Players_found") or scout.get("players_found", "0")
        success_rate_str = scout.get("Success Rate") or scout.get("success_rate", "0 percent")
        
        experience_years = parse_experience(experience_str)
        experience_level = map_experience_to_level(experience_years)
        
        try:
            players_found = int(players_found_str)
        except:
            players_found = 0
            
        success_rate = parse_success_rate(success_rate_str)
        
        status = scout.get("Status") or scout.get("status", "Unknown")
        
        transformed_scout = {
            "scoutId": str(scout.get("_id")),
            "name": name,
            "region": region,
            "contactInfo": contact_info,
            "status": status,
            "experienceLevel": experience_level,
            "players_found": players_found,
            "success_rate": success_rate
        }
        
        if "statusId" in scout:
            transformed_scout["statusId"] = scout["statusId"]
            
        return jsonify(transformed_scout)
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route("/api/scouts", methods=["POST"])
def add_scout():
    try:
        data = request.json
        if not data.get("name") or not data.get("region"):
            return jsonify({"error": "Scout name and region are required"}), 400
        
        # Prepare scout data for database
        scout_data = {
            "Scout_name": data.get("name"),
            "Region": data.get("region"),
            "Contact Info": data.get("contactInfo", ""),
            "statusId": data.get("statusId", 1),  # Default to Active
            "Experience": f"{data.get('experienceLevel', 'Junior')}",
            "Players_found": str(data.get("players_found", 0)),
            "Success Rate": f"{data.get('success_rate', 0)} percent"
        }
        
        # Insert the new scout
        result = scouts_collection.insert_one(scout_data)
        
        # Clear caches
        cache.delete_memoized(get_scouts)
        cache.delete_memoized(get_scouts_stats)
        
        return jsonify({
            "message": "Scout added successfully",
            "scoutId": str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route("/api/scouts/<scout_id>", methods=["PUT"])
def update_scout(scout_id):
    try:
        data = request.json
        scout = scouts_collection.find_one({"_id": ObjectId(scout_id)})
        if not scout:
            return jsonify({"error": "Scout not found"}), 404
        
        # Prepare update data
        update_data = {}
        if "name" in data:
            update_data["Scout_name"] = data["name"]
        if "region" in data:
            update_data["Region"] = data["region"]
        if "contactInfo" in data:
            update_data["Contact Info"] = data["contactInfo"]
        if "statusId" in data:
            update_data["statusId"] = data["statusId"]
        if "experienceLevel" in data:
            update_data["Experience"] = data["experienceLevel"]
        if "players_found" in data:
            update_data["Players_found"] = str(data["players_found"])
        if "success_rate" in data:
            update_data["Success Rate"] = f"{data['success_rate']} percent"
        
        # Update the scout
        scouts_collection.update_one({"_id": ObjectId(scout_id)}, {"$set": update_data})
        
        # Clear caches
        cache.delete_memoized(get_scouts)
        cache.delete_memoized(get_scout, scout_id)
        cache.delete_memoized(get_scouts_stats)
        
        return jsonify({"message": "Scout updated successfully"})
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route("/api/scouts/<scout_id>", methods=["DELETE"])
def delete_scout(scout_id):
    try:
        scout = scouts_collection.find_one({"_id": ObjectId(scout_id)})
        if not scout:
            return jsonify({"error": "Scout not found"}), 404
        
        scouts_collection.delete_one({"_id": ObjectId(scout_id)})
        
        # Clear caches
        cache.delete_memoized(get_scouts)
        cache.delete_memoized(get_scout, scout_id)
        cache.delete_memoized(get_scouts_stats)
        
        return jsonify({"message": "Scout deleted successfully"})
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route("/api/scouts/<scout_id>/stats", methods=["PUT"])
def update_scout_stats(scout_id):
    try:
        data = request.json
        scout = scouts_collection.find_one({"_id": ObjectId(scout_id)})
        if not scout:
            return jsonify({"error": "Scout not found"}), 404        
                
        # Update only the stats fields
        update_data = {}
        if "players_found" in data:
            update_data["Players_found"] = str(data["players_found"])
        if "success_rate" in data:
            update_data["Success Rate"] = f"{data['success_rate']} percent"
        
        scouts_collection.update_one({"_id": ObjectId(scout_id)}, {"$set": update_data})
        
        # Clear caches
        cache.delete_memoized(get_scouts)
        cache.delete_memoized(get_scout, scout_id)
        cache.delete_memoized(get_scouts_stats)
        
        return jsonify({"message": "Scout stats updated successfully"})
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route("/api/scouts/stats", methods=["GET"])
def get_scouts_stats():
    try:
        scouts = list(scouts_collection.find({}))
        
        # Calculate statistics
        total_scouts = len(scouts)
        
        # Count active scouts (assuming statusId 1 is active)
        active_scouts = 0
        for scout in scouts:
            status_id = scout.get("statusId", 1)
            if status_id == 1:
                active_scouts += 1
                
        inactive_scouts = total_scouts - active_scouts
        
        # Find most active scout (by players found)
        most_active = None
        for scout in scouts:
            players_found = 0
            try:
                players_found = int(scout.get("Players_found", 0))
            except:
                pass
                
            if not most_active or players_found > int(most_active.get("Players_found", 0)):
                most_active = scout
        
        # Prepare most active scout data
        most_active_data = {
            "name": most_active.get("Scout_name", "Unknown") if most_active else "No data",
            "initials": "".join([n[0] for n in (most_active.get("Scout_name", "NA") if most_active else "NA").split()[:2]]).upper(),
            "players_found": int(most_active.get("Players_found", 0)) if most_active else 0,
            "success_rate": parse_success_rate(most_active.get("Success Rate", "0")) if most_active else 0
        }
        
        # Calculate average success rate
        total_success = 0
        count = 0
        for scout in scouts:
            success_rate = parse_success_rate(scout.get("Success Rate", "0"))
            if success_rate > 0:
                total_success += success_rate
                count += 1
                
        avg_success_rate = round(total_success / count, 1) if count > 0 else 0
        
        # Generate weekly activity data (mock data)
        weekly_activity = []
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day in days:
            weekly_activity.append({
                "label": day,
                "value": random.randint(10, 100)
            })
        
        return jsonify({
            "totalScouts": total_scouts,
            "activeScouts": active_scouts,
            "inactiveScouts": inactive_scouts,
            "mostActive": most_active_data,
            "avgSuccessRate": avg_success_rate,
            "weeklyActivity": weekly_activity
        })
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# -----------------------
# CLUBS ROUTES
# -----------------------
@app.route("/api/clubs", methods=["GET"])
def get_clubs():
    try:
        clubs = list(clubs_collection.find({}))
        serialized_clubs = [serialize_doc(club) for club in clubs]
        return jsonify(serialized_clubs)
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# -----------------------
# RUN APP
# -----------------------
if __name__ == "__main__":
    # Ensure statuses collection exists
    try:
        if statuses_collection.count_documents({}) == 0:
            default_statuses = [
                {"statusId": 1, "description": "Active"},
                {"statusId": 2, "description": "Inactive"},
                {"statusId": 3, "description": "Pending"}
            ]
            statuses_collection.insert_many(default_statuses)
            print("✅ Default statuses created")
    except Exception as e:
        print(f"❌ Error creating default statuses: {e}")
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, threaded=True, debug=True)
