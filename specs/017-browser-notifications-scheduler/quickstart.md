# Quickstart Validation Guide: Browser Notifications Scheduler

This guide details step-by-step instructions to validate standard permissions requesting, scheduling accuracy, local storage caching, background timers, and click refocus behaviors on standard secure contexts.

## Prerequisites
Ensure the static assets are served locally on `localhost` (browsers automatically recognize `localhost` as a secure context to permit W3C notification request triggers):
```bash
# Start the local backend simulator & static server on port 3000
python3 backend/sim_server.py
```

---

## Scenario 1: Validate Permissions Request and Switch Caching

1. Open your browser and navigate to Charlotte's Logging Portal:
   [http://localhost:3000/admin.html?u=cha](http://localhost:3000/admin.html?u=cha)
2. Locate the new **Telemetry Reminder Notifications** panel on the page.
3. Verify that:
   * The switch displays as **"Off"** by default.
   * The interval dropdown selector is disabled (or grayed out) as long as notifications are off.
4. Toggle the notifications switch to **"On"**.
5. Confirm that:
   * The browser's native notification authorization pop-up displays.
   * Click **"Allow"**.
6. Verify that:
   * The switch state updates to **"On"**.
   * A clean green success confirmation displays.
   * The interval dropdown selector becomes active and selectable.
7. Open the browser's developer console (F12) and check Local Storage. Confirm that `reminder_notifications_enabled` is stored as `"true"`.
8. Refresh the tab. Verify that the notifications switch remains toggled **"On"** automatically based on the cached state.

---

## Scenario 2: Validate Interval Scheduling and Background Timers

1. On Charlotte's admin portal, locate the interval selection dropdown.
2. Select **"1 Minute (Test Option)"** from the dropdown list.
3. Open the console or confirm that the schedule updates cleanly.
4. Minimize your browser, lock your screen, or switch to a different tab.
5. Wait exactly **60 seconds**.
6. Verify that:
   * A system notification banner pops up: **"EMF Camper Reminder ⛺"**.
   * The body displays a friendly reminder tailored to Charlotte: *"Hey Charlotte! Remember to log your active steps..."*.
7. Now, toggle the notifications switch to **"Off"**.
8. Wait another **60 seconds** and verify that no further notifications are delivered, confirming background timers have been completely torn down.

---

## Scenario 3: Validate Interactive Tap and Refocus Behavior

1. Enable reminder notifications on `/admin.html?u=cha` and select **"1 Minute (Test Option)"**.
2. Open another tab or navigate to a different webpage.
3. When the system notification banner fires, click on the banner.
4. Verify that:
   * The browser immediately closes the notification banner.
   * It refocuses and brings Charlotte's active logging portal `/admin.html?u=cha` tab to the foreground.
