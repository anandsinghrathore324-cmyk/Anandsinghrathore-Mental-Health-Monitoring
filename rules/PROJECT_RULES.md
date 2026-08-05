# AIRA Project Architecture Rules

This document defines the foundational architectural invariants and system design rules that all contributors must follow.

---

## 1. Top-Level Folder Structure
The repository strictly consists of 5 top-level functional directories:
* **`docs/`**: All technical specifications, audit reports, and viva evaluation materials.
* **`frontend/`**: All client-side UI, styles, interactions, and assets.
* **`backend/`**: Flask API server, database layer, machine learning models, and automated test suite.
* **`rules/`**: Engineering guidelines, coding standards, and security policies.
* **`tools/`**: Developer automation utilities and tooling scripts.

No ad-hoc files or scratch folders should be placed in the project root.

---

## 2. Backend Architectural Principles
1. **Blueprint Modularization**: Every functional domain must be encapsulated within its own Flask Blueprint registered under the `/api` prefix in `backend/app.py`.
2. **Fail-Fast Database Mode**: Production environments (`RENDER=true` or `FLASK_ENV=production`) must immediately fail fast if MongoDB connection fails. In-memory mock databases (`mongomock`) are strictly prohibited in production.
3. **In-Process ML Inference**: Machine learning inference must run directly in-process via `PredictionService`. Do not spawn unmanaged microservice ports (e.g. 5001/5002).
4. **Transparent Model Calibration**: Models must provide calibrated probability outputs. Fallbacks (e.g. lexical keyword heuristics) must be explicitly flagged and logged without misleading accuracy claims.

---

## 4. Geolocation & External API Integration Rules
1. **Live Google Places API Protocol**: Specialist queries must prioritize live Google Places API (New) endpoints (`https://places.googleapis.com/v1/places:searchText`) via `GooglePlacesService`. Hardcoded coordinate dictionary lookups are strictly prohibited.
2. **Proximity & Distance Filtering**: All nearby specialist queries must calculate real-time spatial distances using Haversine trigonometric equations. Fallback results must be strictly distance-constrained (`<= 100 km`) to prevent geographic leakage (e.g. distant cities).
3. **HTML5 Browser GPS Integration**: Client location resolution must support browser HTML5 Geolocation (`navigator.geolocation`) with reverse-geocoding to detect user coordinates and city automatically on page load.
4. **Dynamic Avatar Generation**: Specialist avatars must be dynamically generated via initial-based SVG services (`ui-avatars.com`) with medical styling rather than generic or unverified stock photos.
5. **Full Dynamic Fallback**: In the event of API quota limits (HTTP 429) or network failure, the system must seamlessly fall back to MongoDB seeded records while enforcing local suburb matching (e.g. Sanganer/Mansarovar mapped to Jaipur region).

