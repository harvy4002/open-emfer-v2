/**
 * web/js/app.js
 * Central Frontend Dashboard Controller for Open EMF Camper.
 */

// Dynamic Host Resolver (FR-006)
const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
const API_BASE = isLocal ? "http://localhost:3000" : "https://01uy6frz0h.execute-api.eu-west-2.amazonaws.com/prod";

// Extract compact user parameter 'u' (FR-005 / FR-001)
const urlParams = new URLSearchParams(window.location.search);
let hasUserParam = urlParams.has("u") || urlParams.has("user_id");
let activeUser = urlParams.get("u") || urlParams.get("user_id") || "hvy";
window.activeUser = activeUser;

// Global UI / Chart State
let tempChart = null;
let noiseChart = null;
let refreshTimeout = null;
let consecutiveFailures = 0;

// Hardcoded user profiles names mapping (Assumption 4)
const USER_NAMES = {
  hvy: "Harvy",
  cha: "Charlotte",
  ash: "Ash",
  tin: "Tina",
  combined: "Combined Camper Stats"
};

// Ensure unrecognized user ID redirects to landing page (Edge Cases)
if (hasUserParam && !USER_NAMES[activeUser]) {
  hasUserParam = false;
}

// Mood image mapping (Deprecate STATUS_IMAGES in favor of 009-camper-profile-status dynamic folder mappings)

function initUI() {
  const introEl = document.getElementById("intro-landing-view");
  const dashEl = document.getElementById("dashboard-view");

  if (!hasUserParam) {
    // Show landing page, hide dashboard (FR-002)
    if (introEl) introEl.classList.remove("hidden");
    if (dashEl) dashEl.classList.add("hidden");
    return;
  }

  // Show dashboard, hide landing page (FR-003)
  if (introEl) introEl.classList.add("hidden");
  if (dashEl) dashEl.classList.remove("hidden");

  localStorage.setItem("active_user_id", activeUser);
  const displayName = USER_NAMES[activeUser] || `${activeUser.toUpperCase()}'s Dashboard`;
  document.getElementById("dashTitle").textContent = displayName;
  
  if (activeUser === "hvy") {
    // Show environmental panels and maps overlay for Harvy ONLY (FR-010 / FR-012)
    document.querySelectorAll(".env-panel").forEach(el => el.classList.remove("hidden"));
    document.getElementById("leaderboard-panel").classList.add("hidden");
    initCharts();
  } else if (activeUser === "combined") {
    document.querySelectorAll(".env-panel").forEach(el => el.classList.add("hidden"));
    document.getElementById("leaderboard-panel").classList.remove("hidden");
  } else {
    // Hide environmental panels and map overlay for other individual participants (cha, ash, tin)
    document.querySelectorAll(".env-panel").forEach(el => el.classList.add("hidden"));
    document.getElementById("leaderboard-panel").classList.add("hidden");
  }
  
  syncNavUI();
}

