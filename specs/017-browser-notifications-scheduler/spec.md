# Feature Specification: Browser Notifications Scheduler

**Feature Branch**: `017-browser-notifications-scheduler`

**Created**: Wednesday, July 15, 2026

**Status**: Draft

**Input**: User description: "allow the participant subscribe to browser notifications. There should be a toggle to subscribe to the notifications and then an option to set the time between the notifications. The notification is to remind the participant to fill in their stats."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Notification Subscription Switch (Priority: P1)

As an admin portal user, I want a touch-friendly toggle on my manual logging screen to subscribe to browser reminder notifications, so that I can easily authorize or revoke reminder alerts.

**Why this priority**: Core subscription gateway. Without user authorization and permission granting, notifications cannot display in modern secure browsers.

**Independent Test**: Load the admin logging portal `/admin.html`. Find the "Telemetry Reminder Notifications" panel, and toggle the switch to "On". Confirm that the native browser permission dialog pops up, and granting permission updates the cached state to "Subscribed".

**Acceptance Scenarios**:

1. **Given** a user has not previously granted permission, **When** they toggle the reminder switch to "On", **Then** the browser requests native notification permission.
2. **Given** a user has already granted permission, **When** they load the page, **Then** the toggle switch defaults to "On" based on cached `localStorage` state.
3. **Given** a user toggles the switch to "Off", **When** they verify, **Then** all background notification timers are completely stopped.

---

### User Story 2 - Customizable Reminder Interval Dropdown (Priority: P2)

As a subscribed participant, I want to configure the time interval between reminders (e.g., 1 hour, 2 hours, 4 hours, or a 1-minute test option) from a select dropdown, so that I can schedule alerts that fit my pace.

**Why this priority**: Crucial for usability. Prevents spam and allows developers/participants to quickly verify the notifications work using the short test options.

**Independent Test**: Select the "1 Minute (Testing)" option from the interval select menu on `/admin.html`. Confirm that a notification is triggered exactly 60 seconds later, and that changing the option instantly cancels the old scheduler and runs the new schedule.

**Acceptance Scenarios**:

1. **Given** the user is subscribed, **When** they select "2 Hours" from the interval menu, **Then** the browser saves the interval selection to `localStorage` and schedules the recurring background reminder.
2. **Given** the user is subscribed, **When** they change the interval from "1 Hour" to "4 Hours", **Then** the previous background interval loop is cleanly destroyed and rescheduled for the new 4-hour period.

---

### User Story 3 - Interactive Focus and Portal Launch (Priority: P3)

As a participant, when I click on a received reminder notification, I want my browser to automatically focus or reload my personal Logging Portal page, so that I can immediately type or tap my stats.

**Why this priority**: Simplifies the log transaction workflow by closing the loop between receiving the reminder and acting on it.

**Independent Test**: Lock your screen or switch to another tab. When the reminder notification fires, click on the notification pop-up. Verify that the browser immediately refocuses Charlotte's active logging portal `/admin.html?u=cha`.

**Acceptance Scenarios**:

1. **Given** the participant has clicked on a received telemetry reminder, **When** the browser processes the click, **Then** the browser focuses the existing `/admin.html` page.

---

### Edge Cases

- **User Denied Permission**: If the user selects "Deny" on the browser's permission dialog, the portal switch MUST automatically toggle back to "Off" and display a friendly, high-contrast warning (e.g. "Notifications blocked by browser settings").
- **Tab Inactivity**: Since the scheduler runs in a background tab, modern browsers may throttle `setInterval` loops. The timer must handle wake/resume checks on tab activation to fire overdue reminders.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Responsive Switch Control)**: The manual logging portal (`web/admin.html`) MUST display a dedicated, Bulma-styled card panel containing a toggle/switch to subscribe/unsubscribe to reminder alerts.
- **FR-002 (Flexible Interval Selection)**: The logging portal (`web/admin.html`) MUST include a dropdown select list mapping intervals of: `1 Minute (Test)`, `5 Minutes (Test)`, `1 Hour`, `2 Hours`, `4 Hours`, and `8 Hours`.
- **FR-003 (W3C Notification Binding)**: The admin controller (`web/js/admin.js`) MUST request permission using the standard browser `Notification.requestPermission()` API on toggle activation.
- **FR-004 (Robust Scheduling Loop)**: The controller (`web/js/admin.js`) MUST manage background interval loops using `setInterval()` mapping the configured interval to trigger custom browser notification blocks containing reminder copy.
- **FR-005 (Refocus Tap Behavior)**: The generated `Notification` instance MUST override the `onclick` handler to refocus or open the current `window` context.
- **FR-006 (Persistent Local Storage Caching)**: The subscription status (enabled/disabled boolean) and selected interval value MUST be saved to `localStorage` and restored on page initialization.

### Key Entities

This feature operates purely as a **browser-native, client-side** system with **zero** backend/database tables or server compute requirements, maintaining complete compliance with Principle VII (Cost-Optimized Static Frontend).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Notification permissions are requested instantly upon toggling the switch to "On".
- **SC-002**: Under "1 Minute" test intervals, notifications fire exactly 60 seconds (±1s precision) after scheduling, with 100% reliability.
- **SC-003**: Clicks on received notification banners successfully focus or reopen the `/admin.html` browser tab in under 100ms.
- **SC-004**: Toggling the switch to "Off" instantly and completely tears down all background `setInterval` timers, preventing further alerts.

## Assumptions

- **Local Storage Reliability**: `localStorage` is assumed to be fully supported and enabled in the participant's browser environment.
- **HTTPS/Secure Context Requirements**: Since browser notification APIs require a secure context (HTTPS) or `localhost` to request permission, we assume this page is served over HTTPS in production or localhost during camp testing.
