# Feature Specification: Public Landing Page and Dynamic Dashboard Routing

**Feature Branch**: `008-public-landing-page`

**Created**: 2026-07-12

**Status**: Draft

**Input**: User description: "make it so the main site page explains what the project is about but then each url that encodes the partipants names shows their dashboard. harvy is the only one with the t1000 and browan sensor. Update their dashboard with that sensor data, on the main dashboard mention that Harvy has more sensors. Remove those features from the other participants. the t1000 also has sensor data, so hook that up as well. I want people to see the last few hours of location data overlaing with a map that is to be provided."

---

## Purpose and Overview

The **Public Landing Page and Dynamic Dashboard Routing** feature improves the onboarding experience for general visitors accessing the tracking system's root URL. 

Previously, loading the root dashboard domain (`https://emf.harvinderatwal.com/` or `index.html` with no parameters) defaulted immediately to Harvy Atwal's personal dashboard (`hvy`), which lacked context for new public visitors. 

With this update:
1. **The Root Domain acts as an Informational Landing Page**: When accessed with no user query parameters, the page displays a welcoming, high-contrast introduction explaining what the Open EMF Camper tracking project is, what telemetry is gathered, and how to use it.
2. **Instant Bypassing for Bookmarks and QR Scans**: When accessed with a valid camper query parameter (such as `?u=cha`, `?u=hvy`, `?u=ash`, `?u=tin`, or `?u=combined`), the static introductory content is completely bypassed/hidden, loading that participant's telemetry dashboard instantly.
3. **Communal Directory**: The informational landing page provides clear, easily clickable buttons for each participant, allowing users to dive into individual dashboards with a single tap.
4. **Sensor payload differentiation (T1000 & Browan)**: Since Harvy is the only participant carrying the advanced T1000 and Browan environment tracking hardware, his individual dashboard strictly features these environmental sensors (ambient temperature and noise level charts). These environmental widgets are removed/hidden from Charlotte, Ash, and Tina's telemetry dashboards. The main onboarding landing page portal directory specifically highlights that Harvy's rig contains more sensors.
5. **GPS Location History Map Overlay (T1000)**: Harvy's dashboard also displays his recent campsite location history (from the T1000 tracker) overlaid onto a provided camp map graphic. This maps his movement path over the last few hours, giving visitors a visual trail of his camp activity.

### Out of Scope
- **Participant Admin Portal Integration**: The administrative page (`admin.html`) and associated logging/manual entry features are completely separate and out of scope; no links or redirection pathways will be visible on the public landing page.
- **Dynamic Participant Management**: Adding, editing, or deleting active tracking participants cannot be performed dynamically from the landing page or a dynamic API configuration.

---

## Clarifications

### Session 2026-07-13

- Q: Participant Directory Storage Pattern → A: Hardcoded client-side list (Option A). Define the participant list and route mappings directly in static client JavaScript code to keep infrastructure cost at zero (AWS Free Tier optimized).
- Q: Browser Back/Forward Button Navigation (Popstate) → A: Full popstate handling (Option A). Intercept browser back/forward popstate events to seamlessly toggle view states in the single-page app without forcing a full page reload.
- Q: Public Landing Page Boundaries and Admin Separation → A: Complete Segregation (Option A). Keep the public landing page strictly focused on public informational content; administrative access (`admin.html`) is completely out-of-scope and separate.
- Q: Dynamic Tracker User Accounts → A: Hardcode the 4 active participants: Harvy (`hvy`), Charlotte (`cha`), Ash (`ash`), and Tina (`tin`) along with their 3-letter shortcodes.
- Q: Sensor Hardware Restrictions → A: Temperature and ambient noise telemetry widgets (T1000 and Browan) belong exclusively to Harvy's dashboard. Hide them for Charlotte, Ash, Tina, and Combined views. Highlight his extra sensor capability on the main landing portal directory.
- Q: Location Map Overlay Display → A: Plot Harvy's last few hours of T1000 coordinate telemetry as a visual plotted line path overlaid directly onto a static camp map background image on his dashboard only.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Welcoming Project Introduction (Priority: P1)

As a public visitor navigating to the project's root domain, I want to see an informational landing page that explains the tracking project's goals, telemetry types (drinks, toilet visits, steps, expenses), and participants, so that I can understand the context of the data.

