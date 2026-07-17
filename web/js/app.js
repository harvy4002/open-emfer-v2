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
let mapInstance = null;
let mapLayersGroup = null;

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
  // Initialize Google Analytics tracking (US1 / US2 / US3)
  initGoogleAnalytics();

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
    
    // Show individual panels
    document.getElementById("camper-activity-panel").classList.remove("hidden");
    document.getElementById("steps-panel").classList.remove("hidden");
    document.getElementById("monzo-panel").classList.remove("hidden");
    initCharts();
  } else if (activeUser === "combined") {
    document.querySelectorAll(".env-panel").forEach(el => el.classList.add("hidden"));
    document.getElementById("leaderboard-panel").classList.remove("hidden");
    
    // Hide individual panels on combined view (US-combined UX requirements)
    document.getElementById("camper-activity-panel").classList.add("hidden");
    document.getElementById("steps-panel").classList.add("hidden");
    document.getElementById("monzo-panel").classList.add("hidden");
  } else {
    // Hide environmental panels and map overlay for other individual participants (cha, ash, tin)
    document.querySelectorAll(".env-panel").forEach(el => el.classList.add("hidden"));
    document.getElementById("leaderboard-panel").classList.add("hidden");
    
    // Show individual panels
    document.getElementById("camper-activity-panel").classList.remove("hidden");
    document.getElementById("steps-panel").classList.remove("hidden");
    document.getElementById("monzo-panel").classList.remove("hidden");
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
      labels: [],
      datasets: [{
        label: "Campsite Temperature (°C) [Offline]",
        data: [],
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
      labels: [],
      datasets: [{
        label: "Noise Amplitude (dB) [Offline]",
        data: [],
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
  } else {
    tempChart.data.datasets[0].data = [];
    tempChart.data.labels = [];
    tempChart.update();
  }

  if (noiseHistory && noiseHistory.length > 0) {
    noiseChart.data.datasets[0].data = noiseHistory;
    noiseChart.update();
  } else {
    noiseChart.data.datasets[0].data = [];
    noiseChart.update();
  }
}

async function fetchTelemetry() {
  if (!hasUserParam) return;

  const warningDiv = document.getElementById("connection-status-warning");
  const syncStatusSpan = document.getElementById("syncStatus");

  try {
    // 1. Fetch aggregates
    const resAggs = await fetch(`${API_BASE}/beer?user_id=${activeUser}&_=${Date.now()}`);
    if (!resAggs.ok) throw new Error("Aggregates fetch failure");
    const data = await resAggs.json();

    // Update Counters
    document.getElementById("total-drinks-counter").textContent = data.total_drinks || 0;
    document.getElementById("beer-drinks-counter").textContent = `Beer subsets: ${data.beer_drinks || 0}`;

    // Update Drinks Breakdown (FR-004 / FR-005 / FR-006)
    updateDrinksBreakdown(data.categories || {});

    // Update Leaderboard if Combined view
    if (activeUser === "combined") {
      updateLeaderboard(data.leaderboard || []);
      updateStepsLeaderboard(data.steps_leaderboard || []);
    }

    if (activeUser !== "combined") {
      // 2. Fetch history (steps & temperature & GPS location history map)
      const resHistory = await fetch(`${API_BASE}/history?user_id=${activeUser}&_=${Date.now()}`);
      if (resHistory.ok) {
        const historyData = await resHistory.json();
        document.getElementById("stepsVal").textContent = Number(historyData.cumulative_steps || 0).toLocaleString();
        document.getElementById("distVal").textContent = `Distance: ${Number(historyData.cumulative_distance_km || 0).toFixed(2)} km`;

        const locationHistory = historyData.location_history || [];

        if (activeUser === "hvy") {
          // Temperature and noise sensors are currently offline/not set up yet
          updateCharts([], []);
          drawLocationTrail(locationHistory);
        }
      }

      // 3. Fetch status text (StatusLatestResponse)
      const resStatus = await fetch(`${API_BASE}/beer?event=status&type=latest&user_id=${activeUser}&_=${Date.now()}`);
      if (resStatus.ok) {
        const statusData = await resStatus.json();
        const statusText = statusData.status || "Chilling";
        const badgeEl = document.getElementById("camper-status-badge");
        if (badgeEl) {
          badgeEl.textContent = statusText;
        }

        // Resolve status photo file path dynamically using keyword matching (009/011 alignment)
        const resolvedFileKeyword = resolveStatusImage(statusText);
        loadStatusImage(resolvedFileKeyword);
      }

      // 4. Fetch Monzo expenses
      const resExpenses = await fetch(`${API_BASE}/monzo?user_id=${activeUser}&_=${Date.now()}`);
      if (resExpenses.ok) {
        const expenseData = await resExpenses.json();
        document.getElementById("expenditure-counter").textContent = `£${Number(expenseData.total_expenditure_gbp || 0).toFixed(2)}`;
      }
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
        <span style="color: #ff780a;">${user.total_drinks} total drinks</span>
      </div>
    `;
  });
}

function updateStepsLeaderboard(stepsLeaderboard) {
  const listEl = document.getElementById("steps-board-list") || document.getElementById("steps-leaderboard-list");
  if (!listEl) return;
  listEl.innerHTML = "";

  if (stepsLeaderboard.length === 0) {
    listEl.innerHTML = `<div class="has-text-grey has-text-centered p-3">No step telemetry available yet.</div>`;
    return;
  }

  stepsLeaderboard.forEach(user => {
    const fullName = USER_NAMES[user.user_id] || `${user.user_id.toUpperCase()}`;
    const stepsFormatted = Number(user.all_time_steps || 0).toLocaleString();
    listEl.innerHTML += `
      <div class="leaderboard-item">
        <span>${fullName}</span>
        <span style="color: #ff780a;">${stepsFormatted} steps</span>
      </div>
    `;
  });
}

function initializeMap() {
  const container = document.getElementById("map-container");
  if (!container || mapInstance) return;

  mapInstance = L.map('map-container', {
    center: [52.0411, -2.3784],
    zoom: 16,
    zoomControl: true
  });

  const emfTiles = L.tileLayer('https://map.emfcamp.org/tiles/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.emfcamp.org">EMF Camp</a>'
  });

  emfTiles.addTo(mapInstance);

  // Fallback to OSM tiles on load failure
  emfTiles.on('tileerror', function() {
    console.warn("EMF Camp tile server failed to load tile. Falling back to OpenStreetMap.");
    emfTiles.remove();
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(mapInstance);
  });

  mapLayersGroup = L.layerGroup().addTo(mapInstance);
}

// Draw dynamic coordinates path overlays onto static map background (FR-012)
function drawLocationTrail(locationHistory) {
  // Ensure map is initialized first
  initializeMap();
  if (!mapInstance || !mapLayersGroup) return;

  // Clear previous plotted trail
  mapLayersGroup.clearLayers();

  if (!locationHistory || locationHistory.length === 0) return;

  // Find the latest coordinate point (chronologically latest)
  let latestPoint = null;
  let maxTimeMs = -Infinity;

  locationHistory.forEach(pt => {
    const timeMs = pt.time ? Date.parse(pt.time) : 0;
    if (timeMs > maxTimeMs) {
      maxTimeMs = timeMs;
      latestPoint = pt;
    }
  });

  if (!latestPoint) return;

  // 3-hour delta filter relative to the latest point's timestamp
  const threeHoursInMs = 3 * 60 * 60 * 1000;
  const thresholdTime = maxTimeMs - threeHoursInMs;

  const filteredPoints = locationHistory.filter(pt => {
    const timeMs = pt.time ? Date.parse(pt.time) : 0;
    return timeMs >= thresholdTime;
  });

  if (filteredPoints.length === 0) return;

  // Map to Leaflet latlng format [lat, lng]
  const latlngs = filteredPoints.map(pt => [pt.lat, pt.lng]);

  // Draw the polyline path
  const polyline = L.polyline(latlngs, {
    color: '#ff780a',
    weight: 4,
    opacity: 0.9,
    lineJoin: 'round',
    lineCap: 'round'
  }).addTo(mapLayersGroup);

  // Plot markers for each coordinate check
  filteredPoints.forEach((pt, idx) => {
    const isLatest = (pt === latestPoint);
    const pointTime = pt.time ? new Date(pt.time) : null;
    const timeString = pointTime ? pointTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : "N/A";

    let popupContent = `<strong>Time</strong>: ${timeString}`;
    
    let marker;
    if (isLatest) {
      // Active head marker: large red pulsing circle marker
      marker = L.circleMarker([pt.lat, pt.lng], {
        radius: 8,
        fillColor: '#e02f44',
        color: '#ffffff',
        weight: 2,
        fillOpacity: 1
      }).addTo(mapLayersGroup);

      // Pulse aura ring
      L.circleMarker([pt.lat, pt.lng], {
        radius: 14,
        fillColor: '#e02f44',
        color: '#e02f44',
        weight: 1,
        opacity: 0.4,
        fillOpacity: 0.15
      }).addTo(mapLayersGroup);

      // Append cumulative user stats if available
      const stepsText = document.getElementById("stepsVal") ? document.getElementById("stepsVal").textContent : null;
      const distText = document.getElementById("distVal") ? document.getElementById("distVal").textContent : null;
      
      popupContent += `<br/><strong>Status</strong>: Latest Active Check-In`;
      if (stepsText) popupContent += `<br/><strong>Cumulative Steps</strong>: ${stepsText}`;
      if (distText) popupContent += `<br/><strong>Cumulative Distance</strong>: ${distText.replace("Distance: ", "")}`;
    } else {
      // Past trail breadcrumbs: small orange circle marker
      marker = L.circleMarker([pt.lat, pt.lng], {
        radius: 5,
        fillColor: '#ff780a',
        color: '#1f2226',
        weight: 1,
        fillOpacity: 0.9
      }).addTo(mapLayersGroup);
    }

    marker.bindPopup(popupContent);
  });

  // Fit map bounds to frame the trail nicely
  try {
    mapInstance.fitBounds(polyline.getBounds(), { padding: [30, 30] });
  } catch (e) {
    console.error("Leaflet fitBounds failed: ", e);
    mapInstance.setView([latestPoint.lat, latestPoint.lng], 16);
  }

  // Force map invalidation to correct size issues after container transitions
  setTimeout(() => {
    mapInstance.invalidateSize();
  }, 100);
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
  if (status.includes("drink") || status.includes("beer") || status.includes("pub") || status.includes("pint") || status.includes("beverage") || status.includes("drunk")) {
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

// Load status image by checking for .jpg first, then falling back to .png, and finally to normal.jpg
function loadStatusImage(resolvedFileKeyword) {
  const imgEl = document.getElementById("camper-status-image");
  if (!imgEl) return;

  const jpgSrc = `${activeUser}_status/${activeUser}_${resolvedFileKeyword}.jpg`;
  const pngSrc = `${activeUser}_status/${activeUser}_${resolvedFileKeyword}.png`;
  const fallbackSrc = `${activeUser}_status/${activeUser}_normal.jpg`;

  imgEl.onerror = function() {
    // If the .jpg version failed (even if it's the normal/fallback image), try the .png version
    if (this.src.endsWith(".jpg")) {
      this.src = pngSrc;
    } else if (this.src.endsWith(".png")) {
      // If the .png version also failed, fall back to the active user's standard normal status image (.jpg)
      this.src = fallbackSrc;
    } else {
      // Prevent infinite loops if both .jpg and .png of both keyword and fallback fail
      this.onerror = null;
      this.src = "hvy_status/hvy_normal.jpg";
    }
  };

  imgEl.src = jpgSrc;
}

// Render a detailed drinks breakdown on the public dashboard (FR-004 / FR-005 / FR-006)
function updateDrinksBreakdown(categories) {
  const listEl = document.getElementById("drinks-breakdown-list");
  if (!listEl) return;

  listEl.innerHTML = "";
  
  // Define emojis or display text map for beverage categories to make them visually pleasing!
  const emojiMap = {
    "Water": "💧",
    "Coffee": "☕",
    "Tea": "🍵",
    "Soft": "🥤",
    "ClubMate": "🧉",
    "Lager": "🍺",
    "IPA": "🍺",
    "Cider": "🍺",
    "Ale": "🍺",
    "Martini": "🍸",
    "G+T": "🍹",
    "Negroni": "🥃",
    "Port": "🍷",
    "BoxWine": "📦🍷",
    "BoxPerry": "📦🍐",
    "Stout": "🍺",
    "Porter": "🍺"
  };

  let hasBreakdown = false;

  // Filter and sort categories where count is strictly greater than 0 (count >= 1)
  const breakdownItems = Object.entries(categories)
    .filter(([name, count]) => {
      const countInt = parseInt(count, 10) || 0;
      // Filter out non-beverage or internal metadata keys (e.g. toilet visits, sync status, etc.)
      const isInternalMetadata = ["toilet_visits", "ToiletVisit", "Start", "Stop", "Reset", "ResetDay", "Pee", "Poo"].includes(name);
      return !isInternalMetadata && countInt >= 1;
    })
    .sort((a, b) => b[1] - a[1]); // Sort descending by consumed count for highest signal

  if (breakdownItems.length > 0) {
    breakdownItems.forEach(([name, count]) => {
      const emoji = emojiMap[name] || "🥤";
      const tagSpan = document.createElement("span");
      tagSpan.className = "tag is-dark has-text-weight-bold";
      tagSpan.style.border = "1px solid #ff780a";
      tagSpan.style.color = "#ff780a";
      tagSpan.textContent = `${name} ${emoji}: ${count}`;
      listEl.appendChild(tagSpan);
    });
    hasBreakdown = true;
  }

  if (!hasBreakdown) {
    listEl.innerHTML = `<span class="has-text-grey is-size-7">None logged yet</span>`;
  }
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
            this.src = 'hvy_status/hvy_normal.jpg';
          } else {
            this.src = '' + (window.activeUser || 'hvy') + '_status/' + (window.activeUser || 'hvy') + '_normal.jpg';
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

// Dynamic Google Analytics 4 (GA4) Tracking Compiler & Injector (FR-002 / FR-003 / FR-004)
function initGoogleAnalytics() {
  const config = window.EMF_CONFIG || {};
  const gaId = config.google_analytics_id;

  // Graceful opt-out and unconfigured placeholder gates (FR-004)
  if (!gaId || gaId === "G-XXXXXXXXXX" || !gaId.startsWith("G-")) {
    console.log("[ANALYTICS] Google Analytics Measurement ID is unconfigured or blank. Bypassing injection.");
    return;
  }

  console.log(`[ANALYTICS] Configured Measurement ID [${gaId}] detected. Compiling and injecting standard gtag.js site tags.`);

  // 1. Create and inject external gtag.js script node
  const externalScript = document.createElement("script");
  externalScript.async = true;
  externalScript.src = `https://www.googletagmanager.com/gtag/js?id=${gaId}`;
  document.head.appendChild(externalScript);

  // 2. Initialize global dataLayer and gtag configurations
  window.dataLayer = window.dataLayer || [];
  window.gtag = function() {
    window.dataLayer.push(arguments);
  };
  
  window.gtag('js', new Date());
  window.gtag('config', gaId);
}

// App Start
initUI();
if (hasUserParam) {
  fetchTelemetry();
  scheduleRefresh();
}
