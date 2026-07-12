/**
 * web/js/admin.js
 * JavaScript Controller for the Participant Manual Logging panel.
 */

// Dynamic Host Resolver (FR-006)
const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
const API_BASE = isLocal ? "http://localhost:3000" : "https://emf.harvinderatwal.com";
const TRACKER_KEY = "mock-super-secret-key";

// Extract compact user parameter 'u' (FR-005)
const urlParams = new URLSearchParams(window.location.search);
let activeUser = urlParams.get("u") || localStorage.getItem("active_user_id") || "hvy";

// Enforce UI initialization on load
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("userSelect").value = activeUser;
  localStorage.setItem("active_user_id", activeUser);
});

function switchProfile() {
  const selected = document.getElementById("userSelect").value;
  activeUser = selected;
  localStorage.setItem("active_user_id", selected);
  
  // Re-write query parameter without reloading page for low-friction switching
  const newUrl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?u=' + selected;
  window.history.pushState({ path: newUrl }, '', newUrl);
  
  showFlash(`Logging profile switched to ${selected.toUpperCase()}`, "success");
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

// 500ms submission click throttling (Edge Cases)
let submitLocked = false;

async function submitLog(eventCategory, typeName) {
  if (submitLocked) return;
  
  // Lock submissions
  submitLocked = true;
  document.querySelectorAll(".button.touch-btn").forEach(btn => btn.setAttribute("disabled", "true"));
  
  const reverse = document.getElementById("reverseCheck").checked;
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

    if (response.status === 201) {
      const resJson = await response.json();
      showFlash(`Success: logged ${typeName}${reverse ? ' (REVERSED)' : ''} for ${activeUser.toUpperCase()}`, "success");
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
    }, 500);
  }
}

async function triggerReset() {
  const confirmation = confirm(`Are you sure you want to RESET ALL camper data for ${activeUser.toUpperCase()}? This cannot be undone.`);
  if (!confirmation) return;
  
  await submitLog("Reset", "ResetDay");
}
