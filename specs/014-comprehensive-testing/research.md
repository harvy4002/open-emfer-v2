# Research Report: Comprehensive Test Coverage

This report outlines the technical solutions, framework selections, and execution patterns for establishing unit, integration, and browser tests across the project.

## 1. Browser/E2E DOM Testing Strategy

### Decision
Build a lightweight, zero-dependency browser-native testing suite at `web/test_suite.html`.

### Rationale
- **Compliance with Principle VII (Serverless Cost & Simplicity)**: The user-facing dashboard is a responsive static web app. Introducing heavy Node.js frameworks (Jest, Playwright, Puppeteer) would require initializing `package.json`, installing massive `node_modules`, and adding complex compiler pipelines.
- **Zero Configuration & Instant Feedback**: A single, clean `web/test_suite.html` can load Leaflet and Chart.js, mock the browser-native `fetch()` API to return custom telemetry JSON streams, mount a sandboxed version of the dashboard controls, simulate clicks, and run vanilla JS assertion blocks, outputting a clear visual pass/fail dashboard in any browser (mobile or desktop).

### Alternatives Considered
- **Python Playwright (Headless)**: Playwright provides real headless browser interactions. However, it requires installing Node binaries and system-level system browser webdrivers, which complicates local setup in some platforms. It is kept as a potential upstream CI stage, but browser-native standalone tests are preferred for fast local developer feedback loops (Principle VIII).
- **Jest/Puppeteer (Node.js)**: Requires npm package setup, which violates serverless static frontend simplicity guidelines. Rejected.

---

## 2. Backend Coverage Tracking & Verification

### Decision
Utilize the standard python library `unittest` or standard `pytest` toolchain alongside `coverage.py` (`pytest-cov`) to verify backend simulation coverage.

### Rationale
- **Target Metrics (Q2 Selection)**: 
  - **100% Coverage** on critical core logic file primitives (such as step computation math, Haversine coordinates delta calculation, and event chronological state playback reconstruction).
  - **80%+ Coverage** on overall handler structures (routing, content-type mapping, local database reading/writing).
- **Lightweight Tooling**: Complying with Principle II, we avoid heavy frameworks and leverage `coverage.py` to produce clean color-coded coverage summaries inside the local sandbox.

---

## 3. Automation Runner Script

### Decision
Create a unified python wrapper test runner script `backend/run_tests.py` that starts the local server, runs python unit/integration checks with code coverage statistics, triggers browser DOM test coverage, and aggregates exit codes cleanly.

### Rationale
- **Compliance with Principle VIII (Fast Feedback Loop)**: Gives developers a one-click validation command to execute the entire testing matrix in under 3.0 seconds, returning an exit code of `0` on success and `1` on failure for deployment gates.
