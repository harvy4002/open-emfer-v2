# backend/tests/unit/test_status_resolver.py
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

def test_status_resolver_default_and_normalization():
    """Verify that user status resolution falls back to chilling and normalizes text correctly."""
    user_id = "hvy"
    auth_key = sim_server.USER_KEYS.get(user_id)
    
    # 1. Before posting anything, check status
    status_get, _, body = sim_server.process_api_get("/beer", {
        "user_id": user_id,
        "event": "status",
        "type": "latest"
    })
    assert status_get == 200
    data = json.loads(body)
    assert data["status"] == "normal"  # Should default to lowercase "normal"
    
    # 2. Post a custom status containing mixed-case text using 'type' representing admin panel
    status_post, _, _ = sim_server.process_api_post("/beer", {
        "user_id": user_id,
        "event": "status",
        "type": "Sleeping"
    }, auth_key)
    assert status_post == 201
    
    # 3. Retrieve status and check normalization
    status_get_2, _, body_2 = sim_server.process_api_get("/beer", {
        "user_id": user_id,
        "event": "status",
        "type": "latest"
    })
    assert status_get_2 == 200
    data_2 = json.loads(body_2)
    assert data_2["status"] == "sleeping"  # Must normalize "Sleeping" -> "sleeping"
    
    # 4. Verify that the aggregate totals record was successfully updated with status
    agg_key = f"camper#aggregates#{user_id}"
    user_totals = sim_server.db_get_item(agg_key, "totals")
    assert user_totals is not None
    assert user_totals.get("status") == "sleeping"


def test_status_drunk():
    """Verify that posting 'Drunk' status saves it successfully and normalizes it."""
    user_id = "hvy"
    auth_key = sim_server.USER_KEYS.get(user_id)
    
    # Post Drunk status
    status_post, _, _ = sim_server.process_api_post("/beer", {
        "user_id": user_id,
        "event": "status",
        "type": "Drunk"
    }, auth_key)
    assert status_post == 201
    
    # Retrieve status and verify
    status_get, _, body = sim_server.process_api_get("/beer", {
        "user_id": user_id,
        "event": "status",
        "type": "latest"
    })
    assert status_get == 200
    data = json.loads(body)
    assert data["status"] == "drunk"

