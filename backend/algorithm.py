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
    Calculate an adaptive distance threshold based on the average distance between all pairs of places.
    Parameters:
        places (list): A list of tuples containing the latitudes and longitudes of the places
        percentage (float): The percentage of the average distance to use as the threshold (default is 15%).
    Returns:
        float: The computed adaptive distance threshold.
    """
    total_distance = 0
    count = 0
    
    n = len(places)
    for i in range(n):
        for j in range(i + 1, n):
            coord_i = (places[i].lat, places[i].lon)
            coord_j = (places[j].lat, places[j].lon)
            total_distance += distance(coord_i, coord_j)
            count += 1
    average_distance = total_distance / count if count > 0 else 0
    result = percentage * average_distance

    return result

def compute_adaptive_threshold(places, percentage=0.15):
    """
    Calcule un seuil de distance adapté à l'échelle du voyage.
    
    Seuil = percentage × médiane des distances entre toutes les paires de villes.
    
    On utilise la médiane (et non la moyenne) pour la ROBUSTESSE aux valeurs
    aberrantes : si certaines villes sont très éloignées des autres (ex : un voyage 
    Tokyo + Paris + LA mélangé avec des villes locales), la moyenne serait tirée
    vers le haut par les trajets transcontinentaux, ce qui ferait croire à 
    l'algorithme que des villes pourtant lointaines sont "proches". La médiane,
    elle, ignore ces extrêmes.
    """
    n = len(places)
    if n < 2:
        return 0
    
    distances = []
    for i in range(n):
        for j in range(i + 1, n):
            distances.append(distance(places[i], places[j]))
    
    distances.sort()
    nb = len(distances)
    
    if nb % 2 == 1:
        mediane = distances[nb // 2]
    else:
        mediane = (distances[nb // 2 - 1] + distances[nb // 2]) / 2
    
    return percentage * mediane

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



