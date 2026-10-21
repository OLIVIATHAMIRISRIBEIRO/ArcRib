"""
arcpy.py - Top-level ArcGIS ArcPy alias
Allows direct `import arcpy` in client scripts.
"""

from arcgeo.arcpy import analysis, management, env
from arcgeo.geometry import SpatialReference, Point, Polygon, Polyline, Envelope
from arcgeo.data import FeatureLayer, Feature

__all__ = [
    "analysis", "management", "env",
    "SpatialReference", "Point", "Polygon", "Polyline", "Envelope",
    "FeatureLayer", "Feature"
]
