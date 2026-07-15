# Feature Specification: All-Time Leaderboard Steps and Daily Resets

**Feature Branch**: `016-all-time-leaderboard-steps`

**Created**: Wednesday, July 15, 2026

**Status**: Draft

**Input**: User description: "the stats should reset for each participant at the start of each day. They should be stored in the database for historical analysis. The combined dashboard should show total steps for all time for each person, same for leaderboard items"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - All-Time Beverage Leaderboard (Priority: P1)

As a camp visitor viewing the combined dashboard, I want to see a leaderboard of participants ranked by their **all-time** total drink count rather than a daily-resetting total, so that I can see who has logged the most drinks over the entire course of the camp.

**Why this priority**: Crucial for persistent gamification and ranking across the entire festival event.

**Independent Test**: Populate the database with historical event logs spanning multiple days for Ash (10 drinks total) and Charlotte (15 drinks total). Navigate to `/index.html?u=combined` and verify that the Leaderboard ranks Charlotte first with 15 drinks and Ash second with 10 drinks, regardless of what they logged today.

**Acceptance Scenarios**:

1. **Given** Charlotte has logged 5 drinks yesterday and 2 drinks today, **When** the combined dashboard loads, **Then** her rank is based on her cumulative count of 7 drinks.
2. **Given** Harvy resets his daily stats, **When** the combined dashboard leaderboard is rendered, **Then** Harvy's position and drink count do not drop to zero, preserving his historical total.

---

### User Story 2 - Cumulative All-Time Steps Rankings (Priority: P2)

As a camp visitor viewing the combined dashboard, I want to see a list of participants ranked by their **all-time** cumulative steps walked, so that I can see who is exploring the festival the most.

**Why this priority**: Enhances the combined telemetry dashboard with cooperative fitness analytics.

**Independent Test**: Load `/index.html?u=combined` and confirm that a new panel labeled "All-Time Steps Leaderboard" displays. Ensure it lists all active participants sorted in descending order of their total logged steps.

**Acceptance Scenarios**:

1. **Given** Ash has logged 25,000 steps and Charlotte has logged 30,000 steps, **When** the combined dashboard loads, **Then** Charlotte is listed above Ash in the steps rankings.
2. **Given** Harvy posts a steps update increasing his steps from 5,000 to 10,000, **When** the steps leaderboard refreshes, **Then** Harvy's steps total instantly updates to 10,000.

---

### User Story 3 - Automated Daily Participant Stats Reset (Priority: P3)

As a camp participant, I want my active telemetry counts (drinks, steps, environmental logs) to reset to zero at the start of each calendar day (00:00 UTC) on my personal dashboard, while knowing my raw logs are preserved forever in the event store for historical analysis.

**Why this priority**: Ensures that active, daily telemetry displays are clean, meaningful, and focused on current-day activities.

**Independent Test**: Log a drink for Charlotte at 23:59:55 UTC. Wait for the clock to transition past 00:00:00 UTC and load Charlotte's dashboard. Verify that her daily total drinks display resets to `0`, but calling `/playback?until=<yesterday_23_59_59>` successfully reconstructs her full previous day's metrics.

**Acceptance Scenarios**:

1. **Given** the current date transitions to a new calendar day UTC, **When** the participant's dashboard queries aggregates or posts logs on the new day, **Then** the active daily total counters for that user reset to 0.
2. **Given** a daily reset has occurred, **When** a user queries `/playback` for historical analysis up to a specific date/time, **Then** the system replays the event store to reconstruct correct historical aggregates.

---

### Edge Cases

- **Daylight Saving / Timezone Transitions**: Daily resets are standardized strictly to **00:00 UTC** to ensure a uniform boundary across all serverless API instances.
- **Combined Dashboard Step Preservation**: Daily participant-level resets do not affect the combined steps counter, which remains cumulative for all-time.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Automated Reset Trigger)**: The backend API handler (`backend/sim_server.py`) MUST check the timestamp of the last logged event for a user against the current calendar day (UTC) on any post action. If a calendar day transition has occurred, it MUST append a `Reset` event with type `ResetDay` to trigger a clean slate for the new day's aggregates.
- **FR-002 (All-Time Leaderboard Storage)**: The backend MUST maintain a dedicated all-time leaderboard aggregate record in DynamoDB/JSON mapping cumulative drink totals for each camper.
- **FR-003 (All-Time Steps Tracking)**: The backend MUST maintain an all-time steps record for each camper and return it on combined query requests.
- **FR-004 (Combined Dashboard Display)**: The combined public dashboard (`web/index.html` and `web/js/app.js`) MUST render both the All-Time Beverage Leaderboard and the All-Time Steps Leaderboard.
- **FR-005 (Historical Playback Persistence)**: All raw logged events MUST remain fully preserved in the event partition (`camper#events#<user_id>`) for historical retrospective replay, regardless of daily reset events.

### Key Entities

- **AllTimeLeaderboard**:
  - `user_id`: Unique camper id
  - `display_name`: Formatted camper name
  - `total_drinks`: Cumulative drinks across all time (does not reset daily)
  - `cumulative_steps`: Cumulative steps across all time (does not reset daily)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of raw log events remain stored in the database and are queryable for historical analysis through the `/playback` API.
- **SC-002**: Upon transition past 00:00 UTC, the first API request automatically executes a daily reset in under 100ms without causing any request failures.
- **SC-003**: The combined dashboard successfully displays ranked columns for both all-time steps and all-time drinks.

## Assumptions

- **Standard Timezone**: Resets are bound to **UTC** to maintain serverless uniformity across lambdas.
- **Leaderboard Scope**: The leaderboard remains focused on active, registered campers (Harvy, Charlotte, Ash, and Tina).
