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
)
from models import PlaceSchema


def test_distance_to_self_is_zero():
    """
    Test that the distance from a point to itself is zero.
    """
    point = (35.6820172, 139.76216)
    assert distance(point, point) == 0


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


def test_plan_tour_returns_correct_format():
    """
    Test that the fonction plan_tour returns xhat is expected  in the models.
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
