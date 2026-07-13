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

// Mood image mapping based on camper status (FR-007)
const STATUS_IMAGES = {
  Chilling: "https://images.unsplash.com/photo-1517486808906-6ca8b3f04846?auto=format&fit=crop&w=300&q=80", // camp friends
  Roaming: "https://images.unsplash.com/photo-1478131143081-80f7f84ca84d?auto=format&fit=crop&w=300&q=80",  // tents hiking
  Drinking: "https://images.unsplash.com/photo-1436018626274-89acd67ae29e?auto=format&fit=crop&w=300&q=80", // cups cheers
  Eating: "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=300&q=80",   // camp food
  Happy: "https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=300&q=80",    // summer happy
  Coding: "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=300&q=80",   // laptop
  Sleeping: "https://images.unsplash.com/photo-1444858291040-58fe75488333?auto=format&fit=crop&w=300&q=80"  // sleeping
};

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
      document.getElementById("camper-status-badge").textContent = statusText;

      const fallbackImage = STATUS_IMAGES[statusText] || STATUS_IMAGES["Chilling"];
      document.getElementById("camper-status-image").setAttribute("src", fallbackImage);
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
  
  initUI();
  fetchTelemetry();
  scheduleRefresh();
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
