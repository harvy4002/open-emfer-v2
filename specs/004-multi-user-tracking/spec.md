# Feature Specification: Multi-User Tracking

**Feature Branch**: `004-multi-user-tracking`

**Created**: 2026-07-10

**Status**: Ready

**Input**: User description: "I also want the ability to track multiple users, so each would have their own dashboard and a combined dashboard for all stats. Each user has a backend dashboard to add to their stats for example each can increment a beer or toilet visit. See the index.html in the backend folder for more details" + "Also the public and backend dashboard need to be mobile first, as we are going to be using this in the field." + "each user will have a unique URL their public dashboard and backend amin. Their public dashboard will be on a QR code used in the field with a domain starting with https://emf.harvinderatwal.com for the interests of time I don't have a nice vanity folder name they can use, so just use a unique idenfier that small enough it won't affect the QR code too much."

---

## Purpose and Overview

The **Multi-User Tracking** feature extends the Open EMF Camper API and Public Dashboard to support multiple independent logging participants. Each tracking camper has their own profile and personalized S3/CloudFront dashboard. 

To support reliable operation on mobile devices under active outdoor field conditions (limited network, physical movement, single-hand touch inputs):
* **The public dashboard is developed using a mobile-first, highly responsive design.**
* **Public dashboards are easily accessible via physical QR codes printed for field scanning.** To keep the physical QR code grid density as low as possible (ensuring instant, sub-second camera focus and lock under poor lighting or movement), URLs utilize extremely compact, short unique identifiers (3-4 alphanumeric characters) instead of heavy vanity paths.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Individual Camper Dashboard (Priority: P1)

As an attendee or friend in the field, I want to scan a physical QR code on a camper's gear/tent to instantly open their public telemetry dashboard (e.g. `https://emf.harvinderatwal.com/?u=ali`) on my phone to monitor their real-time statistics, temperature, and tracking updates.

**Why this priority**: Essential to maintain the core public display value of the project for multiple separate camp participants under mobile network and scanning constraints.

**Independent Test**: Generate a QR code for the short URL `https://emf.harvinderatwal.com/?u=ali`, scan it with a mobile camera under sub-optimal lighting, and confirm it instantly opens and renders Alice's text counters, active status badges, and Chart.js canvases cleanly with zero overlapping text.

**Acceptance Scenarios**:

1. **Given** a user scans a camper's field QR code, **When** the browser navigates to `https://emf.harvinderatwal.com/?u=ali`, **Then** the page resolves the short identifier `ali` to load Alice's active image and environmental readings, arranging widgets in a single stacked column layout.

---

### User Story 2 - Combined Leaderboard & Totals (Priority: P2)

As a camp visitor, I want to access a combined public dashboard showing accumulated sum metrics across all campers (total camp-wide beers, total campsite cash spent, total combined steps) along with a camper leaderboard on my phone, so that I can easily see overall camp-wide activities.

**Why this priority**: Enhances social interaction and engagement by showing aggregate group statistics.

**Independent Test**: Load `/index.html` (with no user parameter) or `/index.html?u=combined` on a phone and verify that the numeric tiles display the combined sum of Alice's and Harvy's drinks.

**Acceptance Scenarios**:

1. **Given** multiple active campers logging telemetry, **When** the combined dashboard is loaded on a mobile screen, **Then** the page retrieves pre-aggregated combined stats and displays a vertically stacked leaderboard sorting campers.

---

### Edge Cases

- **Varying Screen Widths (320px - 480px)**: Displays range from small iPhone SE to large Android devices. Text and grid paddings must scale dynamically (using relative `rem`/`em` or percentage widths) to prevent content overflow on smaller screens.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Multi-User Payload)**: All telemetry ingestion POST endpoints MUST accept a `user_id` parameter in the request body, defaulting to `hvy` if omitted.
- **FR-002 (Pre-Aggregation Writes)**: On receiving a mutative telemetry POST, the backend system MUST update both the individual camper's aggregate partition (`camper#aggregates#<user_id>`) and the combined aggregate partition (`camper#aggregates#combined`) in DynamoDB to support low-latency combined views.
- **FR-003 (Capped GPS State)**: The backend MUST maintain isolated `state` singleton records for each user (`device#<device_id>` / `state`), enforcing the maximum 20-entry coordinate history limit per camper (Principle IV).
- **FR-004 (Combined Dashboard Charting)**: The combined public dashboard MUST display accumulated camp-wide numeric aggregates (such as total beers consumed, total distance traveled, and total campsite expenditures) on visual card tiles, while keeping individual environmental historical charts isolated on each camper's personal dashboard.
- **FR-005 (Short URL Binding)**: Frontend static assets MUST dynamically parse the user identifier from a compact query parameter `u` (e.g. `?u=ali`), defaulting to `hvy` if absent. This small parameter keeps the total URL size minimal for QR code density optimization.
- **FR-006 (Mobile-First Layout)**: The public dashboard MUST prioritize mobile-first display principles, utilizing responsive column structures (via Bulma CSS or custom flexbox) that stack cleanly on vertical mobile screens (down to 320px width) with zero horizontal scrolling.
- **FR-007 (Touch-Target Usability)**: All interactive controls, links, and buttons on the public dashboard MUST maintain a minimum height of **48px** to guarantee reliable tap targets for one-handed field operations.
- **FR-008 (QR Code URL Optimization)**: The public dashboard URL format MUST be optimized for physical QR code scanning in the field by utilizing the shortest possible unique user identifier keys (3-4 characters, alphanumeric), minimizing the QR grid density for sub-second scanner lock under low field lighting.

### Key Entities *(include if feature involves data)*

- **CamperProfile**: Represents a tracking participant. Key attributes: `user_id`, display name, short identifier (e.g., `ali`), registration timestamp.
- **CamperAggregates**: Partition containing sums across all tracked categories for a single camper (`camper#aggregates#<user_id>`).
- **CombinedAggregates**: Partition caching overall campaign totals across all campers (`camper#aggregates#combined`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of telemetry POSTs containing a specified `user_id` successfully update both the individual user aggregates and combined aggregate partitions in under 500ms.
- **SC-002**: Loading the combined dashboard totals (`u=combined`) retrieves and displays the sum of all camp activities in under 2 seconds.
- **SC-003**: The public dashboard passes 100% of mobile-responsive structural validations (e.g. Chrome DevTools responsive tests at 360px width) with zero text overflows or horizontal scrolls.
- **SC-004**: The generated QR codes for individual user dashboards (e.g. `https://emf.harvinderatwal.com/?u=ali`) resolve and scan successfully in under 1 second under standard low-light mobile testing conditions.

## Assumptions

- **Assumption 1**: A single global `tracker_key` authorization token is shared among all trusted logging campers.
- **Assumption 2**: Dynamic user profile registration is permitted—submitting a write for an unrecognized `user_id` automatically instantiates their aggregate partition.
- **Assumption 3**: S3 static frontend files can extract URL parameters via standard browser `URLSearchParams` APIs without server-side routing (SSR) requirements.
- **Assumption 4**: The frontend JavaScript contains a hardcoded mapping of short user identifiers (e.g. `ali`) to the corresponding full display names (e.g. `Alice`) to display descriptive headings in the UI.
