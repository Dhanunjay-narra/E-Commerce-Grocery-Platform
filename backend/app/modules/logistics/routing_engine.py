"""Last-Mile Route Optimization, Haversine Matrix, and Traveling Salesperson Heuristics."""
import math
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel

class GeoLocation(BaseModel):
    latitude: float
    longitude: float
    label: str = ""
    order_id: str = ""
    estimated_drop_duration_mins: int = 5

class RouteSegment(BaseModel):
    from_point: GeoLocation
    to_point: GeoLocation
    distance_km: float
    transit_duration_mins: float

class OptimizedRoute(BaseModel):
    total_distance_km: float
    total_duration_mins: float
    waypoints_order: List[GeoLocation]
    segments: List[RouteSegment]

class FleetRoutingEngine:
    """Solves multi-stop drop sequencing from dark store hub to customer doorsteps."""
    
    EARTH_RADIUS_KM = 6371.0
    AVERAGE_URBAN_SPEED_KMPH = 24.0  # Urban electric scooter speed

    @classmethod
    def haversine_distance(cls, loc1: GeoLocation, loc2: GeoLocation) -> float:
        lat1, lon1 = math.radians(loc1.latitude), math.radians(loc1.longitude)
        lat2, lon2 = math.radians(loc2.latitude), math.radians(loc2.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat / 2.0)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2.0)**2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        
        return round(cls.EARTH_RADIUS_KM * c, 3)

    @classmethod
    def estimate_travel_time(cls, distance_km: float) -> float:
        # Distance / Speed in hours -> convert to minutes + traffic buffer
        hours = distance_km / cls.AVERAGE_URBAN_SPEED_KMPH
        mins = hours * 60.0
        return round(mins * 1.15, 1)  # 15% traffic buffer

    @classmethod
    def solve_nearest_neighbor(cls, origin: GeoLocation, destinations: List[GeoLocation]) -> OptimizedRoute:
        if not destinations:
            return OptimizedRoute(total_distance_km=0.0, total_duration_mins=0.0, waypoints_order=[origin], segments=[])
            
        unvisited = list(destinations)
        current = origin
        route_order = [origin]
        segments = []
        total_dist = 0.0
        total_time = 0.0
        
        while unvisited:
            nearest = None
            min_dist = float('inf')
            
            for candidate in unvisited:
                d = cls.haversine_distance(current, candidate)
                if d < min_dist:
                    min_dist = d
                    nearest = candidate
                    
            unvisited.remove(nearest)
            transit_time = cls.estimate_travel_time(min_dist)
            drop_time = nearest.estimated_drop_duration_mins
            
            segment = RouteSegment(
                from_point=current,
                to_point=nearest,
                distance_km=min_dist,
                transit_duration_mins=transit_time,
            )
            segments.append(segment)
            route_order.append(nearest)
            
            total_dist += min_dist
            total_time += transit_time + drop_time
            current = nearest
            
        return OptimizedRoute(
            total_distance_km=round(total_dist, 2),
            total_duration_mins=round(total_time, 1),
            waypoints_order=route_order,
            segments=segments,
        )
