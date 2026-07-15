# Feature Specification: Additional Drinks Tracking and Dynamic Public Dashboard Breakdown

**Feature Branch**: `015-additional-drinks-tracking`

**Created**: Wednesday, July 15, 2026

**Status**: Draft

**Input**: User description: "Add some more drinks. Martini's, G+T, negroni, port. And ensure each drink is shown on the public dashboard if more than 1 is consumed"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add Secure Logging for New Drinks on Admin Portal (Priority: P1)

As a camp participant, I want to log when I consume a Martini, G+T (Gin & Tonic), Negroni, or Port from the mobile-first logging portal, so that my active beverage aggregates are securely tracked.

**Why this priority**: Core MVP logging capability. Participants must be able to record their intake of these new beverages in the field.

**Independent Test**: Navigate to `/admin.html?u=cha`, input Charlotte's secure tracker key, click the "+" button next to "Negroni", and confirm that a POST request is dispatched to `/beer` with `type: "Negroni"` and returned with status code 201.

**Acceptance Scenarios**:

1. **Given** Charlotte is logged into her admin logging portal, **When** she taps the "+" button for "G+T", **Then** the local "G+T" counter increments to 1, and the backend records the drink.
2. **Given** Harvy's admin portal has loaded, **When** he taps the "-" button for "Martini" (where current Martini count is 2), **Then** the local "Martini" counter decrements to 1, and a reverse-log event is sent to the backend.
3. **Given** any admin portal, **When** the current count of "Port" is 0, **Then** the "-" button next to "Port" is disabled to prevent counts from going below zero.

---

### User Story 2 - Conditional Public Dashboard Drinks Breakdown (Priority: P2)

As a camp visitor or follower, I want to see a detailed breakdown of specific beverages consumed on a camper's public dashboard, but only if they have consumed more than 1 of that drink, so that I can monitor their favorite beverages without cluttering the view with single drinks.

**Why this priority**: Crucial visual tracking requirement from user feedback. Keeps the UI focused on "significant" consumption (2 or more) while hiding single trial drink logs.

**Independent Test**: Update Charlotte's telemetry database to reflect: "Water: 1", "Lager: 5", "Negroni: 2", "Port: 0", and "G+T: 1". Navigate to Charlotte's public dashboard. Verify that under a "Drinks Breakdown" section, "Lager: 5" and "Negroni: 2" are displayed, while "Water", "Port", and "G+T" are completely hidden from the list.

**Acceptance Scenarios**:

1. **Given** Harvy's active categories has `Port: 2`, **When** Harvy's dashboard is opened or refreshed, **Then** "Port: 2" is displayed in the Drinks Breakdown container.
2. **Given** Charlotte's active categories has `Martini: 1`, **When** Charlotte's dashboard loads, **Then** "Martini" is not rendered in the Drinks Breakdown list.
3. **Given** a user has consumed 1 G+T and then logs a second G+T via the admin portal, **When** the public dashboard auto-refreshes, **Then** "G+T: 2" instantly appears in the breakdown section.

---

### User Story 3 - Live Admin Sync & State Verification (Priority: P3)

As a camp participant, I want the admin panel to sync the current counts of Martini, G+T, Negroni, and Port when clicking the "Sync State" button, so that I always see the exact state of my logged drinks.

**Why this priority**: Provides consistent and accurate feedback to the participant.

**Independent Test**: Load the admin portal for Ash. Log a Martini from another device or manually via curl. Click "Sync State" on Ash's admin portal, and verify that the "Martini" count increments to reflect the correct database state.

**Acceptance Scenarios**:

1. **Given** Ash has logged 3 negronis, **When** Ash clicks "Sync State" on `/admin.html`, **Then** the negroni count updates to 3.

---

### Edge Cases

- **Decrement below threshold**: If a camper has consumed 2 negronis (visible on public dashboard) and then decrements/reverses one negroni via the admin portal (bringing count to 1), the public dashboard must immediately hide the Negroni entry from the breakdown on next sync.
- **Combined Dashboard Support**: The `combined` camper aggregate must dual-write and sum up the new drink categories across all active campers. The combined public dashboard must also display the breakdown for these new categories if the sum is greater than 1.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Admin Logger UI Extension)**: The manual logging portal (`web/admin.html`) MUST display increment/decrement controls (with touch-friendly buttons adhering to the min-48px touch-target guideline) for `Martini`, `G+T`, `Negroni`, and `Port` drinks.
- **FR-002 (Admin Script Binding)**: The admin controller (`web/js/admin.js`) MUST bind and manage local storage caching, API POST requests, and UI state sync for `Martini`, `G+T`, `Negroni`, and `Port`.
- **FR-003 (Backend Route Support)**: The unified serverless API handler (`backend/sim_server.py`) MUST accept `Drinks` logs containing types `Martini`, `G+T`, `Negroni`, and `Port`, and correctly write these events to DynamoDB/local JSON db.
- **FR-004 (Public Breakdown Grid)**: The public telemetry dashboard (`web/index.html`) MUST include a structured section/container labeled "Drinks Breakdown" (or similar clean visual title).
- **FR-005 (Conditional rendering logic)**: The public dashboard controller (`web/js/app.js`) MUST query the database, iterate over the `categories` map, and render drink categories in the breakdown container ONLY if the count of that specific category is strictly greater than 1 (`count >= 2`).
- **FR-006 (Zero-state handling)**: If no drink category has a count greater than 1, the public dashboard Drinks Breakdown container MUST render a clean placeholder message (e.g. "No substantial drinks logged yet" or be hidden cleanly).

### Key Entities

- **CamperAggregates**:
  - `user_id`: Unique identifier (e.g., `hvy`, `cha`, `ash`, `tin`, `combined`)
  - `total_drinks`: Cumulative drinks count
  - `beer_drinks`: Cumulative beer subset count (contains Lager, IPA, Cider, Ale)
  - `categories`: Map containing beverage categories and their counts, including new categories: `Martini`, `G+T`, `Negroni`, and `Port`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: API writes for the new drink types (`Martini`, `G+T`, `Negroni`, `Port`) succeed with a `201 Created` status code and complete in under 500ms under standard latency constraints.
- **SC-002**: 100% of drink categories on the public dashboard with counts less than or equal to 1 are hidden from the detailed breakdown.
- **SC-003**: 100% of drink categories on the public dashboard with counts of 2 or more are rendered accurately in the breakdown.
- **SC-004**: The public dashboard breakdown behaves responsively on mobile views without causing any horizontal page scrolling.

## Assumptions

- **Local Storage Caching**: The new drinks will use the existing `admin_tracker_key` cached authentication structure without changes.
- **Existing Beer Subsets**: Martini, G+T, Negroni, and Port are not considered beer subsets, so they will not increment the `beer_drinks` total.
