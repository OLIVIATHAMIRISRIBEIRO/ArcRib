"""
tests/test_arcgeo.py - Comprehensive Unit & Benchmark Tests for ArcGEO
Tests all geometric, spatial indexing, geoprocessing, and mapping operations
against mathematical baselines and standard OGC / ESRI ArcGIS behaviors.
"""

import unittest
import math
import os
import sys

# Ensure arcgeo package is in Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from arcgeo.geometry import Point, Polyline, Polygon, Envelope, SpatialReference
from arcgeo.spatial_index import SpatialIndex
from arcgeo.data import Feature, FeatureLayer
from arcgeo.geoprocessing import Geoprocessing
from arcgeo.mapping import Map, SimpleRenderer, UniqueValueRenderer


class TestGeometryPrimitives(unittest.TestCase):
    def test_point_distances(self):
        # 3-4-5 right triangle Euclidean test
        p1 = Point(0, 0)
        p2 = Point(3, 4)
        self.assertAlmostEqual(p1.distance_to(p2), 5.0, places=7)

        # Geodesic distance test: Sao Paulo (-46.6333, -23.5505) to Rio de Janeiro (-43.1729, -22.9068)
        # Expected distance: ~357 km = 357,000 meters (+- 5 km on spherical model)
        sp = Point(-46.6333, -23.5505)
        rj = Point(-43.1729, -22.9068)
        dist_km = sp.geodesic_distance_to(rj) / 1000.0
        self.assertTrue(350.0 <= dist_km <= 365.0, f"Calculated distance {dist_km} km is outside expected range")

    def test_coordinate_projections(self):
        # Round trip test: WGS84 -> Web Mercator -> WGS84
        lon, lat = -46.6333, -23.5505
        mx, my = SpatialReference.wgs84_to_web_mercator(lon, lat)
        rt_lon, rt_lat = SpatialReference.web_mercator_to_wgs84(mx, my)
        self.assertAlmostEqual(lon, rt_lon, places=5)
        self.assertAlmostEqual(lat, rt_lat, places=5)

    def test_polygon_area_shoelace(self):
        # 10x10 square -> Area = 100
        square = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
        self.assertAlmostEqual(square.area, 100.0, places=5)

        # Centroid of 10x10 square -> (5, 5)
        c = square.centroid
        self.assertAlmostEqual(c.x, 5.0, places=5)
        self.assertAlmostEqual(c.y, 5.0, places=5)

        # Square with a 2x2 hole (Area: 100 - 4 = 96)
        square_with_hole = Polygon(
            exterior=[(0, 0), (10, 0), (10, 10), (0, 10)],
            interiors=[[(4, 4), (6, 4), (6, 6), (4, 6)]]
        )
        self.assertAlmostEqual(square_with_hole.area, 96.0, places=5)

    def test_point_in_polygon_ray_casting(self):
        poly = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)], interiors=[[(4, 4), (6, 4), (6, 6), (4, 6)]])
        # Inside outer ring, outside hole
        self.assertTrue(poly.contains_point(Point(2, 2)))
        # Outside outer ring
        self.assertFalse(poly.contains_point(Point(12, 5)))
        self.assertFalse(poly.contains_point(Point(-1, 5)))
        # Inside hole (should return False)
        self.assertFalse(poly.contains_point(Point(5, 5)))

    def test_polyline_length(self):
        # Polyline along axis: (0,0) -> (0,10) -> (10,10) -> length = 20
        line = Polyline([(0, 0), (0, 10), (10, 10)])
        self.assertAlmostEqual(line.length(), 20.0, places=5)


class TestSpatialIndex(unittest.TestCase):
    def test_quadtree_vs_linear_search(self):
        index = SpatialIndex(initial_bounds=Envelope(-100, -100, 100, 100), capacity=4)
        points = []
        # Insert grid of 100 points
        for x in range(10):
            for y in range(10):
                pt = Point(x * 10, y * 10)
                item_id = f"pt_{x}_{y}"
                points.append((pt, item_id))
                index.insert(pt, item_id)

        # Query a sub-box: [25, 25] to [65, 65]
        search_box = Envelope(25, 25, 65, 65)
        indexed_results = set(index.query_envelope(search_box))

        # Naive linear ground truth
        naive_results = set()
        for pt, item_id in points:
            if search_box.contains_point(pt.x, pt.y):
                naive_results.add(item_id)

        # QuadTree must match ground truth exactly
        self.assertEqual(indexed_results, naive_results)
        self.assertEqual(len(indexed_results), 16)  # x in [30,40,50,60], y in [30,40,50,60] = 4x4 = 16


class TestFeatureLayerAndData(unittest.TestCase):
    def test_layer_operations(self):
        layer = FeatureLayer("Cities", geometry_type="Point")
        layer.add_feature(Point(-46.63, -23.55), {"name": "Sao Paulo", "pop": 12300000})
        layer.add_feature(Point(-43.17, -22.90), {"name": "Rio de Janeiro", "pop": 6700000})
        layer.add_feature(Point(-47.88, -15.78), {"name": "Brasilia", "pop": 3000000})

        self.assertEqual(len(layer), 3)

        # Attribute query
        large_cities = layer.select_by_attributes(lambda attrs: attrs["pop"] > 5000000)
        self.assertEqual(len(large_cities), 2)
        names = {f.get("name") for f in large_cities}
        self.assertEqual(names, {"Sao Paulo", "Rio de Janeiro"})

        # GeoJSON export verification
        geojson = layer.to_geojson()
        self.assertEqual(geojson["type"], "FeatureCollection")
        self.assertEqual(len(geojson["features"]), 3)


