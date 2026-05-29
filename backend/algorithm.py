import math
from math import cos, sin, acos, radians

Rearth = 6378.197


def distance(Va, Vb):
    """
    Calculate the length of the arc between two points on the surface of the Earth, given their latitudes and longitudes.
    Parameters:
        Va (list): A list containing the latitude and longitude of the first point.
        Vb (list): A list containing the latitude and longitude of the second point.
    Returns:
        float: The length of the arc between the two points in kilometers.
    """
    lat1 = radians(Va[0])
    lon1 = radians(Va[1])
    lat2 = radians(Vb[0])
    lon2 = radians(Vb[1])

    distance = Rearth * acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon1 - lon2))
    return distance


def personalised_tour_length(places):
    """
    Calculate the total length of a tour that visits a list of places in a specific order, including the return trip to the starting point.
    Parameters:
        places (list): A list of PlaceSchema objects representing the places in the tour.
    Returns:
        float: The total length of the tour in kilometers.
    """
    n = len(places)
    total_length = 0
    for i in range(n - 1):
        coord_i = (places[i].lat, places[i].lon)
        coord_j = (places[i + 1].lat, places[i + 1].lon)
        total_length += distance(coord_i, coord_j)
    total_length += distance((places[-1].lat, places[-1].lon), (places[0].lat, places[0].lon))
    return total_length


def build_distance_matrix(places):
    """
    Build a distance matrix for a list of places for remembering the calculated distances without recalculating.
    Parameters:
        places (list): A list of PlaceSchema objects containing lat and lon attributes.
    Returns:
        list: A 2D list representing the distance matrix.
    """
    n = len(places)
    distance_matrix = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            coord_i = (places[i].lat, places[i].lon)
            coord_j = (places[j].lat, places[j].lon)
            dist = distance(coord_i, coord_j)
            distance_matrix[i][j] = dist
            distance_matrix[j][i] = dist
    return distance_matrix


def nearest_neighbor_tour(distance_matrix, start=0):
    """
    Generate a tour using the nearest neighbor heuristic from a given starting point.
    Parameters:
        distance_matrix (list): A 2D list representing the distance matrix.
        start (int): The index of the starting place.
    Returns:
        list: A list representing the order of places in the generated tour.
    """
    n = len(distance_matrix)
    if n == 0:
        return []
    tour = [start]
    current = start
    visited = set(tour)
    while len(visited) < n:
        next_place = min(
            (j for j in range(n) if j not in visited),
            key=lambda j: distance_matrix[current][j]
        )
        tour.append(next_place)
        visited.add(next_place)
        current = next_place
    return tour


def best_nearest_neighbor_tour(distance_matrix):
    """
    Try all starting points for the nearest neighbor heuristic and return the best tour found.
    Parameters:
        distance_matrix (list): A 2D list representing the distance matrix.
    Returns:
        list: The best tour found across all starting points.
    """
    n = len(distance_matrix)
    best = None
    best_length = float('inf')
    for start in range(n):
        tour = nearest_neighbor_tour(distance_matrix, start)
        length = tour_length(tour, distance_matrix)
        if length < best_length:
            best_length = length
            best = tour
    return best


def tour_length(tour, distance_matrix):
    """
    Calculate the total length of a tour.
    Parameters:
        tour (list): A list representing the order of places in the tour.
        distance_matrix (list): A 2D list representing the distance matrix.
    Returns:
        float: The total length of the tour in kilometers.
    """
    total_length = 0
    for i in range(len(tour) - 1):
        total_length += distance_matrix[tour[i]][tour[i + 1]]
    total_length += distance_matrix[tour[-1]][tour[0]]
    return total_length


def two_opt_swap(tour, distance_matrix):
    """
    Improve a tour by reversing segments that shorten it.
    Stops when no further improvement can be found.
    Parameters:
        tour (list): A list representing the order of places in the tour.
        distance_matrix (list): A 2D list representing the distance matrix.
    Returns:
        list: An improved tour resulting from the 2-opt swap.
    """
    n = len(tour)
    improved = True
    while improved:
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                a, b = tour[i - 1], tour[i]
                c, d = tour[j], tour[(j + 1) % n]
                delta = (
                    distance_matrix[a][c] + distance_matrix[b][d]
                    - distance_matrix[a][b] - distance_matrix[c][d]
                )
                if delta < -1e-10:
                    tour[i:j + 1] = tour[i:j + 1][::-1]
                    improved = True
                    break
            if improved:
                break
    return tour


