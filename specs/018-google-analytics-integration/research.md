# Research Document: Google Analytics Integration

## Summary

This document evaluates the architectural design, security considerations, and dynamic script injection patterns to integrate standard Google Analytics 4 (GA4) page tracking on the public static dashboard.

---

## Key Decisions

### 1. Static Configuration Segregation via `config.js`
*   **Decision**: Decouple the environment-specific Google Analytics measurement ID from the core dashboard code by creating a dedicated static configuration file `web/js/config.js` declaring a global `window.EMF_CONFIG` namespace.
*   **Rationale**: Aligning strictly with Principle VII (Cost-Optimized Static Frontend), the application remains 100% static and served directly over CDN, but allows administrators or operators to paste their deployment-specific GA key in one clean file without altering application controller logic.
*   **Alternatives Considered**: Fetching the GA Key via an API call to the backend Lambda. Rejected because it introduces an unnecessary network dependency, minor latency overhead on page load, and AWS Lambda runtime costs for a purely public static configuration parameter.

### 2. Dynamic Tag Manager Script Injection
*   **Decision**: Implement browser-native runtime script injection inside the dashboard controller `web/js/app.js`. If `window.EMF_CONFIG.google_analytics_id` is populated, the script dynamically compiles and appends the standard Global Site Tag (`gtag.js`) element to the document `<head>` on load.
*   **Rationale**: Minimizes initial page weights for unconfigured environments and protects user privacy by completely avoiding any external requests to Google Tag Manager endpoints unless a valid key is intentionally supplied.
*   **Alternatives Considered**: Hardcoding standard analytics `<script>` blocks directly in `index.html` with empty variables. Rejected because hardcoded blocks trigger browser console warning exceptions and attempt to fetch generic libraries even when unconfigured.

### 3. Graceful Opt-Out and Bypass Boundaries
*   **Decision**: Incorporate strict boundary validation. If the key is left empty, matches the template default placeholder (`"G-XXXXXXXXXX"`), or fails standard format checks, the injection logic immediately exits, throwing zero exceptions.
*   **Rationale**: Prevents any tracking leakage and ensures a pristine, error-free browser developer console for offline development.
