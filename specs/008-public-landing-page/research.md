# Technical Research: Public Landing Page and Dynamic Dashboard Routing

## Decisions & Technical Architecture

### 1. Unified Single-Page Conditional Rendering
- **Decision**: Wrap the static project introduction content in an HTML container (`#intro-landing-view`) and the existing Grafana-style telemetry dashboard widgets in another container (`#dashboard-view`). Use a standard CSS helper class `.hidden { display: none !important; }` to toggle their visibility based on the presence of the `u` parameter.
- **Rationale**: Serves the onboarding landing page and the telemetry dashboards from a single, unified static asset file (`web/index.html`). This preserves Principle VII (Cost-Optimized Serverless Frontends) since no complex frontend build compilation or multi-page server routing is required.
- **Alternatives Considered**: Creating a separate `intro.html` file and redirecting to `index.html`. Rejected because a single-page conditional toggle has faster transition times, avoids double page load requests on slow campsite cellular networks, and allows seamless state transition animations.

### 2. URL State Mutation via History API
- **Decision**: Use the browser's standard `window.history.pushState` API to dynamically append `?u=<camperId>` when a visitor clicks a portal button on the landing page.
- **Rationale**: Dynamically transitions the browser view from the landing page introduction to the dynamic dashboard in under 100ms without requiring a full browser page refresh. It maintains active browser history, allowing standard back/forward navigation.
- **Alternatives Considered**: Using standard `window.location.href` redirects. Rejected because full page reloads introduce unnecessary browser preflight, DNS resolution, and asset reload delays, which degrades the UX under spotty outdoor mobile conditions.

### 3. Local Storage Bypass Strategy (Strict Parameter Checks)
- **Decision**: Modify `web/js/app.js` initialization logic to strictly check for the presence of query parameters on page load. If the URL contains no user query parameters, the portal MUST render the introductory landing page, ignoring any cached `active_user_id` inside `localStorage`.
- **Rationale**: Guarantees that public visitors navigating directly to the root domain (`https://emf.harvinderatwal.com/`) are always welcomed by the informational landing page, even if they have previously viewed a camper dashboard.

---

## Technical Specifications & Variables

- **View Containers**:
  - `#intro-landing-view` (Project introduction text, explanation, and portal directory buttons)
  - `#dashboard-view` (Grafana dashboard metrics tiles, environmental line charts, steps displays)
- **State Check Rule**:
  ```javascript
  const urlParams = new URLSearchParams(window.location.search);
  const userParam = urlParams.get("u") || urlParams.get("user_id");
  ```
- **Camper Mappings**:
  - `hvy` -> "Harvy Atwal"
  - `ali` -> "Alice Smith"
  - `bob` -> "Bob Camper"
  - `combined` -> "Combined Camper Stats"
