# Feature Specification: Google Analytics Integration

**Feature Branch**: `018-google-analytics-integration`

**Created**: Wednesday, July 15, 2026

**Status**: Draft

**Input**: User description: "add in google analytics for the public dashboard. Allow an entry in a config where I can paste my GA key."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Centralized Analytics Configuration (Priority: P1)

As a camp system administrator, I want a dedicated configuration file to store my Google Analytics Measurement ID, so that I can easily configure analytics tracking without editing main dashboard code.

**Why this priority**: Foundational prerequisite for configuration segregation. Allows quick deployment-specific key customization.

**Independent Test**: Verify that a configuration file `web/js/config.js` is present in the repository, and that it declares a global configuration block:
```javascript
window.EMF_CONFIG = {
  google_analytics_id: "G-XXXXXXXXXX"
};
```

**Acceptance Scenarios**:

1. **Given** the administrator opens the repository, **When** they look inside `web/js/`, **Then** the file `config.js` is present and contains the `google_analytics_id` field.
2. **Given** the administrator changes the string value of `google_analytics_id` to `"G-ABC123XYZ"`, **When** the webpage loads, **Then** the dashboard initializes analytics with the updated key.

---

### User Story 2 - Dynamic Analytics Script Injection (Priority: P2)

As a camp organizer, when visitors load the public dashboard, I want the standard Google Analytics tracking code to be dynamically injected and initialized using my configured measurement ID, so that I can securely capture visitor page views.

**Why this priority**: Core tracking function. Ensures standard traffic signals are captured.

**Independent Test**: Set `google_analytics_id` to `"G-EMFCAMP2026"`. Load `web/index.html?u=cha` in your browser. Inspect the `<head>` element, verify that the external Google Tag Manager `<script>` element is present with `src="https://www.googletagmanager.com/gtag/js?id=G-EMFCAMP2026"`, and that `window.dataLayer` is initialized correctly.

**Acceptance Scenarios**:

1. **Given** a valid GA Measurement ID is configured in `config.js`, **When** the public dashboard page initializes, **Then** the global tag manager script is appended to the document header, and a standard `pageview` event is fired.

---

### User Story 3 - Graceful Analytics Bypass (Priority: P3)

As a privacy-conscious visitor, if the Google Analytics key is unconfigured or left as an empty placeholder string, I want the system to completely bypass analytics tracking code injection, ensuring no analytics scripts are requested.

**Why this priority**: Enhances default privacy controls and prevents errors if an operator chooses not to use Google Analytics.

**Independent Test**: Set `google_analytics_id` to `""` (empty string) in `config.js`. Clear your browser cache and load the public dashboard. Confirm that no googletagmanager script is loaded, and that the console remains completely free of tracking exceptions.

**Acceptance Scenarios**:

1. **Given** the GA key is empty, **When** the webpage is loaded, **Then** the global site tag injection routine is bypassed, and the webpage operates normally.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Central Configuration Block)**: The static frontend MUST provide a configuration file `web/js/config.js` declaring a global `window.EMF_CONFIG` object mapping `google_analytics_id` to a string.
- **FR-002 (Dynamic Script Injection)**: The public dashboard controller (`web/js/app.js`) MUST check `window.EMF_CONFIG.google_analytics_id`. If populated with a non-empty string starting with `G-` (or matching standard GA measurement ID formats), it MUST dynamically compile, inject, and execute the standard Google Analytics library (`https://www.googletagmanager.com/gtag/js?id=<GA_ID>`).
- **FR-003 (Robust Initialization)**: The injected code MUST initialize `window.dataLayer = window.dataLayer || []`, configure the `gtag` function, and execute the standard page tracking triggers:
  ```javascript
  gtag('js', new Date());
  gtag('config', GA_ID);
  ```
- **FR-004 (Graceful Placeholder Bypass)**: If `google_analytics_id` is empty, set to a generic placeholder (e.g. `"G-XXXXXXXXXX"`), or contains an invalid format, the injection routine MUST immediately exit, ensuring zero tracking scripts are loaded or console errors are thrown.
- **FR-005 (HTML Execution Order)**: The public dashboard (`web/index.html`) MUST import `web/js/config.js` in its header before executing any telemetry or controller scripts.

### Key Entities

This feature operates strictly as a **browser-native, client-side** static configuration with **zero** backend/database schemas or AWS Lambda dependencies, maintaining complete compliance with Principle VII (Cost-Optimized Static Frontend).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Page loads dynamically append the external `<script>` tag matching the configured Measurement ID in under 50ms upon DOM initialization.
- **SC-002**: Standard Google Analytics page views and session signals are successfully received by Google's endpoints when a valid measurement ID is used.
- **SC-003**: In unconfigured states, 100% of tracking tag loading is bypassed, throwing 0 errors.

## Assumptions

- **Global Config Availability**: The global `window.EMF_CONFIG` object is assumed to be accessible by all subsequently executed frontend controller scripts.
- **W3C Standard Compliance**: The measurement ID follows the standard W3C Google Analytics 4 format starting with the prefix `G-`.
