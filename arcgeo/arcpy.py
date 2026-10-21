"""
arcgeo.arcpy - ArcGIS ArcPy Compatibility Layer
Implements the familiar arcpy scripting interface used in ArcGIS Pro:
- arcpy.analysis.Buffer
- arcpy.analysis.SpatialJoin
- arcpy.analysis.Clip
- arcpy.management.GetCount
- arcpy.management.SelectLayerByAttribute
- arcpy.management.SelectLayerByLocation
- arcpy.SpatialReference
- arcpy.env (workspace, overwriteOutput)
"""

from typing import Union, List, Dict, Any, Optional
from arcgeo.geometry import SpatialReference, Point, Polygon, Polyline
from arcgeo.data import FeatureLayer, Feature
from arcgeo.geoprocessing import Geoprocessing


class Environment:
    def __init__(self):
        self.workspace: str = ""
        self.overwriteOutput: bool = True


env = Environment()


class Analysis:
    @staticmethod
    def Buffer(in_features: FeatureLayer, out_feature_class: str, buffer_distance_or_field: Union[float, str],
               line_side: str = "FULL", line_end_type: str = "ROUND") -> FeatureLayer:
        """
        ArcPy Buffer tool.
        buffer_distance_or_field can be a float or string like '50 Kilometers', '1.5 DecimalDegrees'.
        """
        dist = 1.0
        if isinstance(buffer_distance_or_field, (int, float)):
            dist = float(buffer_distance_or_field)
        elif isinstance(buffer_distance_or_field, str):
            parts = buffer_distance_or_field.strip().split()
            val = float(parts[0])
            unit = parts[1].lower() if len(parts) > 1 else "degrees"
            if "kilo" in unit:
                # 1 degree lat is approx 111 km
                dist = val / 111.0
            elif "meter" in unit:
                dist = val / 111000.0
            else:
                dist = val

        return Geoprocessing.buffer_layer(in_features, distance=dist, output_name=out_feature_class)

    @staticmethod
    def SpatialJoin(target_features: FeatureLayer, join_features: FeatureLayer, out_feature_class: str,
                    join_operation: str = "JOIN_ONE_TO_ONE", join_type: str = "KEEP_ALL") -> FeatureLayer:
        """ArcPy SpatialJoin tool."""
        return Geoprocessing.spatial_join(target_features, join_features, out_feature_class)

    @staticmethod
    def Clip(in_features: FeatureLayer, clip_features: FeatureLayer, out_feature_class: str) -> FeatureLayer:
        """ArcPy Clip tool."""
        # Merge all clip polygon boundaries
        if not clip_features.features:
            return in_features
        first_poly = next((f.geometry for f in clip_features.features.values() if isinstance(f.geometry, Polygon)), None)
        if not first_poly:
            return in_features
        return Geoprocessing.clip_layer(in_features, first_poly, out_feature_class)


class Management:
    @staticmethod
    def GetCount(in_rows: Union[FeatureLayer, str, Any]) -> int:
        """Returns the number of rows/features in a layer."""
        if isinstance(in_rows, str):
            if hasattr(env, "active_layers") and env.active_layers:
                for l in env.active_layers:
                    if l.name == in_rows:
                        return len(l)
        return len(in_rows)

    @staticmethod
    def SelectLayerByAttribute(in_layer_or_view: FeatureLayer, selection_type: str = "NEW_SELECTION",
                               where_clause: str = "") -> List[Feature]:
        """Filters layer features by a where clause expression."""
        if not where_clause:
            return list(in_layer_or_view.features.values())

        # Simple where clause evaluator (e.g., "POP > 5000000" or "REGION = 'Sudeste'")
        def _predicate(attrs: Dict[str, Any]) -> bool:
            try:
                # Replace SQL-like single = with == for eval safety
                safe_expr = where_clause.replace(" = ", " == ").replace(" AND ", " and ").replace(" OR ", " or ")
                return bool(eval(safe_expr, {}, attrs))
            except Exception:
                return False

        return in_layer_or_view.select_by_attributes(_predicate)

    @staticmethod
    def SelectLayerByLocation(in_layer: FeatureLayer, overlap_type: str = "INTERSECT",
                              select_features: FeatureLayer = None) -> List[Feature]:
        """Selects features based on spatial relationship with another layer."""
        if not select_features or not select_features.features:
            return []
        results = []
        for sf in select_features.features.values():
            rel = "contains" if overlap_type in ("COMPLETELY_CONTAINS", "CONTAINS") else "intersects"
            results.extend(in_layer.select_by_location(sf.geometry, relation=rel))
        return list({f.fid: f for f in results}.values())


analysis = Analysis()
management = Management()
