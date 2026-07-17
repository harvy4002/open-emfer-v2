# backend/tests/unit/test_math_helpers.py
import os
import json
import pytest
import backend.sim_server as sim_server

@pytest.fixture(autouse=True)
def mock_temp_db(tmp_path):
    """Fixture to isolate the local database file during test runs."""
    test_db_file = os.path.join(tmp_path, "test_local_db.json")
    original_db_file = sim_server.DB_FILE
    sim_server.DB_FILE = test_db_file
    
    # Initialize with default structure
    with open(test_db_file, "w") as fh:
        json.dump(sim_server.DEFAULT_DB, fh, indent=2)
        
    yield test_db_file
    
    # Restore original path
    sim_server.DB_FILE = original_db_file
    if os.path.exists(test_db_file):
        try:
            os.remove(test_db_file)
        except OSError:
            pass

def test_distance_and_steps_calculations():
    """Verify that posting consecutive coordinates calculates distance increments correctly."""
    user_id = "hvy"
    auth_key = sim_server.USER_KEYS.get(user_id)
    
    # 1. First payload (baseline coordinates)
    payload_1 = {
        "user_id": user_id,
        "device_id": "eui-70b3d57ed0051111",
        "timestamp": "2026-07-14T12:00:00Z",
        "latitude": 52.0411,
        "longitude": -2.3784,
        "temperature": 22.0,
        "light": 150
    }
    status, _, _ = sim_server.process_api_post("/sensecap", payload_1, auth_key)
    assert status == 201
    
    # Since first coordinate is different from default London center, it starts at 0.05
    status_get, _, body = sim_server.process_api_get("/history", {"user_id": user_id})
    assert status_get == 200
    data = json.loads(body)
    assert data["cumulative_distance_km"] == 0.05
    assert data["cumulative_steps"] == int(0.05 / 0.00063)
    assert len(data["location_history"]) == 1
    
    # 2. Second payload with modified coordinates (should increment distance to 0.10km)
    payload_2 = {
        "user_id": user_id,
        "device_id": "eui-70b3d57ed0051111",
        "timestamp": "2026-07-14T12:30:00Z",
        "latitude": 52.0418,  # Changed
        "longitude": -2.3790,  # Changed
        "temperature": 22.5,
        "light": 160
    }
    status_post_2, _, _ = sim_server.process_api_post("/sensecap", payload_2, auth_key)
    assert status_post_2 == 201
    
    # Verify values are correctly incremented
    status_get_2, _, body_2 = sim_server.process_api_get("/history", {"user_id": user_id})
    assert status_get_2 == 200
    data_2 = json.loads(body_2)
    assert data_2["cumulative_distance_km"] == 0.10
    assert data_2["cumulative_steps"] == int(0.10 / 0.00063)
    assert len(data_2["location_history"]) == 2

def test_location_history_bounds_cap():
    """Verify that coordinates history array maintains a strict max limit of 20 elements."""
    user_id = "hvy"
    auth_key = sim_server.USER_KEYS.get(user_id)
    
    # Post 22 coordinates
    for i in range(22):
        payload = {
            "user_id": user_id,
            "device_id": "eui-70b3d57ed0051111",
            "timestamp": f"2026-07-14T13:{i:02d}:00Z",
            "latitude": 52.0411 + (i * 0.0001),
            "longitude": -2.3784 + (i * 0.0001),
            "temperature": 22.0,
            "light": 150
        }
        status, _, _ = sim_server.process_api_post("/sensecap", payload, auth_key)
        assert status == 201
        
    # Get history and check length
    status_get, _, body = sim_server.process_api_get("/history", {"user_id": user_id})
    assert status_get == 200
    data = json.loads(body)
    assert len(data["location_history"]) == 20

