from typing import List, Dict
import math

def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return round(math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111.0, 2)

def optimize_delivery_waypoints(start: tuple, waypoints: List[tuple]) -> List[tuple]:
    ordered = []
    current = start
    remaining = list(waypoints)
    while remaining:
        nearest = min(remaining, key=lambda pt: calculate_distance_km(current[0], current[1], pt[0], pt[1]))
        ordered.append(nearest)
        remaining.remove(nearest)
        current = nearest
    return ordered
