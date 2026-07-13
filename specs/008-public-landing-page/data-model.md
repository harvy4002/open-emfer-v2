# Data Model: Public Landing Page and Dynamic Dashboard Routing

This document describes the routing state model managed by the client-side browser session.

## 1. Browser Session Route Model (DOM State)

At runtime, the single-page application (`web/index.html`) maintains a virtual state machine that determines which top-level container to render.

### DOM View Structure
- **Container 1**: `#intro-landing-view` (Informational portal panel)
  - Key sections: Project Introduction paragraphs, Active Participant quick link buttons (`hvy`, `cha`, `ash`, `tin`, `combined`).
- **Container 2**: `#dashboard-view` (Telemetry widgets panel)
  - Key sections: Title header, metric cards, chart panels, historical logs list.

### View Visibility State Mapping
The visibility states of the containers map to the presence and validation of the URL parameters on load:

| Query Parameter `u` value | `#intro-landing-view` visibility | `#dashboard-view` visibility | Active Dashboard Context |
|-------------------------|--------------------------------|------------------------------|--------------------------|
| `(absent)` / `null` | **VISIBLE** | **HIDDEN** | N/A (Project Landing Page) |
| `hvy` | **HIDDEN** | **VISIBLE** | Harvy's stats |
| `cha` | **HIDDEN** | **VISIBLE** | Charlotte's stats |
| `ash` | **HIDDEN** | **VISIBLE** | Ash's stats |
| `tin` | **HIDDEN** | **VISIBLE** | Tina's stats |
| `combined` | **HIDDEN** | **VISIBLE** | Combined Camper stats |
| `(any other value)` | **VISIBLE** | **HIDDEN** | Fallback (displays intro page) |

---

## 2. Local Storage Cache Interactions

The browser maintains standard cache indicators, but they are dynamically bypassed under strict routing rules:

| LocalStorage Key | Data Type | Role in Onboarding Routing |
|------------------|-----------|----------------------------|
| `active_user_id` | String | Cached ID representing the last viewed camper profile. Bypassed on initial page load if no URL parameters are present to ensure the introductory landing page is shown. |
