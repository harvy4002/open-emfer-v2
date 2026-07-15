# Research Document: Additional Drinks Tracking and Dynamic Public Dashboard Breakdown

## Summary

This document evaluates the architectural design, storage impact, and user experience patterns for integrating four additional beverages (`Martini`, `G+T`, `Negroni`, `Port`) and rendering a conditional, responsive "Drinks Breakdown" section on the public telemetry dashboard that only shows drink categories with more than 1 unit consumed.

---

## Key Decisions

### 1. Storage Schema Design and No-Migration Patterns
*   **Decision**: Reuse the existing single-table database schema pattern on AWS DynamoDB and local emulation file `web_local_db.json`. The `categories` dictionary inside the `camper#aggregates#<user_id>` aggregate partition will dynamically accept and serialize the new drink fields: `Martini`, `G+T`, `Negroni`, and `Port`.
*   **Rationale**: Avoids the operational overhead, cost, and complexity of provisioning new database tables or running database migrations, complying fully with Principle II (Serverless Simplicity) and Principle IV (Safe and Secure Database Modeling).
*   **Alternatives Considered**: Creating a dedicated `DrinksBreakdown` table partition. Rejected because storing category-level drink tallies in the existing single-table `categories` map is extremely efficient, type-safe, and self-contained.

### 2. Admin Portal Extension and Touch target Usability
*   **Decision**: Extend the touch-friendly drinkscounter Bulma panel in `web/admin.html` to include logging rows for `Martini`, `G+T`, `Negroni`, and `Port`, each with decrement and increment buttons adhering to the core touch target constraint (minimum 48px height).
*   **Rationale**: Ensures consistent mobile usability for field logging in the campsite under low-light and cold conditions, complying with Principle VII.
*   **Alternatives Considered**: A dropdown menu selection. Rejected because multi-tap row layouts provide a significantly faster, lower-friction feedback loop than opening and selecting from a dropdown on mobile screens.

### 3. Conditional Public Dashboard Render Filtering
*   **Decision**: Implement browser-native vanilla JavaScript filtering in `web/js/app.js` that iterates over the `data.categories` key-value pairs returned by the serverless `/beer` GET API endpoint. The front-end will dynamically filter the entries to only render elements where `count >= 2` (count strictly greater than 1).
*   **Rationale**: Shifts the visual filtering logic to the client side. This minimizes Lambda CPU runtime compute constraints, keeps edge caching on S3/CloudFront optimal, and simplifies backend aggregation logic.
*   **Alternatives Considered**: Performing the filtering server-side in the Python Lambda handler. Rejected because if the participant's admin logger wants to sync and view *all* drinks (including those with 0 or 1 counts), the API must still return the full `categories` dataset, so client-side rendering is the most flexible and robust approach.

### 4. Backwards-Compatible Drink Inclusion
*   **Decision**: Apply the new dynamic conditional filter to *all* beverage categories (both existing and newly added). Any beverage—including Water, Coffee, Tea, Soft, Lager, IPA, Cider, Ale, and the new spirits—will be displayed in the dynamic "Drinks Breakdown" section of the public dashboard as soon as its tally reaches 2 or more.
*   **Rationale**: Delivers a cohesive, unified, and highly satisfying user experience, showing friends and followers exactly what is being consumed in significant quantities.
