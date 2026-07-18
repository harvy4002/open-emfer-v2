#!/usr/bin/env python3
"""
backend/test_endpoints.py
Zero-dependency Integration Test for Open EMF Camper API Endpoints.
Queries /beer, /history, and /expenditure for all active dashboards to verify HTTP codes,
payload structure, and check for any live API errors.
"""

import sys
import json
import urllib.request
import urllib.error
from datetime import datetime

# Config target API Base URL (Default to live AWS API Gateway Production stage)
LIVE_API_BASE = "https://01uy6frz0h.execute-api.eu-west-2.amazonaws.com/prod"
LOCAL_API_BASE = "http://localhost:3000"

CAMPERS = ["hvy", "cha", "ash", "tin", "combined"]

# ANSI Color escapes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def make_request(url):
    """Executes an HTTP GET request and returns (status_code, body_string, error_message)."""
    try:
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "EMF-Camper-Test-Runner/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, response.read().decode("utf-8"), None
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8")
        except Exception:
            err_body = str(e)
        return e.code, err_body, f"HTTP Error {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return 0, "", f"URL Connection Error: {e.reason}"
    except Exception as e:
        return 0, "", f"Unexpected Exception: {e}"

def test_camper_endpoints(base_url, camper_id):
    """Runs a suite of GET tests for a specific camper and reports status."""
    print(f"\n{BLUE}--- Testing Dashboard Context: ?u={camper_id} ---{RESET}")
    errors = []

    # 1. Test /beer endpoint
    beer_url = f"{base_url}/beer?user_id={camper_id}"
    print(f"GET {beer_url} ... ", end="")
    status, body, err = make_request(beer_url)
    
    if err:
        print(f"{RED}[FAIL]{RESET} -> {err}")
        errors.append(f"/beer: {err} (Response: {body})")
    elif status != 200:
        print(f"{RED}[FAIL]{RESET} -> HTTP {status}")
        errors.append(f"/beer: HTTP {status} (Response: {body})")
    else:
        try:
            data = json.loads(body)
            # Verify required properties
            if data.get("status") != "success":
                raise KeyError(f"'status' is {data.get('status')} instead of 'success'")
            if "total_drinks" not in data or "beer_drinks" not in data:
                raise KeyError("missing 'total_drinks' or 'beer_drinks' attributes")
            if camper_id == "combined" and "leaderboard" not in data:
                raise KeyError("missing 'leaderboard' on combined stats payload")
                
            print(f"{GREEN}[PASS]{RESET} (drinks: {data.get('total_drinks')})")
        except Exception as e:
            print(f"{RED}[FAIL]{RESET} -> JSON Parse/Validation: {e}")
            errors.append(f"/beer JSON: {e} (Response: {body})")

    # 2. Test /history endpoint
    history_url = f"{base_url}/history?user_id={camper_id}"
    print(f"GET {history_url} ... ", end="")
    status, body, err = make_request(history_url)
    
    if err:
        print(f"{RED}[FAIL]{RESET} -> {err}")
        errors.append(f"/history: {err} (Response: {body})")
    elif status != 200:
        print(f"{RED}[FAIL]{RESET} -> HTTP {status}")
        errors.append(f"/history: HTTP {status} (Response: {body})")
    else:
        try:
            data = json.loads(body)
            # Verify required properties
            if data.get("status") != "success":
                raise KeyError(f"'status' is {data.get('status')} instead of 'success'")
            if "cumulative_steps" not in data or "cumulative_distance_km" not in data or "location_history" not in data:
                raise KeyError("missing 'cumulative_steps', 'cumulative_distance_km', or 'location_history'")
            if not isinstance(data.get("location_history"), list):
                raise TypeError("'location_history' is not a list")
                
            print(f"{GREEN}[PASS]{RESET} (steps: {data.get('cumulative_steps')}, map_pts: {len(data.get('location_history'))})")
        except Exception as e:
            print(f"{RED}[FAIL]{RESET} -> JSON Parse/Validation: {e}")
            errors.append(f"/history JSON: {e} (Response: {body})")

    # 3. Test /expenditure endpoint
    expenditure_url = f"{base_url}/expenditure?user_id={camper_id}"
    print(f"GET {expenditure_url} ... ", end="")
    status, body, err = make_request(expenditure_url)
    
    if err:
        print(f"{RED}[FAIL]{RESET} -> {err}")
        errors.append(f"/expenditure: {err} (Response: {body})")
    elif status != 200:
        print(f"{RED}[FAIL]{RESET} -> HTTP {status}")
        errors.append(f"/expenditure: HTTP {status} (Response: {body})")
    else:
        try:
            data = json.loads(body)
            # Verify required properties
            if data.get("status") != "success":
                raise KeyError(f"'status' is {data.get('status')} instead of 'success'")
            if "total_expenditure_gbp" not in data or "transactions" not in data:
                raise KeyError("missing 'total_expenditure_gbp' or 'transactions'")
                
            print(f"{GREEN}[PASS]{RESET} (spend: £{data.get('total_expenditure_gbp'):.2f}, txs: {len(data.get('transactions', []))})")
        except Exception as e:
            print(f"{RED}[FAIL]{RESET} -> JSON Parse/Validation: {e}")
            errors.append(f"/expenditure JSON: {e} (Response: {body})")

    # 4. Test /playback endpoint (T009)
    playback_url = f"{base_url}/playback?user_id={camper_id}&until={datetime.now().isoformat()}Z"
    print(f"GET {playback_url} ... ", end="")
    status, body, err = make_request(playback_url)
    
    if err:
        print(f"{RED}[FAIL]{RESET} -> {err}")
        errors.append(f"/playback: {err} (Response: {body})")
    elif status != 200:
        print(f"{RED}[FAIL]{RESET} -> HTTP {status}")
        errors.append(f"/playback: HTTP {status} (Response: {body})")
    else:
        try:
            data = json.loads(body)
            # Verify required properties
            if data.get("status") != "success":
                raise KeyError(f"'status' is {data.get('status')} instead of 'success'")
            if "reconstructed_state" not in data or "events_processed" not in data:
                raise KeyError("missing 'reconstructed_state' or 'events_processed'")
                
            print(f"{GREEN}[PASS]{RESET} (replayed_events: {data.get('events_processed')})")
        except Exception as e:
            print(f"{RED}[FAIL]{RESET} -> JSON Parse/Validation: {e}")
            errors.append(f"/playback JSON: {e} (Response: {body})")

    return errors

def main():
    # Allow target override via cmd args (e.g. `test_endpoints.py local`)
    base_url = LIVE_API_BASE
    if len(sys.argv) > 1 and sys.argv[1].lower() in ["local", "localhost", "dev"]:
        base_url = LOCAL_API_BASE
        print(f"{YELLOW}Testing LOCAL Simulator environment: {base_url}{RESET}")
    else:
        print(f"{YELLOW}Testing LIVE Production stage environment: {base_url}{RESET}")
        print(f"{YELLOW}Note: Ensure you let the CI/CD pipeline deploy completely first if you just pushed a hotfix.{RESET}")

    total_errors = 0
    for camper in CAMPERS:
        camper_errors = test_camper_endpoints(base_url, camper)
        total_errors += len(camper_errors)

    print("\n" + "=" * 40)
    if total_errors == 0:
        print(f"{GREEN}✓ ALL TESTS PASSED SUCCESSFULLY! No API errors detected.{RESET}")
        sys.exit(0)
    else:
        print(f"{RED}✗ DETECTED {total_errors} ENDPOINT FAILURES DURING VALIDATION.{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
