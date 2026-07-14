# Test Contract: Comprehensive Test Coverage

This document outlines the contracts, input parameters, and output schemas for executing the test suites.

## 1. Unified Test Runner Interface

The unified test runner wrapper is run locally from the workspace.

- **Command**: `python backend/run_tests.py`
- **Output (Stdout)**:
  ```text
  ============================================================
  RUNNING SYSTEM TEST SUITE & COVERAGE CHECKS
  ============================================================
  
  [1/3] Backend Unit Tests ... PASSED
  [2/3] Backend Code Coverage:
        - backend/sim_server.py: 84.2% (Target: 80%+)  PASSED
        - core math/logic handlers: 100.0% (Target: 100%) PASSED
  [3/3] Browser-Native DOM Assertions ... PASSED
  
  ✓ ALL SESSIONS PASSED SUCCESSFULLY. EXIT CODE: 0
  ```

---

## 2. Browser-Native Test Runner Contract

The `web/test_suite.html` file renders a graphical browser-based test dashboard when loaded in any browser.

- **URL**: `http://localhost:3000/test_suite.html` (when simulator is running) or direct file load `web/test_suite.html`.
- **Mock DOM Bindings**:
  The test page injects a mocked DOM sandbox simulating `web/index.html` elements:
  - `<div id="map-container"></div>`
  - `<canvas id="temperature-chart-canvas"></canvas>`
  - `<span id="stepsVal"></span>`
- **Asserted DOM Properties**:
  - Leaflet instance `mapInstance` is successfully instantiated and is not `null`.
  - Leaflet `mapInstance.getCenter()` matches the default campsite center coordinate (`52.0411, -2.3784`).
  - Active pulsing head marker and breadcrumb markers are attached correctly.
  - Standard fetch intercepts respond with mocked tracking lists.