def test_spirit_drinks_aggregation():
    """Verify that logging Martini, G+T, Negroni, and Port increments total_drinks but NOT beer_drinks."""
    user_id = "cha"
    auth_key = sim_server.USER_KEYS.get(user_id)
    
    # 1. Log a G+T
    payload_gt = {
        "user_id": user_id,
        "event": "Drinks",
        "type": "G+T"
    }
    status, _, _ = sim_server.process_api_post("/beer", payload_gt, auth_key)
    assert status == 201
    
    # 2. Log a Negroni
    payload_negroni = {
        "user_id": user_id,
        "event": "Drinks",
        "type": "Negroni"
    }
    status, _, _ = sim_server.process_api_post("/beer", payload_negroni, auth_key)
    assert status == 201
    
    # 3. Get totals and assert counts
    status_get, _, body = sim_server.process_api_get("/beer", {"user_id": user_id})
    assert status_get == 200
    data = json.loads(body)
    assert data["total_drinks"] == 2
    assert data["beer_drinks"] == 0
    assert data["categories"].get("G+T") == 1
    assert data["categories"].get("Negroni") == 1

def test_all_time_drinks_aggregation():
    """Verify that posting a drink POST aggregates all_time_total_drinks and is unaffected by manual daily resets."""
    user_id = "cha"
    auth_key = sim_server.USER_KEYS.get(user_id)
    
    # 1. Log drinks
    payload_m = {"user_id": user_id, "event": "Drinks", "type": "Martini"}
    sim_server.process_api_post("/beer", payload_m, auth_key)
    
    # Verify both total_drinks and all_time_total_drinks are 1
    agg_key = f"camper#aggregates#{user_id}"
    user_totals = sim_server.db_get_item(agg_key, "totals")
    assert user_totals["total_drinks"] == 1
    assert user_totals["all_time_total_drinks"] == 1
    
    # 2. Reset the daily totals
    payload_reset = {"user_id": user_id, "event": "Reset", "type": "ResetDay"}
    sim_server.process_api_post("/beer", payload_reset, auth_key)
    
    # Verify daily total_drinks resets to 0 but all_time_total_drinks is preserved at 1
    user_totals_2 = sim_server.db_get_item(agg_key, "totals")
    assert user_totals_2["total_drinks"] == 0
    assert user_totals_2["all_time_total_drinks"] == 1

def test_lazy_daily_reset():
    """Verify that a UTC calendar day transition automatically triggers a lazy daily reset."""
    user_id = "cha"
    auth_key = sim_server.USER_KEYS.get(user_id)
    
    # 1. Log a baseline drink to initialize and set today's date
    payload_w = {"user_id": user_id, "event": "Drinks", "type": "Water"}
    sim_server.process_api_post("/beer", payload_w, auth_key)
    
    agg_key = f"camper#aggregates#{user_id}"
    user_totals = sim_server.db_get_item(agg_key, "totals")
    assert user_totals["total_drinks"] == 1
    assert user_totals["last_reset_date"] is not None
    
    # 2. Simulate date boundary transition by setting last_reset_date to yesterday
    user_totals["last_reset_date"] = "2026-07-14"
    sim_server.db_put_item(agg_key, "totals", user_totals)
    
    # 3. Post a new drink on the "new" day (today, July 15)
    sim_server.process_api_post("/beer", payload_w, auth_key)
    
    # Verify daily total_drinks reset and counts start at 1 for the new day
    user_totals_after = sim_server.db_get_item(agg_key, "totals")
    assert user_totals_after["total_drinks"] == 1
    assert user_totals_after["all_time_total_drinks"] == 2

def test_push_subscribe_storage():
    """Verify that posting a push subscription securely registers and stores it in the aggregate."""
    user_id = "cha"
    auth_key = sim_server.USER_KEYS.get(user_id)
    
    payload = {
        "user_id": user_id,
        "subscription": {
            "endpoint": "https://fcm.googleapis.com/fcm/send/sample-token",
            "keys": {
                "p256dh": "sample-p256dh-key",
                "auth": "sample-auth-secret"
            }
        },
        "interval_minutes": 120
    }
    
    # 1. Post subscription
    status, _, body = sim_server.process_api_post("/push-subscribe", payload, auth_key)
    assert status == 201
    data = json.loads(body)
    assert data["status"] == "success"
    
    # 2. Retrieve aggregate and assert values
    agg_key = f"camper#aggregates#{user_id}"
    user_totals = sim_server.db_get_item(agg_key, "totals")
    assert user_totals["push_subscription"]["endpoint"] == "https://fcm.googleapis.com/fcm/send/sample-token"
    assert user_totals["push_subscription"]["keys"]["p256dh"] == "sample-p256dh-key"
    assert user_totals["push_interval_minutes"] == 120
    assert user_totals["push_last_notified_time"] is not None


