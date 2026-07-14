# Research Report: Sensecap Location Map Integration

This report details the technical choices, rationales, and alternatives evaluated for implementing the Sensecap location map integration for the EMF Camp public dashboard.

## 1. Map Library Selection

### Decision
Use **Leaflet.js** (v1.9.4) loaded via unpkg CDN.

### Rationale
- **Compliance with Principle VII**: Keeping the frontend as a cost-optimized, responsive static web application with **zero complex build pipelines**. Leaflet is highly lightweight (~40KB JS, ~4KB CSS), mobile-friendly, and loads directly via standard `<script>` and `<link>` tags in `web/index.html`.
- **Feature Set**: Perfectly supports plotting marker paths (`L.polyline`), adding customizable markers (`L.marker` / `L.circleMarker`), rendering map popups with timestamp telemetry, and defining custom tile layers with fallbacks.
- **No API Keys Required**: Leaflet allows direct rendering of custom tile URLs without requiring paid API keys (such as Mapbox or Google Maps).

### Alternatives Considered
- **Mapbox GL JS / MapLibre GL JS**: Offers vector tiling and high performance. However, MapLibre GL JS is heavier and requires more boilerplate. Mapbox requires API keys and has potential usage fees, violating the serverless zero-cost Principle VII.
- **HTML Canvas Overlays**: The current dashboard uses an HTML5 Canvas drawing coordinates over a static Unsplash photo background. While this requires no external libraries, it lacks zoom, pan, real physical geographic scaling, map labels, and proper spatial context. It is rejected in favor of a true geographical map.

---

## 2. Base Map Tile Server

### Decision
Use the custom EMF Camp tile server: `https://map.emfcamp.org/tiles/{z}/{x}/{y}.png` as the primary layer, with a standard OpenStreetMap tile server (`https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`) as an automatic fallback.

### Rationale
- **True Site Context**: The `map.emfcamp.org` tile server contains EMF Camp specific cartography (village zones, stages, power lines, toilets, campsite naming), which is critical for rendering the camper's precise position within the event.
- **Fail-safe Design**: Standard OSM serves as a perfect backup. If the EMF Camp tile server goes offline, the Leaflet map automatically switches or handles load failure by reverting to standard OSM tiles, ensuring the map remains functional.

### Alternatives Considered
- **Standard OpenStreetMap Tiles Only**: Works perfectly for geographical mapping, but lacks EMF-specific site data (villages, stages, camp-specific features). It is kept strictly as a fallback.

---

## 3. 3-Hour Location Path Filtering

### Decision
Perform client-side coordinate filtering inside the public dashboard (`web/js/app.js`). Calculate the 3-hour window **relative to the latest coordinate's timestamp** in the retrieved list (Option A chosen by the user).

### Rationale
- **Camper Signal Resiliency**: Since a camper is camping and trackers may go offline, fall asleep, or be in dead zones, filtering relative to the latest coordinate ensures we always show a 3-hour path of active movement leading up to their last known position.
- **Zero Additional Server Load**: We leverage the existing `/history` payload (which already returns up to 20 coordinates, capped at the backend) and filter them instantly on the client side, avoiding any server-side database date query complexities.

### Alternatives Considered
- **Filtering relative to current real-time**: If the tracker was asleep or lost cellular/LoRa signal 2 hours ago, the map would only display the last 1 hour of history, or potentially show a blank map with no trail. Rejected.
- **Database-level filtering**: Querying DynamoDB with a timestamp range. This is computationally inefficient and violates DynamoDB best practices for single-table designs where state snapshots are read sequentially. Capping history to 20 entries at the backend and filtering on the client is lightweight and extremely fast.

---

## 4. Simulation & Mock Data Generation

### Decision
Update the local simulator (`backend/sim_server.py` and `web/simulator.html`) to inject a sequence of sequential coordinates winding through Eastnor Castle's campsite area, with timestamps staggered at intervals (e.g., `-180 mins`, `-120 mins`, `-60 mins`, `now`).

### Rationale
- **Compliance with Principle VIII (Fast Feedback Cycles)**: Developers can instantly test the end-to-end telemetry pipeline, database persistence, and dashboard plotting locally within sub-seconds.
- **Boundary Verification**: Includes coordinates deliberately outside the 3-hour window to empirically prove that the client-side map filtering works correctly.

### Alternatives Considered
- **Manual input of individual points only**: Slow and tedious to test. An automated mock generator preset is much faster.