class TestGeoprocessing(unittest.TestCase):
    def test_buffer_point_area(self):
        # Buffer of radius r around origin
        r = 10.0
        buf = Geoprocessing.buffer_point(Point(0, 0), distance=r, num_segments=64)
        expected_area = math.pi * (r ** 2)
        # 64-sided regular polygon area is slightly under pi*r^2
        self.assertAlmostEqual(buf.area, expected_area, delta=expected_area * 0.01)

    def test_spatial_join(self):
        # Create a points layer and a polygon zones layer
        pts_layer = FeatureLayer("Sensors", "Point")
        pts_layer.add_feature(Point(5, 5), {"sensor_id": "S1"})
        pts_layer.add_feature(Point(25, 25), {"sensor_id": "S2"})

        poly_layer = FeatureLayer("Zones", "Polygon")
        zone_a = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
        poly_layer.add_feature(zone_a, {"zone_name": "Sector Alpha"})

        joined = Geoprocessing.spatial_join(pts_layer, poly_layer, "JoinedSensors")
        f1 = joined.get_feature(1)
        self.assertEqual(f1.get("JOIN_zone_name"), "Sector Alpha")

        f2 = joined.get_feature(2)
        self.assertIsNone(f2.get("JOIN_zone_name"))

    def test_summary_statistics(self):
        layer = FeatureLayer("Parcels", "Polygon")
        for i, val in enumerate([100, 200, 300, 400]):
            layer.add_feature(Point(i, i), {"value": val})

        stats = Geoprocessing.summary_statistics(layer, "value")
        self.assertEqual(stats["count"], 4)
        self.assertEqual(stats["sum"], 1000.0)
        self.assertEqual(stats["mean"], 250.0)
        self.assertEqual(stats["min"], 100.0)
        self.assertEqual(stats["max"], 400.0)


class TestMappingAndRendering(unittest.TestCase):
    def test_map_export_svg(self):
        mp = Map("Test Map")
        layer = FeatureLayer("Points", "Point")
        layer.add_feature(Point(10, 10), {"NAME": "Point A"})
        layer.add_feature(Point(20, 20), {"NAME": "Point B"})
        mp.add_layer(layer, SimpleRenderer(fill="#ef4444"))

        svg = mp.export_svg(400, 300)
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue("Test Map" in svg)
        self.assertTrue("Point A" in svg)
        self.assertTrue("Point B" in svg)
        self.assertTrue("circle" in svg)


class TestArcGISStandards(unittest.TestCase):
    def test_esri_fields_and_json(self):
        poly_layer = FeatureLayer("Parcels", "Polygon")
        sq = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
        feat = poly_layer.add_feature(sq, {"PARCEL_ID": "A101"})

        # Check standard ArcGIS Geodatabase fields
        self.assertEqual(feat.objectid, 1)
        self.assertEqual(feat.get("OBJECTID"), 1)
        self.assertAlmostEqual(feat.get("Shape_Area"), 100.0, places=3)

        # Check ESRI FeatureSet JSON format
        esri_json = poly_layer.to_esri_json()
        self.assertEqual(esri_json["objectIdFieldName"], "OBJECTID")
        self.assertEqual(esri_json["geometryType"], "esriGeometryPolygon")
        self.assertEqual(esri_json["spatialReference"]["wkid"], 4326)
        self.assertEqual(len(esri_json["features"]), 1)
        self.assertIn("rings", esri_json["features"][0]["geometry"])

    def test_arcpy_module(self):
        import arcpy

        cities = FeatureLayer("Cities", "Point")
        cities.add_feature(Point(-46.63, -23.55), {"NAME": "Sao Paulo", "POP": 12000000})
        cities.add_feature(Point(-43.17, -22.90), {"NAME": "Rio", "POP": 6000000})

        # Test arcpy.management.GetCount
        count = arcpy.management.GetCount(cities)
        self.assertEqual(count, 2)

        # Test arcpy.analysis.Buffer
        buf_layer = arcpy.analysis.Buffer(cities, "Cities_Buffer", "50 Kilometers")
        self.assertEqual(len(buf_layer), 2)
        self.assertEqual(buf_layer.esri_geometry_type, "esriGeometryPolygon")

        # Test arcpy.management.SelectLayerByAttribute
        selected = arcpy.management.SelectLayerByAttribute(cities, where_clause="POP > 10000000")
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].get("NAME"), "Sao Paulo")

    def test_esri_basemap_tile_math(self):
        from arcgeo.basemaps import EsriBasemapManager
        mgr = EsriBasemapManager()
        # Test Sao Paulo (-23.5505, -46.6333) at zoom 5
        xtile, ytile = mgr.deg2num(-23.5505, -46.6333, 5)
        self.assertTrue(0 <= xtile < 32)
        self.assertTrue(0 <= ytile < 32)
        # Invert back: tile top-left corner (Tile covers [-56.25°, -45.0°])
        lat_back, lon_back = mgr.num2deg(xtile, ytile, 5)
        self.assertTrue(-30.0 <= lat_back <= -15.0)
        self.assertTrue(-60.0 <= lon_back <= -40.0)


if __name__ == "__main__":
    unittest.main()
