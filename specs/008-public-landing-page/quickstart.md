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
     - The participant portal buttons ("Harvy Atwal", "Alice Smith", "Bob Camper", "Combined Leaderboard") render cleanly in a single stacked column (down to 320px width).
     - No telemetry charts (Chart.js) or dashboard widget tiles are visible on the page.

---

### Validation Scenario 2: Dynamic Transition to Dashboard
- **Steps**:
  1. From the landing page, click the button labeled **"Alice Smith"**.
  2. Verify that:
     - The browser's URL instantly updates to [http://localhost:8080/index.html?u=ali](http://localhost:8080/index.html?u=ali) without triggering a full page refresh.
     - The static project introduction card hides immediately (FR-003 / FR-005).
     - The main telemetry dashboard container becomes visible, showing "Alice Smith's Dashboard".
     - Active chart canvases (temperature, noise) and numeric counters fetch and load Alice's live values.

---

### Validation Scenario 3: Direct Dashboard Bypass URL
- **Steps**:
  1. Open a new, blank browser tab.
  2. Directly load: [http://localhost:8080/index.html?u=bob](http://localhost:8080/index.html?u=bob).
  3. Verify that:
     - The welcoming introductory landing page card is **completely bypassed and invisible** from the very first frame.
     - The interface immediately renders Bob Camper's stats dashboard and initiates telemetry sync fetches.
