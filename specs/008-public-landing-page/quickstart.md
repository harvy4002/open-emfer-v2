# Quickstart Validation Guide: Public Landing Page and Dynamic Dashboard Routing

This guide provides step-by-step instructions to run the local simulation environment and verify the landing page display and dynamic dashboard bypass routing in the public portal.

---

## 1. Prerequisites & Setup

Ensure you have Python 3.12+ installed.

1. **Start the Local API & Assets Server**:
   From the project root, run the static assets server on port `8080`:
   ```bash
   python3 -m http.server -d web 8080
   ```
   *Expected Output*:
   ```text
   Serving HTTP on :: port 8080 (http://[::]:8080/) ...
   ```

2. **Open the Root Landing Page**:
   Open your browser and navigate to:
   [http://localhost:8080/index.html](http://localhost:8080/index.html)

---

## 2. Validation Scenarios

### Validation Scenario 1: Initial Landing Page Intro Render (u is absent)
- **Steps**:
  1. Load [http://localhost:8080/index.html](http://localhost:8080/index.html).
  2. Verify that:
     - The welcoming project introduction card is **fully visible**.
     - Paragraphs explaining EMF Camp, LoRa telemetry, steps tracking, and expenses are legible.
     - The participant portal buttons ("Harvy", "Charlotte", "Ash", "Tina", "Combined Leaderboard") render cleanly in a single stacked column (down to 320px width).
     - No telemetry charts (Chart.js) or dashboard widget tiles are visible on the page.

---

### Validation Scenario 2: Dynamic Transition to Dashboard
- **Steps**:
  1. From the landing page, click the button labeled **"Charlotte"**.
  2. Verify that:
     - The browser's URL instantly updates to [http://localhost:8080/index.html?u=cha](http://localhost:8080/index.html?u=cha) without triggering a full page refresh.
     - The static project introduction card hides immediately (FR-003 / FR-005).
     - The main telemetry dashboard container becomes visible, showing "Charlotte's Dashboard".
     - Active chart canvases (temperature, noise) and numeric counters fetch and load Charlotte's live values.

---

### Validation Scenario 3: Direct Dashboard Bypass URL
- **Steps**:
  1. Open a new, blank browser tab.
  2. Directly load: [http://localhost:8080/index.html?u=ash](http://localhost:8080/index.html?u=ash).
  3. Verify that:
     - The welcoming introductory landing page card is **completely bypassed and invisible** from the very first frame.
     - The interface immediately renders Ash's stats dashboard and initiates telemetry sync fetches.

---

### Validation Scenario 4: Popstate History Navigation (Back/Forward Buttons)
- **Steps**:
  1. Load [http://localhost:8080/index.html](http://localhost:8080/index.html).
  2. Verify that the `#intro-landing-view` container is **fully visible**.
  3. Click the button labeled **"Charlotte"**. Verify `#dashboard-view` displays Charlotte's stats, and the URL is `?u=cha`.
  4. Click the browser's **Back** button.
  5. Verify that:
     - The URL changes back to [http://localhost:8080/index.html](http://localhost:8080/index.html).
     - `#dashboard-view` is hidden.
     - `#intro-landing-view` is displayed immediately without a full page reload.
  6. Click the browser's **Forward** button.
  7. Verify that `#intro-landing-view` is hidden, and `#dashboard-view` is shown with Charlotte's stats.

---

### Validation Scenario 5: Harvy's Exclusive T1000 GPS Location History Map
- **Steps**:
  1. Open a browser tab and load [http://localhost:8080/index.html?u=hvy](http://localhost:8080/index.html?u=hvy).
  2. Verify that:
     - The main dashboard title displays "Harvy's Telemetry Dashboard".
     - Environmental widgets (Ambient Temperature line graph and Ambient Noise level bar chart) are fully visible.
     - A dedicated **"📡 Camper Location History Map"** overlay card renders, displaying a graphical camp map background.
     - A visual trail/route representing Harvy's last 6 GPS coordinate points is plotted cleanly on top of the map background.
  3. Now load [http://localhost:8080/index.html?u=cha](http://localhost:8080/index.html?u=cha).
  4. Verify that:
     - The environmental temperature and noise widgets are completely hidden.
     - The "Camper Location History Map" overlay is completely hidden/removed from Charlotte's dashboard.

