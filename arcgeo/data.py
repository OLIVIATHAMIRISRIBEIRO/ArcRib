"""
arcgeo.data - Feature and FeatureLayer Data Model
Corresponds to ArcGIS.Core.Data (FeatureClass, Feature, Row, Table)
Provides attributes, spatial indexing, GeoJSON serialization, and spatial querying.
"""

from typing import List, Dict, Any, Optional, Callable
from arcgeo.geometry import Geometry, Point, Polyline, Polygon, Envelope, SpatialReference
from arcgeo.spatial_index import SpatialIndex


class Feature:
    """Represents an ESRI-compatible spatial Feature with Geometry and Attributes."""
    def __init__(self, fid: int, geometry: Geometry, attributes: Optional[Dict[str, Any]] = None):
        self.fid = fid
        self.geometry = geometry
        self.attributes = dict(attributes) if attributes else {}

        # Standard ArcGIS Geodatabase fields
        if "OBJECTID" not in self.attributes:
            self.attributes["OBJECTID"] = self.fid

        if isinstance(self.geometry, Polygon):
            if "Shape_Area" not in self.attributes:
                self.attributes["Shape_Area"] = round(self.geometry.area, 4)
        elif isinstance(self.geometry, Polyline):
            if "Shape_Length" not in self.attributes:
                self.attributes["Shape_Length"] = round(self.geometry.length(), 4)

    @property
    def objectid(self) -> int:
        return self.attributes.get("OBJECTID", self.fid)

    def get(self, key: str, default: Any = None) -> Any:
        return self.attributes.get(key, default)

    def set(self, key: str, value: Any):
        self.attributes[key] = value

    def to_geojson(self) -> Dict[str, Any]:
        return {
            "type": "Feature",
            "id": self.fid,
            "geometry": self.geometry.to_geojson(),
            "properties": self.attributes
        }

    def to_esri_json(self) -> Dict[str, Any]:
        """Exports feature in native ESRI JSON format."""
        return {
            "attributes": dict(self.attributes),
            "geometry": self.geometry.to_esri_json()
        }

    def __repr__(self) -> str:
        return f"Feature(OBJECTID={self.objectid}, geom={self.geometry.esri_geometry_type}, attrs={self.attributes})"


class FeatureLayer:
    """
    An ESRI ArcGIS-compatible FeatureLayer.
    Equipped with an automatic Spatial Index for fast bounding-box lookups.
    """
    def __init__(self, name: str, geometry_type: str, spatial_reference: Optional[SpatialReference] = None):
        self.name = name
        self.geometry_type = geometry_type  # "Point", "Polyline", or "Polygon"
        self.spatial_reference = spatial_reference or SpatialReference(4326)
        self.features: Dict[int, Feature] = {}
        self.spatial_index = SpatialIndex()
        self._next_fid = 1

    @property
    def esri_geometry_type(self) -> str:
        mapping = {
            "Point": "esriGeometryPoint",
            "Polyline": "esriGeometryPolyline",
            "Polygon": "esriGeometryPolygon"
        }
        return mapping.get(self.geometry_type, "esriGeometryPoint")

    def add_feature(self, geometry: Geometry, attributes: Optional[Dict[str, Any]] = None) -> Feature:
        fid = self._next_fid
        self._next_fid += 1
        feat = Feature(fid, geometry, attributes)
        self.features[fid] = feat
        self.spatial_index.insert(geometry, fid)
        return feat

    def get_feature(self, fid: int) -> Optional[Feature]:
        return self.features.get(fid)

    def get_extent(self) -> Optional[Envelope]:
        if not self.features:
            return None
        extent = None
        for feat in self.features.values():
            env = feat.geometry.get_envelope()
            extent = env if extent is None else extent.union(env)
        return extent

    def select_by_envelope(self, search_env: Envelope) -> List[Feature]:
        """Uses spatial index to filter features intersecting the given envelope in O(log N)."""
        matching_fids = set(self.spatial_index.query_envelope(search_env))
        return [self.features[fid] for fid in matching_fids if fid in self.features]

    def select_by_attributes(self, predicate: Callable[[Dict[str, Any]], bool]) -> List[Feature]:
        """SQL-like attribute query (matches arcpy.management.SelectLayerByAttribute)."""
        return [feat for feat in self.features.values() if predicate(feat.attributes)]

    def select_by_location(self, target_geom: Geometry, relation: str = "contains") -> List[Feature]:
        """Spatial query (matches arcpy.management.SelectLayerByLocation)."""
        candidate_fids = set(self.spatial_index.query_envelope(target_geom.get_envelope()))
        results = []
        for fid in candidate_fids:
            feat = self.features[fid]
            if relation == "contains":
                if isinstance(target_geom, Polygon) and isinstance(feat.geometry, Point):
                    if target_geom.contains_point(feat.geometry):
                        results.append(feat)
                elif isinstance(feat.geometry, Polygon) and isinstance(target_geom, Point):
                    if feat.geometry.contains_point(target_geom):
                        results.append(feat)
            elif relation == "intersects":
                if target_geom.get_envelope().intersects(feat.geometry.get_envelope()):
                    results.append(feat)
        return results

    def to_geojson(self) -> Dict[str, Any]:
        """Exports the layer to GeoJSON FeatureCollection."""
        return {
            "type": "FeatureCollection",
            "name": self.name,
            "crs": {
                "type": "name",
                "properties": {"name": f"urn:ogc:def:crs:EPSG::{self.spatial_reference.wkid}"}
            },
            "features": [f.to_geojson() for f in self.features.values()]
        }

    def to_esri_json(self) -> Dict[str, Any]:
        """Exports the layer in official ESRI FeatureSet JSON format."""
        fields = [
            {"name": "OBJECTID", "type": "esriFieldTypeOID", "alias": "OBJECTID"}
        ]
        sample_attrs = {}
        for f in self.features.values():
            sample_attrs.update(f.attributes)

        for k, v in sample_attrs.items():
            if k == "OBJECTID":
                continue
            f_type = "esriFieldTypeDouble" if isinstance(v, float) else ("esriFieldTypeInteger" if isinstance(v, int) else "esriFieldTypeString")
            fields.append({"name": k, "type": f_type, "alias": k})

        return {
            "objectIdFieldName": "OBJECTID",
            "geometryType": self.esri_geometry_type,
            "spatialReference": {"wkid": self.spatial_reference.wkid, "latestWkid": self.spatial_reference.wkid},
            "fields": fields,
            "features": [f.to_esri_json() for f in self.features.values()]
        }

    def __len__(self) -> int:
        return len(self.features)

    def __repr__(self) -> str:
        return f"FeatureLayer('{self.name}', type={self.esri_geometry_type}, count={len(self.features)})"