**Why this priority**: High value for public outreach. New visitors from social media or camp forums need an introductory landing page to understand what they are looking at before browsing data.

**Independent Test**: Load `http://localhost:8080/index.html` with no query parameters. Verify that a clean, welcoming introduction is displayed with descriptive paragraphs, and no telemetry dashboard widgets are visible.

**Acceptance Scenarios**:

1. **Given** a visitor navigates to the root URL with no query parameters, **When** the page loads, **Then** they see introductory paragraphs about EMF Camp, steps/drinks trackers, and a list of active participants (Harvy, Charlotte, Ash, Tina).
2. **Given** the active participants directory is shown, **When** viewed, **Then** Harvy's directory button features a distinct badge or text mentioning that his tracker contains more environmental sensors (T1000, Browan).
3. **Given** the introductory landing page is active, **When** viewed, **Then** all live telemetry charts and individual widget panels are hidden from view.

---

### User Story 2 - Seamless Telemetry Dashboard Bypass (Priority: P1)

As a camp follower scanning a camper's gear QR code (e.g. `https://emf.harvinderatwal.com/?u=cha`), I want the website to instantly load Charlotte's personal telemetry dashboard, bypassing the static introduction completely, so that I can monitor her active camp stats on-the-go.

**Why this priority**: Crucial for field usability. Camphouse scans must be fast; attendees scanning QR codes on gear do not want to see static intro text on every scan.

**Independent Test**: Load `http://localhost:8080/index.html?u=cha` in a browser. Verify that the informational project introduction is completely hidden, and Charlotte's telemetry dashboard widgets load immediately.

**Acceptance Scenarios**:

1. **Given** a user opens a link containing `?u=cha`, **When** the page resolves, **Then** the introduction card is hidden, the main telemetry panel displays "Charlotte's Dashboard", and dynamic fetches load Charlotte's live values.
2. **Given** Charlotte's telemetry dashboard is loaded, **When** viewed, **Then** the ambient temperature and noise level charts (T1000/Browan features) are completely hidden/removed from her interface.
3. **Given** a user opens a link containing `?u=hvy`, **When** the page resolves, **Then** the main telemetry dashboard displays Harvy's stats, and his ambient temperature, noise charts, and location history map overlay are fully visible.

---

### User Story 3 - Interactive Camper Portal Directory (Priority: P2)

As a landing page visitor, I want to see clear, high-contrast quick links/buttons for each participant (Harvy, Charlotte, Ash, Tina) and the Combined Stats view, so that I can easily navigate into any dashboard with a single click.

**Why this priority**: Integrates the introductory landing page with the dashboard system, acting as a portal index.

**Independent Test**: Tap the "Charlotte" portal button on the landing page, verify that the browser URL updates to `?u=cha`, and the page transitions seamlessly to load her dashboard.

**Acceptance Scenarios**:

1. **Given** the informational landing page is displayed, **When** the visitor clicks on the "Charlotte" button, **Then** the page dynamically updates the browser address history and re-renders, displaying Charlotte's telemetry panel.

---

### Edge Cases

