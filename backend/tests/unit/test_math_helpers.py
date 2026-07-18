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
    status, _, body = sim_server.process_api_post("/expenditure", payload_item, auth_key)
    assert status == 201
    
    # Verify transaction list has the Burger
    status_get, _, body_get = sim_server.process_api_get("/expenditure", {"user_id": user_id})
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
    status, _, body = sim_server.process_api_post("/expenditure", payload_no_item, auth_key)
    assert status == 201
    
    # Verify description defaults to formatted price "£7.25"
    status_get_2, _, body_get_2 = sim_server.process_api_get("/expenditure", {"user_id": user_id})
    assert status_get_2 == 200
    data_2 = json.loads(body_get_2)
    price_tx = [t for t in data_2["transactions"] if t["description"] == "£7.25"]
    assert len(price_tx) == 1
    assert price_tx[0]["amount_gbp"] == -7.25


def test_expenditure_migration():
    """Verify that old monzo#transactions data is correctly migrated to camper#aggregates#hvy."""
    # 1. Manually insert an old monzo transaction record into the DB
    old_txs = [
        {
            "id": "tx_old_1",
            "description": "Old Monzo Expense",
            "amount_gbp": -15.50,
            "timestamp": "2026-07-14T20:00:00Z"
        }
    ]
    sim_server.db_put_item("monzo#transactions", "latest", {
        "total_expenditure_gbp": 15.50,
        "transactions": old_txs
    })

    # 2. Query /expenditure for 'hvy' and verify that it performs the migration
    status, _, body = sim_server.process_api_get("/expenditure", {"user_id": "hvy"})
    assert status == 200
    data = json.loads(body)
    assert data["total_expenditure_gbp"] == 15.50
    assert len(data["transactions"]) == 1
    assert data["transactions"][0]["id"] == "tx_old_1"
    assert data["transactions"][0]["description"] == "Old Monzo Expense"

    # 3. Assert that it is now persistently saved in hvy's aggregates
    user_totals = sim_server.db_get_item("camper#aggregates#hvy", "totals")
    assert user_totals["total_expenditure_gbp"] == 15.50
    assert len(user_totals["transactions"]) == 1


