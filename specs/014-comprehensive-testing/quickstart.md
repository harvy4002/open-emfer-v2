# Quickstart Guide: Comprehensive Test Coverage

This guide explains how to locally trigger and validate the complete testing matrix.

## 1. Prerequisites
- **Python**: Ensure `coverage` is installed:
  ```bash
  pip install coverage pytest pytest-cov
  ```

---

## 2. Running Backend Tests & Code Coverage
To trigger the python unit/integration tests and check code coverage:

```bash
# 1. Navigate to the backend directory (or run from root)
coverage run -m pytest backend/

# 2. View the coverage report in the terminal
coverage report -m
```

Verify that:
- `backend/sim_server.py` achieves $\ge$ 80% coverage.
- Mathematical helper libraries (Haversine calculations) achieve 100% coverage.

---

## 3. Running Browser DOM Tests
1. Load `web/test_suite.html` directly in any web browser.
2. The page executes the test suite instantly on load and renders a color-coded test report card:
   - Green items represent passing assertions (Leaflet initialized, Charts mounted, Simulator trigger bound).
   - Red items identify failing selectors or JavaScript exceptions.
