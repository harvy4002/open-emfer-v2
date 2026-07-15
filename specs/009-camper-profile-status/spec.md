# Feature Specification: Camper Profile Status Photos

**Feature Branch**: `009-camper-profile-status`

**Created**: 2026-07-13

**Status**: Ready

**Input**: User description: "for the camper status for Harvy specifically, although allow the provision for other users as well, to use the photos in the harvy_status folder to show the state harvy is in. The photo names should map to camping statuses. The public dashboard show the status in a box matching the photo dimensions and it will be like a profile picture."

---

## Purpose and Overview

The **Camper Profile Status Photos** feature introduces custom, telemetry-driven profile picture indicators on the public dashboard. Instead of static avatars, the profile picture box acts as a dynamic state indicator.
- Harvy's dashboard will load pictures from the `harvy_status/` static folder.
- Other participants (Charlotte, Ash, Tina) will have the same provision, loading from their respective sub-directories (e.g., `cha_status/`).
- The image file names will map directly to their current camping status and be prefixed with their user ID (e.g., `/web/harvy_status/harvy_sleeping.jpg` or `/web/harvy_status/harvy_drinking.jpg`), updating instantly when state changes.
- The photo renders inside a responsive, dedicated profile picture container preserving the image aspect ratio and layout boundaries.

---

## Clarifications

### Session 2026-07-13
- **Q**: What is the preferred image file format extension for camper status photos? → **A**: The pictures will be standard JPG/JPEG (`.jpg`) format only.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Dynamic Harvy Status Avatar (Priority: P1)

As Harvy, I want my public telemetry dashboard to display a profile picture representing my current camping status using custom photos from my `harvy_status/` directory, so that camp followers can immediately see my real-time physical state.

**Why this priority**: Core value of the user request. Establishes the dynamic image-swapping mechanism based on telemetry state.

**Independent Test**: Put the simulator or logger into "sleeping" state for user `hvy`. Load Harvy's public dashboard, and verify that the status container renders the image `/harvy_status/harvy_sleeping.jpg` in place of the generic profile avatar.

**Acceptance Scenarios**:

1. **Given** Harvy's telemetry status is "sleeping", **When** a user views Harvy's dashboard, **Then** the profile picture box displays the file `/harvy_status/harvy_sleeping.jpg`.
2. **Given** Harvy's telemetry status changes from "sleeping" to "drinking", **When** the dashboard telemetry synchronizes, **Then** the profile picture box smoothly updates to `/harvy_status/harvy_drinking.jpg`.

---

### User Story 2 - Multi-Camper Provision (Priority: P2)

As a camp participant (Charlotte, Ash, Tina), I want my dashboard to support custom status images loaded from my own status folder (e.g. `cha_status/`, `ash_status/`), so that all campers have access to personalized dynamic avatars.

**Why this priority**: Part of the core requirements to allow identical provisions for other users.

**Independent Test**: Load Charlotte's dashboard (`u=cha`) and set her telemetry status to "coding". Verify that her profile box displays `/cha_status/cha_coding.jpg`.

**Acceptance Scenarios**:

1. **Given** Charlotte has a status folder `cha_status/` and her telemetry status is "coding", **When** Charlotte's public dashboard is viewed, **Then** the page displays the photo `/cha_status/cha_coding.jpg`.
2. **Given** a participant has no custom status photo folder configured, **When** their dashboard is viewed, **Then** the page gracefully renders a standard fallback profile avatar.

---

### User Story 3 - Camper Status Text Display Label (Priority: P3)

As a public dashboard viewer, I want to see the name of the active camper status rendered in clean, readable text directly underneath their visual profile photo, so that I can immediately read what they are doing in real time.

**Why this priority**: Enhances visual tracking by providing linguistic clarity to the status image cards.

**Independent Test**: Log into the admin portal, set the status to "Sleeping", and open Harvy's dashboard. Verify that underneath the sleeping photo, a centered text label "Sleeping" is visible.

**Acceptance Scenarios**:

1. **Given** Harvy's active status is "Eating" in the database, **When** the dashboard loads, **Then** the image displays `harvy_eating.jpg` and a text label reading `"Eating"` is rendered directly underneath it.
2. **Given** Charlotte's active status is "Coding", **When** Charlotte's dashboard loads, **Then** the image displays `cha_workshop.jpg` and a text label reading `"Coding"` is displayed.

---

### Edge Cases

- **Missing Status Photo**: If Harvy transitions to a status that has no corresponding photo in the `/harvy_status/` directory (e.g., `harvy_active.jpg`), the dashboard must fall back to a default `harvy_normal.jpg` or fallback avatar without breaking the layout.
- **Varying Photo Dimensions**: Images inside the folder may have different aspect ratios. The container box must enforce a maximum sizing boundary (e.g., `max-width: 300px`) and preserve the image's natural aspect ratio without horizontal stretching or layout shifting.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Dynamic Directory Mapping)**: The public dashboard MUST dynamically resolve the status photo file path based on the active user identifier and their current telemetry status (e.g., `/web/<user_id>_status/<user_id>_<status_name>.jpg`).
- **FR-002 (Configurable Fallbacks)**: If a specific status photo is missing or a user does not have a status photo folder, the dashboard MUST display a standard fallback placeholder image (e.g., `/web/<user_id>_status/<user_id>_normal.jpg` or a generic avatar).
- **FR-003 (Status Code Normalization)**: The system MUST normalize status strings (e.g., converting "Drinking" or "Lecture" to lowercase "drinking" or "lecture") to match the file names of the images in the status folder.
- **FR-004 (Visual Profile Container)**: The public dashboard MUST render the status photo inside a prominent profile box (resembling a high-contrast profile picture) that maintains proper visual alignment on both mobile and desktop screens.
- **FR-005 (Responsive Sizing)**: The visual profile picture container MUST automatically scale responsively up to standard bounds (e.g., max-width 300px), maintaining aspect ratio and preventing layout shifts or horizontal scrolls on narrow screens.
- **FR-006 (File Format Standardization)**: The status photo file resolver MUST check for files in the standard JPG/JPEG (`.jpg`) format only.
- **FR-007 (Status Text Display Label)**: The public dashboard MUST render a centered, readable text label directly underneath the Camper Activity status image, displaying the exact capitalized name of the active camper status (e.g. "Chilling" or "Sleeping").

### Key Entities *(include if feature involves data)*

- **CamperProfile**: Existing entity representing a tracking participant. Extended to resolve the status folder path (e.g., `/web/<user_id>_status/`).
- **CamperStatusPhoto**: Represents a single state-image mapping. Key attributes: `status_name`, `file_path`, `aspect_ratio`.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of recognized telemetry status tags for Harvy successfully map to their corresponding photo files inside `/web/harvy_status/`.
- **SC-002**: Dynamically updated status images render inside the dashboard container in under 300ms after a telemetry sync event.
- **SC-003**: Dashboards for users without custom status folders gracefully fallback to standard avatars with zero broken image tags (`404` image loads).
- **SC-004**: The profile box conforms to mobile screens down to 320px width without exceeding grid boundaries or causing horizontal scroll.

---

## Assumptions

- **Assumption 1**: The status photo folders (e.g. `/web/harvy_status/`) are hosted as public static directories under the same root domain.
- **Assumption 2**: Standard status names correspond directly to file names in lowercase prefixed by the user ID (e.g., status "Sleeping" for user "harvy" maps to `harvy_sleeping.jpg`).
- **Assumption 3**: Browser caching of identical URLs does not block rendering of transitions when statuses change.
