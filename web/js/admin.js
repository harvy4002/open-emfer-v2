/**
 * web/js/admin.js
 * JavaScript Controller for the Participant Manual Logging panel with bi-directional counter controls.
 */

// Dynamic Host Resolver (FR-008)
const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
const API_BASE = isLocal ? "http://localhost:3000" : "https://01uy6frz0h.execute-api.eu-west-2.amazonaws.com/prod";

// Hardcoded user profiles names mapping (Assumption 4)
const USER_NAMES = {
  hvy: "Harvy",
  cha: "Charlotte",
  ash: "Ash",
  tin: "Tina"
};

// Extract compact user parameter 'u' (FR-006 / FR-007)
const urlParams = new URLSearchParams(window.location.search);
let activeUser = urlParams.get("u") || urlParams.get("user_id") || "hvy";

// Ensure fallback to hvy if invalid/unrecognized
if (!USER_NAMES[activeUser]) {
  activeUser = "hvy";
}

let TRACKER_KEY = localStorage.getItem("admin_tracker_key") || "";

// Global reminder notification interval timer handle (US2)
let reminderIntervalTimer = null;

// Enforce UI initialization on load
document.addEventListener("DOMContentLoaded", () => {
  // Set up header titles
  const displayName = USER_NAMES[activeUser] || `${activeUser.toUpperCase()}'s Dashboard`;
  document.getElementById("camperNameHeader").textContent = `${displayName}'s Logging Portal`;
  document.getElementById("camperSubHeader").textContent = `Locked context: ${activeUser.toUpperCase()}`;

  // Dynamically configure the link back to the user's public telemetry dashboard
  const publicLink = document.getElementById("publicDashboardLink");
  if (publicLink) {
    publicLink.href = `index.html?u=${activeUser}`;
  }

  // Initialize Tracker Key input UI
  if (TRACKER_KEY) {
    document.getElementById("trackerKeyInput").value = TRACKER_KEY;
    document.getElementById("keyStatus").textContent = "✓ Tracker Key saved and cached";
    document.getElementById("keyStatus").className = "help is-success";
  } else {
    document.getElementById("keyStatus").textContent = "⚠ No Tracker Key found. Please save a key to authorize logs.";
    document.getElementById("keyStatus").className = "help is-warning";
  }
  
  // Sync live values on load (FR-009)
  syncState();

  // Initialize Reminder Notifications preference (US1 / US2)
  initNotificationsUI();
});

function saveTrackerKey() {
  const keyVal = document.getElementById("trackerKeyInput").value.trim();
  if (!keyVal) {
    showFlash("Please enter a valid key", "error");
    return;
  }
  localStorage.setItem("admin_tracker_key", keyVal);
  TRACKER_KEY = keyVal;
  document.getElementById("keyStatus").textContent = "✓ Tracker Key saved and cached";
  document.getElementById("keyStatus").className = "help is-success";
  showFlash("Authorization credentials cached successfully", "success");
  syncState();
}

function showFlash(message, type) {
  const responseDiv = document.getElementById("response");
  responseDiv.textContent = message;
  responseDiv.className = type;
  
  setTimeout(() => {
    responseDiv.textContent = "";
    responseDiv.className = "";
  }, 3000);
}

// 500ms submission click throttling (FR-005 / Edge Cases)
let submitLocked = false;

// Unified fetch to pull telemetry totals (FR-009)
async function syncState() {
  if (!TRACKER_KEY) return;
  
  try {
    // 1. Fetch Beer/Drinks/Toilet aggregates
    const resBeer = await fetch(`${API_BASE}/beer?user_id=${activeUser}&_=${Date.now()}`);
    if (resBeer.ok) {
      const data = await resBeer.json();
      const categories = data.categories || {};
      
      // Update counts inside the UI
      updateDisplayCount("Water", categories["Water"] || 0);
      updateDisplayCount("Coffee", categories["Coffee"] || 0);
      updateDisplayCount("Tea", categories["Tea"] || 0);
      updateDisplayCount("Soft", categories["Soft"] || 0);
      updateDisplayCount("Lager", categories["Lager"] || 0);
      updateDisplayCount("IPA", categories["IPA"] || 0);
      updateDisplayCount("Cider", categories["Cider"] || 0);
      updateDisplayCount("Ale", categories["Ale"] || 0);
      updateDisplayCount("Martini", categories["Martini"] || 0);
      updateDisplayCount("G+T", categories["G+T"] || 0);
      updateDisplayCount("Negroni", categories["Negroni"] || 0);
      updateDisplayCount("Port", categories["Port"] || 0);
      updateDisplayCount("Pee", categories["Pee"] || 0);
      updateDisplayCount("Poo", categories["Poo"] || 0);
    }
    
    // 2. Fetch Steps telemetry from /history
    const resHistory = await fetch(`${API_BASE}/history?user_id=${activeUser}&_=${Date.now()}`);
    if (resHistory.ok) {
      const data = await resHistory.json();
      const steps = data.cumulative_steps || 0;
      document.getElementById("display-steps").textContent = Number(steps).toLocaleString();
    }
  } catch (err) {
    console.error("Sync Error:", err);
    showFlash("Error: Failed to sync live values from API", "error");
  }
}

