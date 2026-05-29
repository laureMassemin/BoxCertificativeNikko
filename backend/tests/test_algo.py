import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithm import (
    distance,
    build_distance_matrix,
    nearest_neighbor_tour,
    tour_length,
    two_opt_swap,
    plan_tour,
    personalised_tour_length,
    best_nearest_neighbor_tour,
    compute_adaptive_threshold,
    cluster_places,
    find_central_place,
    calculate_intra_group_distance,
    plan_tour_with_hotels,
)
from models import PlaceSchema


# ---------------------------------------------------------------------------
# distance
# ---------------------------------------------------------------------------

def test_distance_to_self_is_zero():
    """
    Test that the distance from a point to itself is zero.
    """
    point = (35.6820172, 139.76216)
    assert distance(point, point) == 0


# ---------------------------------------------------------------------------
# build_distance_matrix
# ---------------------------------------------------------------------------

def test_distance_symmetry():
    """
    Test that the distance matrix is symmetric. Meaning that the distance from A to B is the same as from B to A.
    """
    places = [
        PlaceSchema(name="Tokyo",   lat=35.6820172, lon=139.76216),
        PlaceSchema(name="Osaka",   lat=34.6937378, lon=135.5021651),
        PlaceSchema(name="Sapporo", lat=43.062095,  lon=141.354376),
    ]
    m = build_distance_matrix(places)
    for i in range(len(places)):
        for j in range(len(places)):
            assert m[i][j] == m[j][i]


# ---------------------------------------------------------------------------
# nearest_neighbor_tour
# ---------------------------------------------------------------------------

def test_nn_visits_all_places():
    """
    Test that the fonction nearest neighbor visits all places.
    """
    places = [
        PlaceSchema(name="Tokyo",   lat=35.6820172, lon=139.76216),
        PlaceSchema(name="Osaka",   lat=34.6937378, lon=135.5021651),
        PlaceSchema(name="Sapporo", lat=43.062095,  lon=141.354376),
    ]
    m = build_distance_matrix(places)
    tour = nearest_neighbor_tour(m)
    assert set(tour) == set(range(len(places)))


# ---------------------------------------------------------------------------
# tour_length
# ---------------------------------------------------------------------------

def test_tour_length_includes_return_to_start():
    """
    Test that the tour length calculation includes the return trip to the starting point.
    """
    matrix = [
        [0, 10, 20],
        [10, 0, 30],
        [20, 30, 0],
    ]
    tour = [0, 1, 2]
    assert tour_length(tour, matrix) == 60


# ---------------------------------------------------------------------------
# two_opt_swap
# ---------------------------------------------------------------------------

def test_2opt_improves_a_crossed_tour():
    """
    Test that the fonction 2-opt can improve a tour with a crossing.
    """
    places = [
        PlaceSchema(name="A", lat=0.0, lon=0.0),
        PlaceSchema(name="B", lat=0.0, lon=1.0),
        PlaceSchema(name="C", lat=1.0, lon=1.0),
        PlaceSchema(name="D", lat=1.0, lon=0.0),
    ]
    matrix = build_distance_matrix(places)
    bad_tour = [0, 2, 1, 3]
    fixed = two_opt_swap(bad_tour, matrix)
    assert tour_length(fixed, matrix) < tour_length(bad_tour, matrix)


# ---------------------------------------------------------------------------
# plan_tour
# ---------------------------------------------------------------------------

def test_plan_tour_returns_correct_format():
    """
    Test that the fonction plan_tour returns what is expected in the models.
    """
    places = [
        PlaceSchema(name="Tokyo",   lat=35.6820172, lon=139.76216),
        PlaceSchema(name="Kyoto",   lat=34.9946315, lon=135.7344318),
        PlaceSchema(name="Osaka",   lat=34.6937,    lon=135.5023),
        PlaceSchema(name="Sapporo", lat=43.0618,    lon=141.3545),
    ]
    result = plan_tour(places)
    assert "tour" in result
    assert "length" in result
    assert len(result["tour"]) == len(places)
    assert result["length"] > 0


