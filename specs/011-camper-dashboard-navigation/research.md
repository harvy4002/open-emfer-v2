# Technical Research: Camper Dashboard Quick Navigation

## Unknowns & Clarifications (from Technical Context)

All previously identified unknowns from the specification phase have been thoroughly researched and resolved.

1. **How do we inject the navigation header inside the existing dashboard layout without causing massive structural changes?**
   - *Investigation*: Checked `web/index.html`. Pinned right above the level container containing `#dashTitle`.
   - *Resolution*: We will add a new Bulma container container `#dashboard-navigation-bar` as the first child of the `#dashboard-view` section. This places the navigation links right above the dashboard header, ensuring high visibility.

2. **How to hide/show the navigation bar cleanly?**
   - *Resolution*: Since the onboarding landing page `#intro-landing-view` has a `.hidden` class toggled by `initUI()`, placing `#dashboard-navigation-bar` inside `#dashboard-view` will automatically hide it when the onboarding view is active. This avoids any complex secondary toggling logic!

3. **How do we implement the responsive mobile dropdown collapsing logic in Bulma CSS?**
   - *Decision*: We will configure a dual-layout container using Bulma's responsive helper classes:
     - On desktop and tablet viewports (screens >= 768px), we render a classic horizontal button row wrapper: `<div class="is-hidden-mobile">...</div>`.
     - On mobile viewports (screens < 768px), we collapse this into a Bulma-styled dropdown selector menu or standard `<div class="select is-fullwidth is-hidden-tablet">...</div>` carrying a `<select>` drop-down list. This is natively supported by Bulma, requires zero dependencies, and functions flawlessly on viewports down to 320px while conserving maximum screen real-estate.

## Technology Choices & Best Practices

1. **HTML5 History APIs (`pushState` / `popstate`)**
   - **Decision**: Trigger standard `window.history.pushState` on clicking other participants or selecting a participant from the mobile `<select>` dropdown.
   - **Rationale**: Reuses the exact same routing pipelines established inside `web/js/app.js`, ensuring that the charts, maps, and widgets reload immediately and correctly.
