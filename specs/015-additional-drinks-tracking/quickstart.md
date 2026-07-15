# Quickstart Validation Guide: Additional Drinks Tracking and Dynamic Public Dashboard Breakdown

This guide provides step-by-step instructions to validate the manual logging of new drink categories and their conditional, high-contrast display on the public dashboard.

## Prerequisites
Ensure the local frontend assets are being served statically, and that the backend simulation server is active:
```bash
# Start the local backend simulator & static server on port 3000
python3 backend/sim_server.py
```

---

## Scenario 1: Validate New Drinks Logging via Admin Panel

1. Open your browser and navigate to Charlotte's admin logging panel:
   [http://localhost:3000/admin.html?u=cha](http://localhost:3000/admin.html?u=cha)
2. Enter Charlotte's secure admin key:
   * **Key**: `cha_k_1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d`
   * Click **"Save Key"**.
3. Locate the new beverage rows under the **Drinks Counter** panel: `Martini`, `G+T`, `Negroni`, and `Port`.
4. Click the **"+"** button next to **"Negroni"**.
5. Verify that a POST request is triggered to the backend, the flash message confirms success, and the local Negroni count displays `1`.
6. Tapping the **"-"** button next to Negroni decrements the count back to `0`, and disables the "-" button to enforce the floor protection boundary.

---

## Scenario 2: Validate Conditional Render Filter (Strictly Greater Than 1)

1. Set up a mock database state for Charlotte where some drinks have a count of 1, and others have a count of 2 or more:
   * **Negroni**: 2 (Should be shown in breakdown)
   * **G+T**: 1 (Should be hidden from breakdown)
   * **Port**: 3 (Should be shown in breakdown)
   * **Lager**: 1 (Should be hidden from breakdown)
2. You can achieve this state by logging them on Charlotte's admin portal (bringing Negroni to 2, Port to 3, G+T to 1, and Lager to 1) or by verifying using standard admin portal taps.
3. Open a second browser tab to Charlotte's public dashboard:
   [http://localhost:3000/index.html?u=cha](http://localhost:3000/index.html?u=cha)
4. Scroll to the **Drinks Intake** card and locate the new **"Drinks Breakdown"** section.
5. Verify that:
   * **Negroni: 2** is clearly visible.
   * **Port: 3** is clearly visible.
   * **G+T** is **NOT** visible anywhere in the breakdown.
   * **Lager** is **NOT** visible anywhere in the breakdown.
6. Now return to Charlotte's admin panel and tap **"+"** next to **"G+T"** (bringing its total to 2).
7. Return to the public dashboard. On the next sync tick, verify that **G+T: 2** automatically and dynamically appears in the breakdown list in real-time.
