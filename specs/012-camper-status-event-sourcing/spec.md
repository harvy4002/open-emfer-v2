# Feature Specification: Event-Sourced Camper Status Image Matching

**Feature Branch**: `012-camper-status-event-sourcing`

**Created**: 2026-07-13

**Status**: Ready

**Input**: User description: "ensure the camp status like "chilling" for each user is stored using event sourcing and the aggregate. This will then be used to drive the logic for the public dashboard to show the camper status as an image."

---

## Purpose and Overview

The **Event-Sourced Camper Status Image Matching** feature standardizes active visual tracking on public participant dashboards. It ensures that the active visual portrait (e.g. sleeping, drinking, coding) shown on a camper's dashboard matches their explicitly logged status stored in the central database.

Key attributes of this feature include:
1. **Event-Sourced Storage**: Active status selections (such as "Chilling", "Sleeping", "Drinking", or custom states) are written as immutable event records to the single-table event log partition (`camper#events#<user_id>`).
2. **Case-Insensitive Resolution**: The backend standardizes and retrieves the most recent explicit status event, resolving case conflicts cleanly (e.g. logging "Status" or "status").
3. **Keyword-Fuzzy Asset Mapping**: The client-side dashboard parses the latest status string, fuzzy-matches it against the 11 available canonical photograph filenames, and dynamically loads the camper's individual folder asset path (e.g., `Coding` -> `workshop.jpg`).
4. **Reliable Touch targets and Fallbacks**: Maintains touch targets strictly >= 48px, while providing a double-fallback image `onerror` handler to prevent layout gaps.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Explicit Status Image Mapping (Priority: P1) 🎯 MVP

As a public dashboard viewer, I want the active camper activity visual to match the most recently logged explicit status on the admin panel, so that I can see what they are doing in real time.

**Why this priority**: Core value of the feature. Ensures status alignment between the administrator panel and follower views.

**Independent Test**: Log into the admin portal and click **"Coding"** under Camper Status. Navigating to the public dashboard view, verify that the activity photo displays the camper's `workshop.jpg` (mapped from "Coding") cleanly, and does not fallback to normal.

**Acceptance Scenarios**:

1. **Given** Charlotte is currently "Sleeping" (`cha_sleeping.jpg`), **When** Charlotte logs a steps telemetry event (implicit), **Then** Charlotte's visual profile image remains strictly pinned to `cha_sleeping.jpg` (ignoring implicit sensors).
2. **Given** Harvy is currently "Chilling", **When** Harvy logs a new explicit "Coding" status from the admin panel, **Then** Harvy's visual profile instantly updates to `/hvy_status/hvy_workshop.jpg` on the public dashboard.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Event-Sourced Status Schema)**: Status events MUST be saved as immutable records under the primary table composite keys: PK `"camper#events#<user_id>"` and SK `"event#<iso_timestamp>#<short_uuid_hash>"`.
- **FR-002 (Explicit Status Interception)**: The GET status retrieval API endpoint MUST filter history strictly for `"status"` or `"Status"` event type records, ignoring all implicit sensor telemetries (such as Drinks, steps, or Toilet).
- **FR-003 (Client Keyword Resolver)**: The frontend dashboard controller MUST incorporate a fuzzy keyword-matching map to dynamically bind arbitrary string inputs (e.g. Sleep, Nap, Bed) to the exact 11 local JPEG filenames (sleeping, drinking, eating, wet, lecture, workshop, roaming, tired, chilling, annoyed, normal).
- **FR-004 (Double-Fallback Safety)**: The profile status `<img>` element MUST register a double-fallback `onerror` loop to safely cascade image loading errors back to the user's normal picture, and finally the global `hvy_normal.jpg` baseline, preventing broken image layout gaps.

### Key Entities *(include if feature involves data)*

- **TelemetryEvent**: Existing single-table schema partition managing raw telemetry event streams.
- **CamperAggregate**: Cached aggregates table updating totals and summaries.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Custom status inputs dynamically update the public dashboard image in under **300ms** after background synchronization.
- **SC-002**: Triggering missing image 404 loads results in exactly **0** broken browser image icons displayed across viewports.
- **SC-003**: The responsive selector and quick navigation targets maintain a height strictly **>= 48px** to guarantee touch target usability.

---

## Assumptions

- **Assumption 1**: The client browser supports HTML5 history states and standard Javascript image error event listener loops.
- **Assumption 2**: S3 and CloudFront are configured with proper CORS permissions allowing browser GET/POST queries to the API Gateway domain.
