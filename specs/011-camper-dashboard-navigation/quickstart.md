# Quickstart Validation Guide: Camper Dashboard Quick Navigation

This guide verifies the persistent header navigation, the click transitions, active button highlights, and smooth home redirects.

## Prerequisites
Ensure the local frontend assets are served statically:
```bash
python3 backend/sim_server.py
```

## Scenario 1: Validate Landing Hide vs Dashboard Show

1. Load the root portal onboarding page:
   [http://localhost:3000/index.html](http://localhost:3000/index.html)
2. **Verify** that the `#dashboard-navigation-bar` is **completely hidden** from view.
3. Select "Charlotte (cha)" from the link buttons.
4. **Verify** that:
   * The onboarding box fades away.
   * Charlotte's dashboard renders successfully.
   * The `#dashboard-navigation-bar` becomes **visible** at the very top of Charlotte's dashboard.

## Scenario 2: Validate Cross-Dashboard Switches

1. Locate the navigation buttons inside the header bar.
2. Click the **"Tina"** button.
3. **Verify** that:
   * The page does not trigger a full reload (zero flash).
   * The URL in the address bar dynamically changes to `?u=tin`.
   * The dashboard title instantly updates to `"Tina's Telemetry Dashboard"`.
   * The "Tina" button highlights with Bulma's link color, while "Charlotte" is reset to inactive gray.

## Scenario 3: Return to Portal Home

1. Click the **"Home"** button on the far left of the navigation bar.
2. **Verify** that:
   * The URL query parameter is completely cleared.
   * The dashboard view fades out, and the introductory portal landing view fades back in cleanly.
