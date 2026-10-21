"""
ArcGEO - Pure Python GIS Engine inspired by ArcGIS Pro architecture
Modular, high-performance spatial data processing, spatial indexing, geoprocessing and cartography.
"""

from arcgeo.geometry import (
    Point, Polyline, Polygon, Envelope, SpatialReference
)
from arcgeo.spatial_index import SpatialIndex
from arcgeo.data import Feature, FeatureLayer
from arcgeo.geoprocessing import Geoprocessing
from arcgeo.mapping import Map, SimpleRenderer, UniqueValueRenderer

__version__ = "1.0.0"
__all__ = [
    "Point", "Polyline", "Polygon", "Envelope", "SpatialReference",
    "SpatialIndex", "Feature", "FeatureLayer", "Geoprocessing",
    "Map", "SimpleRenderer", "UniqueValueRenderer"
]