# ---------------------------------------------------------------------------
# personalised_tour_length
# ---------------------------------------------------------------------------

def test_personalised_tour_length_includes_return():
    """
    Test that the personalised tour length calculation includes the return trip to the starting point.
    """
    places = [
        PlaceSchema(name="A", lat=0.0, lon=0.0),
        PlaceSchema(name="B", lat=0.0, lon=1.0),
        PlaceSchema(name="C", lat=0.0, lon=2.0),
    ]
    length = personalised_tour_length(places)
    assert length > 0


def test_personalised_tour_length_single_place():
    """
    Test that the personalised tour length for a single place is 0.
    """
    places = [PlaceSchema(name="Paris", lat=48.8566, lon=2.3522)]
    assert personalised_tour_length(places) == 0


def test_personalised_tour_length_two_places():
    """
    Test that the personalised tour length for two places is twice the distance between them.
    """
    places = [
        PlaceSchema(name="Paris", lat=48.8566, lon=2.3522),
        PlaceSchema(name="Lyon",  lat=45.7640, lon=4.8357),
    ]
    length = personalised_tour_length(places)
    assert length > 0
    d = distance((48.8566, 2.3522), (45.7640, 4.8357))
    assert abs(length - 2 * d) < 1e-9


# ---------------------------------------------------------------------------
# best_nearest_neighbor_tour
# ---------------------------------------------------------------------------

def test_best_nn_visits_all_places():
    """
    Test that the best nearest neighbor tour visits all places.
    """
    places = [
        PlaceSchema(name="Tokyo",   lat=35.6820, lon=139.7621),
        PlaceSchema(name="Osaka",   lat=34.6937, lon=135.5023),
        PlaceSchema(name="Sapporo", lat=43.0618, lon=141.3545),
        PlaceSchema(name="Kyoto",   lat=34.9946, lon=135.7344),
    ]
    matrix = build_distance_matrix(places)
    tour = best_nearest_neighbor_tour(matrix)
    assert set(tour) == set(range(len(places)))


def test_best_nn_is_at_least_as_good_as_single_start():
    """
    Test that the best nearest neighbor tour is at least as good as the tour starting from the first place.
    """
    places = [
        PlaceSchema(name="A", lat=0.0, lon=0.0),
        PlaceSchema(name="B", lat=1.0, lon=0.0),
        PlaceSchema(name="C", lat=1.0, lon=1.0),
        PlaceSchema(name="D", lat=0.0, lon=1.0),
        PlaceSchema(name="E", lat=0.5, lon=0.5),
    ]
    matrix = build_distance_matrix(places)
    best = best_nearest_neighbor_tour(matrix)
    single = nearest_neighbor_tour(matrix, start=0)
    assert tour_length(best, matrix) <= tour_length(single, matrix)


# ---------------------------------------------------------------------------
# compute_adaptive_threshold
# ---------------------------------------------------------------------------

def test_adaptive_threshold_single_place_is_zero():
    """
    Test that the adaptive threshold for a single place is 0.
    """
    places = [PlaceSchema(name="Paris", lat=48.8566, lon=2.3522)]
    assert compute_adaptive_threshold(places) == 0


def test_adaptive_threshold_is_positive():
    """
    Test that the adaptive threshold is strictly positive for multiple distant places.
    """
    places = [
        PlaceSchema(name="Paris", lat=48.8566, lon=2.3522),
        PlaceSchema(name="Lyon",  lat=45.7640, lon=4.8357),
        PlaceSchema(name="Nice",  lat=43.7102, lon=7.2620),
    ]
    threshold = compute_adaptive_threshold(places)
    assert threshold > 0


def test_adaptive_threshold_scales_with_percentage():
    """
    Test that a higher percentage produces a higher threshold.
    """
    places = [
        PlaceSchema(name="Paris", lat=48.8566, lon=2.3522),
        PlaceSchema(name="Lyon",  lat=45.7640, lon=4.8357),
        PlaceSchema(name="Nice",  lat=43.7102, lon=7.2620),
    ]
    t10 = compute_adaptive_threshold(places, percentage=0.10)
    t30 = compute_adaptive_threshold(places, percentage=0.30)
    assert t30 > t10


