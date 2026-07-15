/**
 * web/sw.js
 * Standard W3C Service Worker for Open EMF Camper Telemetry background Web Push.
 */

self.addEventListener("push", function(event) {
  console.log("[Service Worker] Push Received.");
  
  let title = "EMF Camper Reminder ⛺";
  let options = {
    body: "Time to log your active steps, status, and beverage count on your Logging Portal!",
    icon: "favicon.svg",
    badge: "favicon.svg",
    requireInteraction: true,
    data: {
      url: "/admin.html"
    }
  };

  if (event.data) {
    try {
      const payload = event.data.json();
      title = payload.title || title;
      if (payload.options) {
        options = { ...options, ...payload.options };
      }
    } catch (e) {
      // Fallback to text payload if not JSON
      options.body = event.data.text();
    }
  }

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

self.addEventListener("notificationclick", function(event) {
  console.log("[Service Worker] Notification Clicked.");
  event.notification.close();

  const targetUrl = event.notification.data && event.notification.data.url 
    ? event.notification.data.url 
    : "/admin.html";

  // Re-focus open window or open new portal tab (FR-006 / US3)
  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then(function(clientList) {
      for (let i = 0; i < clientList.length; i++) {
        const client = clientList[i];
        if (client.url.indexOf("admin.html") !== -1 && "focus" in client) {
          return client.focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow(targetUrl);
      }
    })
  );
});
