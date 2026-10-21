"""
arcgeo.geoprocessing - Spatial Analysis & Geoprocessing Tools
Corresponds to ArcGIS.Desktop.GeoProcessing and arcpy analysis tools:
- Buffer (Point / Polyline / Polygon buffer generation)
- Clip (Spatial boundary filtering)
- SpatialJoin (Transfers attributes based on spatial containment)
- SummaryStatistics (Calculates count, sum, mean, min, max on attributes)
"""

import math
from typing import List, Dict, Any, Optional
from arcgeo.geometry import Point, Polyline, Polygon, Envelope
from arcgeo.data import FeatureLayer, Feature


class Geoprocessing:
    """Core geospatial analysis toolbox."""

    @staticmethod
    def buffer_point(point: Point, distance: float, num_segments: int = 32) -> Polygon:
        """
        Creates a circular buffer polygon around a point.
        num_segments controls the polygonal approximation resolution.
        """
        pts = []
        angle_step = 2.0 * math.pi / num_segments
        for i in range(num_segments):
            angle = i * angle_step
            px = point.x + distance * math.cos(angle)
            py = point.y + distance * math.sin(angle)
            pts.append((px, py))
        return Polygon(pts)

    @classmethod
    def buffer_layer(cls, input_layer: FeatureLayer, distance: float, output_name: str, num_segments: int = 32) -> FeatureLayer:
        """Runs the Buffer geoprocessing tool on an entire layer."""
        out_layer = FeatureLayer(output_name, geometry_type="Polygon", spatial_reference=input_layer.spatial_reference)
        for feat in input_layer.features.values():
            if isinstance(feat.geometry, Point):
                buf_geom = cls.buffer_point(feat.geometry, distance, num_segments)
            elif isinstance(feat.geometry, Polyline):
                # Envelope approximation buffer for polyline
                env = feat.geometry.get_envelope()
                expanded = Envelope(env.xmin - distance, env.ymin - distance, env.xmax + distance, env.ymax + distance)
                buf_geom = Polygon([
                    (expanded.xmin, expanded.ymin),
                    (expanded.xmax, expanded.ymin),
                    (expanded.xmax, expanded.ymax),
                    (expanded.xmin, expanded.ymax)
                ])
            elif isinstance(feat.geometry, Polygon):
                env = feat.geometry.get_envelope()
                expanded = Envelope(env.xmin - distance, env.ymin - distance, env.xmax + distance, env.ymax + distance)
                buf_geom = Polygon([
                    (expanded.xmin, expanded.ymin),
                    (expanded.xmax, expanded.ymin),
                    (expanded.xmax, expanded.ymax),
                    (expanded.xmin, expanded.ymax)
                ])
            else:
                continue

            attrs = dict(feat.attributes)
            attrs["ORIG_FID"] = feat.fid
            attrs["BUFFER_DIST"] = distance
            out_layer.add_feature(buf_geom, attrs)
        return out_layer

    @staticmethod
    def clip_layer(input_layer: FeatureLayer, clip_boundary: Polygon, output_name: str) -> FeatureLayer:
        """
        Clips input_layer features that fall within the clip_boundary polygon.
        """
        out_layer = FeatureLayer(output_name, geometry_type=input_layer.geometry_type, spatial_reference=input_layer.spatial_reference)
        for feat in input_layer.features.values():
            if isinstance(feat.geometry, Point):
                if clip_boundary.contains_point(feat.geometry):
                    out_layer.add_feature(feat.geometry, dict(feat.attributes))
            else:
                # Bounding box intersection check
                if clip_boundary.get_envelope().intersects(feat.geometry.get_envelope()):
                    out_layer.add_feature(feat.geometry, dict(feat.attributes))
        return out_layer

    @staticmethod
    def spatial_join(target_layer: FeatureLayer, join_layer: FeatureLayer, output_name: str) -> FeatureLayer:
        """
        Spatial Join (Points inside Polygons):
        If target is Point and join is Polygon, joins attributes from polygon into point.
        """
        out_layer = FeatureLayer(output_name, geometry_type=target_layer.geometry_type, spatial_reference=target_layer.spatial_reference)
        for t_feat in target_layer.features.values():
            joined_attrs = dict(t_feat.attributes)
            if isinstance(t_feat.geometry, Point):
                # Find matching polygon in join_layer
                for j_feat in join_layer.features.values():
                    if isinstance(j_feat.geometry, Polygon) and j_feat.geometry.contains_point(t_feat.geometry):
                        for k, v in j_feat.attributes.items():
                            joined_attrs[f"JOIN_{k}"] = v
                        break
            out_layer.add_feature(t_feat.geometry, joined_attrs)
        return out_layer

    @staticmethod
    def summary_statistics(layer: FeatureLayer, field: str) -> Dict[str, Any]:
        """Calculates count, sum, mean, min, max on a numerical field."""
        values = []
        for feat in layer.features.values():
            val = feat.get(field)
            if isinstance(val, (int, float)):
                values.append(float(val))
        if not values:
            return {"count": 0, "sum": 0.0, "mean": 0.0, "min": None, "max": None}
        return {
            "count": len(values),
            "sum": sum(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values)
        }