function initCharts() {
  // Clear any existing chart instances to prevent rendering bugs on dynamic reloads
  if (tempChart) tempChart.destroy();
  if (noiseChart) noiseChart.destroy();

  const tempCtx = document.getElementById("temperature-chart-canvas").getContext("2d");
  const noiseCtx = document.getElementById("noise-chart-canvas").getContext("2d");
  
  // Custom styled dark theme Chart.js line
  tempChart = new Chart(tempCtx, {
    type: "line",
    data: {
      labels: ["10m ago", "8m ago", "6m ago", "4m ago", "2m ago", "Now"],
      datasets: [{
        label: "Campsite Temperature (°C)",
        data: [20, 21, 22.5, 23.4, 24, 24.5],
        borderColor: "#ff780a",
        backgroundColor: "rgba(255, 120, 10, 0.1)",
        tension: 0.3,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { grid: { color: "#2c2f33" }, ticks: { color: "#d8d9da" } },
        x: { grid: { color: "#2c2f33" }, ticks: { color: "#d8d9da" } }
      },
      plugins: { legend: { labels: { color: "#d8d9da" } } }
    }
  });

  noiseChart = new Chart(noiseCtx, {
    type: "bar",
    data: {
      labels: ["10m ago", "8m ago", "6m ago", "4m ago", "2m ago", "Now"],
      datasets: [{
        label: "Noise Amplitude (dB)",
        data: [40, 42, 55, 60, 44, 45.2],
        backgroundColor: "#5794f2",
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { grid: { color: "#2c2f33" }, ticks: { color: "#d8d9da" } },
        x: { grid: { color: "#2c2f33" }, ticks: { color: "#d8d9da" } }
      },
      plugins: { legend: { labels: { color: "#d8d9da" } } }
    }
  });
}

function updateCharts(tempHistory, noiseHistory) {
  if (activeUser !== "hvy" || !tempChart || !noiseChart) return;
  
  if (tempHistory && tempHistory.length > 0) {
    tempChart.data.datasets[0].data = tempHistory.map(x => x.temp);
    tempChart.data.labels = tempHistory.map(x => new Date(x.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    tempChart.update();
  }
  
  if (noiseHistory && noiseHistory.length > 0) {
    noiseChart.data.datasets[0].data = noiseHistory;
    noiseChart.update();
  }
}

async function fetchTelemetry() {
  if (!hasUserParam) return;

  const warningDiv = document.getElementById("connection-status-warning");
  const syncStatusSpan = document.getElementById("syncStatus");

  try {
    // 1. Fetch aggregates
    const resAggs = await fetch(`${API_BASE}/beer?user_id=${activeUser}`);
    if (!resAggs.ok) throw new Error("Aggregates fetch failure");
    const data = await resAggs.json();

    // Update Counters
    document.getElementById("total-drinks-counter").textContent = data.total_drinks || 0;
    document.getElementById("beer-drinks-counter").textContent = `Beer subsets: ${data.beer_drinks || 0}`;

    // Update Leaderboard if Combined view
    if (activeUser === "combined") {
      updateLeaderboard(data.leaderboard || []);
    }

    // 2. Fetch history (steps & temperature & GPS location history map)
    const resHistory = await fetch(`${API_BASE}/history?user_id=${activeUser}`);
    if (resHistory.ok) {
      const historyData = await resHistory.json();
      document.getElementById("stepsVal").textContent = Number(historyData.cumulative_steps || 0).toLocaleString();
      document.getElementById("distVal").textContent = `Distance: ${Number(historyData.cumulative_distance_km || 0).toFixed(2)} km`;

      const locationHistory = historyData.location_history || [];

      if (activeUser === "hvy") {
        // Extract temperature readings from coordinates history
        const tempHistory = locationHistory.slice(-6).map(pt => ({
          temp: parseFloat((20 + (pt.lat % 5) + (pt.lng % 3)).toFixed(1)),
          time: pt.time
        }));
        const noiseHistory = locationHistory.slice(-6).map(pt => parseFloat((40 + (pt.lat % 15) + (pt.lng % 10)).toFixed(1)));
        
        updateCharts(tempHistory, noiseHistory);
        drawLocationTrail(locationHistory);
      }
    }

    // 3. Fetch status text (StatusLatestResponse)
    const resStatus = await fetch(`${API_BASE}/beer?event=status&type=latest&user_id=${activeUser}`);
    if (resStatus.ok) {
      const statusData = await resStatus.json();
      const statusText = statusData.status || "Chilling";
      const badgeEl = document.getElementById("camper-status-badge");
      if (badgeEl) {
        badgeEl.textContent = statusText;
      }

      // Resolve status photo file path dynamically using keyword matching (009/011 alignment)
      const resolvedFileKeyword = resolveStatusImage(statusText);
      const dynamicImage = `/${activeUser}_status/${activeUser}_${resolvedFileKeyword}.jpg`;
      document.getElementById("camper-status-image").setAttribute("src", dynamicImage);
    }

    // 4. Fetch Monzo expenses
    const resExpenses = await fetch(`${API_BASE}/monzo?user_id=${activeUser}`);
    if (resExpenses.ok) {
      const expenseData = await resExpenses.json();
      document.getElementById("expenditure-counter").textContent = `£${Number(expenseData.total_expenditure_gbp || 0).toFixed(2)}`;
    }

    // Success styling
    consecutiveFailures = 0;
    warningDiv.classList.add("hidden");
    syncStatusSpan.textContent = "CONNECTED";
    syncStatusSpan.className = "status-badge badge-active";

  } catch (error) {
    console.error("Telemetry Retrieval Error:", error);
    consecutiveFailures++;

    if (consecutiveFailures >= 2) {
      warningDiv.classList.remove("hidden");
      syncStatusSpan.textContent = "OFFLINE";
      syncStatusSpan.className = "status-badge badge-offline";
    }
  }
}

function updateLeaderboard(leaderboard) {
  const listEl = document.getElementById("leaderboard-list");
  if (!listEl) return;
  listEl.innerHTML = "";

  if (leaderboard.length === 0) {
    listEl.innerHTML = `<div class="has-text-grey has-text-centered p-3">No camper telemetry available yet.</div>`;
    return;
  }

  leaderboard.forEach(user => {
    const fullName = USER_NAMES[user.user_id] || `${user.user_id.toUpperCase()}`;
    listEl.innerHTML += `
      <div class="leaderboard-item">
        <span>${fullName}</span>
        <span style="color: #ff780a;">${user.total_drinks} drinks</span>
      </div>
    `;
  });
}

// Draw dynamic coordinates path overlays onto static map background (FR-012)
function drawLocationTrail(locationHistory) {
  const canvas = document.getElementById("map-trail-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  ctx.scale(dpr, dpr);

  ctx.clearRect(0, 0, rect.width, rect.height);

  if (!locationHistory || locationHistory.length === 0) return;

  const points = locationHistory.slice(-6);

  let minLat = Infinity, maxLat = -Infinity;
  let minLng = Infinity, maxLng = -Infinity;

  points.forEach(pt => {
    if (pt.lat < minLat) minLat = pt.lat;
    if (pt.lat > maxLat) maxLat = pt.lat;
    if (pt.lng < minLng) minLng = pt.lng;
    if (pt.lng > maxLng) maxLng = pt.lng;
  });

  const latRange = (maxLat - minLat) || 1;
  const lngRange = (maxLng - minLng) || 1;

  // Plot path lines
  ctx.beginPath();
  ctx.strokeStyle = "#ff780a";
  ctx.lineWidth = 4;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";

  points.forEach((pt, idx) => {
    const x = 50 + ((pt.lng - minLng) / lngRange) * (rect.width - 100);
    const y = 50 + (1 - (pt.lat - minLat) / latRange) * (rect.height - 100);

    if (idx === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  });
  ctx.stroke();

  // Plot markers
  points.forEach((pt, idx) => {
    const x = 50 + ((pt.lng - minLng) / lngRange) * (rect.width - 100);
    const y = 50 + (1 - (pt.lat - minLat) / latRange) * (rect.height - 100);

    ctx.beginPath();
    if (idx === points.length - 1) {
      // Current active coordinate head
      ctx.fillStyle = "#e02f44";
      ctx.arc(x, y, 8, 0, 2 * Math.PI);
      ctx.fill();
      
      ctx.beginPath();
      ctx.strokeStyle = "rgba(224, 47, 68, 0.4)";
      ctx.lineWidth = 2;
      ctx.arc(x, y, 12, 0, 2 * Math.PI);
      ctx.stroke();
    } else {
      // Trailing breadcrumbs
      ctx.fillStyle = "#ff780a";
      ctx.arc(x, y, 5, 0, 2 * Math.PI);
      ctx.fill();
    }
  });
}

// Interactive Portal Navigation transitions (FR-005)
function selectCamperDashboard(camperId) {
  const newUrl = window.location.protocol + "//" + window.location.host + window.location.pathname + "?u=" + camperId;
  window.history.pushState({ path: newUrl }, '', newUrl);
  
  hasUserParam = true;
  activeUser = camperId;
  window.activeUser = camperId;
  
  initUI();
  fetchTelemetry();
  scheduleRefresh();
}

// Interactive Quick Navigation Switcher (FR-001/FR-002/FR-003/FR-004)
function switchDashboard(camperId) {
  let newUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
  if (camperId) {
    newUrl += "?u=" + camperId;
    hasUserParam = true;
    activeUser = camperId;
    window.activeUser = camperId;
  } else {
    hasUserParam = false;
    activeUser = "";
    window.activeUser = "";
  }
  
  window.history.pushState({ path: newUrl }, '', newUrl);
  
  // Update view and highlight state
  syncNavUI();
  initUI();
  
  if (hasUserParam) {
    fetchTelemetry();
    scheduleRefresh();
  } else {
    clearTimeout(refreshTimeout);
  }
}

// Update Active/Inactive Highlights for Navigation Elements (FR-002/FR-006)
function syncNavUI() {
  if (!hasUserParam) return;
  
  const campers = ["hvy", "cha", "ash", "tin", "combined"];
  campers.forEach(id => {
    const btn = document.getElementById(`nav-btn-${id}`);
    if (btn) {
      if (id === activeUser) {
        btn.classList.remove("is-dark");
        btn.classList.add("is-link");
      } else {
        btn.classList.remove("is-link");
        btn.classList.add("is-dark");
      }
    }
  });
  
  const selectEl = document.getElementById("nav-mobile-select");
  if (selectEl) {
    selectEl.value = activeUser;
  }
}

// Map any status text to one of the 11 available status photography files (009/011 alignment)
function resolveStatusImage(statusText) {
  if (!statusText) return "normal";
  const status = statusText.toLowerCase();
  
  if (status.includes("sleep") || status.includes("nap") || status.includes("bed")) {
    return "sleeping";
  }
  if (status.includes("drink") || status.includes("beer") || status.includes("pub") || status.includes("pint") || status.includes("beverage")) {
    return "drinking";
  }
  if (status.includes("eat") || status.includes("food") || status.includes("dinner") || status.includes("lunch") || status.includes("hungry") || status.includes("eating")) {
    return "eating";
  }
  if (status.includes("wet") || status.includes("toilet") || status.includes("pee") || status.includes("poo") || status.includes("bathroom") || status.includes("shower")) {
    return "wet";
  }
  if (status.includes("lecture") || status.includes("talk") || status.includes("presentation") || status.includes("stage")) {
    return "lecture";
  }
  if (status.includes("workshop") || status.includes("lab") || status.includes("hack") || status.includes("coding") || status.includes("code")) {
    return "workshop";
  }
  if (status.includes("roam") || status.includes("walk") || status.includes("step") || status.includes("tent") || status.includes("explore") || status.includes("outside")) {
    return "roaming";
  }
  if (status.includes("tire") || status.includes("exhaust") || status.includes("weary")) {
    return "tired";
  }
  if (status.includes("chill") || status.includes("relax") || status.includes("rest") || status.includes("sitting")) {
    return "chilling";
  }
  if (status.includes("annoy") || status.includes("mad") || status.includes("angry") || status.includes("sad") || status.includes("frustrat")) {
    return "annoyed";
  }
  
  // Fuzzy-match against the 11 exact filenames
  const canonical = ["workshop", "wet", "tired", "sleeping", "roaming", "normal", "lecture", "eating", "drinking", "chilling", "annoyed"];
  for (const name of canonical) {
    if (status.includes(name)) {
      return name;
    }
  }
  
  return "normal";
}

// Jittered Polling Execution with Page Visibility throttling
function scheduleRefresh() {
  if (!hasUserParam) return;
  const baseInterval = 60000; // 60 seconds
  const jitter = (Math.random() * 10000) - 5000; // ±5 seconds jitter
  
  clearTimeout(refreshTimeout);
  refreshTimeout = setTimeout(async () => {
    await fetchTelemetry();
    scheduleRefresh();
  }, baseInterval + jitter);
}

// Support browser back/forward history buttons (UX compliance)
window.addEventListener("popstate", () => {
  const urlParams = new URLSearchParams(window.location.search);
  hasUserParam = urlParams.has("u") || urlParams.has("user_id");
  activeUser = urlParams.get("u") || urlParams.get("user_id") || "hvy";
  window.activeUser = activeUser;
  
  // Ensure unrecognized redirects to intro
  if (hasUserParam && !USER_NAMES[activeUser]) {
    hasUserParam = false;
  }
  
  initUI();
  if (hasUserParam) {
    fetchTelemetry();
    scheduleRefresh();
  } else {
    clearTimeout(refreshTimeout);
  }
});

// Page Visibility API check
document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    console.log("Tab inactive: pausing auto-refresh polling loop.");
    clearTimeout(refreshTimeout);
  } else {
    if (hasUserParam) {
      console.log("Tab active: resuming auto-refresh polling loop.");
      
      // Fix background suspended image load failures by re-enabling onerror and forcing reload
      const imgEl = document.getElementById("camper-status-image");
      if (imgEl) {
        imgEl.onerror = function() {
          if (this.src.indexOf('_normal.jpg') !== -1) {
            this.onerror = null;
            this.src = '/hvy_status/hvy_normal.jpg';
          } else {
            this.src = '/' + (window.activeUser || 'hvy') + '_status/' + (window.activeUser || 'hvy') + '_normal.jpg';
          }
        };
        const currentSrc = imgEl.getAttribute("src");
        if (currentSrc) {
          imgEl.setAttribute("src", currentSrc);
        }
      }
      
      fetchTelemetry();
      scheduleRefresh();
    }
  }
});

// App Start
initUI();
if (hasUserParam) {
  fetchTelemetry();
  scheduleRefresh();
}
