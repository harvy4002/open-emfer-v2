#!/usr/bin/env python3
"""
backend/sim_server.py
Zero-dependency, Dual-Mode Server for Open EMF Camper (V2).
- Local Mode: Run standalone as a local HTTP server on port 3000 (uses local JSON file).
- AWS Mode: Runs as an event-driven AWS Lambda handler querying and saving to live DynamoDB tables.
"""

import os
import json
import urllib.parse
import decimal
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

def make_event_sort_key(timestamp=None):
    """Generates a lexicographically sortable event sort key: event#<iso8601>#<short_uuid_hash>."""
    if not timestamp:
        timestamp = datetime.now().isoformat()
    # Clean timestamp format to ensure perfect sorting and compatibility
    if not timestamp.endswith("Z") and "+" not in timestamp:
        timestamp += "Z"
    short_uuid = str(uuid.uuid4())[:8]
    return f"event#{timestamp}#{short_uuid}"

# Custom Decimal Encoder to ensure DynamoDB types are JSON-serializable (Constitution Principle VI/VIII compliance)
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            try:
                if o.is_nan():
                    return None
                if o.is_infinite():
                    return "Infinity" if o > 0 else "-Infinity"
                if o == o.to_integral_value():
                    return int(o)
                return float(o)
            except Exception:
                return float(o)
        return super(DecimalEncoder, self).default(o)

def json_dumps(obj, **kwargs):
    if "cls" not in kwargs:
        kwargs["cls"] = DecimalEncoder
    return json.dumps(obj, **kwargs)

PORT = 3000
DB_FILE = os.path.join(os.path.dirname(__file__), "..", "web", "web_local_db.json")

# Participant tracker keys mapping (Constitution Principle V multi-tenant lock)
USER_KEYS = {
    "hvy": "mock-super-secret-key",
    "cha": "cha-mock-secret-key",
    "ash": "ash-mock-secret-key",
    "tin": "tin-mock-secret-key",
    "combined": "mock-super-secret-key"
}

# AWS Environment detection
IS_AWS = "AWS_LAMBDA_FUNCTION_NAME" in os.environ
TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "open_emfer_v2_production")

table = None

def get_db_table():
    global table
    if table is not None:
        return table
    if IS_AWS:
        try:
            import boto3
            # Explicitly specify region to prevent region-load errors (Constitution Principle VIII robust loops)
            dynamodb = boto3.resource("dynamodb", region_name="eu-west-2")
            table = dynamodb.Table(TABLE_NAME)
            return table
        except Exception as e:
            print(f"Lazy DynamoDB Table Init Error: {e}")
            return None
    return None