def test_expenditure_migration_one_off():
    """Verify that one-off rebuild endpoint successfully triggers expenditure migration."""
    # 1. Manually insert an old monzo transaction record into the DB
    old_txs = [
        {
            "id": "tx_old_2",
            "description": "Old Monzo Expense 2",
            "amount_gbp": -25.00,
            "timestamp": "2026-07-14T21:00:00Z"
        }
    ]
    sim_server.db_put_item("monzo#transactions", "latest", {
        "total_expenditure_gbp": 25.00,
        "transactions": old_txs
    })

    # Also make sure there's a hvy aggregate totals record to migrate into
    sim_server.db_put_item("camper#aggregates#hvy", "totals", {
        "user_id": "hvy",
        "total_drinks": 0,
        "beer_drinks": 0,
        "categories": {},
        "all_time_total_drinks": 0,
        "all_time_cumulative_steps": 0,
        "total_expenditure_gbp": 0.0,
        "transactions": [],
        "last_reset_date": "2026-07-18"
    })

    # 2. Call the /rebuild-steps-one-off endpoint
    status, _, body = sim_server.process_api_get("/rebuild-steps-one-off", {})
    assert status == 200

    # 3. Assert that it migrated persistently to hvy's aggregates
    user_totals = sim_server.db_get_item("camper#aggregates#hvy", "totals")
    assert user_totals["total_expenditure_gbp"] == 25.00
    assert len(user_totals["transactions"]) == 1


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
    from datetime import datetime, timedelta
    eff_date = (datetime.utcnow() - timedelta(hours=4)).strftime("%Y-%m-%d")
    
    user_id = "cha"
    auth_key = sim_server.USER_KEYS.get(user_id)
    agg_key = f"camper#aggregates#{user_id}"
    dev_key = f"device#eui-70b3d57ed0051111#{user_id}"
    
    # 1. Base setup: baseline is 10000 steps
    user_totals = {
        "user_id": user_id,
        "steps_baseline": 10000,
        "last_reset_date": eff_date
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


def test_update_baseline_steps():
    """Verify that posting a baseline parameter to /steps updates steps_baseline successfully."""
    from datetime import datetime, timedelta
    eff_date = (datetime.utcnow() - timedelta(hours=4)).strftime("%Y-%m-%d")
    
    user_id = "cha"
    auth_key = sim_server.USER_KEYS.get(user_id)
    agg_key = f"camper#aggregates#{user_id}"
    
    # 1. Base setup: baseline is 10000 steps
    user_totals = {
        "user_id": user_id,
        "steps_baseline": 10000,
        "last_reset_date": eff_date
    }
    sim_server.db_put_item(agg_key, "totals", user_totals)
    
    # 2. Post a baseline update to /steps
    payload = {"user_id": user_id, "baseline": 12500}
    status, _, body = sim_server.process_api_post("/steps", payload, auth_key)
    assert status == 201
    
    # Verify DB update
    totals = sim_server.db_get_item(agg_key, "totals")
    assert totals["steps_baseline"] == 12500


def test_steps_by_date_overrides():
    """Verify that posting date and steps parameter to /steps updates that specific date's steps successfully."""
    from datetime import datetime, timedelta
    eff_date = (datetime.utcnow() - timedelta(hours=4)).strftime("%Y-%m-%d")
    yesterday = (datetime.utcnow() - timedelta(days=1, hours=4)).strftime("%Y-%m-%d")
    
    user_id = "cha"
    auth_key = sim_server.USER_KEYS.get(user_id)
    agg_key = f"camper#aggregates#{user_id}"
    dev_key = f"device#eui-70b3d57ed0051111#{user_id}"
    
    # 1. Base setup: user has 10000 steps yesterday, and 15000 steps today cumulative
    user_totals = {
        "user_id": user_id,
        "steps_baseline": 10000,
        "all_time_cumulative_steps": 15000,
        "last_reset_date": eff_date,
        "daily_steps_history": {
            yesterday: 10000,
            eff_date: 15000
        }
    }
    sim_server.db_put_item(agg_key, "totals", user_totals)
    
    # 2. Post a specific date override (update yesterday to 12000 steps cumulative)
    payload = {
        "user_id": user_id,
        "date": yesterday,
        "steps": 12000
    }
    status, _, body = sim_server.process_api_post("/steps", payload, auth_key)
    assert status == 201
    
    # Verify aggregates are recalculated (baseline becomes 12000, cumulative becomes 12000 + 5000 = 17000)
    totals = sim_server.db_get_item(agg_key, "totals")
    assert totals["daily_steps_history"][yesterday] == 12000
    assert totals["daily_steps_history"][eff_date] == 17000
    assert totals["steps_baseline"] == 12000
    assert totals["all_time_cumulative_steps"] == 17000
    
    # Verify device state is updated
    state = sim_server.db_get_item(dev_key, "state")
    assert state["cumulative_steps"] == 17000


def test_history_endpoint_daily_steps_history():
    """Verify that GET /history endpoint returns daily_steps_history correctly."""
    user_id = "cha"
    agg_key = f"camper#aggregates#{user_id}"
    user_totals = {
        "user_id": user_id,
        "steps_baseline": 1000,
        "all_time_cumulative_steps": 2500,
        "daily_steps_history": {
            "2026-07-16": 1000,
            "2026-07-17": 1500
        }
    }
    sim_server.db_put_item(agg_key, "totals", user_totals)

    # Fetch history for this user
    status, _, body = sim_server.process_api_get("/history", {"user_id": user_id})
    assert status == 200
    data = json.loads(body)
    assert "daily_steps_history" in data
    assert data["daily_steps_history"]["2026-07-16"] == 1000
    assert data["daily_steps_history"]["2026-07-17"] == 1500


def test_rebuild_steps_one_off_history_reconstruction():
    """Verify that /rebuild-steps-one-off reconstructs cumulative steps and history map from events."""
    user_id = "cha"
    event_key = f"camper#events#{user_id}"
    
    # 1. Map events with custom timestamps into the database
    sim_server.db_put_item(event_key, "event#2026-07-16T12:00:00.000Z#hash1", {
        "event_id": "e1",
        "user_id": user_id,
        "event_type": "steps",
        "payload": {"steps": 1000},
        "timestamp": "2026-07-16T12:00:00.000Z"
    })
    sim_server.db_put_item(event_key, "event#2026-07-16T23:00:00.000Z#hash2", {
        "event_id": "e2",
        "user_id": user_id,
        "event_type": "steps",
        "payload": {"steps": 1500},
        "timestamp": "2026-07-16T23:00:00.000Z"
    })
    sim_server.db_put_item(event_key, "event#2026-07-17T03:00:00.000Z#hash3", {  # 3:00 UTC is still 2026-07-16 calendar day after subtracting 4 hours
        "event_id": "e3",
        "user_id": user_id,
        "event_type": "steps",
        "payload": {"steps": 1800},
        "timestamp": "2026-07-17T03:00:00.000Z"
    })
    sim_server.db_put_item(event_key, "event#2026-07-17T04:30:00.000Z#hash4", {  # This is after 4am, so it starts the new day 2026-07-17
        "event_id": "e4",
        "user_id": user_id,
        "event_type": "Reset",
        "payload": {"type": "ResetDay"},
        "timestamp": "2026-07-17T04:30:00.000Z"
    })
    sim_server.db_put_item(event_key, "event#2026-07-17T12:00:00.000Z#hash5", {
        "event_id": "e5",
        "user_id": user_id,
        "event_type": "steps",
        "payload": {"steps": 3000},
        "timestamp": "2026-07-17T12:00:00.000Z"
    })

    # 2. Trigger the rebuild endpoint
    status, _, body = sim_server.process_api_get("/rebuild-steps-one-off", {})
    assert status == 200
    data = json.loads(body)
    
    # 3. Assert reconstructed values inside response
    results = data["results"]["cha"]
    assert results["reconstructed_cumulative_steps"] == 3000
    
    daily_history = results["reconstructed_daily_steps_history"]
    # 2026-07-16: max cumulative reached was 1800 -> 1800 steps cumulative
    assert daily_history["2026-07-16"] == 1800
    # 2026-07-17: max cumulative 3000 -> 3000 steps cumulative
    assert daily_history["2026-07-17"] == 3000

    # 4. Verify values are saved persistently in the database camper aggregates
    user_totals = sim_server.db_get_item("camper#aggregates#cha", "totals")
    assert user_totals["all_time_cumulative_steps"] == 3000
    assert user_totals["daily_steps_history"]["2026-07-16"] == 1800
    assert user_totals["daily_steps_history"]["2026-07-17"] == 3000











