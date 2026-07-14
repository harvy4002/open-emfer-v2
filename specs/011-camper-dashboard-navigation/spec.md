# Feature Specification: Camper Dashboard Quick Navigation

**Feature Branch**: `011-camper-dashboard-navigation`

**Created**: 2026-07-13

**Status**: Ready

**Input**: User description: "edit the public dashbaord to add nagivation to the other participants from a particpant page"

---

## Purpose and Overview

The **Camper Dashboard Quick Navigation** feature enhances the user experience of the public telemetry dashboard by introducing a persistent navigation panel. 
Currently, once a user selects a camper (e.g. Charlotte) from the onboarding landing portal, they are locked into that dashboard context. To view another camper (e.g. Harvy), they must use the browser back button or manually return to the landing portal directory.

This feature adds a quick-switching navigation header visible exclusively when an individual dashboard is active:
- It will render a horizontal bar containing quick-navigation buttons for all other campers (`Harvy`, `Charlotte`, `Ash`, `Tina`, `Combined Stats`).
- Clicking a participant immediately transitions the single-page application (SPA) state to the new participant using HTML5 history APIs, updating all telemetry metrics in real time.
- It will also feature a "Home" button to return to the onboarding portal directory.

---

## Clarifications

### Session 2026-07-13
- **Q**: Should the navigation bar be rendered as a sticky top navbar, a horizontal scrolling list, or a responsive dropdown menu on mobile viewports? → **A**: Standardize on a responsive mobile dropdown (Option C). On desktop and tablet viewports, the navigation header displays as a clear horizontal row of buttons. On small mobile viewports below 768px, it collapses into a compact, responsive dropdown selector container to conserve maximum screen real-estate.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Quick Dashboard Switching (Priority: P1) 🎯 MVP

As a campsite viewer currently on an individual camper's dashboard, I want a prominent navigation bar containing links to other participants' dashboards, so that I can switch between camper dashboards without having to return to the root landing directory.

**Why this priority**: Core value of the user request. Solves the primary navigation gap between dashboards.

**Independent Test**: Navigate to Charlotte's dashboard (`u=cha`). Locate the navigation bar and click the "Tina" button. Verify that the browser seamlessly transitions to Tina's dashboard (`u=tin`) and updates the metrics without any page reloading or lost parameters.

**Acceptance Scenarios**:

1. **Given** a user is on Charlotte's dashboard, **When** they click the quick navigation link for "Tina", **Then** the client-side router executes `pushState` and loads Tina's telemetry metrics.
2. **Given** a user is on any individual dashboard, **When** they click the "Home" link in the quick navigation, **Then** the page cleanly returns to the onboarding portal directory.

---

## Edge Cases

- **Maintaining Warning State**: If a user switches dashboards while the connection banner is active, the connection warning banner state must be preserved, and the automatic polling interval must resume cleanly for the newly selected user.
- **Active Navigation Highlights**: When viewing a specific camper's dashboard (e.g., Harvy), the navigation link for "Harvy" must be visually highlighted/active or disabled to indicate the current page state.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Persistent Header Navigation)**: The public dashboard view MUST include a horizontal navigation header (or sticky mobile-optimized sub-header) that is only visible when an individual dashboard is active (hidden on the landing page).
- **FR-002 (Quick Switch Controls)**: The navigation header MUST display clear, responsive tap buttons for all other registered participants (`hvy`, `cha`, `ash`, `tin`, `combined`) enabling sub-second, client-side dashboard switching.
- **FR-003 (Parameter Alignment)**: Switching dashboards via the quick navigation links MUST trigger standard client-side `popstate` and `pushState` routing, synchronizing URL queries and immediately fetching the target camper's telemetry state.
- **FR-004 (Visual Home Link)**: The quick navigation header MUST contain a "Back to Onboarding" or "Portal Home" button enabling users to easily toggle back to the root landing directory.
- **FR-005 (Usable Sizing Bounds)**: All quick-switch buttons inside the header MUST maintain a minimum height of **48px** to serve as reliable mobile tap targets (Principle VII).
- **FR-006 (Responsive Dropdown Layout)**: The quick navigation bar MUST render as a standard horizontal row of buttons on desktop/tablet viewports, and collapse into a compact, responsive dropdown selector (using `<select>` or Bulma dropdown structures) on mobile viewports below 768px wide to conserve screen real-estate.

### Key Entities *(include if feature involves data)*

- **PortalSession**: Existing client-side model managing `activeUser` state. Extended to trigger navigation updates on header button clicks.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Clicking any navigation link successfully transitions the active camper dashboard context and triggers telemetry updates in under 300ms.
- **SC-002**: Transitioning between dashboards via quick-links triggers exactly 0 full page reloads, maintaining single-page state metrics.
- **SC-003**: Sizing of all quick navigation targets is strictly greater than or equal to 48px to prevent mis-clicks.
- **SC-004**: The navigation bar adjusts responsively across viewports down to 320px with zero horizontal scrolls.

---

## Assumptions

- **Assumption 1**: The list of active participants is static and matching the registered camper codes (`hvy`, `cha`, `ash`, `tin`).
- **Assumption 2**: The client-side browser supports standard HTML5 History APIs (`pushState` and `popstate` events) to handle SPA transitions.
- **Assumption 3**: CSS styling can easily hide/show the navigation bar depending on whether the onboarding landing page is active.
