# Data Model: Comprehensive Test Coverage

Since this feature implements a testing and validation framework rather than database entities, there are no physical AWS DynamoDB single-table schema changes. Instead, we define the standard **Test Assertion Structures** and **Coverage Target Objects** that the test runners analyze.

## 1. Test Assertion Entities

### Entity: `AssertionResult`
Represents an individual unit, integration, or browser DOM test verification outcome.

#### Fields
- `test_id` (string): Unique identifier for the test case (e.g. `TEST-BACKEND-001`).
- `category` (string): One of `unit`, `integration`, or `browser`.
- `description` (string): Description of the feature under verification.
- `passed` (boolean): `true` if assertions were met, `false` otherwise.
- `error` (string, optional): Detailed stack trace or mismatch summary if failed.

---

### Entity: `CoverageMetrics`
Represents code coverage statistics returned by the Python code coverage execution wrapper (`coverage.py`).

#### Fields
- `file_path` (string): Path to the python source file (e.g. `backend/sim_server.py`).
- `percent_covered` (float): Percentage of lines executed during the test runs.
- `missing_lines` (list of integers): Line numbers that were not evaluated.

---

## 2. Test Execution Flow

```text
+-----------------------+
|  run_tests.py Runner  |
+-----------------------+
           |
           +-----------------------------+
           |                             |
           v                             v
+-----------------------+     +-----------------------+
|  Backend Pytest/Cov   |     | Browser Test Suite    |
|  (sim_server.py 80%+) |     | (test_suite.html DOM) |
|  (core logic 100%)    |     +-----------------------+
+-----------------------+
```
