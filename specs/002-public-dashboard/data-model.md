# Data Model: Grafana-Style Public Dashboard and Participant Admin

This document defines the client-side browser schemas, browser `localStorage` structures, and in-memory state variables used by the static frontends.

---

## 1. Browser LocalStorage Structures

The static frontend is entirely serverless, relying on the user's browser `localStorage` to retain configuration and sessions:

| Key | Format | Purpose | Lifetime |
| :--- | :--- | :--- | :--- |
| `dashboard_panel_layout` | JSON String | Caches user preferences for panel visualization types (e.g. line vs bar graph). | Indefinite |
| `admin_tracker_key` | Plain String | Stores the participant's access key for authenticated API writes. | User-managed |

### A. Panel Layout Caching Schema
```json
{
  "temperature_widget": "line" | "bar",
  "noise_widget": "gauge" | "line",
  "refresh_interval_seconds": 60
}
```

---

## 2. In-Memory Application State

Inside `web/js/app.js`, the running application maintains a centralized state object (`window.appState`) to manage reactive rendering and prevent redundant API queries:

```javascript
window.appState = {
  // Connection Status State
  connection: {
    status: "connected" | "stale" | "disconnected",
    last_fetch_time: "2026-07-10T12:00:00Z",
    consecutive_failures: 0
  },
  
  // Local Telemetry Cache
  telemetry: {
    total_drinks: 0,
    beer_drinks: 0,
    current_status: "chilling",
    status_image_url: "harvy_chilling.jpg",
    ambient_temperature: null,
    ambient_noise_level: null,
    total_expenditure_gbp: 0.00
  },
  
  // Tracked Chart.js Instances
  charts: {
    temperature_chart: null, // Chart.js Object
    noise_chart: null        // Chart.js Object
  }
};
```

#### State Transition Actions:
1. **Fetch Telemetry**: On success, update `telemetry` properties, set `consecutive_failures = 0`, transition `status = "connected"`, update `last_fetch_time`, and redraw Chart.js instances.
2. **Network Offline / Timeout**: After 1 failed attempt, transition `status = "stale"`. After 3 consecutive failed attempts, transition `status = "disconnected"`, update card borders to red, and display "Disconnected" warning banners in the UI.