- **Missing or Invalid User ID**: If a user parameter is specified but unrecognized (e.g. `?u=xyz`), the system must fallback gracefully to rendering the project introduction page, rather than displaying an empty or broken dashboard.
- **Empty Local Storage Cache**: Since the active user ID can be cached in `localStorage`, if a user returns to the root URL with no query parameter after previously viewing a dashboard, the page MUST prioritize the root landing page (introduction) over the cached user state, ensuring they can always re-read the intro from the root URL.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Root Path Routing)**: The frontend script MUST check on load if a valid query parameter `u` (or `user_id`) is present in the URL.
- **FR-002 (Introductory Landing View)**: If the user parameter `u` is absent or invalid, the page MUST display the informational introduction container, explaining the Open EMF Camper project, LoRa telemetry, step sensors, and Monzo sync.
- **FR-003 (Telemetry Dashboard View)**: If a valid user parameter `u` (matching `hvy`, `cha`, `ash`, `tin`, or `combined`) is present, the page MUST show the corresponding telemetry dashboard and hide the project introduction container completely.
- **FR-004 (Interactive Camper Buttons)**: The introductory landing view MUST provide dedicated, mobile-optimized buttons for each participant (Harvy, Charlotte, Ash, Tina) and the Combined dashboard.
- **FR-005 (URL Parameter State Updates)**: Clicking any participant portal button on the landing page MUST update the browser's URL query parameter using the standard History API (`pushState`), and trigger the page to transition and render the dashboard view without requiring a full page refresh.
- **FR-006 (Touch-Target Usability)**: All interactive portal buttons and links on the landing page MUST maintain a minimum height/width of **48px** to guarantee reliable tap targets on mobile viewports.
- **FR-007 (Responsive Layout)**: Both the landing page introduction text and the telemetry dashboard panels MUST be fully responsive, stacking vertically on smaller viewports (down to 320px width) with zero horizontal scrolls.
- **FR-008 (History Back/Forward Navigation)**: The application MUST listen for standard browser `popstate` events, dynamically toggling the active view container (Introduction vs. specific user dashboard) to handle browser Back and Forward button interactions correctly without requiring a full page reload.
- **FR-009 (Static Directory Hosting)**: The list of active tracking participants (`hvy`, `cha`, `ash`, `tin`, `combined`) and their metadata MUST be hardcoded within the static frontend assets (`web/js/app.js`), preventing dynamic backend requests or DB queries on load, optimizing for zero-cost static S3 hosting (AWS Free Tier optimized).
- **FR-010 (Sensor Ownership Restrictions)**: The environmental sensor tracking charts (Ambient Temperature and Noise Level, powered by T1000 and Browan LoRa hardware) MUST strictly be displayed ONLY when the active dashboard is Harvy's (`?u=hvy`). These environmental panels MUST be completely hidden from all other participants' dashboards (`cha`, `ash`, `tin`) and the combined leaderboard.
- **FR-011 (Onboarding Landing Page Highlight)**: Harvy's button entry on the main project onboarding landing directory page MUST feature a prominent textual indicator (e.g. "📡 Extra sensors active (T1000, Browan)") to inform public visitors of his additional environmental telemetry payload.
- **FR-012 (Camper Location History Map Overlay)**: Harvy's dashboard MUST strictly display a camper location history panel (`#map-overlay-view`). This panel displays a campground map image as a background with a plotted coordinates route path representing the last few hours of his movement telemetry from the T1000 LoRa tracker. This map overlay is removed/hidden from all other participants' dashboards and combined views.

### Key Entities *(include if feature involves data)*

- **PortalSession**: Represents the current visitor routing session, parsing the URL query parameter `u` on load to toggle active view containers in the DOM.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Loading the root URL without parameters displays the Project Introduction and quick-links in under 1.5 seconds.
- **SC-002**: Navigating to `index.html?u=cha` renders Charlotte's active dashboard, with 100% of the project introduction text successfully hidden.
- **SC-003**: Clicking any participant button on the landing page or using browser Back/Forward navigation transitions the page to the target view state in under 500ms, with zero visual layout overflows or overlaps.
- **SC-004**: All portal navigation buttons pass 100% of mobile-responsive touch validation tests with at least a 48px sizing envelope.
- **SC-005**: Loading Charlotte's (`cha`), Ash's (`ash`), or Tina's (`tin`) dashboard hides 100% of the environmental sensor widgets (Ambient Temperature and Noise Level), and loading Harvy's (`hvy`) dashboard shows them with 100% visibility.
- **SC-006**: Harvy's portal button on the landing page displays his name alongside the specific textual indication of additional active sensors.
- **SC-007**: When Harvy's dashboard is active, the location history map overlay is rendered displaying his plotted active campsite tracking coordinates overlaid onto a campground background graphic, loading in under 1.5 seconds.

---

## Assumptions

- **Assumption 1**: The main dashboard page (`web/index.html` and `web/js/app.js`) is served as a single unified static asset file. View toggling (Introductory Landing vs Telemetry Dashboard) is controlled dynamically via CSS toggle classes (e.g. `.hidden`).
- **Assumption 2**: The static project introduction has brief paragraphs explaining EMF Camp, LoRa telemetry ingestion, steps tracking, and Monzo expenses sync.
- **Assumption 3**: Standard browser History APIs (`pushState` and `popstate` events) are fully supported by target mobile browsers in the field.