def plan_tour(places):
    """
    Generate a tour for a list of places using the nearest neighbor heuristic (all starting points) followed by 2-opt optimization.
    Parameters:
        places (list): A list of PlaceSchema objects containing lat and lon attributes.
    Returns:
        dict: A dictionary with keys:
            - "tour": ordered list of PlaceSchema objects.
            - "length": total length of the tour in kilometers.
    """
    distance_matrix = build_distance_matrix(places)
    initial_tour = best_nearest_neighbor_tour(distance_matrix)
    optimized_tour = two_opt_swap(initial_tour, distance_matrix)
    ordered_places = [places[i] for i in optimized_tour]
    total_length = tour_length(optimized_tour, distance_matrix)
    return {"tour": ordered_places, "length": total_length}


def compute_adaptive_threshold(places, percentage=0.15):
    """
    Compute an adaptive distance threshold for clustering places based on the distribution of distances between them.
    The threshold is calculated as a percentage of the median of all pairwise distances between the places.
    Parameters:
        places (list): A list of PlaceSchema objects representing the places to be clustered.
        percentage (float): The percentage of the median distance to be used as the threshold (default is 0.15 for 15%).
    Returns:
        float: The computed adaptive distance threshold in kilometers.
    """
    n = len(places)
    if n < 2:
        return 0

    distances = []
    for i in range(n):
        for j in range(i + 1, n):
            coord_i = (places[i].lat, places[i].lon)
            coord_j = (places[j].lat, places[j].lon)
            distances.append(distance(coord_i, coord_j))

    distances.sort()
    nb = len(distances)

    if nb % 2 == 1:
        mediane = distances[nb // 2]
    else:
        mediane = (distances[nb // 2 - 1] + distances[nb // 2]) / 2

    return percentage * mediane


def cluster_places(places, distance_max_km=None, percentage=0.15):
    """
    Cluster places based on their geographical proximity using an adaptive distance threshold.
    Each place is compared to existing clusters, and if it is within the threshold distance of any place in a cluster, it is added to that cluster.
    Otherwise, a new cluster is created for that place.
    Parameters:
        places (list): A list of PlaceSchema objects representing the places to be clustered.
        distance_max_km (float, optional): The maximum distance for clustering. If None, an adaptive threshold is computed.
        percentage (float): The percentage of the median distance to be used as the threshold (default is 0.15 for 15%).
    Returns:
        list: A list of clusters, where each cluster is a list of PlaceSchema objects.
    """
    if distance_max_km is None:
        distance_max_km = compute_adaptive_threshold(places, percentage)

    groupes = []

    for place in places:
        groupe_trouve = None
        for groupe in groupes:
            for ville in groupe:
                coord_p = (place.lat, place.lon)
                coord_v = (ville.lat, ville.lon)
                if distance(coord_p, coord_v) <= distance_max_km:
                    groupe_trouve = groupe
                    break
            if groupe_trouve is not None:
                break

        if groupe_trouve is not None:
            groupe_trouve.append(place)
        else:
            groupes.append([place])

    return groupes


def find_central_place(groupe):
    """
    Find the most central place in a group of places, defined as the one with the smallest total distance to all other places in the group.
    Parameters:
        groupe (list): A list of PlaceSchema objects representing the places in the group.
    Returns:
        PlaceSchema: The place that is the most central in the group.
    """
    if len(groupe) == 1:
        return groupe[0]

    best_place = None
    best_distance_sum = float('inf')

    for candidate in groupe:
        distance_sum = 0
        coord_c = (candidate.lat, candidate.lon)
        for other in groupe:
            if other is not candidate:
                coord_o = (other.lat, other.lon)
                distance_sum += distance(coord_c, coord_o)

        if distance_sum < best_distance_sum:
            best_distance_sum = distance_sum
            best_place = candidate

    return best_place


def calculate_intra_group_distance(hotel, groupe, distance_matrix_groupe, hotel_index):
    """
    Calculate the total distance of individual round trips from the hotel to each place.
    hotel -> A -> hotel -> B -> hotel -> C -> hotel
    Places are sorted by distance from the hotel (closest first).
    Parameters:
        hotel (PlaceSchema): The central place serving as the hotel.
        groupe (list): A list of PlaceSchema objects in the group.
        distance_matrix_groupe (list): Precomputed distance matrix for the group.
        hotel_index (int): Index of the hotel in the group/distance matrix.
    Returns:
        tuple: (total_distance, ordered_places) where:
            - total_distance (float): total round-trip distance in kilometers.
            - ordered_places (list): ALL places with hotel first, then others sorted by distance.
                                     e.g. [hotel, closest, ..., farthest]
    """
    if len(groupe) == 1:
        return 0, [hotel]

    other_indices = [i for i in range(len(groupe)) if i != hotel_index]
    other_indices.sort(key=lambda i: distance_matrix_groupe[hotel_index][i])

    total = sum(2 * distance_matrix_groupe[hotel_index][i] for i in other_indices)
    ordered_places = [hotel] + [groupe[i] for i in other_indices]  # ← hôtel en tête

    return total, ordered_places


def plan_tour_with_hotels(places, percentage=0.15):
    """
    Plan a tour for a list of places by grouping them around central "hotel" locations and optimizing the order of visiting these hotels.
    The algorithm consists of the following steps:
    1. Clustering: Group the places into clusters based on their geographical proximity using an adaptive distance threshold.
    2. Hotel Selection: For each cluster, select a central place to serve as the "hotel" for that cluster.
    3. Inter-Hotel TSP: Solve a TSP to determine the optimal order of visiting the hotels.
    4. Intra-Group Distance Calculation: For each hotel, calculate the total distance of individual round trips to visit all places in its cluster (hotel -> A -> hotel -> B -> hotel -> ...).
    Parameters:
        places (list): A list of PlaceSchema objects representing the places to be included in the tour.
        percentage (float): The percentage of the median distance to be used as the threshold for clustering (default is 0.15 for 15%).
    Returns:
        dict: A dictionary containing the following keys:
            - "etapes": A list of dictionaries, each with:
                - "hotel": the central PlaceSchema for this stage.
                - "villes": non-hotel places ordered by distance from the hotel (visit order).
                - "distance_intra": total round-trip distance for this stage in kilometers.
            - "distance_inter": The total distance of the inter-hotel tour in kilometers.
            - "distance_intra": The total intra-group round-trip distance in kilometers.
            - "distance_total": The sum of inter-hotel and intra-group distances in kilometers.
    """
    if len(places) < 2:
        return {
            "etapes": [{"hotel": p, "villes": [], "distance_intra": 0} for p in places],
            "distance_inter": 0,
            "distance_intra": 0,
            "distance_total": 0
        }

    groupes = cluster_places(places, percentage=percentage)

    hotels = []
    groupe_par_hotel_index = {}
    for groupe in groupes:
        hotel = find_central_place(groupe)
        groupe_par_hotel_index[len(hotels)] = groupe
        hotels.append(hotel)

    if len(hotels) == 1:
        ordre_indices = [0]
        distance_inter = 0
    else:
        distance_matrix = build_distance_matrix(hotels)
        initial_tour = best_nearest_neighbor_tour(distance_matrix)
        ordre_indices = two_opt_swap(initial_tour, distance_matrix)
        distance_inter = tour_length(ordre_indices, distance_matrix)

    etapes = []
    distance_intra_totale = 0
    for idx_hotel in ordre_indices:
        hotel = hotels[idx_hotel]
        groupe = groupe_par_hotel_index[idx_hotel]

        dm_groupe = build_distance_matrix(groupe)
        hotel_index = groupe.index(hotel)

        d_intra, villes_ordonnees = calculate_intra_group_distance(hotel, groupe, dm_groupe, hotel_index)
        distance_intra_totale += d_intra
        etapes.append({
            "hotel": hotel,
            "villes": villes_ordonnees,
            "distance_intra": d_intra
        })

        tour_complet = []
        for etape in etapes:
            tour_complet.extend(etape["villes"])

    return {
        "etapes": etapes,
        "tour_complet": tour_complet,
        "distance_inter": distance_inter,
        "distance_intra": distance_intra_totale,
        "distance_total": distance_inter + distance_intra_totale
    }