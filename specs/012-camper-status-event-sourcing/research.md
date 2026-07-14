# Technical Research: Event-Sourced Camper Status Image Matching

## Unknowns & Clarifications

1. **How do we isolate explicit status clicks from implicit sensor telemetries in DynamoDB?**
   - *Investigation*: Checked the schema partitions in DynamoDB. All logged activities write to the composite key partitions PK `camper#events#<user_id>`.
   - *Decision*: Since all events reside in a single Partition Key, the query handler must retrieve the event logs chronologically up to the current timestamp and filter the array inside memory for entries where `event_type.lower() == "status"`:
     ```python
     status_events = [e for e in events if e.get("event_type", "").lower() == "status"]
     ```
   - *Rationale*: This is exceptionally fast, leverages the database's sequential key structure, and guarantees that implicit events (like step increments or drink logging) never corrupt or override the user's explicitly selected active photo.

2. **How can we map custom logged status texts to our 11 existing image assets?**
   - *Decision*: We will configure a client-side keyword resolver inside `web/js/app.js` using case-insensitive substring search checks (e.g. "Nap" or "Sleep" maps to "sleeping", "Coding" or "Code" maps to "workshop").
   - *Rationale*: Eliminates any image 404 broken link errors in the browser, providing a modern, smooth, and bulletproof UX without duplicating assets.

## Technology Choices & Best Practices

1. **Dynamic Fallbacks (`onerror`)**:
   - Registering a client-side `onerror` fallback ensures that if an image is completely missing on AWS (e.g. during build-propagation delays), the layout falls back cleanly to `<camper>_normal.jpg` and eventually the global baseline `harvy_normal.jpg`.
