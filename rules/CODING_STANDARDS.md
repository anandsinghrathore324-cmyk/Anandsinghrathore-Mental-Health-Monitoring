# AIRA Coding Standards & Quality Guidelines

---

## 1. Python (Backend) Standards

1. **Python Version**: Target Python 3.10+ (Fully compatible with Python 3.12).
2. **Timezone Awareness**:
   * **NEVER** use `datetime.datetime.utcnow()`, which is deprecated in Python 3.12.
   * **ALWAYS** use timezone-aware UTC datetime:
     ```python
     from datetime import datetime, timezone
     now_utc = datetime.now(timezone.utc)
     ```
3. **Exception Safety & Logging**:
   * Always catch specific exceptions (`PyMongoError`, `ValueError`, `FileNotFoundError`) instead of silent bare `except:`.
   * Log meaningful contextual messages using the standard library `logging` module.
4. **Type Annotations & Documentation**:
   * All public methods and route handlers must include descriptive docstrings and type hints where appropriate.

---

## 2. JavaScript (Frontend) Standards

1. **Modern ECMAScript**:
   * Use ES6+ syntax (`const`, `let`, arrow functions, template literals, async/await).
   * Avoid global namespace pollution; scope functions to modules or dedicated state objects.
2. **Asynchronous Operations**:
   * Always wrap `fetch()` calls in `.catch()` or `try/catch` blocks.
   * Provide immediate visual loading feedback (`fa-spin`, disabled buttons) during network latency.
3. **DOM Manipulation & Geolocation**:
   * Prefer `textContent` over `innerHTML` when rendering user-supplied strings to prevent Cross-Site Scripting (XSS).
   * Geolocation requests (`navigator.geolocation.getCurrentPosition`) must include reverse-geocoding fallbacks and explicit timeout/accuracy settings (`timeout: 10000`, `enableHighAccuracy: true`).

---

## 3. Automated Testing Requirements

1. **Test Coverage**:
   * All new routes, services, and Google Places API integrations must include automated unit tests in `backend/tests/test_pytest_unit.py`.
   * Tests must run with `pytest` and maintain a 100% pass rate (175/175 tests passed) before deployment.

