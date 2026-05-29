# Travel Planner — How to run

A travel planning application built with **FastAPI** (Python) and **Vue 3** (TypeScript).  
It generates optimized tours using nearest neighbor + 2-opt algorithms, with optional hotel-based clustering.

---

## Requirements

- Python 3.9+
- Node.js 18+
- Git

---

## 1. Clone the repository

```bash
git clone https://github.com/laureMassemin/BoxCertificativeNikko.git
cd BoxCertificativeNikko
```

---

## 2. Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy "python-jose[cryptography]" "passlib[bcrypt]" bcrypt==4.0.1 geopy requests pdoc
```

Start the server:

```bash
uvicorn main:app --reload
```

The API runs on **http://localhost:8000**  
Interactive API docs available at **http://localhost:8000/docs**

---

## 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The app runs on **http://localhost:5173**

---

## 4. Test the API

Go to **http://localhost:8000/docs** and test:

- **POST /register** — create an account

```json
{ "username": "hubert", "password": "1234" }
```

- **POST /login** — log in and get a JWT token

```json
{ "username": "hubert", "password": "1234" }
```

- **POST /tours/generate** — generate an optimized tour
- **POST /tourswithhotels/generate** — generate a tour with hotel stops
- **GET /tours/{id}** — retrieve a tour by ID
- **GET /tours/share/{token}** — retrieve a tour by share token (public access)

---

## 5. Documentation

Generate or update the auto-generated API documentation:

```bash
cd backend
source venv/bin/activate
pdoc api.py algorithm.py models.py database.py --docformat google --output-dir docs/
```

Open `backend/docs/index.html` in your browser to view the full documentation.
Open `docs/technical_documentation.md`
Open `docs/test_protocole.md`
Open `docs/user_manual.md`

---
