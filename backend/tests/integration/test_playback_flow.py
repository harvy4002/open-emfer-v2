# backend/tests/integration/test_playback_flow.py
import os
import json
import pytest
import time
from datetime import datetime
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

def test_playback_chronological_state_reconstruction():
    """Verify that /playback correctly plays back state chronologically up to a boundary timestamp."""
    user_id = "hvy"
    auth_key = sim_server.USER_KEYS.get(user_id)
    
    # 1. Post Event A (12:00) - 2 pints of IPA
    payload_a = {
        "user_id": user_id,
        "event": "Drinks",
        "type": "IPA",
        "beer": True
    }
    status, _, _ = sim_server.process_api_post("/beer", payload_a, auth_key)
    assert status == 201
    
    # Post Event B (12:05) - another IPA
    payload_b = {
        "user_id": user_id,
        "event": "Drinks",
        "type": "IPA",
        "beer": True
    }
    status_2, _, _ = sim_server.process_api_post("/beer", payload_b, auth_key)
    assert status_2 == 201
    
    # Capture intermediate timestamp
    time.sleep(0.01)
    intermediate_timestamp = datetime.now().isoformat() + "Z"
    time.sleep(0.01)
    
    # 2. Post Event C (13:00) - 1 Toilet trip
    payload_c = {
        "user_id": user_id,
        "event": "Toilet",
        "type": "Pee"
    }
    status_3, _, _ = sim_server.process_api_post("/beer", payload_c, auth_key)
    assert status_3 == 201
    
    # Capture final timestamp
    time.sleep(0.01)
    final_timestamp = datetime.now().isoformat() + "Z"
    
    # 3. Query playback at intermediate boundary (should only reconstruct Event A and B)
    status_get, _, body = sim_server.process_api_get("/playback", {
        "user_id": user_id,
        "until": intermediate_timestamp
    })
    assert status_get == 200
    data = json.loads(body)
    assert data["events_processed"] == 2
    state = data["reconstructed_state"]
    assert state["categories"]["IPA"] == 2
    assert "Pee" not in state["categories"]
    
    # 4. Query playback at final boundary (should reconstruct all events)
    status_get_2, _, body_2 = sim_server.process_api_get("/playback", {
        "user_id": user_id,
        "until": final_timestamp
    })
    assert status_get_2 == 200
    data_2 = json.loads(body_2)
    assert data_2["events_processed"] == 3
    state_2 = data_2["reconstructed_state"]
    assert state_2["categories"]["IPA"] == 2
    assert state_2["categories"]["Pee"] == 1
