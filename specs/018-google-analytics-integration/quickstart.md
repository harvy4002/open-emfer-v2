# Quickstart Validation Guide: Google Analytics Integration

This guide outlines step-by-step instructions to validate configuration loading, dynamic tag injection, and graceful unconfigured opt-out bypasses.

## Prerequisites
Ensure the static assets are served locally on `localhost` (browsers automatically serve static pages perfectly on local port loops):
```bash
# Start the local backend simulator & static server on port 3000
python3 backend/sim_server.py
```

---

## Scenario 1: Validate Centralized Analytics Configuration

1. In your editor, navigate to `web/js/` and open the newly created config file `config.js`.
2. Confirm that the default configuration block is declared exactly as:
   ```javascript
   window.EMF_CONFIG = {
     google_analytics_id: "G-XXXXXXXXXX"
   };
   ```
3. Open `web/index.html` in your editor. Locate the `<head>` section.
4. Confirm that the script tag importing `config.js` is positioned **above** the core controller import `app.js`, ensuring proper execution order:
   ```html
   <script src="js/config.js"></script>
   <script src="js/app.js"></script>
   ```

---

## Scenario 2: Validate Dynamic Script Injection

1. Edit `web/js/config.js` and set the GA Measurement ID to a valid testing key:
   ```javascript
   window.EMF_CONFIG = {
     google_analytics_id: "G-EMF1234567"
   };
   ```
2. Open your browser and navigate to the public dashboard:
   [http://localhost:3000/index.html?u=cha](http://localhost:3000/index.html?u=cha)
3. Open the browser's developer tools (F12 or right-click -> Inspect), and select the **Elements** tab.
4. Inspect the `<head>` element of the document.
5. Verify that:
   * An external `<script async src="https://www.googletagmanager.com/gtag/js?id=G-EMF1234567"></script>` tag has been dynamically appended.
   * A subsequent inline script block is appended, declaring `window.dataLayer` and calling `gtag('config', 'G-EMF1234567')`.
6. Go to the **Console** tab and confirm there are zero JavaScript errors.

---

## Scenario 3: Validate Graceful Opt-Out and Unconfigured State

1. Edit `web/js/config.js` and revert the ID to empty or the default placeholder:
   ```javascript
   window.EMF_CONFIG = {
     google_analytics_id: ""
   };
   ```
2. Clear your browser cache and refresh Charlotte's public dashboard.
3. Inspect the document `<head>` and verify that **no** Googletagmanager scripts are loaded, and that the console has zero analytical script warnings, proving graceful bypass logic is fully operational.