def test_manual_expenditure_logging():
    """Verify manual expenditure logs item description when provided, and defaults to price when absent."""
    user_id = "cha"
    auth_key = sim_server.USER_KEYS.get(user_id)
    
    # 1. Post manual expenditure with item name
    payload_item = {
        "user_id": user_id,
        "amount": -5.50,
        "merchant": "Burger"
    }
    status, _, body = sim_server.process_api_post("/monzo-sync-simulation", payload_item, auth_key)
    assert status == 201
    
    # Verify transaction list has the Burger
    status_get, _, body_get = sim_server.process_api_get("/monzo", {"user_id": user_id})
    assert status_get == 200
    data = json.loads(body_get)
    burger_tx = [t for t in data["transactions"] if t["description"] == "Burger"]
    assert len(burger_tx) == 1
    assert burger_tx[0]["amount_gbp"] == -5.50
    
    # 2. Post manual expenditure without item name (merchant is empty string or absent)
    payload_no_item = {
        "user_id": user_id,
        "amount": -7.25,
        "merchant": ""
    }
    status, _, body = sim_server.process_api_post("/monzo-sync-simulation", payload_no_item, auth_key)
    assert status == 201
    
    # Verify description defaults to formatted price "£7.25"
    status_get_2, _, body_get_2 = sim_server.process_api_get("/monzo", {"user_id": user_id})
    assert status_get_2 == 200
    data_2 = json.loads(body_get_2)
    price_tx = [t for t in data_2["transactions"] if t["description"] == "£7.25"]
    assert len(price_tx) == 1
    assert price_tx[0]["amount_gbp"] == -7.25


def test_classy_beverages_aggregation():
    """Verify that logging BoxPerry increments beer_drinks, while BoxWine increments total_drinks but NOT beer_drinks."""
    user_id = "cha"
    auth_key = sim_server.USER_KEYS.get(user_id)
    
    # 1. Log BoxPerry (classified as beer/cider equivalent)
    payload_perry = {
        "user_id": user_id,
        "event": "Drinks",
        "type": "BoxPerry",
        "beer": "true"
    }
    status, _, _ = sim_server.process_api_post("/beer", payload_perry, auth_key)
    assert status == 201
    
    # 2. Log BoxWine (classified as classy wine equivalent, not beer_drinks)
    payload_wine = {
        "user_id": user_id,
        "event": "Drinks",
        "type": "BoxWine",
        "beer": ""
    }
    status, _, _ = sim_server.process_api_post("/beer", payload_wine, auth_key)
    assert status == 201
    
    # 3. Retrieve and assert counts
    status_get, _, body = sim_server.process_api_get("/beer", {"user_id": user_id})
    assert status_get == 200
    data = json.loads(body)
    assert data["total_drinks"] == 2
    assert data["beer_drinks"] == 1  # BoxPerry incremented it, BoxWine did not
    assert data["categories"].get("BoxPerry") == 1
    assert data["categories"].get("BoxWine") == 1


def test_club_mate_aggregation():
    """Verify that logging ClubMate increments total_drinks but NOT beer_drinks."""
    user_id = "cha"
    auth_key = sim_server.USER_KEYS.get(user_id)
    
    payload = {
        "user_id": user_id,
        "event": "Drinks",
        "type": "ClubMate",
        "beer": ""
    }
    status, _, _ = sim_server.process_api_post("/beer", payload, auth_key)
    assert status == 201
    
    status_get, _, body = sim_server.process_api_get("/beer", {"user_id": user_id})
    assert status_get == 200
    data = json.loads(body)
    assert data["total_drinks"] == 1
    assert data["beer_drinks"] == 0
    assert data["categories"].get("ClubMate") == 1