# ---------------------------------------------------------------------------
# cluster_places
# ---------------------------------------------------------------------------

def test_cluster_places_obvious_two_clusters():
    """
    Test that two geographically distant cities (Paris vs Tokyo) are separated into two clusters, even with unreasonably high distance_max_km.
    """
    places = [
        PlaceSchema(name="Paris",      lat=48.8566, lon=2.3522),
        PlaceSchema(name="Versailles", lat=48.8044, lon=2.1204),
        PlaceSchema(name="Tokyo",      lat=35.6820, lon=139.7621),
    ]
    clusters = cluster_places(places, distance_max_km=50)
    assert len(clusters) == 2


def test_cluster_places_all_in_one_cluster():
    """
    Test that three very close cities must all be in the same cluster.
    """
    places = [
        PlaceSchema(name="Paris",      lat=48.8566, lon=2.3522),
        PlaceSchema(name="Versailles", lat=48.8044, lon=2.1204),
        PlaceSchema(name="Boulogne",   lat=48.8350, lon=2.2400),
    ]
    clusters = cluster_places(places, distance_max_km=50)
    assert len(clusters) == 1
    assert len(clusters[0]) == 3


def test_cluster_places_all_isolated():
    """
    Test that with a threshold of 0 km, each city must form its own cluster.
    """
    places = [
        PlaceSchema(name="Paris", lat=48.8566, lon=2.3522),
        PlaceSchema(name="Lyon",  lat=45.7640, lon=4.8357),
        PlaceSchema(name="Nice",  lat=43.7102, lon=7.2620),
    ]
    clusters = cluster_places(places, distance_max_km=0)
    assert len(clusters) == len(places)


def test_cluster_places_uses_adaptive_threshold_when_none():
    """
    Test that cluster_places uses the adaptive threshold when no distance_max_km is provided.
    """
    places = [
        PlaceSchema(name="Paris",      lat=48.8566, lon=2.3522),
        PlaceSchema(name="Versailles", lat=48.8044, lon=2.1204),
        PlaceSchema(name="Lyon",       lat=45.7640, lon=4.8357),
        PlaceSchema(name="Grenoble",   lat=45.1885, lon=5.7245),
    ]
    clusters = cluster_places(places)
    total = sum(len(c) for c in clusters)
    assert total == len(places)


# ---------------------------------------------------------------------------
# find_central_place
# ---------------------------------------------------------------------------

def test_find_central_place_single():
    """
    Test that the central place of a single-city cluster is that city itself.
    """
    places = [PlaceSchema(name="Paris", lat=48.8566, lon=2.3522)]
    assert find_central_place(places) == places[0]


def test_find_central_place_selects_middle():
    """
    Test that the central place of a three-city cluster is the middle city.
    """
    places = [
        PlaceSchema(name="A", lat=0.0, lon=0.0),
        PlaceSchema(name="B", lat=0.0, lon=1.0),
        PlaceSchema(name="C", lat=0.0, lon=2.0),
    ]
    central = find_central_place(places)
    assert central.name == "B"


# ---------------------------------------------------------------------------
# calculate_intra_group_distance
# ---------------------------------------------------------------------------

def test_intra_group_distance_single_place():
    """
    Test that the intra-group distance for a single-place group is 0.
    """
    hotel = PlaceSchema(name="Paris", lat=48.8566, lon=2.3522)
    groupe = [hotel]
    matrix = build_distance_matrix(groupe)
    total, ordered = calculate_intra_group_distance(hotel, groupe, matrix, 0)
    assert total == 0
    assert ordered == [hotel]


def test_intra_group_distance_hotel_is_first():
    """
    Test that the ordered list always starts with the hotel.
    """
    hotel = PlaceSchema(name="Paris",      lat=48.8566, lon=2.3522)
    city1 = PlaceSchema(name="Versailles", lat=48.8044, lon=2.1204)
    city2 = PlaceSchema(name="Boulogne",   lat=48.8350, lon=2.2400)
    groupe = [hotel, city1, city2]
    matrix = build_distance_matrix(groupe)
    _, ordered = calculate_intra_group_distance(hotel, groupe, matrix, 0)
    assert ordered[0] == hotel