# Default database seed structure matching single-table patterns
DEFAULT_DB = {
    "camper#aggregates#combined": {
        "totals": {
            "user_id": "combined",
            "total_drinks": 0,
            "beer_drinks": 0,
            "categories": {
                "Water": 0, "Coffee": 0, "Tea": 0, "Soft": 0, "Lager": 0,
                "IPA": 0, "Cider": 0, "Ale": 0, "Stout": 0, "Porter": 0,
                "Spirits": 0, "Martini": 0, "toilet_visits": 0, "Pee": 0, "Poo": 0
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

# --- Database Storage Abstraction Layer ---

def load_local_db():
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

def save_local_db(db):
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with open(DB_FILE, "w") as fh:
        json.dump(db, fh, indent=2)

def db_get_item(event, type_val):
    """Fetches an item from either live DynamoDB or the local JSON file database."""
    tbl = get_db_table()
    if tbl is not None:
        try:
            res = tbl.get_item(Key={"event": event, "type": type_val})
            return res.get("Item")
        except Exception as e:
            print(f"DynamoDB GET Error: {e}")
            return None
    else:
        db = load_local_db()
        return db.get(event, {}).get(type_val)

def db_put_item(event, type_val, attributes):
    """Saves an item to either live DynamoDB or the local JSON file database."""
    attributes["event"] = event
    attributes["type"] = type_val
    
    tbl = get_db_table()
    if tbl is not None:
        try:
            # DynamoDB requires floats to be represented as Decimal numbers or parsed
            # Convert any floats to strings/decimals to prevent boto3 type exceptions
            safe_attributes = json.loads(json_dumps(attributes), parse_float=str)
            tbl.put_item(Item=safe_attributes)
            return True
        except Exception as e:
            print(f"DynamoDB PUT Error: {e}")
            return False
    else:
        db = load_local_db()
        if event not in db:
            db[event] = {}
        db[event][type_val] = attributes
        save_local_db(db)
        return True

def append_telemetry_event(user_id, event_type, payload):
    """Appends an immutable telemetry event log record to the database (FR-001/FR-002/FR-003)."""
    event_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    if not timestamp.endswith("Z") and "+" not in timestamp:
        timestamp += "Z"
    
    event_key = f"camper#events#{user_id}"
    sort_key = make_event_sort_key(timestamp)
    
    event_payload = {
        "event_id": event_id,
        "user_id": user_id,
        "event_type": event_type,
        "payload": payload,
        "timestamp": timestamp
    }
    return db_put_item(event_key, sort_key, event_payload)

def db_query_events(user_id, until_timestamp):
    """Retrieves all TelemetryEvent logs for a user up to a given ISO 8601 UTC timestamp."""
    event_key = f"camper#events#{user_id}"
    events = []
    
    if IS_AWS:
        # Live AWS DynamoDB query using boto3 Query with KeyConditionExpression (Principles II/IV)
        tbl = get_db_table()
        if tbl is not None:
            try:
                from boto3.dynamodb.conditions import Key
                upper_bound_sk = f"event#{until_timestamp}"
                res = tbl.query(
                    KeyConditionExpression=Key("event").eq(event_key) & Key("type").le(upper_bound_sk)
                )
                items = res.get("Items", [])
                items = sorted(items, key=lambda x: x.get("type", ""))
                return items
            except Exception as e:
                print(f"DynamoDB Query Error: {e}")
                return []
    else:
        # Local JSON database emulation
        db = load_local_db()
        user_events_map = db.get(event_key, {})
        upper_bound_sk = f"event#{until_timestamp}"
        for sk, item in user_events_map.items():
            if sk <= upper_bound_sk:
                events.append(item)
        events = sorted(events, key=lambda x: x.get("type", ""))
        return events

def process_playback(user_id, until_timestamp):
    """Reconstructs and returns the aggregate state of a camper by replaying chronological event logs (FR-005/FR-006)."""
    events = db_query_events(user_id, until_timestamp)
    
    # Initialize blank aggregate snapshot structure
    totals = {
        "user_id": user_id,
        "total_drinks": 0,
        "beer_drinks": 0,
        "categories": {},
        "status": "normal"
    }
    
    for event in events:
        event_type = event.get("event_type")
        payload = event.get("payload") or {}
        name = payload.get("type")
        is_beer = payload.get("beer") == "true" or payload.get("beer") is True
        reverse = payload.get("reverse") is True or payload.get("reverse") == "true"
        
        val_offset = -1 if reverse else 1
        
        if event_type == "Drinks":
            totals["categories"][name] = max(0, int(totals["categories"].get(name, 0)) + val_offset)
            totals["total_drinks"] = max(0, int(totals["total_drinks"]) + val_offset)
            if is_beer:
                totals["beer_drinks"] = max(0, int(totals["beer_drinks"]) + val_offset)
        elif event_type in ["Toilet", "Lecture", "Workshop", "Gaming", "Tent", "NewPeople", "Martini"]:
            totals["categories"][name] = max(0, int(totals["categories"].get(name, 0)) + val_offset)
        elif event_type.lower() == "status":
            totals["status"] = name.lower()
        elif event_type == "Reset" and name == "ResetDay":
            totals["categories"] = {}
            totals["total_drinks"] = 0
            totals["beer_drinks"] = 0
            totals["status"] = "normal"
            
    return totals, len(events)

# --- Unified REST Core Routing Logic ---

def process_api_get(path, query_params):
    """Processes GET routes and returns status code, headers, and body."""
    headers = {"Content-Type": "application/json"}
    
    if path == "/beer":
        user_id = query_params.get("user_id", "hvy")
        
        # Check if the query is requesting the latest status of the user (009/010 event-sourced status support)
        if query_params.get("event") == "status" and query_params.get("type") == "latest":
            # Query the latest event for this user
            events = db_query_events(user_id, datetime.now().isoformat() + "Z")
            status_text = "normal"
            if events:
                # Filter strictly for explicit "Status" / "status" events (T007/FR-002 alignment)
                status_events = [e for e in events if e.get("event_type", "").lower() == "status"]
                if status_events:
                    latest_status_event = status_events[-1]
                    payload = latest_status_event.get("payload") or {}
                    status_text = payload.get("status") or payload.get("type") or "normal"
            
            # Normalize to lowercase to match the .jpg files in the folder (FR-003)
            status_text = status_text.lower()
            
            return 200, headers, json_dumps({
                "status": status_text,
                "user_id": user_id,
                "last_updated": datetime.now().isoformat() + "Z"
            }, indent=2)

        agg_key = f"camper#aggregates#{user_id}"
        
        # Load aggregates from database
        user_aggregates = db_get_item(agg_key, "totals")
        if not user_aggregates:
            user_aggregates = {
                "user_id": user_id,
                "total_drinks": 0,
                "beer_drinks": 0,
                "categories": {}
            }
        
        response_payload = {
            "status": "success",
            "user_id": user_id,
            "last_updated": datetime.now().isoformat() + "Z",
            "categories": user_aggregates.get("categories", {}),
            "total_drinks": int(user_aggregates.get("total_drinks", 0)),
            "beer_drinks": int(user_aggregates.get("beer_drinks", 0))
        }
        
        # Append leaderboard standings if combined stats are requested
        if user_id == "combined":
            combined_aggs = db_get_item("camper#aggregates#combined", "totals") or {}
            response_payload["categories"] = combined_aggs.get("categories", {})
            response_payload["total_drinks"] = int(combined_aggs.get("total_drinks", 0))
            response_payload["beer_drinks"] = int(combined_aggs.get("beer_drinks", 0))
            response_payload["leaderboard"] = combined_aggs.get("leaderboard", [])

        return 200, headers, json_dumps(response_payload, indent=2)
        
    elif path == "/history":
        user_id = query_params.get("user_id", "hvy")
        dev_key = f"device#eui-70b3d57ed0051111#{user_id}"
        device_state = db_get_item(dev_key, "state") or {
            "last_known_latitude": 51.5074,
            "last_known_longitude": -0.1278,
            "last_known_timestamp": datetime.now().isoformat() + "Z",
            "cumulative_distance_km": 0.0,
            "cumulative_steps": 0,
            "location_history": []
        }
        
        # Convert DynamoDB string floats back to numeric for response
        try:
            dist = float(device_state.get("cumulative_distance_km", 0.0))
        except ValueError:
            dist = 0.0
            
        history = device_state.get("location_history", [])
        safe_history = []
        for pt in history:
            try:
                safe_history.append({
                    "lat": float(pt.get("lat", 51.5074)),
                    "lng": float(pt.get("lng", -0.1278)),
                    "time": pt.get("time")
                })
            except Exception:
                pass
        
        return 200, headers, json_dumps({
            "status": "success",
            "user_id": user_id,
            "cumulative_distance_km": dist,
            "cumulative_steps": int(device_state.get("cumulative_steps", 0)),
            "location_history": safe_history
        }, indent=2)
        
    elif path == "/monzo":
        monzo_state = db_get_item("monzo#transactions", "latest") or {
            "total_expenditure_gbp": 0.00,
            "transactions": []
        }
        
        try:
            exp = float(monzo_state.get("total_expenditure_gbp", 0.00))
        except ValueError:
            exp = 0.0
            
        return 200, headers, json_dumps({
            "status": "success",
            "total_expenditure_gbp": exp,
            "transactions": monzo_state.get("transactions", [])
        }, indent=2)
        
    elif path == "/playback":
        user_id = query_params.get("user_id", "hvy")
        until = query_params.get("until") or datetime.now().isoformat()
        
        reconstructed, processed_count = process_playback(user_id, until)
        
        return 200, headers, json_dumps({
            "status": "success",
            "reconstructed_state": reconstructed,
            "events_processed": processed_count,
            "playback_boundary": until
        }, indent=2)
        
    return 404, headers, "Not Found"

def process_api_post(path, payload, auth_header):
    """Processes POST routes and writes state updates to the database."""
    headers = {"Content-Type": "application/json"}
    
    # Dynamically resolve expected key per participant to ensure administrative segregation (Principle V)
    user_id = payload.get("user_id") or "hvy"
    expected_key = USER_KEYS.get(user_id, "mock-super-secret-key")
    
    # Token authorization check (Principle V)
    if path in ["/beer", "/sensecap", "/browan", "/monzo-sync-simulation", "/steps"] and auth_header != expected_key:
        return 401, headers, json_dumps({
            "error": "Unauthorized",
            "message": "Invalid or missing tracker key"
        })

    if path == "/beer":
        user_id = payload.get("user_id") or "hvy"
        event_type = payload.get("event")
        name = payload.get("type")
        is_beer = payload.get("beer") == "true" or payload.get("beer") is True
        reverse = payload.get("reverse") is True or payload.get("reverse") == "true"
        
        # Append immutable event to event store (FR-001/FR-002)
        append_telemetry_event(user_id, event_type, payload)
        
        # 1. Update User aggregate
        user_key = f"camper#aggregates#{user_id}"
        user_totals = db_get_item(user_key, "totals") or {
            "user_id": user_id,
            "total_drinks": 0,
            "beer_drinks": 0,
            "categories": {}
        }
        
        val_offset = -1 if reverse else 1
        
        if event_type == "Drinks":
            user_totals["categories"][name] = max(0, int(user_totals["categories"].get(name, 0)) + val_offset)
            user_totals["total_drinks"] = max(0, int(user_totals["total_drinks"]) + val_offset)
            if is_beer:
                user_totals["beer_drinks"] = max(0, int(user_totals["beer_drinks"]) + val_offset)
        elif event_type in ["Toilet", "Lecture", "Workshop", "Gaming", "Tent", "NewPeople", "Martini"]:
            user_totals["categories"][name] = max(0, int(user_totals["categories"].get(name, 0)) + val_offset)
        elif event_type.lower() == "status":
            user_totals["status"] = name.lower()
        elif event_type == "Reset" and name == "ResetDay":
            user_totals["categories"] = {}
            user_totals["total_drinks"] = 0
            user_totals["beer_drinks"] = 0
            user_totals["status"] = "normal"
            
        db_put_item(user_key, "totals", user_totals)
        
        # 2. Update Combined aggregates (Pre-aggregation dual-write, FR-002)
        combined_totals = db_get_item("camper#aggregates#combined", "totals") or {
            "user_id": "combined",
            "total_drinks": 0,
            "beer_drinks": 0,
            "categories": {},
            "leaderboard": []
        }
        
        if event_type == "Drinks":
            combined_totals["categories"][name] = max(0, int(combined_totals["categories"].get(name, 0)) + val_offset)
            combined_totals["total_drinks"] = max(0, int(combined_totals["total_drinks"]) + val_offset)
            if is_beer:
                combined_totals["beer_drinks"] = max(0, int(combined_totals["beer_drinks"]) + val_offset)
        elif event_type in ["Toilet", "Lecture", "Workshop", "Gaming", "Tent", "NewPeople", "Martini"]:
            combined_totals["categories"][name] = max(0, int(combined_totals["categories"].get(name, 0)) + val_offset)
        elif event_type.lower() == "status":
            combined_totals["status"] = name.lower()
        elif event_type == "Reset" and name == "ResetDay":
            combined_totals["categories"] = {}
            combined_totals["total_drinks"] = 0
            combined_totals["beer_drinks"] = 0
            combined_totals["leaderboard"] = []
            combined_totals["status"] = "normal"
            
        # 3. Update Leaderboard Standing (FR-003)
        leaderboard = combined_totals.get("leaderboard", [])
        user_entry = next((x for x in leaderboard if x["user_id"] == user_id), None)
        
        if user_entry:
            user_entry["total_drinks"] = int(user_totals["total_drinks"])
        else:
            leaderboard.append({
                "user_id": user_id,
                "display_name": user_id.capitalize(),
                "total_drinks": int(user_totals["total_drinks"])
            })
        combined_totals["leaderboard"] = sorted([x for x in leaderboard if int(x["total_drinks"]) > 0], key=lambda x: int(x["total_drinks"]), reverse=True)
        
        db_put_item("camper#aggregates#combined", "totals", combined_totals)
        
        return 201, headers, json_dumps({
            "status": "success",
            "user_id": user_id,
            "category": event_type,
            "name": name,
            "reverse": reverse
        })
        
    elif path == "/sensecap":
        user_id = payload.get("user_id") or "hvy"
        
        # Append immutable event to event store (FR-001/FR-002)
        append_telemetry_event(user_id, "sensecap", payload)
        
        lat = payload.get("latitude")
        lng = payload.get("longitude")
        temp = payload.get("temperature")
        light = payload.get("light")
        timestamp = payload.get("timestamp") or datetime.now().isoformat() + "Z"
        
        dev_key = f"device#eui-70b3d57ed0051111#{user_id}"
        device_state = db_get_item(dev_key, "state") or {
            "last_known_latitude": 51.5074,
            "last_known_longitude": -0.1278,
            "last_known_timestamp": timestamp,
            "cumulative_distance_km": 0.0,
            "cumulative_steps": 0,
            "location_history": []
        }
        
        staleness_seconds = 0
        
        if lat is not None and lng is not None:
            try:
                old_lat = float(device_state.get("last_known_latitude", 51.5074))
                old_lng = float(device_state.get("last_known_longitude", -0.1278))
                dist_inc = 0.05 if old_lat != float(lat) or old_lng != float(lng) else 0.0
            except Exception:
                dist_inc = 0.0
                
            try:
                current_distance = float(device_state.get("cumulative_distance_km", 0.0))
            except Exception:
                current_distance = 0.0
            
            device_state["last_known_latitude"] = lat
            device_state["last_known_longitude"] = lng
            device_state["last_known_timestamp"] = timestamp
            device_state["cumulative_distance_km"] = current_distance + dist_inc
            device_state["cumulative_steps"] = int(device_state.get("cumulative_steps", 0)) + int(dist_inc / 0.00063)
            
            # Capped location history (max 20)
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
            try:
                last_time = datetime.fromisoformat(device_state["last_known_timestamp"].replace("Z", ""))
                curr_time = datetime.fromisoformat(timestamp.replace("Z", ""))
                staleness_seconds = int((curr_time - last_time).total_seconds())
            except Exception:
                staleness_seconds = 0
                
        db_put_item(dev_key, "state", device_state)
        
        return 201, headers, json_dumps({
            "status": "success",
            "user_id": user_id,
            "staleness_seconds": staleness_seconds
        })
        
    elif path == "/browan":
        user_id = payload.get("user_id") or "hvy"
        
        # Append immutable event to event store (FR-001/FR-002)
        append_telemetry_event(user_id, "browan", payload)
        
        sound = payload.get("sound_level") or 45.0
        
        combined_totals = db_get_item("camper#aggregates#combined", "totals") or {
            "categories": {}
        }
        if "categories" not in combined_totals:
            combined_totals["categories"] = {}
        combined_totals["categories"]["noise_level_db"] = sound
        
        db_put_item("camper#aggregates#combined", "totals", combined_totals)
        
        return 201, headers, json_dumps({
            "status": "success",
            "user_id": user_id
        })
        
    elif path == "/monzo-sync-simulation":
        user_id = payload.get("user_id") or "hvy"
        
        # Append immutable event to event store (FR-001/FR-002)
        append_telemetry_event(user_id, "monzo", payload)
        
        amount = float(payload.get("amount") or -5.00)
        desc = payload.get("merchant") or "Simulated Expense"
        timestamp = datetime.now().isoformat() + "Z"
        
        monzo_latest = db_get_item("monzo#transactions", "latest") or {
            "total_expenditure_gbp": 0.00,
            "transactions": []
        }
        
        try:
            exp = float(monzo_latest.get("total_expenditure_gbp", 0.00))
        except Exception:
            exp = 0.0
            
        tx_id = f"tx_local_{int(datetime.now().timestamp())}"
        transactions = monzo_latest.get("transactions", [])
        transactions.append({
            "id": tx_id,
            "description": desc,
            "amount_gbp": amount,
            "timestamp": timestamp
        })
        monzo_latest["transactions"] = transactions
        
        if amount < 0:
            monzo_latest["total_expenditure_gbp"] = exp + abs(amount)
            
        db_put_item("monzo#transactions", "latest", monzo_latest)
        
        return 201, headers, json_dumps({
            "status": "success",
            "id": tx_id,
            "total_expenditure_gbp": monzo_latest["total_expenditure_gbp"]
        })

    elif path == "/steps":
        user_id = payload.get("user_id") or "hvy"
        steps = int(payload.get("steps") or 0)
        timestamp = datetime.now().isoformat() + "Z"

        # Append immutable event to event store (FR-001/FR-002)
        append_telemetry_event(user_id, "steps", payload)

        dev_key = f"device#eui-70b3d57ed0051111#{user_id}"
        device_state = db_get_item(dev_key, "state") or {
            "last_known_latitude": 51.5074,
            "last_known_longitude": -0.1278,
            "last_known_timestamp": timestamp,
            "cumulative_distance_km": 0.0,
            "cumulative_steps": 0,
            "location_history": []
        }

        device_state["cumulative_steps"] = steps
        device_state["cumulative_distance_km"] = steps * 0.00063

        db_put_item(dev_key, "state", device_state)

        return 201, headers, json_dumps({
            "status": "success",
            "user_id": user_id,
            "cumulative_steps": steps
        })
        
    return 404, headers, "Not Found"

# --- AWS Lambda Handler Entrypoint ---

def lambda_handler(event, context):
    """
    Core entrypoint invoked by AWS API Gateway v2.
    Translates raw API Gateway JSON events into standard router responses.
    """
    try:
        # Extract query params and paths
        path = event.get("rawPath") or "/"
        # Normalize API Gateway stage path prefix (Constitution Principle VIII robust loops)
        if path.startswith("/prod/"):
            path = path[5:]
        elif path == "/prod":
            path = "/"
            
        http_method = event.get("requestContext", {}).get("http", {}).get("method", "GET")
        query_params_raw = event.get("queryStringParameters") or {}
        headers = event.get("headers") or {}
        
        # Handle CORS Preflight OPTIONS requests
        if http_method == "OPTIONS":
            return {
                "statusCode": 204,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, TRACKER_KEY, tracker_key"
                },
                "body": ""
            }
            
        # Standardize case-insensitive Authorization check (Constitution Principle V / VIII)
        auth_header = (
            headers.get("authorization") or 
            headers.get("Authorization") or 
            headers.get("tracker_key") or 
            headers.get("TRACKER_KEY") or 
            headers.get("tracker-key") or 
            headers.get("Tracker-Key")
        )
        
        if http_method == "GET":
            status, res_headers, body = process_api_get(path, query_params_raw)
        elif http_method == "POST":
            post_body_raw = event.get("body") or ""
            # Handle base64 decoded bodies if needed
            if event.get("isBase64Encoded"):
                import base64
                post_body_raw = base64.b64decode(post_body_raw).decode("utf-8")
            try:
                payload = json.loads(post_body_raw) if post_body_raw else {}
            except Exception:
                payload = {}
            status, res_headers, body = process_api_post(path, payload, auth_header)
        else:
            status, res_headers, body = 405, {"Content-Type": "application/json"}, "Method Not Allowed"
            
        # Inject CORS into all responses
        res_headers["Access-Control-Allow-Origin"] = "*"
        res_headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        res_headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, TRACKER_KEY, tracker_key"
        
        return {
            "statusCode": status,
            "headers": res_headers,
            "body": body
        }
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, TRACKER_KEY, tracker_key"
            },
            "body": json.dumps({
                "error": "Internal Server Error",
                "message": str(e),
                "traceback": tb,
                "event_context": str(event)[:1000]
            })
        }

# --- Local Standalone HTTP Socket Server ---

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
        query = {k: v[0] for k, v in urllib.parse.parse_qs(parsed_url.query).items()}
        
        status, headers, body = process_api_get(path, query)
        
        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length).decode("utf-8")
        try:
            payload = json.loads(post_data) if post_data else {}
        except Exception:
            payload = {}
            
        auth_header = self.headers.get("Authorization") or self.headers.get("TRACKER_KEY") or self.headers.get("tracker_key")
        
        status, headers, body = process_api_post(path, payload, auth_header)
        
        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

def run_local_server(server_class=HTTPServer, handler_class=SimAPIHandler, port=PORT):
    load_local_db()
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f">> Local API Simulator running on http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n>> Server shutting down...")
        httpd.server_close()

if __name__ == "__main__":
    run_local_server()