function updateDisplayCount(metricName, val) {
  const valInt = parseInt(val, 10) || 0;
  const countEl = document.getElementById(`count-${metricName}`);
  if (countEl) {
    countEl.textContent = valInt;
  }
  
  // Floor Count Protection: lock "-" button if count is 0 (FR-012)
  const decBtn = document.getElementById(`dec-${metricName}`);
  if (decBtn) {
    if (valInt <= 0) {
      decBtn.setAttribute("disabled", "true");
    } else {
      decBtn.removeAttribute("disabled");
    }
  }
}

async function submitLog(eventCategory, typeName, reverse = false) {
  if (submitLocked) return;
  if (!TRACKER_KEY) {
    showFlash("Error: Please provide a valid Tracker Key first", "error");
    return;
  }
  
  // Lock submissions
  submitLocked = true;
  document.querySelectorAll(".button.touch-btn").forEach(btn => btn.setAttribute("disabled", "true"));
  
  const certainBeerValues = ["Lager", "IPA", "Cider", "Ale"];
  const isBeer = certainBeerValues.includes(typeName);

  const payload = {
    user_id: activeUser,
    event: eventCategory,
    type: typeName,
    beer: isBeer ? "true" : "",
    reverse: reverse
  };

  try {
    const response = await fetch(`${API_BASE}/beer`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": TRACKER_KEY
      },
      body: JSON.stringify(payload)
    });

    if (response.status === 201 || response.status === 200) {
      showFlash(`Success: logged ${typeName}${reverse ? ' (REVERSED)' : ''}`, "success");
      // Instant local feedback + API sync
      await syncState();
    } else {
      const err = await response.json();
      showFlash(`Failed: ${err.message || 'Server error'}`, "error");
    }
  } catch (error) {
    console.error(error);
    showFlash(`Error: Network offline or blocked`, "error");
  } finally {
    // Unlock submissions after 500ms throttle interval
    setTimeout(() => {
      submitLocked = false;
      document.querySelectorAll(".button.touch-btn").forEach(btn => btn.removeAttribute("disabled"));
      // Re-apply zero floor disabled states
      syncState();
    }, 500);
  }
}

async function submitManualSteps() {
  if (submitLocked) return;
  if (!TRACKER_KEY) {
    showFlash("Error: Please provide a valid Tracker Key first", "error");
    return;
  }
  const stepsInput = document.getElementById("manualStepsInput");
  const stepVal = parseInt(stepsInput.value.trim(), 10);
  if (isNaN(stepVal) || stepVal < 0) {
    showFlash("Please enter a valid positive step count", "error");
    return;
  }

  submitLocked = true;
  const payload = {
    user_id: activeUser,
    steps: stepVal
  };

  try {
    const response = await fetch(`${API_BASE}/steps`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": TRACKER_KEY
      },
      body: JSON.stringify(payload)
    });

    if (response.status === 201 || response.status === 200) {
      showFlash(`Success: step count updated to ${stepVal.toLocaleString()}`, "success");
      stepsInput.value = "";
      await syncState();
    } else {
      const err = await response.json();
      showFlash(`Failed: ${err.message || 'Server error'}`, "error");
    }
  } catch (error) {
    console.error(error);
    showFlash(`Error: Network offline or blocked`, "error");
  } finally {
    submitLocked = false;
  }
}

async function triggerReset() {
  const confirmation = confirm(`Are you sure you want to RESET ALL camper data for ${activeUser.toUpperCase()}? This cannot be undone.`);
  if (!confirmation) return;
  
  await submitLog("Reset", "ResetDay");
}

// --- Reminder Notifications System (W3C Notifications, localStorage, US1/US2/US3) ---

