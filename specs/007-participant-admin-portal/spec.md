# Feature Specification: Participant Admin Portal

**Feature Branch**: `007-participant-admin-portal`

**Created**: 2026-07-12

**Status**: Draft

**Input**: User description: "There should be a seperate admin link for each user. I can list out the user shortcode for each user if that helps."

---

## Purpose and Overview

The **Participant Admin Portal** is the dedicated interface for campers and tracking participants in the field to manually log their activities, manage their active tracking session, and authenticate requests securely. 

By isolating this feature into its own specification, we ensure that administrative capabilities, user identification, and mobile-optimized manual entry workflows are managed independently of the public-facing Grafana-style dashboard and telemetry ingestion pipelines.

This specification enforces **strict user link isolation** and **session context locking**. Instead of using a shared tablet or in-page dropdown where users can easily switch contexts (which risks logging data on the wrong participant's account), each camper is assigned their own **immutable personal admin link** (such as `admin.html?u=ali` or `admin.html?u=hvy`). The admin portal automatically binds and locks the session strictly to that parsed user ID, loading their active values and sending all mutative or reverse counts on behalf of that user.

To support reliable operation on mobile devices under active outdoor field conditions (such as limited network, movement, and single-hand touch inputs):
* **The admin dashboard is developed using a mobile-first, highly responsive design.**
* **All interactive elements are optimized for tactile feedback and single-handed use.**
* **Input actions are secured via a header-based security key.**
* **Admin screens are locked to the specific user parsed from their unique URL query string.**

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Secure Telemetry Logging (Priority: P1)

As a tracking participant or admin, I want to access an authenticated admin page to manually log campsite activities (drinks, learning sessions, status changes) and manage my telemetry stream securely.

**Why this priority**: Essential for data collection in the field. Without this manual entry interface, participants cannot record metrics that aren't automatically captured by sensors or IoT devices.

**Independent Test**: Navigate to `/admin.html`, enter a valid `tracker_key`, submit a new status update or drink log, and verify that the backend API receives the authorized request and records the update in DynamoDB.

**Acceptance Scenarios**:

1. **Given** a user is on the admin page, **When** they submit an activity form with a valid `tracker_key` loaded, **Then** the browser successfully dispatches a POST request to the API with the key in the authorization header, and the backend persists the log.
2. **Given** a user on the admin page, **When** they attempt to submit a log without providing a valid `tracker_key` or if the key has expired, **Then** they are prompted for the key, submission is disabled, and the API returns a `401 Unauthorized` block.

---

### User Story 2 - Personalized Mobile-First Field Logging (Priority: P1)

As a tracking camper in the field, I want to open my personal admin logger page via my compact personalized URL (e.g., `admin.html?u=ali`) and log my activities using a mobile-first, touch-friendly UI so that I can easily track my metrics on-the-go with one hand.

**Why this priority**: Crucial for field usability. Campers are walking around the grounds and need a high-contrast, large-button UI that dynamically binds their specific user profile to all logged activities.

**Independent Test**: Load `/admin.html?u=ali` on a simulated mobile browser with a width of 360px, verify that all button heights are a minimum of 48px, tap "Log Lager", and verify that the JSON request payload sent to the API contains `"user_id": "ali"`.

**Acceptance Scenarios**:

1. **Given** the admin page is loaded with `?u=ali`, **When** the page renders, **Then** the interface automatically selects "Alice Smith" as the active user and displays personalized heading information.
2. **Given** the admin page on a mobile viewport (down to 320px width), **When** viewed, **Then** all forms and buttons stack vertically without horizontal scrolling, and all clickable targets are easily tappable with a thumb.

---

### User Story 3 - Camper-Specific Link Locking (Priority: P2)

As a tracking camper using my personal device or bookmark, I want the admin portal to lock strictly to my user identifier when loading my unique link (e.g., `admin.html?u=ali`) without offering a global profile dropdown, so that I cannot accidentally log my activities under another camper's profile.

**Why this priority**: Prevents cross-profile logging errors in the field. Removing global profile selection on individual devices ensures that campers do not misattribute their activities to other participants.

**Independent Test**: Load `/admin.html?u=ali`, verify that there is no active dropdown to switch to Harvy (`hvy`) or Bob (`bob`), and confirm that all form submissions are programmatically bound to the user context `"user_id": "ali"`.

**Acceptance Scenarios**:

1. **Given** a camper loads `/admin.html?u=ali`, **When** they look at the UI, **Then** the page header displays "Alice Smith's Logging Portal" and locks all form contexts to `"ali"` with no profile switching controls visible.
2. **Given** a camper loads `/admin.html?u=bob`, **When** they view the page, **Then** the portal locks context strictly to "Bob Camper" (`bob`) and disables cross-camper selection.

---

### User Story 4 - Live Value Display & Bi-Directional Counter Controls (Priority: P1)

As a tracking camper in the field, I want to see the current values of all my metrics directly in the admin portal, and use large "+" and "-" buttons on my numerical metrics, so that I can monitor my statistics in real time and easily decrement (reverse) an accidental log entry on-the-go.

**Why this priority**: Solves critical user feedback loop issues. Logging in the field often results in accidental double-submits or mistaken clicks. Providing a clear live display and decrement capability gives users immediate verification and correction mechanisms without needing to navigate to the public dashboard.

**Independent Test**:
- Load `/admin.html?u=ali`. Verify that Alice's current beer count (e.g., "5") is loaded and displayed adjacent to the controls.
- Tap the "-" button next to "Beers". Verify that the client dispatches a request to the reverse endpoint with `"user_id": "ali"` and Alice's beer count updates to "4" in real time.

**Acceptance Scenarios**:

1. **Given** Alice has logged 4 beers, **When** she views `/admin.html?u=ali`, **Then** the UI retrieves her aggregates and displays "4 Beers" directly on the panel.
2. **Given** Alice's beer count is displayed as "4", **When** she taps the "-" button, **Then** the client disables the control, fires a reverse API command, and decrements the displayed value to "3" upon success.
3. **Given** a non-numerical metric (such as "Current Status"), **When** displayed, **Then** the UI shows the current value (e.g., "Chilling") without "+" or "-" controls.

---

### Edge Cases

- **Double-Tap Accidental Log**: Walking and logging on touchscreens often results in accidental double-taps. The admin interface client script must throttle button clicks (disabling buttons for 500ms upon submission) to prevent duplicate logged events.
- **Intermittent Mobile Signals / Network Dead-Zones**: Campgrounds often have spotty cellular service. If a telemetry submission or reversal fails due to connection issues, the admin page must display a clear "Retry / Failed" alert, cache the log attempt locally if possible, and allow manual re-submission.
- **Configurable Backend Host Selection**: The client script must dynamically detect whether it is running on a local development server (pointing to `http://localhost:3000`) or in the production CloudFront environment, ensuring seamless debugging and development transitions.
- **Zero-Value Decrement Boundary**: Numeric counters (such as beers or toilet visits) cannot be negative. If an active count is already `0`, the admin portal MUST disable the "-" decrement button and reject any attempts to dispatch reverse logging requests for that metric.
- **Multi-Device Sync Divergence**: If a camper logs data on another device, the values on the admin portal could become stale. The admin portal should pull the latest values from the API on profile load and include a manual "Sync" refresh button to pull the latest state without refreshing the entire page.
- **Missing or Invalid User Parameter**: If the query parameter `u` is missing or represents an unrecognized user shortcode, the portal MUST fallback to the default administrator context (`hvy`) or display an explicit warning prompt asking the camper to use their unique personal link.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Admin Logging Forms)**: The admin dashboard MUST provide clear, easy-to-use form inputs and buttons to manually log camper telemetry: posting drinks, updating status, tracking learning session starts/stops, logging toilet visits, and triggering a tracking reset.
- **FR-002 (Admin Authorization)**: The admin dashboard MUST prompt the participant for the `tracker_key` and include it as an authorization header on all mutative requests to the backend API.
- **FR-003 (Mobile-First responsive Layout)**: The admin site layout MUST stack all forms and panels vertically on smaller viewports (down to 320px width), ensuring 100% responsiveness with zero horizontal scrolling.
- **FR-004 (Touch-Target Sizing)**: All buttons, text fields, and dropdown targets on the admin interface MUST maintain a minimum height/width of **48px** to guarantee tactile usability during physical field activity.
- **FR-005 (Client-Side Click Throttling)**: The interface MUST programmatically disable action submission buttons for **500ms** immediately after a click to prevent duplicate logs from accidental double-taps.
- **FR-006 (Context Link Locking)**: The admin interface MUST automatically parse the user identifier from the compact query parameter `u` (e.g. `?u=ali`), fallback to `hvy` if absent, and lock all logging context and API payloads to that user ID.
- **FR-007 (No Profile Swapping on Locked Panel)**: The user interface MUST NOT present any profile dropdown switchers or manual toggle controls on individual camper logging panels, preventing users from changing their logging target on a locked page.
- **FR-008 (Configurable Host URL)**: The admin JavaScript scripts MUST dynamically resolve the backend API host URL: using `http://localhost:3000` when running on a local server, and pointing to the production cloud API gateway URL when deployed in production.
- **FR-009 (Live Value Display)**: The admin dashboard MUST fetch the selected user's active telemetry state from the backend API aggregates (e.g., GET `/beer`, GET `/history`) on load and display the current values next to each logging category, eliminating the need to check the public dashboard.
- **FR-010 (Bi-Directional Controls)**: For incrementable numeric metrics (such as beer consumption, toilet visits, steps), the admin interface MUST display adjacent "+" and "-" buttons, enabling rapid increases and decreases.
- **FR-011 (Reverse API Integration)**: When the "-" button is tapped, the interface MUST dispatch a POST request to the corresponding reverse API endpoint (e.g. `/beer/reverse`, `/toilet/reverse` or a standard reverse path with a parameter) containing the camper's `user_id` to decrement the count in the database.
- **FR-012 (Floor Count Protection)**: The admin UI MUST enforce a minimum boundary of `0` on all numeric counters. If a displayed metric value is `0`, the corresponding "-" action button MUST be disabled and visual feedback updated.

