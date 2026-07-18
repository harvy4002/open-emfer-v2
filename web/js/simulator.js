/**
 * web/js/simulator.js
 * JavaScript Controller for the web-based Interactive Trigger Playground.
 */

const API_BASE = "http://localhost:3000";
const AUTH_KEY = "mock-super-secret-key";

function logToConsole(method, path, body, status, resJson) {
  const consoleBox = document.getElementById("consoleBox");
  const timestamp = new Date().toISOString();
  
  let logHtml = `<div style="border-bottom: 1px dashed #2c2f33; padding-bottom: 0.5rem; margin-top: 0.5rem;">`;
  logHtml += `<span style="color: #ff780a;">[${timestamp}]</span> `;
  logHtml += `<span style="color: #39ff14; font-weight: bold;">>> ${method} ${path}</span> `;
  logHtml += `<span style="color: cyan;">(Status: ${status})</span><br/>`;
  logHtml += `<strong>Request Body:</strong> <pre style="background: transparent; color: #d8d9da; padding: 0.2rem; font-size: 0.85rem;">${JSON.stringify(body, null, 2)}</pre>`;
  logHtml += `<strong>Response Body:</strong> <pre style="background: transparent; color: #ff780a; padding: 0.2rem; font-size: 0.85rem;">${JSON.stringify(resJson, null, 2)}</pre>`;
  logHtml += `</div>`;
  
  consoleBox.innerHTML += logHtml;
  consoleBox.scrollTop = consoleBox.scrollHeight;
}

async function sendSimRequest(path, payload) {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": AUTH_KEY
      },
      body: JSON.stringify(payload)
    });
    
    const status = response.status;
    const resJson = await response.json();
    logToConsole("POST", path, payload, status, resJson);
  } catch (error) {
    console.error(error);
    logToConsole("POST", path, payload, "FETCH_ERROR", { error: error.message });
  }
}

function injectT1000() {
  const user = document.getElementById("simUser").value || "ali";
  const lat = parseFloat(document.getElementById("t1000Lat").value);
  const lng = parseFloat(document.getElementById("t1000Lng").value);
  const temp = parseFloat(document.getElementById("t1000Temp").value);
  const light = parseInt(document.getElementById("t1000Light").value);

  const payload = {
    user_id: user,
    device_id: "eui-70b3d57ed0051111",
    timestamp: new Date().toISOString(),
    latitude: isNaN(lat) ? null : lat,
    longitude: isNaN(lng) ? null : lng,
    temperature: temp,
    light: light
  };

  sendSimRequest("/sensecap", payload);
}

function injectBrowan() {
  const user = document.getElementById("simUser").value || "ali";
  const db = parseFloat(document.getElementById("browanDb").value);

  const payload = {
    user_id: user,
    device_id: "eui-70b3d57ed0062222",
    timestamp: new Date().toISOString(),
    sound_level: db
  };

  sendSimRequest("/browan", payload);
}

function injectExpenditure() {
  const amount = parseFloat(document.getElementById("expenditureAmount").value);
  const merchant = document.getElementById("expenditureDesc").value || "EMF Camp Bar";

  const payload = {
    amount: amount,
    merchant: merchant
  };

  sendSimRequest("/expenditure", payload);
}

async function inject3HourTrail() {
  const user = document.getElementById("simUser").value || "ali";
  
  // Define a preset of 4 sequential coordinate points winding around Eastnor Castle (campsite area)
  // Point 1: 4 hours ago (should be filtered out of the 3h map view)
  // Point 2: 2.5 hours ago (should render on map)
  // Point 3: 1 hour ago (should render on map)
  // Point 4: Now (should render as distinguished active head)
  const route = [
    { offsetMins: 240, lat: 52.0401, lng: -2.3760, temp: 21.0, light: 100 },
    { offsetMins: 150, lat: 52.0411, lng: -2.3780, temp: 22.0, light: 150 },
    { offsetMins: 60,  lat: 52.0418, lng: -2.3790, temp: 23.0, light: 180 },
    { offsetMins: 0,   lat: 52.0425, lng: -2.3800, temp: 22.5, light: 200 }
  ];

  const nowMs = Date.now();

  for (const pt of route) {
    const timestamp = new Date(nowMs - pt.offsetMins * 60 * 1000).toISOString();
    const payload = {
      user_id: user,
      device_id: "eui-70b3d57ed0051111",
      timestamp: timestamp,
      latitude: pt.lat,
      longitude: pt.lng,
      temperature: pt.temp,
      light: pt.light
    };
    
    // Use sequential await to preserve order in local DB storage
    await sendSimRequest("/sensecap", payload);
  }
}
