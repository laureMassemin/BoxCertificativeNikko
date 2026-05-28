# Authentication — How to run

## Requirements

Make sure you are in the `backend/` folder with the virtual environment activated.

```bash
cd backend
source venv/bin/activate
```

## Install dependencies

```bash
pip install fastapi uvicorn sqlalchemy "python-jose[cryptography]" "passlib[bcrypt]" bcrypt==4.0.1 geopy
```

## Start the server

```bash
uvicorn main:app --reload
```

The server runs on **http://localhost:8000**

## Test the routes

Go to **http://localhost:8000/docs** and test:

- **POST /register** — create an account

```json
{ "username": "hubert", "password": "1234" }
```

- **POST /login** — log in and get a token

```json
{ "username": "hubert", "password": "1234" }
```
