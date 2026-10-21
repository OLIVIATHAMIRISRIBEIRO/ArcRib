"""
arcgeo.geometry - Core Spatial and Geometric Primitives
Implements OGC Simple Features Specification and ESRI ArcGIS-compatible geometry types:
- Point, Polyline, Polygon, Envelope (BoundingBox)
- SpatialReference and coordinate projection (WGS84 EPSG:4326 <-> Web Mercator EPSG:3857)
- Spatial algorithms: Euclidean & Haversine distance, Shoelace area, Ray-casting point-in-polygon
"""

import math
from typing import List, Tuple, Optional, Dict, Any


class SpatialReference:
    """Represents a coordinate reference system (CRS)."""
    def __init__(self, wkid: int = 4326, name: str = "WGS 1984"):
        self.wkid = wkid
        self.name = name

    def is_geographic(self) -> bool:
        return self.wkid == 4326

    def is_projected(self) -> bool:
        return self.wkid == 3857

    @staticmethod
    def wgs84_to_web_mercator(lon: float, lat: float) -> Tuple[float, float]:
        """Projects (lon, lat) WGS84 degrees into (x, y) Web Mercator meters."""
        lat = max(min(lat, 89.5), -89.5)
        x = lon * 20037508.34 / 180.0
        y = math.log(math.tan((90.0 + lat) * math.pi / 360.0)) / (math.pi / 180.0)
        y = y * 20037508.34 / 180.0
        return (x, y)

    @staticmethod
    def web_mercator_to_wgs84(x: float, y: float) -> Tuple[float, float]:
        """Inverse-projects (x, y) Web Mercator meters back into (lon, lat) WGS84 degrees."""
        lon = (x / 20037508.34) * 180.0
        lat = (y / 20037508.34) * 180.0
        lat = 180.0 / math.pi * (2.0 * math.atan(math.exp(lat * math.pi / 180.0)) - math.pi / 2.0)
        return (lon, lat)

    @staticmethod
    def haversine_distance(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
        """Great-circle distance in meters between two (lon, lat) points in WGS84."""
        r = 6371000.0  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return r * c


class Envelope:
    """Represents an axis-aligned bounding box (Extent / BoundingBox)."""
    def __init__(self, xmin: float, ymin: float, xmax: float, ymax: float):
        self.xmin = min(xmin, xmax)
        self.ymin = min(ymin, ymax)
        self.xmax = max(xmin, xmax)
        self.ymax = max(ymin, ymax)

    @property
    def width(self) -> float:
        return self.xmax - self.xmin

    @property
    def height(self) -> float:
        return self.ymax - self.ymin

    @property
    def center(self) -> Tuple[float, float]:
        return ((self.xmin + self.xmax) / 2.0, (self.ymin + self.ymax) / 2.0)

    def intersects(self, other: 'Envelope') -> bool:
        """Determines if this envelope intersects or touches another envelope."""
        return not (other.xmin > self.xmax or
                    other.xmax < self.xmin or
                    other.ymin > self.ymax or
                    other.ymax < self.ymin)

    def contains_point(self, x: float, y: float) -> bool:
        return self.xmin <= x <= self.xmax and self.ymin <= y <= self.ymax

    def union(self, other: 'Envelope') -> 'Envelope':
        """Returns the minimal envelope containing both envelopes."""
        return Envelope(
            min(self.xmin, other.xmin),
            min(self.ymin, other.ymin),
            max(self.xmax, other.xmax),
            max(self.ymax, other.ymax)
        )

    def to_dict(self) -> Dict[str, float]:
        return {"xmin": self.xmin, "ymin": self.ymin, "xmax": self.xmax, "ymax": self.ymax}

    def __repr__(self) -> str:
        return f"Envelope({self.xmin:.4f}, {self.ymin:.4f}, {self.xmax:.4f}, {self.ymax:.4f})"


class Geometry:
    """Base class for all spatial geometries."""
    def get_envelope(self) -> Envelope:
        raise NotImplementedError

    def to_geojson(self) -> Dict[str, Any]:
        raise NotImplementedError


class Point(Geometry):
    """A 2D coordinate pair (x, y)."""
    def __init__(self, x: float, y: float, z: Optional[float] = None):
        self.x = float(x)
        self.y = float(y)
        self.z = z

    def get_envelope(self) -> Envelope:
        return Envelope(self.x, self.y, self.x, self.y)

    def distance_to(self, other: 'Point') -> float:
        """Euclidean distance to another point."""
        return math.hypot(self.x - other.x, self.y - other.y)

    def geodesic_distance_to(self, other: 'Point') -> float:
        """Great-circle distance in meters assuming (x=lon, y=lat) on WGS84 sphere."""
        r = 6371000.0  # Earth radius in meters
        phi1 = math.radians(self.y)
        phi2 = math.radians(other.y)
        delta_phi = math.radians(other.y - self.y)
        delta_lambda = math.radians(other.x - self.x)

        a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return r * c

    def to_geojson(self) -> Dict[str, Any]:
        coords = [self.x, self.y] if self.z is None else [self.x, self.y, self.z]
        return {"type": "Point", "coordinates": coords}

    @property
    def esri_geometry_type(self) -> str:
        return "esriGeometryPoint"

    def to_esri_json(self) -> Dict[str, Any]:
        data = {"x": self.x, "y": self.y}
        if self.z is not None:
            data["z"] = self.z
        return data

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"


class Polyline(Geometry):
    """A sequence of connected line segments."""
    def __init__(self, coordinates: List[Tuple[float, float]]):
        if len(coordinates) < 2:
            raise ValueError("Polyline requires at least 2 points.")
        self.coordinates = [Point(x, y) for (x, y) in coordinates]

    @property
    def points(self) -> List[Point]:
        return self.coordinates

    def length(self) -> float:
        """Calculates total Euclidean length."""
        tot = 0.0
        for i in range(len(self.coordinates) - 1):
            tot += self.coordinates[i].distance_to(self.coordinates[i + 1])
        return tot

    def get_envelope(self) -> Envelope:
        xs = [p.x for p in self.coordinates]
        ys = [p.y for p in self.coordinates]
        return Envelope(min(xs), min(ys), max(xs), max(ys))

    def to_geojson(self) -> Dict[str, Any]:
        return {
            "type": "LineString",
            "coordinates": [[p.x, p.y] for p in self.coordinates]
        }

    @property
    def esri_geometry_type(self) -> str:
        return "esriGeometryPolyline"

    def to_esri_json(self) -> Dict[str, Any]:
        return {"paths": [[[p.x, p.y] for p in self.coordinates]]}

    def __repr__(self) -> str:
        return f"Polyline(points={len(self.coordinates)}, length={self.length():.2f})"


class Polygon(Geometry):
    """
    A 2D surface enclosed by one outer linear ring and optional inner rings (holes).
    """
    def __init__(self, exterior: List[Tuple[float, float]], interiors: Optional[List[List[Tuple[float, float]]]] = None):
        if len(exterior) < 3:
            raise ValueError("Polygon exterior requires at least 3 points.")
        # Ensure exterior ring is closed
        if exterior[0] != exterior[-1]:
            exterior = list(exterior) + [exterior[0]]
        self.exterior = [Point(x, y) for (x, y) in exterior]
        self.interiors = []
        if interiors:
            for hole in interiors:
                if len(hole) >= 3:
                    if hole[0] != hole[-1]:
                        hole = list(hole) + [hole[0]]
                    self.interiors.append([Point(x, y) for (x, y) in hole])

    @staticmethod
    def _ring_area(pts: List[Point]) -> float:
        """Calculates signed area using Green's theorem / Shoelace formula."""
        area = 0.0
        n = len(pts)
        for i in range(n - 1):
            area += pts[i].x * pts[i + 1].y - pts[i + 1].x * pts[i].y
        return area / 2.0

    @property
    def area(self) -> float:
        """Calculates absolute planar area subtracting holes."""
        total = abs(self._ring_area(self.exterior))
        for hole in self.interiors:
            total -= abs(self._ring_area(hole))
        return max(0.0, total)

    @property
    def centroid(self) -> Point:
        """Calculates geometric centroid."""
        cx = 0.0
        cy = 0.0
        pts = self.exterior
        n = len(pts)
        signed_area = self._ring_area(pts)
        if abs(signed_area) < 1e-9:
            return pts[0]
        for i in range(n - 1):
            factor = (pts[i].x * pts[i + 1].y - pts[i + 1].x * pts[i].y)
            cx += (pts[i].x + pts[i + 1].x) * factor
            cy += (pts[i].y + pts[i + 1].y) * factor
        cx /= (6.0 * signed_area)
        cy /= (6.0 * signed_area)
        return Point(cx, cy)

    def contains_point(self, pt: Point) -> bool:
        """
        Ray-casting point-in-polygon algorithm (Jordan Curve Theorem).
        Checks if point is inside exterior ring and not inside any interior hole.
        """
        env = self.get_envelope()
        if not env.contains_point(pt.x, pt.y):
            return False

        def _point_in_ring(p: Point, ring: List[Point]) -> bool:
            inside = False
            n = len(ring)
            for i in range(n - 1):
                p1 = ring[i]
                p2 = ring[i + 1]
                if (p1.y > p.y) != (p2.y > p.y):
                    intersect_x = (p2.x - p1.x) * (p.y - p1.y) / (p2.y - p1.y + 1e-15) + p1.x
                    if p.x < intersect_x:
                        inside = not inside
            return inside

        if not _point_in_ring(pt, self.exterior):
            return False

        # If inside a hole, then not in polygon
        for hole in self.interiors:
            if _point_in_ring(pt, hole):
                return False

        return True

    def get_envelope(self) -> Envelope:
        xs = [p.x for p in self.exterior]
        ys = [p.y for p in self.exterior]
        return Envelope(min(xs), min(ys), max(xs), max(ys))

    def to_geojson(self) -> Dict[str, Any]:
        rings = [[[p.x, p.y] for p in self.exterior]]
        for hole in self.interiors:
            rings.append([[p.x, p.y] for p in hole])
        return {"type": "Polygon", "coordinates": rings}

    @property
    def esri_geometry_type(self) -> str:
        return "esriGeometryPolygon"

    def to_esri_json(self) -> Dict[str, Any]:
        rings = [[[p.x, p.y] for p in self.exterior]]
        for hole in self.interiors:
            rings.append([[p.x, p.y] for p in hole])
        return {"rings": rings}

    def __repr__(self) -> str:
        return f"Polygon(vertices={len(self.exterior)}, holes={len(self.interiors)}, area={self.area:.2f})"
