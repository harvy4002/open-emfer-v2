# Quickstart Validation Guide: Camper Profile Status Photos

This guide provides step-by-step instructions to validate the dynamic profile picture swap rendering against both pre-existing `.jpg` assets and gracefully handled missing fallbacks.

## Prerequisites
Ensure the local frontend assets are being served statically using the backend python module, and that the backend simulator is active:
```bash
# Terminal 1: Run the backend emulator/static server on port 3000
python3 backend/sim_server.py
```

## Scenario 1: Validate Harvy's Dynamic Status Switch

1. Open your browser and navigate to Harvy's dashboard:
   [http://localhost:3000/index.html?u=hvy](http://localhost:3000/index.html?u=hvy)
2. Open another terminal and simulate setting Harvy's status to "Drinking":
   ```bash
   curl -X POST http://localhost:3000/beer \
     -H "Content-Type: application/json" \
     -H "tracker_key: mock-super-secret-key" \
     -d '{"user_id": "hvy", "event": "status", "type": "latest", "status": "Drinking"}'
   ```
3. Return to the browser tab. Upon the next background synchronization tick (approx. 5-10 seconds), verify the profile picture container visually updates from its current image to render `/harvy_status/harvy_drinking.jpg`.

## Scenario 2: Validate the Native HTML Fallback Routine

1. Trigger a completely missing/invalid status text for Harvy ("Supernova"):
   ```bash
   curl -X POST http://localhost:3000/beer \
     -H "Content-Type: application/json" \
     -H "tracker_key: mock-super-secret-key" \
     -d '{"user_id": "hvy", "event": "status", "type": "latest", "status": "Supernova"}'
   ```
2. Return to the browser.
3. Validate that after synchronization, the image frame *briefly* attempts to load `/harvy_status/harvy_supernova.jpg` (which will fail and trigger the browser's `onerror` loop) but instantly and gracefully settles on rendering the guaranteed `harvy_normal.jpg` fallback image, maintaining the layout bounds cleanly without displaying a broken image `[x]` icon.
