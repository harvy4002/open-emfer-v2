/**
 * web/js/app.js
 * Central Frontend Dashboard Controller for Open EMF Camper.
 */

// Dynamic Host Resolver (FR-006)
const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
const API_BASE = isLocal ? "http://localhost:3000" : "https://emf.harvinderatwal.com";

// Extract compact user parameter 'u' (FR-005)
const urlParams = new URLSearchParams(window.location.search);
let activeUser = urlParams.get("u") || urlParams.get("user_id") || localStorage.getItem("active_user_id") || "hvy";

// Global UI / Chart State
let tempChart = null;
let noiseChart = null;
let refreshTimeout = null;
let consecutiveFailures = 0;

// Hardcoded user profiles names mapping (Assumption 4)
const USER_NAMES = {
  hvy: "Harvy Atwal",
  ali: "Alice Smith",
  bob: "Bob Camper",
  combined: "Combined Camper Stats"
};

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
  localStorage.setItem("active_user_id", activeUser);
  const displayName = USER_NAMES[activeUser] || `${activeUser.toUpperCase()}'s Dashboard`;
  document.getElementById("dashTitle").textContent = displayName;
  
  if (activeUser === "combined") {
    // Hide environmental charts on combined view (Option A)
    document.querySelectorAll(".env-panel").forEach(el => el.classList.add("hidden"));
    document.getElementById("leaderboard-panel").classList.remove("hidden");
  } else {
    initCharts();
  }
}

function initCharts() {
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
  if (activeUser === "combined" || !tempChart || !noiseChart) return;
  
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
  try {
    const beerRes = await fetch(`${API_BASE}/beer?user_id=${activeUser}`);
    const beerData = await beerRes.json();
    
    let historyData = { cumulative_steps: 0, cumulative_distance_km: 0.0, location_history: [] };
    if (activeUser !== "combined") {
      const historyRes = await fetch(`${API_BASE}/history?user_id=${activeUser}`);
      historyData = await historyRes.json();
    }
    
    const monzoRes = await fetch(`${API_BASE}/monzo`);
    const monzoData = await monzoRes.json();
    
    // Reset consecutive failures on successful pull
    consecutiveFailures = 0;
    document.getElementById("connection-status-warning").classList.add("hidden");
    document.getElementById("syncStatus").className = "status-badge badge-active";
    document.getElementById("syncStatus").textContent = "CONNECTED";
    
    // Render Counters
    document.getElementById("total-drinks-counter").textContent = beerData.total_drinks || 0;
    document.getElementById("beer-drinks-counter").textContent = `Beer subsets: ${beerData.beer_drinks || 0}`;
    document.getElementById("stepsVal").textContent = historyData.cumulative_steps || 0;
    document.getElementById("distVal").textContent = `Distance: ${(historyData.cumulative_distance_km || 0.0).toFixed(2)} km`;
    
    // Monzo format
    const exp = monzoData.total_expenditure_gbp || 0.00;
    document.getElementById("expenditure-counter").textContent = `£${exp.toFixed(2)}`;
    
    // Render Status Badges & Image (FR-007)
    let statusText = "Chilling";
    if (beerData.categories) {
      const activeStates = Object.keys(beerData.categories).filter(k => STATUS_IMAGES[k]);
      if (activeStates.length > 0) statusText = activeStates[activeStates.length - 1];
    }
    document.getElementById("camper-status-badge").textContent = statusText;
    document.getElementById("camper-status-image").src = STATUS_IMAGES[statusText] || STATUS_IMAGES.Chilling;
    
    // Combined leaderboards (User Story 3)
    if (activeUser === "combined" && beerData.leaderboard) {
      renderLeaderboard(beerData.leaderboard);
    }
    
    // Chart updates (if available)
    if (activeUser !== "combined" && historyData.location_history) {
      // Mock history structures for demo curve
      const mockTemps = historyData.location_history.map((pt, i) => ({
        temp: 20 + (i * 0.3) + (Math.sin(i) * 1.5),
        time: pt.time
      }));
      const mockNoise = historyData.location_history.map((pt, i) => 40 + (Math.cos(i) * 15));
      updateCharts(mockTemps, mockNoise);
    }
  } catch (error) {
    console.error("Telemetry fetch error:", error);
    consecutiveFailures++;
    
    // Dynamic timeout staleness handling (FR-017)
    if (consecutiveFailures >= 3) {
      document.getElementById("connection-status-warning").classList.remove("hidden");
      document.getElementById("syncStatus").className = "status-badge badge-offline";
      document.getElementById("syncStatus").textContent = "OFFLINE";
    }
  }
}

function renderLeaderboard(board) {
  const container = document.getElementById("leaderboard-list");
  container.innerHTML = "";
  
  if (board.length === 0) {
    container.innerHTML = `<div class="has-text-centered has-text-grey py-4">No active drinks logged yet</div>`;
    return;
  }
  
  board.forEach((user, index) => {
    container.innerHTML += `
      <div class="leaderboard-item">
        <span>#${index + 1} &nbsp; ${user.display_name}</span>
        <span style="color: #ff780a;">${user.total_drinks} drinks</span>
      </div>
    `;
  });
}

// Jittered Polling Execution with Page Visibility throttling
function scheduleRefresh() {
  const baseInterval = 60000; // 60 seconds
  const jitter = (Math.random() * 10000) - 5000; // ±5 seconds jitter
  
  refreshTimeout = setTimeout(async () => {
    await fetchTelemetry();
    scheduleRefresh();
  }, baseInterval + jitter);
}

// Page Visibility API check (Load Specs / NFRs)
document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    console.log("Tab inactive: pausing auto-refresh polling loop.");
    clearTimeout(refreshTimeout);
  } else {
    console.log("Tab active: resuming auto-refresh polling loop.");
    fetchTelemetry();
    scheduleRefresh();
  }
});

// App Start
initUI();
fetchTelemetry();
scheduleRefresh();
