#!/usr/bin/env python3
"""
backend/sim_server.py
Zero-dependency, Python-native HTTP API Emulation Server for Open EMF Camper (V2).
Simulates API Gateway routes and Lambda writes locally on port 3000.
"""

import os
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

PORT = 3000
DB_FILE = os.path.join(os.path.dirname(__file__), "..", "web", "web_local_db.json")

# Default database seed structure matching single-table patterns
DEFAULT_DB = {
    "camper#aggregates#combined": {
        "totals": {
            "user_id": "combined",
            "total_drinks": 0,
            "beer_drinks": 0,
            "categories": {
                "Water": 0,
                "Coffee": 0,
                "Tea": 0,
                "Soft": 0,
                "Lager": 0,
                "IPA": 0,
                "Cider": 0,
                "Ale": 0,
                "Stout": 0,
                "Porter": 0,
                "Spirits": 0,
                "Martini": 0,
                "toilet_visits": 0,
                "Pee": 0,
                "Poo": 0
            },
            "leaderboard": []
        }
    },
    "monzo#transactions": {
        "latest": {
            "total_expenditure_gbp": 0.00,
            "transactions": []
        }
    }
}

def load_db():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as fh:
            json.dump(DEFAULT_DB, fh, indent=2)
        return DEFAULT_DB
    try:
        with open(DB_FILE, "r") as fh:
            return json.load(fh)
    except Exception:
        return DEFAULT_DB

def save_db(db):
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with open(DB_FILE, "w") as fh:
        json.dump(db, fh, indent=2)

class SimAPIHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, TRACKER_KEY, tracker_key")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)
        
        db = load_db()
        
        # Route mapping
        if path == "/beer":
            user_id = query.get("user_id", ["hvy"])[0]
            agg_key = f"camper#aggregates#{user_id}"
            
            # Fetch user or fall back to empty aggregates seed
            user_aggregates = db.get(agg_key, {}).get("totals")
            if not user_aggregates:
                user_aggregates = {
                    "user_id": user_id,
                    "total_drinks": 0,
                    "beer_drinks": 0,
                    "categories": {}
                }
            
            # Respond with the totals
            response_payload = {
                "status": "success",
                "user_id": user_id,
                "last_updated": datetime.now().isoformat() + "Z",
                "categories": user_aggregates.get("categories", {}),
                "total_drinks": user_aggregates.get("total_drinks", 0),
                "beer_drinks": user_aggregates.get("beer_drinks", 0)
            }
            
            # Append leaderboard if combined requested
            if user_id == "combined":
                combined_aggs = db.get("camper#aggregates#combined", {}).get("totals", {})
                response_payload["categories"] = combined_aggs.get("categories", {})
                response_payload["total_drinks"] = combined_aggs.get("total_drinks", 0)
                response_payload["beer_drinks"] = combined_aggs.get("beer_drinks", 0)
                response_payload["leaderboard"] = combined_aggs.get("leaderboard", [])

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response_payload, indent=2).encode("utf-8"))
            
        elif path == "/history":
            user_id = query.get("user_id", ["hvy"])[0]
            dev_key = f"device#eui-70b3d57ed0051111#{user_id}"
            device_state = db.get(dev_key, {}).get("state", {
                "last_known_latitude": 51.5074,
                "last_known_longitude": -0.1278,
                "last_known_timestamp": datetime.now().isoformat() + "Z",
                "cumulative_distance_km": 0.0,
                "cumulative_steps": 0,
                "location_history": []
            })
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "user_id": user_id,
                "cumulative_distance_km": device_state.get("cumulative_distance_km", 0.0),
                "cumulative_steps": device_state.get("cumulative_steps", 0),
                "location_history": device_state.get("location_history", [])
            }, indent=2).encode("utf-8"))
            
        elif path == "/monzo":
            monzo_state = db.get("monzo#transactions", {}).get("latest", {
                "total_expenditure_gbp": 0.00,
                "transactions": []
            })
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "total_expenditure_gbp": monzo_state.get("total_expenditure_gbp", 0.00),
                "transactions": monzo_state.get("transactions", [])
            }, indent=2).encode("utf-8"))
        else:
            self.send_response(404)
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        # Read content body
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length).decode("utf-8")
        
        try:
            payload = json.loads(post_data) if post_data else {}
        except Exception:
            payload = {}
            
        db = load_db()
        
        # Token authorization checks (Principle V)
        auth_header = self.headers.get("Authorization") or self.headers.get("TRACKER_KEY") or self.headers.get("tracker_key")
        if path in ["/beer", "/sensecap", "/browan", "/monzo-sync-simulation"] and auth_header != "mock-super-secret-key":
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "Unauthorized",
                "message": "Invalid or missing tracker key"
            }).encode("utf-8"))
            return

        if path == "/beer":
            user_id = payload.get("user_id") or "hvy"
            event_type = payload.get("event")
            name = payload.get("type")
            is_beer = payload.get("beer") == "true" or payload.get("beer") is True
            reverse = payload.get("reverse") is True or payload.get("reverse") == "true"
            
            # 1. Update User aggregate
            user_key = f"camper#aggregates#{user_id}"
            if user_key not in db:
                db[user_key] = {
                    "totals": {
                        "user_id": user_id,
                        "total_drinks": 0,
                        "beer_drinks": 0,
                        "categories": {}
                    }
                }
            user_totals = db[user_key]["totals"]
            
            # Increments offsets helper
            val_offset = -1 if reverse else 1
            
            if event_type == "Drinks":
                user_totals["categories"][name] = max(0, user_totals["categories"].get(name, 0) + val_offset)
                user_totals["total_drinks"] = max(0, user_totals["total_drinks"] + val_offset)
                if is_beer:
                    user_totals["beer_drinks"] = max(0, user_totals["beer_drinks"] + val_offset)
            elif event_type in ["Toilet", "Lecture", "Workshop", "Gaming", "Tent", "NewPeople", "Martini"]:
                user_totals["categories"][name] = max(0, user_totals["categories"].get(name, 0) + val_offset)
            elif event_type == "Reset" and name == "ResetDay":
                # Reset User totals
                user_totals["categories"] = {}
                user_totals["total_drinks"] = 0
                user_totals["beer_drinks"] = 0
            
            # 2. Update Combined aggregates (Pre-aggregation dual-write, FR-002)
            combined_key = "camper#aggregates#combined"
            if combined_key not in db:
                db[combined_key] = {
                    "totals": {
                        "user_id": "combined",
                        "total_drinks": 0,
                        "beer_drinks": 0,
                        "categories": {},
                        "leaderboard": []
                    }
                }
            combined_totals = db[combined_key]["totals"]
            
            if event_type == "Drinks":
                combined_totals["categories"][name] = max(0, combined_totals["categories"].get(name, 0) + val_offset)
                combined_totals["total_drinks"] = max(0, combined_totals["total_drinks"] + val_offset)
                if is_beer:
                    combined_totals["beer_drinks"] = max(0, combined_totals["beer_drinks"] + val_offset)
            elif event_type in ["Toilet", "Lecture", "Workshop", "Gaming", "Tent", "NewPeople", "Martini"]:
                combined_totals["categories"][name] = max(0, combined_totals["categories"].get(name, 0) + val_offset)
            elif event_type == "Reset" and name == "ResetDay":
                # Clear all users' aggregates if global reset triggered, else subtract
                combined_totals["categories"] = {}
                combined_totals["total_drinks"] = 0
                combined_totals["beer_drinks"] = 0
                combined_totals["leaderboard"] = []
                
            # 3. Update Leaderboard Standing (FR-003)
            # Find and update the user's score in the leaderboard
            leaderboard = combined_totals.get("leaderboard", [])
            user_entry = next((x for x in leaderboard if x["user_id"] == user_id), None)
            
            if user_entry:
                user_entry["total_drinks"] = user_totals["total_drinks"]
            else:
                leaderboard.append({
                    "user_id": user_id,
                    "display_name": user_id.capitalize(),
                    "total_drinks": user_totals["total_drinks"]
                })
            # Filter zero/empty entries and sort descending
            combined_totals["leaderboard"] = sorted([x for x in leaderboard if x["total_drinks"] > 0], key=lambda x: x["total_drinks"], reverse=True)
            
            # Save raw log historical entry
            log_key = f"camper#logs#{user_id}"
            if log_key not in db:
                db[log_key] = []
            db[log_key].append({
                "event": event_type,
                "type": name,
                "beer": is_beer,
                "reverse": reverse,
                "timestamp": datetime.now().isoformat() + "Z"
            })
            
            save_db(db)
            
            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "user_id": user_id,
                "category": event_type,
                "name": name,
                "reverse": reverse
            }).encode("utf-8"))
            
        elif path == "/sensecap":
            user_id = payload.get("user_id") or "hvy"
            lat = payload.get("latitude")
            lng = payload.get("longitude")
            temp = payload.get("temperature")
            light = payload.get("light")
            timestamp = payload.get("timestamp") or datetime.now().isoformat() + "Z"
            
            dev_key = f"device#eui-70b3d57ed0051111#{user_id}"
            if dev_key not in db:
                db[dev_key] = {
                    "state": {
                        "last_known_latitude": 51.5074,
                        "last_known_longitude": -0.1278,
                        "last_known_timestamp": timestamp,
                        "cumulative_distance_km": 0.0,
                        "cumulative_steps": 0,
                        "location_history": []
                    }
                }
            device_state = db[dev_key]["state"]
            
            # Handle coordinates history updates and calculations (FR-007, FR-005)
            staleness_seconds = 0
            
            if lat is not None and lng is not None:
                # Simulated incremental step addition
                old_lat = device_state["last_known_latitude"]
                old_lng = device_state["last_known_longitude"]
                
                # Haversine-like steps simulation distance increments
                dist_inc = 0.05 if old_lat != lat or old_lng != lng else 0.0
                
                device_state["last_known_latitude"] = lat
                device_state["last_known_longitude"] = lng
                device_state["last_known_timestamp"] = timestamp
                device_state["cumulative_distance_km"] += dist_inc
                device_state["cumulative_steps"] += int(dist_inc / 0.00063) # Stride 0.63m
                
                # Append to history array capped at 20 (Principle IV / FR-003)
                history = device_state.get("location_history", [])
                history.append({
                    "lat": lat,
                    "lng": lng,
                    "time": timestamp
                })
                if len(history) > 20:
                    history.pop(0)
                device_state["location_history"] = history
            else:
                # Missing GPS Lock staleness calculation
                last_time = datetime.fromisoformat(device_state["last_known_timestamp"].replace("Z", ""))
                curr_time = datetime.fromisoformat(timestamp.replace("Z", ""))
                staleness_seconds = int((curr_time - last_time).total_seconds())

            # Update database
            save_db(db)
            
            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "user_id": user_id,
                "staleness_seconds": staleness_seconds
            }).encode("utf-8"))
            
        elif path == "/browan":
            # Direct mock sound ingestion
            user_id = payload.get("user_id") or "hvy"
            sound = payload.get("sound_level") or 45.0
            
            combined_key = "camper#aggregates#combined"
            if combined_key not in db:
                db[combined_key] = {"totals": {"categories": {}}}
            combined_totals = db[combined_key]["totals"]
            combined_totals["categories"]["noise_level_db"] = sound
            
            save_db(db)
            
            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "user_id": user_id
            }).encode("utf-8"))
            
        elif path == "/monzo-sync-simulation":
            # Web playground hook to simulate Monzo background sync cron updates
            amount = float(payload.get("amount") or -5.00)
            desc = payload.get("merchant") or "Simulated Expense"
            timestamp = datetime.now().isoformat() + "Z"
            
            monzo_key = "monzo#transactions"
            if monzo_key not in db:
                db[monzo_key] = {
                    "latest": {
                        "total_expenditure_gbp": 0.00,
                        "transactions": []
                    }
                }
            monzo_latest = db[monzo_key]["latest"]
            
            # Append transaction
            tx_id = f"tx_local_{int(datetime.now().timestamp())}"
            monzo_latest["transactions"].append({
                "id": tx_id,
                "description": desc,
                "amount_gbp": amount,
                "timestamp": timestamp
            })
            if amount < 0:
                monzo_latest["total_expenditure_gbp"] += abs(amount)
                
            save_db(db)
            
            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "id": tx_id,
                "total_expenditure_gbp": monzo_latest["total_expenditure_gbp"]
            }).encode("utf-8"))
        else:
            self.send_response(404)
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(b"Not Found")

def run(server_class=HTTPServer, handler_class=SimAPIHandler, port=PORT):
    # Ensure local DB seeded
    load_db()
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f">> API Simulator running on http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n>> Server shutting down...")
        httpd.server_close()

if __name__ == "__main__":
    run()