def test_lazy_reset_4am_cutoff():
    """Verify that daily transitions happen exactly at 4:00 AM UTC (effective date transition)."""
    user_id = "cha"
    agg_key = f"camper#aggregates#{user_id}"
    
    # 1. Start with aggregates initialized
    user_totals = {
        "user_id": user_id,
        "total_drinks": 5,
        "beer_drinks": 2,
        "categories": {"Lager": 2, "Water": 3},
        "last_reset_date": "2026-07-14"
    }
    sim_server.db_put_item(agg_key, "totals", user_totals)
    
    # 2. Check at 3:59:59 AM on July 15 (effective date is still July 14 because of 4-hour shift)
    # Should NOT trigger a reset because effective date (July 14) == last_reset_date (July 14)
    sim_server.trigger_lazy_reset(user_id, "2026-07-15T03:59:59Z")
    totals_before = sim_server.db_get_item(agg_key, "totals")
    assert totals_before["total_drinks"] == 5
    assert totals_before["last_reset_date"] == "2026-07-14"
    
    # 3. Check at exactly 4:00:00 AM on July 15 (effective date transitions to July 15)
    # Should trigger a reset because effective date (July 15) != last_reset_date (July 14)
    sim_server.trigger_lazy_reset(user_id, "2026-07-15T04:00:00Z")
    totals_after = sim_server.db_get_item(agg_key, "totals")
    assert totals_after["total_drinks"] == 0
    assert totals_after["last_reset_date"] == "2026-07-15"


def test_step_baseline_self_healing():
    """Verify that if cumulative_steps is smaller than steps_baseline, baseline is healed to 0."""
    user_id = "cha"
    agg_key = f"camper#aggregates#{user_id}"
    dev_key = f"device#eui-70b3d57ed0051111#{user_id}"
    
    # Set up: baseline is 10000 steps
    user_totals = {
        "user_id": user_id,
        "steps_baseline": 10000,
        "last_reset_date": "2026-07-17"
    }
    sim_server.db_put_item(agg_key, "totals", user_totals)
    
    # Device rebooted or reset: cumulative_steps is only 4000
    device_state = {
        "cumulative_steps": 4000,
        "cumulative_distance_km": 2.5,
        "location_history": []
    }
    sim_server.db_put_item(dev_key, "state", device_state)
    
    # Fetch history: should trigger self-healing, reset baseline to 0, and return 4000 steps
    status, _, body = sim_server.process_api_get("/history", {"user_id": user_id})
    assert status == 200
    data = json.loads(body)
    assert data["cumulative_steps"] == 4000  # daily steps are now 4000 instead of 0
    
    # Assert database aggregates are healed too
    healed_totals = sim_server.db_get_item(agg_key, "totals")
    assert healed_totals["steps_baseline"] == 0


def test_steps_dual_interpretation():
    """Verify that posting steps less than baseline is treated as daily, and >= baseline is treated as cumulative."""
    user_id = "cha"
    auth_key = sim_server.USER_KEYS.get(user_id)
    agg_key = f"camper#aggregates#{user_id}"
    dev_key = f"device#eui-70b3d57ed0051111#{user_id}"
    
    # 1. Base setup: baseline is 10000 steps
    user_totals = {
        "user_id": user_id,
        "steps_baseline": 10000,
        "last_reset_date": "2026-07-17"
    }
    sim_server.db_put_item(agg_key, "totals", user_totals)
    
    # 2. Case A: User walks 5000 steps today, and logs "5000" (less than baseline 10000)
    # This should be interpreted as daily steps. Cumulative steps should become 10000 + 5000 = 15000.
    payload_daily = {"user_id": user_id, "steps": 5000}
    status, _, _ = sim_server.process_api_post("/steps", payload_daily, auth_key)
    assert status == 201
    
    # Verify cumulative steps in state and aggregates
    state = sim_server.db_get_item(dev_key, "state")
    assert state["cumulative_steps"] == 15000
    totals = sim_server.db_get_item(agg_key, "totals")
    assert totals["all_time_cumulative_steps"] == 15000
    
    # Verify daily steps is exactly 5000
    status_get, _, body = sim_server.process_api_get("/history", {"user_id": user_id})
    assert status_get == 200
    data = json.loads(body)
    assert data["cumulative_steps"] == 5000
    
    # 3. Case B: User walks and manually logs cumulative "18000" (greater than baseline 10000)
    # This should be interpreted as cumulative steps directly. Cumulative steps should become 18000.
    payload_cum = {"user_id": user_id, "steps": 18000}
    status, _, _ = sim_server.process_api_post("/steps", payload_cum, auth_key)
    assert status == 201
    
    state_2 = sim_server.db_get_item(dev_key, "state")
    assert state_2["cumulative_steps"] == 18000
    totals_2 = sim_server.db_get_item(agg_key, "totals")
    assert totals_2["all_time_cumulative_steps"] == 18000









