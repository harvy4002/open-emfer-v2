/**
 * web/js/admin.js
 * JavaScript Controller for the Participant Manual Logging panel with bi-directional counter controls.
 */

// Dynamic Host Resolver (FR-008)
const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
const API_BASE = isLocal ? "http://localhost:3000" : "https://emf.harvinderatwal.com";

// Hardcoded user profiles names mapping (Assumption 4)
const USER_NAMES = {
  hvy: "Harvy Atwal",
  ali: "Alice Smith",
  bob: "Bob Camper"
};

// Extract compact user parameter 'u' (FR-006 / FR-007)
const urlParams = new URLSearchParams(window.location.search);
let activeUser = urlParams.get("u") || urlParams.get("user_id") || "hvy";

// Ensure fallback to hvy if invalid/unrecognized
if (!USER_NAMES[activeUser]) {
  activeUser = "hvy";
}

let TRACKER_KEY = localStorage.getItem("admin_tracker_key") || "";

// Enforce UI initialization on load
document.addEventListener("DOMContentLoaded", () => {
  // Set up header titles
  const displayName = USER_NAMES[activeUser] || `${activeUser.toUpperCase()}'s Dashboard`;
  document.getElementById("camperNameHeader").textContent = `${displayName}'s Logging Portal`;
  document.getElementById("camperSubHeader").textContent = `Locked context: ${activeUser.toUpperCase()}`;
  
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
    const resBeer = await fetch(`${API_BASE}/beer?user_id=${activeUser}`);
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
      updateDisplayCount("Pee", categories["Pee"] || 0);
      updateDisplayCount("Poo", categories["Poo"] || 0);
    }
    
    // 2. Fetch Steps telemetry from /history
    const resHistory = await fetch(`${API_BASE}/history?user_id=${activeUser}`);
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

async function triggerReset() {
  const confirmation = confirm(`Are you sure you want to RESET ALL camper data for ${activeUser.toUpperCase()}? This cannot be undone.`);
  if (!confirmation) return;
  
  await submitLog("Reset", "ResetDay");
}
