# Data Model: Google Analytics Integration

This document outlines the client-side configuration parameters and global variable structures utilized to store the Google Analytics Measurement ID and initialize standard analytics tags on the public static dashboard.

---

## 1. Static Configuration Variables

Because Google Analytics is a public-facing static tracker, the configuration resides entirely in a dedicated client-side Javascript file (`web/js/config.js`) to maintain the zero-cost static delivery standards outlined in Principle VII (Cost-Optimized Static Frontend).

### Global Namespace: `window.EMF_CONFIG`

Contains the application config parameters loaded during header execution.

| Attribute Name | Type | Description |
| :--- | :--- | :--- |
| `google_analytics_id` | `String` | Google Analytics 4 (GA4) Measurement ID (e.g., `G-XXXXXXXXXX`). Used to dynamically inject and invoke GTag scripts. |

#### Schema Definition Example (`web/js/config.js`):
```javascript
window.EMF_CONFIG = {
  google_analytics_id: "G-XXXXXXXXXX"
};
```

---

## 2. Injected Tag Manager Schema

Upon detection of a valid, configured GA key, the browser dynamically creates and executes standard Google Tag Manager nodes:

```html
<!-- Dynamically Injected Script Element -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>

<!-- Dynamically Appended Inline Script Node -->
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```
