# Data Model: Camper Dashboard Quick Navigation

## 1. Domain Entities & URL Routing Structure

The Quick Navigation feature operates entirely on the client side inside the single-page application framework. It maps DOM-triggered button events to browser state changes.

### 1.1 Navigation State Controller

The existing `window.location` query parser acts as the active controller. We map each of the navigation buttons to standard URL search parameters.

| Suffix | Navigation Action | Browser History Effect | Target Route |
| :--- | :--- | :--- | :--- |
| **Portal Home** | Returns to introductory landing screen | `window.history.pushState(null, "", window.location.pathname)` | `index.html` (no query params) |
| **Harvy** | Switches context to Harvy | `window.history.pushState(null, "", "?u=hvy")` | `index.html?u=hvy` |
| **Charlotte** | Switches context to Charlotte | `window.history.pushState(null, "", "?u=cha")` | `index.html?u=cha` |
| **Ash** | Switches context to Ash | `window.history.pushState(null, "", "?u=ash")` | `index.html?u=ash` |
| **Tina** | Switches context to Tina | `window.history.pushState(null, "", "?u=tin")` | `index.html?u=tin` |
| **Combined** | Switches context to Combined | `window.history.pushState(null, "", "?u=combined")` | `index.html?u=combined` |

## 2. Active Tab Styling Map

Upon each state transition, the javascript engine will add the Bulma CSS modifier class `.is-link` (active highlight) to the button of the currently active camper, while setting all other participant buttons to `.is-dark` (inactive gray), visually indicating the page's current state.
