# YojanaMitra

YojanaMitra is an SIH 2026 MVP for transparent government-scheme matching, indicative finance estimates, and demonstration partner routing.

## Architecture

`Profile -> validation -> deterministic rule engine -> finance engine -> partner routing -> AI explanation`

**Gemini does not determine eligibility.** The backend rule engine returns `ELIGIBLE`, `NOT_ELIGIBLE`, or `UNKNOWN`; Gemini can only explain that completed output. The finance calculator and Haversine distance calculation are deterministic too.

## Stack

- Frontend: React, Vite, Tailwind CSS, React Router, Framer Motion, Lucide, Leaflet/OpenStreetMap, OSRM routing
- Backend: FastAPI, Pydantic, SQLite, SQLAlchemy
- Optional AI: Google Gemini through the backend only

## Run locally

From `D:\YojanaMitra SIH`:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
python -m uvicorn app.main:app --app-dir backend --reload --port 8000
```

In a second PowerShell window:

```powershell
cd "D:\YojanaMitra SIH\frontend"
npm install
npm run dev
```

Open `http://localhost:5173`. FastAPI documentation is at `http://127.0.0.1:8000/docs`.

## Gemini

Copy `.env.example` to `.env` and set `GEMINI_API_KEY`. ArthSetu uses `gemini-2.5-flash`, which is eligible for Google's free tier subject to its quota and regional availability. Without a key, the application remains fully functional and returns a deterministic fallback explanation. The API key never reaches the browser.

## Database and demo data

The partner locator requests driving geometry, distance, and duration from the public OSRM routing service when a partner is selected. If routing is unavailable, the map still shows the partner and labels the straight-line distance fallback; ETA is not estimated. Routes do not include live traffic. No routing API key or new package is required.

The SQLite file (`backend/yojanamitra.db`) is created and seeded on API startup with the requested tables: `users`, `schemes`, `partners`, `eligibility_rules`, and `demo_profiles`. There are three MVP schemes, 24 clearly-labelled `DEMO DATA` partners, and six demo scenarios:

1. Micro Finance Match
2. Term Loan Match
3. Education Loan
4. Rule Failure
5. Missing Information
6. Nearby Partner Routing

## Tests

```powershell
Push-Location backend
..\.venv\Scripts\python.exe -m pytest tests -q
Pop-Location
```

Tests cover all three scheme types, failed and missing rules, EMI math, distance calculation, and deterministic explanation fallback for a missing Gemini key or provider timeout. API endpoints include `/api/health`, `/api/schemes`, `/api/eligibility/check`, `/api/finance/calculate`, `/api/partners`, `/api/partners/nearby`, `/api/ai/explain`, and `/api/demo/profiles`. No endpoint was added or changed for routing; OSRM is called by the frontend.

## Limits and future work

This MVP uses transparent, indicative rules and synthetic partner records rather than a live government directory. OSRM route availability depends on its public demo service. Final eligibility, sanction, terms, and partner availability remain with the applicable authority or channel partner. Future work includes authenticated profiles, verified scheme feeds, multilingual explanations, and consented address geocoding.
