# Data Model: Browser Notifications Scheduler

This document outlines the standard browser-native `localStorage` keys and data structures utilized to cache and persist reminder notification configurations on the client side.

---

## 1. Browser Local Storage Schemas

Since this feature operates strictly client-side to minimize AWS Lambda execution overhead and maintain compliance with Principle VII (Cost-Optimized Static Frontend), no database tables are created. Configuration parameters are persisted inside the user's browser `localStorage`.

### Key 1: `reminder_notifications_enabled` (String Boolean)
* **Description**: Caches whether the user has toggled reminder notifications "On" or "Off".
* **Values**: `"true"` (enabled) or `"false"` (disabled)

### Key 2: `reminder_notifications_interval` (String Integer)
* **Description**: Caches the selected reminder scheduling interval mapped in milliseconds or minutes.
* **Values**:
  * `"1"` (1 Minute - testing option)
  * `"5"` (5 Minutes - testing option)
  * `"60"` (1 Hour)
  * `"120"` (2 Hours)
  * `"240"` (4 Hours)
  * `"480"` (8 Hours)

### Key 3: `reminder_notifications_last_fired` (String Timestamp)
* **Description**: Caches the ISO 8601 UTC timestamp of the most recently fired reminder notification. Used by the visibility wake/refocus listener to evaluate if a scheduled notification was missed while the background tab was throttled by the OS power-saving loop.
* **Format**: ISO 8601 UTC string (e.g., `2026-07-15T16:00:00.000Z`)

---

## 2. Notification Construction Payload (JSON Object)

Standard payload compiled at runtime and passed to the standard browser `Notification(title, options)` constructor.

```json
{
  "title": "EMF Camper Reminder ⛺",
  "options": {
    "body": "Hey Charlotte! Remember to log your active steps, telemetry, and beverage count on your Logging Portal.",
    "icon": "favicon.svg",
    "requireInteraction": true,
    "silent": false
  }
}
```
*Note on options:*
* **`requireInteraction`**: Encourages the browser to keep the notification banner active on screen until the user taps or dismisses it.
* **`icon`**: Points to our modern SVG brand favicon inside the project root, providing cohesive branding on the user's system drawer.
