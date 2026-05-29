# Technical Documentation — Travel Planner

## 1. System Architecture

The application follows a **client-server architecture** with a clear separation between frontend and backend.

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Vue 3)                     │
│  Browser → http://localhost:5173                        │
│                                                          │
│  LoginView  TripView  ToursView  SharedView  MyTrips    │
│                    ↕ HTTP / REST                         │
├─────────────────────────────────────────────────────────┤
│                   Backend (FastAPI)                      │
│  API → http://localhost:8000                            │
│                                                          │
│  api.py        algorithm.py    models.py   database.py  │
│  (routes)      (algorithms)    (schemas)   (SQLite)     │
│                    ↕ SQLAlchemy ORM                      │
├─────────────────────────────────────────────────────────┤
│               Database (SQLite — travel.db)              │
│  users  │  tours  │  places  │  hotels                  │
└─────────────────────────────────────────────────────────┘
```

### File structure

```
BoxCertificativeNikko/
├── README.md
├── docs/
│   ├── technical_documentation.md
│   ├── test_protocol.md
│   └── user_manual.md
├── backend/
│   ├── main.py           # Server entry point, CORS config
│   ├── api.py            # All FastAPI routes
│   ├── algorithm.py      # Tour optimization algorithms
│   ├── models.py         # SQLAlchemy models + Pydantic schemas
│   ├── database.py       # SQLite connection and session
│   ├── requirements.txt
│   └── docs/             # Auto-generated pdoc documentation
└── frontend/
    └── src/
        ├── main.ts
        ├── router.ts
        ├── api.ts
        ├── App.vue
        └── views/
            ├── LoginView.vue
            ├── RegisterView.vue
            ├── TripView.vue
            ├── ToursView.vue
            ├── SharedView.vue
            └── MyTripsView.vue
```

---

## 2. Technology Choices

### Backend — Python + FastAPI

**Why Python?**
The core requirement of this project is the implementation of a graph optimization algorithm (TSP variant). Python provides native mathematical libraries (`math`, `radians`, `acos`) that make distance calculations clear and concise. The algorithm logic is readable and easy to document.

**Why FastAPI?**

- Automatic Swagger documentation at `/docs` — no extra work required
- Pydantic integration for request validation
- Lightweight and fast for a 2-day project
- Simple CORS middleware configuration

**Alternative considered:** Flask — simpler but lacks automatic validation and documentation generation.

### Database — SQLite

**Why SQLite?**

- Zero configuration — a single `.db` file
- No external database server required
- Sufficient for the scale of this project
- Integrated with SQLAlchemy

**Alternative considered:** PostgreSQL — more powerful but requires installation and configuration overhead not justified here.

### Frontend — Vue 3 + TypeScript

**Why Vue 3?**

- Composition API provides clean, modular component logic
- `<script setup>` syntax reduces boilerplate
- Vue Router handles SPA navigation with route guards
- Reactivity system (`ref`, `watch`) ideal for dynamic map updates

**Why TypeScript?**

- Type safety catches errors at compile time
- Interface definitions (`Place`, `Trip`, `Hotel`) document the data structures

**Why Leaflet.js?**

- Free, open-source map library
- Works with OpenStreetMap tiles — no API key required
- Simple API for markers and polylines

### Geocoding — Nominatim (OpenStreetMap)

**Why Nominatim?**

- Free with no API key required
- Returns structured geographic data (lat/lon)
- Sufficient precision for city-level searches

**Alternative considered:** Google Maps API — more accurate but requires billing configuration.

---

## 3. Subject Interpretations

### Tour definition

A tour visits all selected places exactly once and returns to the starting point. The total distance includes the return leg.

### Distance formula

As specified in the subject, the great-circle distance is computed using:

```
D(Va, Vb) = R_earth × arccos(sin(lat_a) × sin(lat_b) + cos(lat_a) × cos(lat_b) × cos(lon_b − lon_a))
```

Where coordinates are expressed in radians, R_earth = 6378.197 km, π = 3.141592.

### Sharing

- **Public**: accessible via share link without authentication
- **Private**: accessible via share link only if the user is authenticated

The share link uses a UUID token (not the database ID) to prevent enumeration attacks.

### Multiple results

Each generated tour is saved to the database and accessible from the "My Trips" page. Users can generate and keep multiple tours.

---

## 4. Algorithm Description

### Standard Tour — Nearest Neighbor + 2-opt

**Step 1: Distance matrix**
Pre-compute all pairwise distances between places to avoid redundant calculations.

**Step 2: Nearest Neighbor heuristic**
Starting from place 0, greedily visit the closest unvisited place at each step. This produces a valid but suboptimal tour in O(n²) time.

**Step 3: 2-opt optimization**
Iteratively improve the tour by reversing segments between indices i and j. If reversing a segment reduces the total distance, apply the swap. Repeat until no improvement is found.

```
Example:
Initial: A → C → B → D → A  (distance: 1500 km)
After 2-opt: A → B → C → D → A  (distance: 1200 km)
```

**Complexity:** O(n²) per iteration, typically converges in a few passes.

### Hotel Tour — Geographic Clustering + TSP

**Step 1: Clustering**
Group places by geographic proximity using an adaptive distance threshold based on the median pairwise distance.

**Step 2: Hotel selection**
For each cluster, select the geographically central place as the "hotel" — the place that minimizes the average distance to all other places in the cluster.

**Step 3: Inter-hotel TSP**
Apply Nearest Neighbor + 2-opt on the hotels to determine the optimal order of hotel visits.

**Step 4: Intra-group routing**
For each hotel, calculate the round-trip distance to visit all places in its cluster.

**Total distance = inter-hotel distance + sum of intra-group distances**

---

## 5. Security

- Passwords are hashed with **bcrypt** before storage — never stored in plain text
- Authentication uses **JWT tokens** (HS256 algorithm) — the token contains the user ID
- Route guards on the frontend redirect unauthenticated users to the login page
- The "My Trips" endpoint verifies that the JWT token belongs to the requesting user
- Share tokens use UUID v4 — non-guessable, preventing enumeration

---

## 6. Installation and Setup

### Prerequisites

- Python 3.9+
- Node.js 18+

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy "python-jose[cryptography]" "passlib[bcrypt]" bcrypt==4.0.1 geopy pdoc
uvicorn main:app --reload
```

API available at: `http://localhost:8000`  
Swagger docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App available at: `http://localhost:5173`

### Generate technical documentation

```bash
cd backend
source venv/bin/activate
pdoc api.py algorithm.py models.py database.py --docformat google --output-dir docs/
```

Open `backend/docs/api.html` in your browser.