def test_intra_group_distance_is_sum_of_round_trips():
    """
    Test that the total intra-group distance is the sum of 2 * dist(hotel, city) for each city.
    """
    hotel = PlaceSchema(name="Paris",      lat=48.8566, lon=2.3522)
    city1 = PlaceSchema(name="Versailles", lat=48.8044, lon=2.1204)
    city2 = PlaceSchema(name="Lyon",       lat=45.7640, lon=4.8357)
    groupe = [hotel, city1, city2]
    matrix = build_distance_matrix(groupe)
    total, _ = calculate_intra_group_distance(hotel, groupe, matrix, 0)
    expected = 2 * matrix[0][1] + 2 * matrix[0][2]
    assert abs(total - expected) < 1e-9


# ---------------------------------------------------------------------------
# plan_tour_with_hotels
# ---------------------------------------------------------------------------

def test_plan_tour_with_hotels_single_place():
    """
    Test that with a single city, all distances (inter, intra, total) must be 0.
    """
    places = [PlaceSchema(name="Paris", lat=48.8566, lon=2.3522)]
    result = plan_tour_with_hotels(places)
    assert result["distance_inter"] == 0
    assert result["distance_intra"] == 0
    assert result["distance_total"] == 0


def test_plan_tour_with_hotels_output_keys():
    """
    Test that the return dictionary contains all expected keys.
    """
    places = [
        PlaceSchema(name="Paris", lat=48.8566, lon=2.3522),
        PlaceSchema(name="Lyon",  lat=45.7640, lon=4.8357),
        PlaceSchema(name="Nice",  lat=43.7102, lon=7.2620),
    ]
    result = plan_tour_with_hotels(places)
    for key in ("etapes", "distance_inter", "distance_intra", "distance_total"):
        assert key in result


def test_plan_tour_with_hotels_all_places_covered():
    """
    Test that all input cities must appear in tour_complet.
    """
    places = [
        PlaceSchema(name="Paris",      lat=48.8566, lon=2.3522),
        PlaceSchema(name="Versailles", lat=48.8044, lon=2.1204),
        PlaceSchema(name="Lyon",       lat=45.7640, lon=4.8357),
        PlaceSchema(name="Grenoble",   lat=45.1885, lon=5.7245),
    ]
    result = plan_tour_with_hotels(places)
    covered_names = {p.name for p in result["tour_complet"]}
    input_names   = {p.name for p in places}
    assert covered_names == input_names


def test_plan_tour_with_hotels_distance_total_consistency():
    """
    Test that distance_total is equal to distance_inter + distance_intra.
    """
    places = [
        PlaceSchema(name="Paris",      lat=48.8566, lon=2.3522),
        PlaceSchema(name="Versailles", lat=48.8044, lon=2.1204),
        PlaceSchema(name="Lyon",       lat=45.7640, lon=4.8357),
        PlaceSchema(name="Grenoble",   lat=45.1885, lon=5.7245),
    ]
    result = plan_tour_with_hotels(places)
    assert abs(result["distance_total"] - (result["distance_inter"] + result["distance_intra"])) < 1e-9


def test_plan_tour_with_hotels_obvious_clusters():
    """
    Test that two obvious geographic clusters (Paris/Versailles vs Lyon/Grenoble) produce exactly 2 steps.
    """
    places = [
        PlaceSchema(name="Paris",      lat=48.8566, lon=2.3522),
        PlaceSchema(name="Versailles", lat=48.8044, lon=2.1204),
        PlaceSchema(name="Lyon",       lat=45.7640, lon=4.8357),
        PlaceSchema(name="Grenoble",   lat=45.1885, lon=5.7245),
    ]
    result = plan_tour_with_hotels(places, percentage=0.15)
    assert len(result["etapes"]) == 2