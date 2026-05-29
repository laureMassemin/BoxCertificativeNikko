# User Manual — Travel Planner

## Overview

Travel Planner is a web application that generates optimized travel routes.
You can add cities, generate the optimal visiting order, save your trips, and share them with others.

---

## 1. Installation

### Requirements

- Python 3.9+
- Node.js 18+

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy "python-jose[cryptography]" "passlib[bcrypt]" bcrypt==4.0.1 geopy
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open your browser at **http://localhost:5173**

---

## 2. Create an account

1. Go to **http://localhost:5173/register**
2. Enter a username and password
3. Click **Register**
4. You are redirected to the login page

---

## 3. Log in

1. Go to **http://localhost:5173/login**
2. Enter your username and password
3. Click **Login**
4. You are redirected to the trip creation page

---

## 4. Create a trip

### Search for cities

1. On the **Create Trip** page, type a city name in the search bar (e.g. "Paris")
2. Click **Search**
3. A list of matching locations appears
4. Click **+ Add** to add a city to your trip

### Manage your city list

- Cities appear in a numbered list below the search bar
- A map shows all selected cities with markers
- Click **✕** on a city to remove it

### Set visibility

- Check **Make this trip public** if you want the trip to be accessible via link without login
- Leave unchecked for a private trip (requires login to access via link)

### Generate the route

- Once you have at least 2 cities, two buttons appear:
  - **Generate Optimal Route** — uses nearest neighbor + 2-opt algorithm
  - **Generate with Hotels** — uses geographic clustering with hotel stops
- Click one to generate the tour
- You are automatically redirected to the trip details page

---

## 5. View a trip

The trip details page shows:

- **Total distance** in km
- **Number of cities**
- **Visibility** (Public or Private)
- **Ordered list of cities** with coordinates
- **Hotel stops** (if generated with the hotel algorithm) — shown in red
- **Interactive map** with the full route

### Reorder cities

- Use the **↑** and **↓** buttons next to each city to change the order
- The total distance and map update automatically after each change

---

## 6. Share a trip

At the bottom of the trip page, you will find a **Share link**.

- Copy the link and send it to anyone
- **Public trip**: the recipient can view it without logging in
- **Private trip**: the recipient must log in first, then will be redirected back to the trip

---

## 7. My Trips

1. Click **My Trips** in the navigation bar
2. All your saved trips are listed with:
   - Number of cities
   - Total distance
   - Visibility (Public / Private)
3. Click **View** on any trip to open it

---

## 8. Log out

Click **Logout** in the navigation bar.  
You are redirected to the login page.  
Protected pages (Create Trip, My Trips) are no longer accessible without logging in again.

---

## 9. Troubleshooting

| Problem                              | Solution                                                                   |
| ------------------------------------ | -------------------------------------------------------------------------- |
| Backend not starting                 | Make sure the venv is activated: `source venv/bin/activate`                |
| Login fails after restarting backend | The database was reset — create a new account                              |
| City not found                       | Try a more specific name (e.g. "Paris, France" instead of "Paris")         |
| Map not loading                      | Check your internet connection — map tiles require network access          |
| Share link shows "Trip not found"    | The backend was restarted and the database was reset — regenerate the tour |
