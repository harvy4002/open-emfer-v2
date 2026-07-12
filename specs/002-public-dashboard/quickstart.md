# Quickstart Validation Guide: Grafana-Style Public Dashboard and Participant Admin

This guide outlines steps to spin up the local static website development server and run browser-native verification checks for both public and admin dashboards.

---

## Prerequisites & Local Setup

1. **Python 3 Interpreter**: Required to run a local static file server.
2. **Network Connection**: Ensure you have an internet connection to fetch the CDN-linked libraries (Bulma CSS, Chart.js) or mock the API endpoints.

---

## Spinning Up the Local Server

Execute a simple Python server mapping the static assets folder `web/`:
```bash
python3 -m http.server -d web 8080
```
Open your browser and navigate to `http://localhost:8080`.

---

## Validation Scenario 1: Initial Public Render

Verifies that loading the root dashboard page retrieves data from the API and displays correct default widgets in dark theme.

### Interaction Steps
1. Open `http://localhost:8080/index.html` in your browser.
2. Verify the background color is dark slate (`#161719`) and Bulma-based card grids display correctly.
3. Open your browser console (F12) and verify telemetry fetch requests are fired to API Gateway routes (`/beer`, `/history`).
4. Ensure the total drinks and Monzo total counters display numeric values instead of `NaN` or blanks.

---

## Validation Scenario 2: Dynamic Panel Toggles (Story 3 & State Spec)

Verifies that toggling a widget representation redraws the canvas instantly and persists choices locally.

### Interaction Steps
1. On the temperature card panel, click the "Toggle Chart (Line/Bar)" setting switch.
2. Verify that Chart.js instantly destroys the line chart instance and redraws a bar chart.
3. Open your browser's Developer Tools → Application → Local Storage.
4. Confirm that the key `dashboard_panel_layout` exists and the `temperature_widget` parameter is updated to `"bar"`.
5. Reload the page. Verify the temperature widget is rendered as a **bar chart** immediately on reload.

---

## Validation Scenario 3: Admin Forms & Authorization

Verifies that submitting activities via `/admin.html` injects the cached credentials correctly.

### Interaction Steps
1. Navigate to `http://localhost:8080/admin.html`.
2. Input `"mock-super-secret-key"` into the Admin Access form and click Save.
3. Verify that the credentials are cached in `localStorage` as `admin_tracker_key`.
4. Click "Log Lager" on the drinks form.
5. In your network tab, verify an HTTP POST request is sent to `/beer` with an `Authorization: mock-super-secret-key` header.

---

## Validation Scenario 4: Connection Offline Warning (Load Spec)

Verifies that consecutive API Gateway network timeouts trigger user-friendly disconnected states.

### Interaction Steps
1. Open `index.html`.
2. Turn off your Wi-Fi connection (or simulate offline/blocked requests in Chrome network throttling).
3. Wait for the 60-second fetch cycle or trigger a manual refresh.
4. Verify that the status banner changes to a red **"Disconnected / Stale Data"** indicator and card borders flash warning highlights (preventing JS crash errors).
