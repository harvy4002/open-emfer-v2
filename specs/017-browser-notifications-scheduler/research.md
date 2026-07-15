# Research Document: Browser Notifications Scheduler

## Summary

This document evaluates the architectural design, browser-native notification standard compatibility, local caching schemas, and background execution behaviors to implement client-side reminder alerts on the participant's admin logging portal.

---

## Key Decisions

### 1. Client-Side W3C Notification API vs. Serverless Push Subscriptions
*   **Decision**: Utilize standard client-side browser `Notification` API combined with standard `setInterval` polling loops, rather than the W3C Push API / Service Worker subscription frameworks.
*   **Rationale**: The W3C Push API requires serverless push payload brokers (such as AWS SNS or WebPush routing), public key certificates (VAPID keys), and database-level tracking of active registration tokens. Using a localized, standard in-browser `Notification` scheme requires zero server compute, zero third-party brokers, and zero persistent database operations, fully conforming to Principle II (Serverless Simplicity) and Principle VII (Cost-Optimized Static Frontend).
*   **Alternatives Considered**: Full service worker based WebPush subscriptions. Rejected because it introduces major backend coordination, certificate deployment overhead, and payload encryption complexity for a purely administrative logging alert.

### 2. Standard Local Storage Schema
*   **Decision**: Persist subscription state and intervals directly inside browser-native `localStorage` under keys `reminder_notifications_enabled` (boolean) and `reminder_notifications_interval` (string mapping selected option).
*   **Rationale**: Ensures subscription preferences survive tab closures and phone restarts, permitting automatic scheduler re-initialization upon reloading the Logging Portal.

### 3. Background Scheduling and Tab Throttling Mitigation
*   **Decision**: Manage active schedulers globally inside `web/js/admin.js` using standard `setInterval` loops. To handle modern mobile browser throttling in background tabs, we will perform a date-comparison check on tab refocus (`visibilitychange` API) to verify if a notification interval was missed while suspended, and fire any overdue reminders immediately.
*   **Rationale**: Guarantees high-precision alert delivery even under aggressive browser power-saving rules, without requiring heavyweight service workers.

### 4. Direct Window Focus Override
*   **Decision**: Bind the standard browser focus action (`window.focus()`) directly inside the `onclick` handler of the generated `Notification` instance.
*   **Rationale**: Closes the loop between alert and action, giving participants an instantaneous, frictionless path back to `/admin.html` to log their campsite details.