function initNotificationsUI() {
  const isEnabled = localStorage.getItem("reminder_notifications_enabled") === "true";
  const intervalVal = localStorage.getItem("reminder_notifications_interval") || "60";

  const toggleBtn = document.getElementById("notificationToggleBtn");
  const selectMenu = document.getElementById("notificationIntervalSelect");
  const statusHelp = document.getElementById("notificationStatus");

  if (!toggleBtn || !selectMenu) return;

  // Restore cached dropdown selection
  selectMenu.value = intervalVal;

  if (isEnabled && Notification.permission === "granted") {
    setNotificationsActive(true);
  } else {
    setNotificationsActive(false);
    // Sync localStorage if permission was manually revoked in browser settings
    if (Notification.permission !== "granted") {
      localStorage.setItem("reminder_notifications_enabled", "false");
    }
  }
}

function setNotificationsActive(active) {
  const toggleBtn = document.getElementById("notificationToggleBtn");
  const selectMenu = document.getElementById("notificationIntervalSelect");
  const statusHelp = document.getElementById("notificationStatus");

  if (active) {
    toggleBtn.textContent = "Enabled  ✅";
    toggleBtn.className = "button is-success is-fullwidth touch-btn";
    selectMenu.removeAttribute("disabled");
    statusHelp.textContent = "✓ Reminders active. You will receive stats reminders at the selected interval.";
    statusHelp.style.color = "#48c774";
    scheduleReminderLoop();
  } else {
    toggleBtn.textContent = "Disabled ❌";
    toggleBtn.className = "button is-dark is-fullwidth touch-btn";
    selectMenu.setAttribute("disabled", "true");
    statusHelp.textContent = "Reminders disabled. Toggle On to authorize and schedule reminders.";
    statusHelp.style.color = "#7b8084";
    clearReminderLoop();
  }
}

async function toggleNotifications() {
  const isCurrentlyEnabled = localStorage.getItem("reminder_notifications_enabled") === "true";

  if (isCurrentlyEnabled) {
    // Disable reminders
    localStorage.setItem("reminder_notifications_enabled", "false");
    setNotificationsActive(false);
    showFlash("Telemetry reminders disabled", "success");
  } else {
    // Check Notifications availability
    if (!("Notification" in window)) {
      showFlash("Error: Your browser does not support standard Notifications API", "error");
      return;
    }

    // Request permissions (FR-003)
    const permission = await Notification.requestPermission();
    if (permission === "granted") {
      localStorage.setItem("reminder_notifications_enabled", "true");
      setNotificationsActive(true);
      showFlash("Successfully subscribed to telemetry reminders!", "success");
      // Trigger a sample instant welcome notification
      new Notification("EMF Camper Reminders Active ⛺", {
        body: `Welcome, ${USER_NAMES[activeUser] || "Camper"}! You will receive periodic reminders to log your stats.`,
        icon: "favicon.svg"
      });
    } else {
      localStorage.setItem("reminder_notifications_enabled", "false");
      setNotificationsActive(false);
      showFlash("Notification permission denied or blocked by browser", "error");
    }
  }
}

function changeNotificationInterval() {
  const selectMenu = document.getElementById("notificationIntervalSelect");
  if (!selectMenu) return;

  const intervalVal = selectMenu.value;
  localStorage.setItem("reminder_notifications_interval", intervalVal);
  showFlash(`Reminder interval updated to ${selectMenu.options[selectMenu.selectedIndex].text}`, "success");

  // Re-schedule the loop with the new interval (FR-007)
  scheduleReminderLoop();
}

function scheduleReminderLoop() {
  clearReminderLoop();

  const isEnabled = localStorage.getItem("reminder_notifications_enabled") === "true";
  if (!isEnabled || Notification.permission !== "granted") return;

  const intervalMinutes = parseInt(localStorage.getItem("reminder_notifications_interval") || "60", 10);
  const intervalMs = intervalMinutes * 60 * 1000;

  console.log(`[SCHEDULER] Scheduling reminders every ${intervalMinutes} minutes (${intervalMs}ms)`);

  reminderIntervalTimer = setInterval(() => {
    triggerReminderNotification();
  }, intervalMs);
}

function clearReminderLoop() {
  if (reminderIntervalTimer) {
    console.log("[SCHEDULER] Clearing previous reminder background timer");
    clearInterval(reminderIntervalTimer);
    reminderIntervalTimer = null;
  }
}

function triggerReminderNotification() {
  if (Notification.permission !== "granted") return;

  const displayName = USER_NAMES[activeUser] || "Camper";
  const notification = new Notification("EMF Camper Reminder ⛺", {
    body: `Hey ${displayName}! Remember to log your active steps, status, and beverage count on your Logging Portal.`,
    icon: "favicon.svg",
    requireInteraction: true
  });

  // Tap/click window refocus interaction (FR-005 / US3)
  notification.onclick = function(event) {
    event.preventDefault();
    window.focus();
    this.close();
  };

  localStorage.setItem("reminder_notifications_last_fired", new Date().toISOString());
}
