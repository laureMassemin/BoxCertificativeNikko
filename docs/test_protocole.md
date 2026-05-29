# Test Protocol — Travel Planner

## 1. Unit Tests (pytest)

Unit tests are located in `backend/tests/test_app.py`.

### Run tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

### Test cases

#### Distance calculation

```python
def test_distance_paris_lyon():
    """Distance between Paris and Lyon should be approximately 392 km."""
    from algorithm import distance
    paris = (48.8566, 2.3522)
    lyon = (45.764, 4.8357)
    result = distance(paris, lyon)
    assert 380 < result < 410

def test_distance_same_point():
    """Distance between the same point should be 0."""
    from algorithm import distance
    paris = (48.8566, 2.3522)
    assert distance(paris, paris) == 0.0
```

#### Tour length

```python
def test_tour_length_triangle():
    """Tour length should be the sum of all segment distances including return."""
    from algorithm import build_distance_matrix, tour_length
    from models import PlaceSchema
    places = [
        PlaceSchema(name="Paris", lat=48.8566, lon=2.3522),
        PlaceSchema(name="Lyon", lat=45.764, lon=4.8357),
        PlaceSchema(name="Marseille", lat=43.2965, lon=5.3698),
    ]
    dm = build_distance_matrix(places)
    length = tour_length([0, 1, 2], dm)
    assert length > 0
    assert isinstance(length, float)
```

#### Nearest neighbor tour

```python
def test_nearest_neighbor_returns_all_places():
    """Nearest neighbor tour must visit all places exactly once."""
    from algorithm import build_distance_matrix, nearest_neighbor_tour
    from models import PlaceSchema
    places = [
        PlaceSchema(name="Paris", lat=48.8566, lon=2.3522),
        PlaceSchema(name="Lyon", lat=45.764, lon=4.8357),
        PlaceSchema(name="Marseille", lat=43.2965, lon=5.3698),
        PlaceSchema(name="Bordeaux", lat=44.8378, lon=-0.5792),
    ]
    dm = build_distance_matrix(places)
    tour = nearest_neighbor_tour(dm)
    assert len(tour) == 4
    assert sorted(tour) == [0, 1, 2, 3]
```

#### 2-opt optimization

```python
def test_two_opt_improves_or_equals():
    """2-opt should never produce a longer tour than the initial tour."""
    from algorithm import build_distance_matrix, nearest_neighbor_tour, two_opt_swap, tour_length
    from models import PlaceSchema
    places = [
        PlaceSchema(name="Paris", lat=48.8566, lon=2.3522),
        PlaceSchema(name="Marseille", lat=43.2965, lon=5.3698),
        PlaceSchema(name="Lyon", lat=45.764, lon=4.8357),
        PlaceSchema(name="Strasbourg", lat=48.5734, lon=7.7521),
    ]
    dm = build_distance_matrix(places)
    initial = nearest_neighbor_tour(dm)
    optimized = two_opt_swap(initial, dm)
    assert tour_length(optimized, dm) <= tour_length(initial, dm)
```

#### plan_tour returns valid result

```python
def test_plan_tour_output():
    """plan_tour should return all places in a valid order with a positive distance."""
    from algorithm import plan_tour
    from models import PlaceSchema
    places = [
        PlaceSchema(name="Paris", lat=48.8566, lon=2.3522),
        PlaceSchema(name="Lyon", lat=45.764, lon=4.8357),
        PlaceSchema(name="Marseille", lat=43.2965, lon=5.3698),
    ]
    result = plan_tour(places)
    assert "tour" in result
    assert "length" in result
    assert len(result["tour"]) == 3
    assert result["length"] > 0
```

---

## 2. API Integration Tests

### Test register endpoint

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'
# Expected: {"message": "User created successfully"}
```

### Test login endpoint

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'
# Expected: {"token": "eyJ...", "username": "testuser"}
```

### Test duplicate username

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "other"}'
# Expected: 400 {"detail": "Username already taken"}
```

### Test wrong password

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "wrongpass"}'
# Expected: 401 {"detail": "Wrong password"}
```

### Test place search

```bash
curl "http://localhost:8000/places/search?name=Paris"
# Expected: list of places with name, lat, lon
```

### Test tour generation

```bash
curl -X POST "http://localhost:8000/tours/generate?username=testuser" \
  -H "Content-Type: application/json" \
  -d '{
    "is_public": true,
    "places": [
      {"name": "Paris", "lat": 48.8566, "lon": 2.3522},
      {"name": "Lyon", "lat": 45.764, "lon": 4.8357},
      {"name": "Marseille", "lat": 43.2965, "lon": 5.3698}
    ]
  }'
# Expected: {"id": 1, "share_token": "uuid..."}
```

---

## 3. Manual Test Protocol

| Test               | Steps                                               | Expected result                                         |
| ------------------ | --------------------------------------------------- | ------------------------------------------------------- |
| Register           | Go to `/register`, fill username + password, submit | Redirected to `/login`                                  |
| Login              | Go to `/login`, fill credentials, submit            | Redirected to `/trip`, nav shows username               |
| Duplicate username | Register with an existing username                  | Error "Username already taken"                          |
| Wrong password     | Login with wrong password                           | Error "Wrong username or password"                      |
| Search city        | On `/trip`, type "Paris", click Search              | List of matching cities appears                         |
| Add city           | Click "Add to trip" on a result                     | City appears in trip list, marker on map                |
| Duplicate city     | Try to add the same city twice                      | City is not added twice                                 |
| Generate tour      | Add 3+ cities, click "Generate Optimal Route"       | Redirected to tour page with ordered cities and map     |
| Change order       | On tour page, click ↑ or ↓                          | City moves, distance updates                            |
| Share link         | Copy the share link, open in incognito              | Public tour: visible. Private tour: redirected to login |
| My Trips           | Click "My Trips" in nav                             | List of all created tours                               |
| View trip          | Click "View" on a trip                              | Tour details page opens                                 |
| Logout             | Click "Logout"                                      | Redirected to login, nav shows Login/Register           |
| Protected route    | Try to access `/trip` without login                 | Redirected to `/login`                                  |
