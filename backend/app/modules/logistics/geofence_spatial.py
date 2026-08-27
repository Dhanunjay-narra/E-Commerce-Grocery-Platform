"""Ray-Casting Polygon Geofencing and Geohash Spatial Clustering for Dark Store Dispatch."""
from typing import List, Tuple, Dict, Any, Optional
from pydantic import BaseModel

class Coordinate(BaseModel):
    latitude: float
    longitude: float

class GeofencePolygon(BaseModel):
    zone_id: str
    zone_name: str
    vertices: List[Coordinate]
    is_active: bool = True

class GeofenceSpatialEngine:
    """Determines if a customer GPS coordinate falls inside a dark-store polygon boundary using Jordan Curve theorem."""

    @staticmethod
    def is_point_in_polygon(point: Coordinate, polygon: List[Coordinate]) -> bool:
        num_vertices = len(polygon)
        if num_vertices < 3:
            return False

        inside = False
        p1 = polygon[0]

        for i in range(1, num_vertices + 1):
            p2 = polygon[i % num_vertices]
            if point.longitude > min(p1.longitude, p2.longitude):
                if point.longitude <= max(p1.longitude, p2.longitude):
                    if point.latitude <= max(p1.latitude, p2.latitude):
                        if p1.longitude != p2.longitude:
                            x_inters = (point.longitude - p1.longitude) * (p2.latitude - p1.latitude) / (p2.longitude - p1.longitude) + p1.latitude
                        if p1.latitude == p2.latitude or point.latitude <= x_inters:
                            inside = not inside
            p1 = p2

        return inside

    @classmethod
    def find_serviceable_dark_store(cls, customer_loc: Coordinate, zones: List[GeofencePolygon]) -> Optional[str]:
        for z in zones:
            if not z.is_active:
                continue
            if cls.is_point_in_polygon(customer_loc, z.vertices):
                return z.zone_id
        return None
