# Feature Specification: Web Push Notifications Scheduler

**Feature Branch**: `017-browser-notifications-scheduler`

**Created**: Wednesday, July 15, 2026

**Status**: Draft

**Input**: User description: "allow the participant subscribe to browser notifications. There should be a toggle to subscribe to the notifications and then an option to set the time between the notifications. The notification is to remind the participant to fill in their stats. Upgrade to Option A: Web Push for mobile background closed-browser delivery."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Web Push Subscription Toggle (Priority: P1)

As an admin portal user, I want a touch-friendly toggle on my manual logging screen to subscribe to browser reminder notifications, so that the system can securely push alerts to my mobile phone even if my browser is completely closed.

**Why this priority**: Core subscription gateway. Secure context registrations and permission granting are required before any push payloads can be processed.

**Independent Test**: Load the admin logging portal `/admin.html`. Find the "Telemetry Reminder Notifications" panel, and toggle the switch to "On". Confirm that the browser requests notification permission, registers the Service Worker, and successfully POSTs the subscription object to `/push-subscribe`.

**Acceptance Scenarios**:

1. **Given** a user has not previously granted permission, **When** they toggle the reminder switch to "On", **Then** the browser requests native notification permission and registers `/sw.js`.
2. **Given** Charlotte is subscribed, **When** she toggles the switch to "Off", **Then** the browser unsubscribes her from the push service and notifies the backend to delete her registration.

---

### User Story 2 - Customizable Reminder Interval (Priority: P2)

As a subscribed participant, I want to configure the time interval between reminders (e.g., 1 hour, 2 hours, 1 minute test option) from a select dropdown, so that the server-side cron scheduler triggers pushes at my chosen pace.

**Why this priority**: Crucial for operational usability and power saving.

**Independent Test**: Select the "1 Minute (Test Option)" from the interval select menu on `/admin.html`. Confirm that a server-side daemon or EventBridge trigger dispatches a push notification exactly 60 seconds later.

**Acceptance Scenarios**:

1. **Given** the user is subscribed, **When** they select "1 Hour" from the interval menu, **Then** the browser sends the selected interval to the backend `/push-subscribe` route, updating their database aggregate `last_notified_time`.

---

### User Story 3 - Interactive Focus and Portal Launch (Priority: P3)

As a participant, when I click on a received reminder notification banner on my mobile device, I want my browser to automatically focus or open my personal Logging Portal page, so that I can instantly record my stats.

**Why this priority**: Completes the loop between prompt and action.

**Independent Test**: Switch tabs or lock your screen. When the push notification banner fires, tap it. Verify that the browser immediately closes the banner and refocuses Charlotte's active logging portal `/admin.html?u=cha`.

**Acceptance Scenarios**:

1. **Given** the participant has tapped a received telemetry reminder, **When** the service worker processes the click, **Then** the browser refocuses the existing `/admin.html` page.

---

### Edge Cases

- **User Revokes Browser Permissions**: If the browser's native notification settings are manually revoked, the frontend must detect this on load, toggle the switch to "Off", and alert the backend.
- **Server Push Failures**: If `pywebpush` returns a `410 Gone` (meaning the subscription has expired or been revoked by the browser), the backend must gracefully delete the subscription from the user's aggregate database record.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Web Manifest & SW registration)**: The static frontend MUST provide a Web App Manifest `web/manifest.json` and a Service Worker `web/sw.js` to enable background push capabilities.
- **FR-002 (PushManager Subscription)**: The admin controller (`web/js/admin.js`) MUST use the browser's native `PushManager.subscribe()` API with a VAPID public key on toggle activation, generating standard endpoint and crypto keys (p256dh, auth).
- **FR-003 (Subscription API Route)**: The backend API Gateway router (`backend/sim_server.py`) MUST expose a `POST /push-subscribe` endpoint that securely stores the user's push subscription JSON and selected `interval_minutes` in their aggregate totals database record.
- **FR-004 (Encrypted Payload Dispatcher)**: The backend (`backend/sim_server.py`) MUST run a background daemon scheduler (or EventBridge Lambda rule) that utilizes the `pywebpush` library to sign (using VAPID private key) and encrypt push payloads to registered endpoints when the interval lapses.
- **FR-005 (Service Worker Push Listener)**: The background Service Worker (`web/sw.js`) MUST listen for the standard `push` event, parse the decrypted payload, and display a native notification reminder containing custom, user-specific copy.
- **FR-006 (Interactive Notification Click)**: The Service Worker (`web/sw.js`) MUST listen for the `notificationclick` event and utilize standard client focus APIs (`clients.openWindow()` or `window.focus()`) to bring the portal `/admin.html` to the foreground.

### Key Entities

- **PushSubscription**: Caches client-specific endpoints. Stored inside the singleton aggregate record `camper#aggregates#<user_id>` totals partition.
  - `endpoint`: W3C push endpoint URL
  - `keys`: Encryption keys (p256dh and auth strings)
  - `interval_minutes`: Interval selection (integer)
  - `last_notified_time`: ISO UTC timestamp of last fired alert

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Notification permissions and push registrations are requested instantly upon toggling the switch to "On".
- **SC-002**: Tapping the notification banner successfully opens or focuses the `/admin.html` tab in under 200ms.
- **SC-003**: The background scheduler dispatches standard W3C encrypted push payloads to browser push endpoints within 60 seconds (±5s precision) under test intervals.
- **SC-004**: 100% of expired push subscriptions (`410 Gone` status returns) are cleanly pruned from the active database aggregates.

## Assumptions

- **W3C Standard Compliance**: Mobile and desktop browsers are assumed to fully support standard Service Worker push mechanics and native Notification interfaces.
- **Secure Context Requirements**: The static portal is served over HTTPS in production or localhost during local development to satisfy browser security bounds.
