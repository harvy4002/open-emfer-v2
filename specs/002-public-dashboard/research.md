# Technical Research: Grafana-Style Public Dashboard and Participant Admin

This document outlines the visual parameters, client-side state caching strategies, and load management patterns chosen to deliver a high-performance, cost-free static dashboard.

---

## 1. Grafana Aesthetic Visual Standard (CSS Grid)

### Decision
Utilize Bulma CSS's grid system combined with customized CSS variables to match Grafana's classic dark theme:
* **Dashboard Background**: Dark slate grey `#161719`
* **Card/Panel Background**: Solid charcoal `#1f2226`
* **Text Base Color**: Off-white `#d8d9da`
* **Metrics Highlight / Trend Accents**: Orange `#ff780a` (primary), Cyan `#5794f2` (secondary)
* **Status Badges**: Neon Green `#56a64b` (active), Red `#e02f44` (disconnected/stale)

### Rationale
- **High-Signal Contrast**: A dark theme maximizes readability under camp sunlight or night operations on mobile and large tracking screens.
- **Zero Compilation Overhead**: Embedding custom CSS variables on top of CDN-linked Bulma CSS structures delivers beautiful layouts with zero build-tool requirements (complying with the Constitution).

---

## 2. UI State-Preservation Layout Schema

### Decision
Store user panel visualization preferences (e.g., toggling between line and bar charts inside the temperature panel) inside browser `localStorage`.

### LocalStorage Layout Keys:
* `dashboard_panel_layout`: JSON string capturing layout toggles:
  ```json
  {
    "temperature_widget": "line" | "bar",
    "noise_widget": "gauge" | "line"
  }
  ```
* `admin_tracker_key`: String cache of the current `tracker_key` so the participant doesn't need to re-type authorization keys across browser sessions.

### Rationale
- **Zero-Cost Personalization**: Storing preferences locally on the client machine is completely free, eliminating the need to write backend database tables or maintain user profiles (complying with the serverless principles).

---

## 3. Load Management, Visibility API, & CDN Caching

### Decision
To protect serverless AWS Lambdas from traffic spikes when hundreds of camp attendees load the auto-refreshing public dashboard (FR-004), implement a three-tiered load-management strategy:

1. **Visibility API Throttling**:
   Use the browser-native `Page Visibility API` (`document.visibilityState`) to pause the 60-second auto-refresh fetching loops when the dashboard tab is hidden or backgrounded, immediately resuming when the tab returns to active focus.
   ```javascript
   document.addEventListener('visibilitychange', () => {
     if (document.hidden) {
       clearTimeout(refreshTimeout);
     } else {
       triggerFetchAndScheduleRefresh();
     }
   });
   ```
2. **CDN Edge Caching (CloudFront TTL)**:
   Configure AWS CloudFront CDN behavior mappings for public API endpoints (GET `/beer`, `/history`, `/browan`) with a short **Cache TTL of 15 seconds** and standard CORS header forwarding.
3. **HTTP Client-Side Jitter**:
   Add a random ±5 seconds of network jitter to the client-side 60-second fetch timer to prevent thundering herd requests on API endpoints.

### Rationale
- **Lambda Cost Containment (Principle II)**: CloudFront edge-caching handles high concurrent reading spikes at near-zero cost, shielding backend Lambda invocations from processing duplicate requests.
- **Camper Mobile Bandwidth Conservation**: Pausing polling on backgrounded browser tabs minimizes data usage on limited EMF camp network infrastructure.