### Key Entities *(include if feature involves data)*

- **AdminSession**: Represents the current participant session in the admin area, caching the active `tracker_key` and locked `user_id` context in the browser's `localStorage` to preserve login state across sessions.
- **CamperProfile**: Represents the active tracking participant. Key attributes: `user_id` (e.g. `ali`, `hvy`, `bob`), display name (e.g. `Alice Smith`, `Harvy Atwal`, `Bob Camper`), and their live telemetry counts retrieved from the backend.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of manual telemetry logs and reverse requests submitted through the admin dashboard are rejected with a `401 Unauthorized` unless the correct `tracker_key` is supplied.
- **SC-002**: Navigating to a specific camper's URL (e.g., `/admin.html?u=ali` or `/admin.html?u=bob`) correctly loads the respective user context and fetches their isolated active telemetry values in under 1 second.
- **SC-003**: The admin dashboard passes 100% of mobile-responsive structural validations (down to 320px viewport width) with zero text overflows or horizontal scrolls.
- **SC-004**: Double-taps on submit buttons within a 500ms window generate exactly one API request, with the button successfully disabling during the throttle window.
- **SC-005**: Tapping the "-" decrement button on any count item that is greater than `0` dispatches a secure request to the reverse endpoint and updates the local value display in under 500ms on standard cellular networks.
- **SC-006**: When a metric count is `0`, the corresponding "-" button is visually locked, preventing any API request dispatch.

---

## Assumptions

- **Assumption 1**: A single global `tracker_key` authorization token is shared among all trusted logging campers.
- **Assumption 2**: S3 static frontend files can extract URL parameters via standard browser `URLSearchParams` APIs and query backend state directly using `fetch`.
- **Assumption 3**: The admin user's `tracker_key` is persisted in the browser's local storage (`localStorage`) to preserve authentication state across browser sessions.
- **Assumption 4**: The frontend JavaScript contains a hardcoded mapping of short user identifiers to their full display names:
  * `hvy` -> "Harvy Atwal"
  * `ali` -> "Alice Smith"
  * `bob` -> "Bob Camper"
- **Assumption 5**: The backend API supports individual user endpoints or query structures to pull isolated counts (e.g., `GET /beer?u=ali`) and reverse endpoints to decrement aggregates (e.g., `POST /beer/reverse`).
