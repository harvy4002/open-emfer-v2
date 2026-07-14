# backend/tests/integration/test_history_flow.py
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

def test_history_coordinate_checking():
    """Verify that GET /history and POST /sensecap coordinate flows process successfully."""
    user_id = "cha"  # Test different user
    auth_key = sim_server.USER_KEYS.get(user_id)
    
    # 1. Post coordinates to /sensecap
    payload = {
        "user_id": user_id,
        "device_id": "eui-70b3d57ed0051111",
        "timestamp": "2026-07-14T14:00:00Z",
        "latitude": 52.0411,
        "longitude": -2.3784,
        "temperature": 23.0,
        "light": 100
    }
    status, _, body = sim_server.process_api_post("/sensecap", payload, auth_key)
    assert status == 201
    assert json.loads(body)["status"] == "success"
    
    # 2. Query /history
    status_get, _, body_get = sim_server.process_api_get("/history", {"user_id": user_id})
    assert status_get == 200
    data = json.loads(body_get)
    assert data["user_id"] == user_id
    assert len(data["location_history"]) == 1
    assert data["location_history"][0]["lat"] == 52.0411
    assert data["location_history"][0]["lng"] == -2.3784
