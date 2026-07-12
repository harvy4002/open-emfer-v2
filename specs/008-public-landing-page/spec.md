# Feature Specification: Public Landing Page and Dynamic Dashboard Routing

**Feature Branch**: `008-public-landing-page`

**Created**: 2026-07-12

**Status**: Draft

**Input**: User description: "make it so the main site page explains what the project is about but then each url that encodes the partipants names shows their dashboard"

---

## Purpose and Overview

The **Public Landing Page and Dynamic Dashboard Routing** feature improves the onboarding experience for general visitors accessing the tracking system's root URL. 

Previously, loading the root dashboard domain (`https://emf.harvinderatwal.com/` or `index.html` with no parameters) defaulted immediately to Harvy Atwal's personal dashboard (`hvy`), which lacked context for new public visitors. 

With this update:
1. **The Root Domain acts as an Informational Landing Page**: When accessed with no user query parameters, the page displays a welcoming, high-contrast introduction explaining what the Open EMF Camper tracking project is, what telemetry is gathered, and how to use it.
2. **Instant Bypassing for Bookmarks and QR Scans**: When accessed with a valid camper query parameter (such as `?u=ali`, `?u=hvy`, `?u=bob`, or `?u=combined`), the static introductory content is completely bypassed/hidden, loading that participant's telemetry dashboard instantly.
3. **Communal Directory**: The informational landing page provides clear, easily clickable buttons for each participant, allowing users to dive into individual dashboards with a single tap.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Welcoming Project Introduction (Priority: P1)

As a public visitor navigating to the project's root domain, I want to see an informational landing page that explains the tracking project's goals, telemetry types (drinks, toilet visits, steps, expenses), and participants, so that I can understand the context of the data.

**Why this priority**: High value for public outreach. New visitors from social media or camp forums need an introductory landing page to understand what they are looking at before browsing data.

**Independent Test**: Load `http://localhost:8080/index.html` with no query parameters. Verify that a clean, welcoming introduction is displayed with descriptive paragraphs, and no telemetry dashboard widgets are visible.

**Acceptance Scenarios**:

1. **Given** a visitor navigates to the root URL with no query parameters, **When** the page loads, **Then** they see introductory paragraphs about EMF Camp, steps/drinks trackers, and a list of active participants.
2. **Given** the introductory landing page is active, **When** viewed, **Then** all live telemetry charts and individual widget panels are hidden from view.

---

### User Story 2 - Seamless Telemetry Dashboard Bypass (Priority: P1)

As a camp follower scanning a camper's gear QR code (e.g. `https://emf.harvinderatwal.com/?u=ali`), I want the website to instantly load Alice's personal telemetry dashboard, bypassing the static introduction completely, so that I can monitor her active camp stats on-the-go.

**Why this priority**: Crucial for field usability. Camphouse scans must be fast; attendees scanning QR codes on gear do not want to see static intro text on every scan.

**Independent Test**: Load `http://localhost:8080/index.html?u=ali` in a browser. Verify that the informational project introduction is completely hidden, and Alice's telemetry dashboard widgets load immediately.

**Acceptance Scenarios**:

1. **Given** a user opens a link containing `?u=ali`, **When** the page resolves, **Then** the introduction card is hidden, the main telemetry panel displays "Alice Smith's Dashboard", and dynamic fetches load Alice's live values.
2. **Given** a user opens a link containing `?u=combined`, **When** the page resolves, **Then** the introduction is hidden and the global camper leaderboard displays.

---

### User Story 3 - Interactive Camper Portal Directory (Priority: P2)

As a landing page visitor, I want to see clear, high-contrast quick links/buttons for each participant (Harvy, Alice, Bob) and the Combined Stats view, so that I can easily navigate into any dashboard with a single click.

**Why this priority**: Integrates the introductory landing page with the dashboard system, acting as a portal index.

**Independent Test**: Tap the "Alice Smith" portal button on the landing page, verify that the browser URL updates to `?u=ali`, and the page transitions seamlessly to load her dashboard.

**Acceptance Scenarios**:

1. **Given** the informational landing page is displayed, **When** the visitor clicks on the "Bob Camper" button, **Then** the page dynamically updates the browser address history and re-renders, displaying Bob's telemetry panel.

---

### Edge Cases

- **Missing or Invalid User ID**: If a user parameter is specified but unrecognized (e.g. `?u=xyz`), the system must fallback gracefully to rendering the project introduction page, rather than displaying an empty or broken dashboard.
- **Empty Local Storage Cache**: Since the active user ID can be cached in `localStorage`, if a user returns to the root URL with no query parameter after previously viewing a dashboard, the page MUST prioritize the root landing page (introduction) over the cached user state, ensuring they can always re-read the intro from the root URL.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Root Path Routing)**: The frontend script MUST check on load if a valid query parameter `u` (or `user_id`) is present in the URL.
- **FR-002 (Introductory Landing View)**: If the user parameter `u` is absent or invalid, the page MUST display the informational introduction container, explaining the Open EMF Camper project, LoRa telemetry, step sensors, and Monzo sync.
- **FR-003 (Telemetry Dashboard View)**: If a valid user parameter `u` (matching `hvy`, `ali`, `bob`, or `combined`) is present, the page MUST show the corresponding telemetry dashboard and hide the project introduction container completely.
- **FR-004 (Interactive Camper Buttons)**: The introductory landing view MUST provide dedicated, mobile-optimized buttons for each participant (Harvy, Alice, Bob) and the Combined dashboard.
- **FR-005 (URL Parameter State Updates)**: Clicking any participant portal button on the landing page MUST update the browser's URL query parameter using the standard History API (`pushState`), and trigger the page to transition and render the dashboard view without requiring a full page refresh.
- **FR-006 (Touch-Target Usability)**: All interactive portal buttons and links on the landing page MUST maintain a minimum height/width of **48px** to guarantee reliable tap targets on mobile viewports.
- **FR-007 (Responsive Layout)**: Both the landing page introduction text and the telemetry dashboard panels MUST be fully responsive, stacking vertically on smaller viewports (down to 320px width) with zero horizontal scrolls.

### Key Entities *(include if feature involves data)*

- **PortalSession**: Represents the current visitor routing session, parsing the URL query parameter `u` on load to toggle active view containers in the DOM.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Loading the root URL without parameters displays the Project Introduction and quick-links in under 1.5 seconds.
- **SC-002**: Navigating to `index.html?u=ali` renders Alice's active dashboard, with 100% of the project introduction text successfully hidden.
- **SC-003**: Clicking any participant button on the landing page transitions the page to that user's dashboard in under 500ms, with zero visual layout overflows or overlaps.
- **SC-004**: All portal navigation buttons pass 100% of mobile-responsive touch validation tests with at least a 48px sizing envelope.

---

## Assumptions

- **Assumption 1**: The main dashboard page (`web/index.html` and `web/js/app.js`) is served as a single unified static asset file. View toggling (Introductory Landing vs Telemetry Dashboard) is controlled dynamically via CSS toggle classes (e.g. `.hidden`).
- **Assumption 2**: The static project introduction has brief paragraphs explaining EMF Camp, LoRa telemetry ingestion, steps tracking, and Monzo expenses sync.
- **Assumption 3**: Standard browser History APIs (`pushState` and `popstate` events) are fully supported by target mobile browsers in the field.
