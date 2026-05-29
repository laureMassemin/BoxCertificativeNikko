import math
from math import cos, sin, acos, radians

Rearth = 6378.197


def distance (Va, Vb):
    """ 
    Calculate the length of the arc between two points on the surface of the Earth, given their latitudes and longitudes. 
    Parameters:
        Va (list): A list containing the latitude and longitude of the first point.
        Vb (list): A list containing the latitude and longitude of the second point.
    Returns:
        float: The length of the arc between the two points.
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
        places (list): A list of tuples containing the latitudes and longitudes of the places.
    Returns:
        list: A list representing the distance matrix.
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

def nearest_neighbor_tour(distance_matrix):
    """
    Generate a tour using the nearest neighbor.
    Parameters:
        distance_matrix (list): A list representing the distance matrix.
    Returns:
        list: A list representing the order of places in the generated tour.
    """
    n = len(distance_matrix)
    if n == 0:
        return []
    tour = [0]
    current = 0
    visited = set(tour)
    while len(visited) < n:
        next_place = None
        smallest_distance = float('inf')
        for j in range(n):
            if j not in visited:
                if distance_matrix[current][j] < smallest_distance:
                    smallest_distance = distance_matrix[current][j]
                    next_place = j
        tour.append(next_place)
        visited.add(next_place)
        current = next_place
    return tour

def tour_length(tour, distance_matrix):
    """
    Calculate the total length of a tour.
    Parameters:
        tour (list): A list representing the order of places in the tour.
        distance_matrix (list): A list representing the distance matrix.
    Returns:
        float: The total length of the tour.
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
        distance_matrix (list): A list representing the distance matrix.
    Returns:
        list: A new tour resulting from the 2-opt swap.
    """
    n = len(tour)
    best_tour = True
    while best_tour:
        best_tour = False
        current_length = tour_length(tour, distance_matrix)
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                new_tour = tour[:i] + tour[i:j][::-1] + tour[j:]
                new_length = tour_length(new_tour, distance_matrix)
                if new_length < current_length:
                    tour = new_tour
                    current_length = new_length
                    best_tour = True
    return tour

def plan_tour(places):
    """
    Generate a tour for a list of places using the nearest neighbor heuristic followed by 2-opt optimization.
    Parameters:
        places (list): A list of tuples containing the latitudes and longitudes of the places.
    Returns:
        list: A list representing the order of places in the generated tour.
    """
    distance_matrix = build_distance_matrix(places)
    initial_tour = nearest_neighbor_tour(distance_matrix)
    optimized_tour = two_opt_swap(initial_tour, distance_matrix)
    ordered_places = [places[i] for i in optimized_tour]
    total_length = tour_length(optimized_tour, distance_matrix)
    return { "tour": ordered_places, "length": total_length }

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

def calculate_intra_group_distance(hotel, groupe):
    """
    Calculate the total distance of round trips between the hotel and each other place in the group.
    Each place is visited separately from the hotel (×2 for go + return).
    Parameters:
        hotel (PlaceSchema): The central place in the group that serves as the hotel.
        groupe (list): A list of PlaceSchema objects representing the places in the group.
    Returns:
        float: The total distance of the round trips in kilometers.
    """
    total = 0
    coord_hotel = (hotel.lat, hotel.lon)
    for ville in groupe:
        if ville is not hotel:
            coord_ville = (ville.lat, ville.lon)
            total += 2 * distance(coord_hotel, coord_ville)
    return total


def plan_tour_with_hotels(places, percentage=0.15):
    """
    Plan a tour for a list of places by grouping them around central "hotel" locations and optimizing the order of visiting these hotels.
    The algorithm consists of the following steps:
    1. Clustering: Group the places into clusters based on their geographical proximity using an adaptive distance threshold.
    2. Hotel Selection: For each cluster, select a central place to serve as the "hotel" for that cluster.
    3. Inter-Hotel TSP: Solve a TSP to determine the optimal order of visiting the hotels.
    4. Intra-Group Distance Calculation: For each hotel, calculate the total distance of round trips to visit all places in its cluster.
    Parameters:
        places (list): A list of PlaceSchema objects representing the places to be included in the tour.
        percentage (float): The percentage of the median distance to be used as the threshold for clustering (default is 0.15 for 15%).
    Returns:
        dict: A dictionary containing the following keys:
            - "etapes": A list of dictionaries, each representing a stage of the tour with   the hotel, the places in its cluster, and the intra-group distance.
            - "distance_inter": The total distance of the inter-hotel tour.
            - "distance_intra": The total distance of the intra-group round trips.
            - "distance_total": The sum of inter-hotel and intra-group distances, representing the total length of the tour.
    """
    if len(places) < 2:
        return {
            "etapes": [{"hotel": p, "villes": [p], "distance_intra": 0} for p in places],
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
        hotels_ordonnes = hotels
        ordre_indices = [0]
        distance_inter = 0
    else:
        distance_matrix = build_distance_matrix(hotels)
        initial_tour = nearest_neighbor_tour(distance_matrix)
        ordre_indices = two_opt_swap(initial_tour, distance_matrix)
        hotels_ordonnes = [hotels[i] for i in ordre_indices]
        distance_inter = tour_length(ordre_indices, distance_matrix)
    
    etapes = []
    distance_intra_totale = 0
    for idx_hotel in ordre_indices:
        hotel = hotels[idx_hotel]
        groupe = groupe_par_hotel_index[idx_hotel]
        d_intra = calculate_intra_group_distance(hotel, groupe)
        distance_intra_totale += d_intra
        etapes.append({
            "hotel": hotel,
            "villes": groupe,
            "distance_intra": d_intra
        })
    
    return {
        "etapes": etapes,
        "distance_inter": distance_inter,
        "distance_intra": distance_intra_totale,
        "distance_total": distance_inter + distance_intra_totale
    }

if __name__ == "__main__":
    from models import PlaceSchema
    
    places = [
        PlaceSchema(name="Tokyo",   lat=35.6820172, lon=139.76216),
        PlaceSchema(name="Kyoto",   lat=34.9946315, lon=135.7344318),
        PlaceSchema(name="Osaka",   lat=34.6937,    lon=135.5023),
        PlaceSchema(name="Sapporo", lat=43.0618,    lon=141.3545),
        PlaceSchema(name="Nikko",   lat=36.7198,    lon=139.6982),
        PlaceSchema(name="Sendai",  lat=38.2682,    lon=140.8694),
    ]

    print("=== TSP classique ===")
    tour = plan_tour(places)
    for place in tour["tour"]:
        print(f"  {place.name}")
    print(f"Total: {tour['length']:.2f} km\n")
    
    print("=== TSP avec regroupement par hôtels ===")
    result = plan_tour_with_hotels(places)
    
    for i, etape in enumerate(result['etapes']):
        noms_villes = [v.name for v in etape['villes']]
        print(f"Étape {i+1} : Hôtel = {etape['hotel'].name}")
        print(f"           Villes = {noms_villes}")
        print(f"           Aller-retours = {etape['distance_intra']:.2f} km")
    
    print(f"\nInter-hôtels  : {result['distance_inter']:.2f} km")
    print(f"Aller-retours : {result['distance_intra']:.2f} km")
    print(f"TOTAL         : {result['distance_total']:.2f} km")