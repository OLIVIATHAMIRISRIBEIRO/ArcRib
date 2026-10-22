"""
arcrib.sample_data - Realistic Sample GIS Datasets matching ArcGIS Pro Tutorials
Includes:
- Christchurch Urban Area (New Zealand - Image 4 & 5):
  - Liquefaction Hazard & Land Use Polygons (Yellow, Orange, Red, Green, Water)
  - Bus Routes Polylines (City Connector, Ferry, Metro Line, Suburban Link)
  - Bus Stops Points
  - Meshblock Points
- Brasil Geografico (South America - Standard Dataset):
  - Capitais do Brasil
  - Regioes / Estados
  - Zonas de Influencia
"""

from typing import Dict, Any, List
from arcgeo.geometry import Point, Polyline, Polygon, Envelope
from arcgeo.data import FeatureLayer, Feature
from arcgeo.mapping import SimpleRenderer, UniqueValueRenderer


def load_christchurch_project() -> Dict[str, Any]:
    """Generates the exact layers shown in ArcGIS Pro Screenshots (Image 4 & 5)."""
    # 1. UrbanArea / Liquefaction Risk Zones (Polygons)
    urban_layer = FeatureLayer("UrbanArea", geometry_type="Polygon")

    # High Liquefaction Zone (Red along Avon river)
    poly_high = Polygon([
        (172.645, -43.525), (172.665, -43.522), (172.678, -43.528),
        (172.682, -43.535), (172.670, -43.538), (172.650, -43.532)
    ])
    urban_layer.add_feature(poly_high, {
        "ZONE_NAME": "Avon River Corridor - High Hazard",
        "RISK_LEVEL": "High",
        "AREA_HA": 340.5
    })

    # Moderate Risk Zone (Orange)
    poly_mod = Polygon([
        (172.620, -43.518), (172.655, -43.515), (172.685, -43.522),
        (172.690, -43.542), (172.660, -43.548), (172.625, -43.538)
    ])
    urban_layer.add_feature(poly_mod, {
        "ZONE_NAME": "Central East - Moderate Hazard",
        "RISK_LEVEL": "Moderate",
        "AREA_HA": 820.0
    })

    # Low Risk Urban Residential (Yellow)
    poly_low = Polygon([
        (172.585, -43.510), (172.635, -43.505), (172.695, -43.512),
        (172.710, -43.555), (172.640, -43.565), (172.580, -43.545)
    ])
    urban_layer.add_feature(poly_low, {
        "ZONE_NAME": "West & Suburbs - Low Hazard",
        "RISK_LEVEL": "Low",
        "AREA_HA": 1940.2
    })

    # Hagley Park & Reserves (Green)
    poly_park = Polygon([
        (172.610, -43.530), (172.625, -43.525), (172.630, -43.536),
        (172.615, -43.540)
    ])
    urban_layer.add_feature(poly_park, {
        "ZONE_NAME": "Hagley Park Reserve",
        "RISK_LEVEL": "Park / Open Space",
        "AREA_HA": 165.0
    })

    # Avon River Waterway (Light Blue)
    poly_river = Polygon([
        (172.625, -43.531), (172.642, -43.527), (172.662, -43.524),
        (172.675, -43.530), (172.660, -43.533), (172.640, -43.534),
        (172.625, -43.533)
    ])
    urban_layer.add_feature(poly_river, {
        "ZONE_NAME": "Avon River Waterway",
        "RISK_LEVEL": "Water",
        "AREA_HA": 45.8
    })

    urban_renderer = UniqueValueRenderer(
        field="RISK_LEVEL",
        color_map={
            "High": "#dc2626",            # Red
            "Moderate": "#f59e0b",        # Orange
            "Low": "#fef08a",             # Light Yellow
            "Park / Open Space": "#86efac", # Light Green
            "Water": "#38bdf8"            # River Blue
        },
        default_fill="#fef08a"
    )

    # 2. Bus Routes (Polylines with categorized Types - Image 5)
    routes_layer = FeatureLayer("Bus Routes", geometry_type="Polyline")

    # City Connector (Green)
    routes_layer.add_feature(
        Polyline([
            (172.595, -43.535), (172.615, -43.534), (172.635, -43.532),
            (172.655, -43.533), (172.685, -43.535)
        ]),
        {"ROUTE_ID": "101", "NAME": "Main City Connector", "Type": "City Connector", "FREQUENCY_MIN": 10}
    )

    # Ferry (Blue dashed)
    routes_layer.add_feature(
        Polyline([
            (172.685, -43.535), (172.705, -43.538), (172.720, -43.545),
            (172.725, -43.555)
        ]),
        {"ROUTE_ID": "F1", "NAME": "Lyttelton Harbor Ferry", "Type": "Ferry", "FREQUENCY_MIN": 30}
    )

    # Metro Line (Dark Blue)
    routes_layer.add_feature(
        Polyline([
            (172.632, -43.510), (172.634, -43.525), (172.635, -43.532),
            (172.636, -43.548), (172.638, -43.560)
        ]),
        {"ROUTE_ID": "M1", "NAME": "North-South Metro Corridor", "Type": "Metro Line", "FREQUENCY_MIN": 8}
    )

    # Suburban Link (Magenta)
    routes_layer.add_feature(
        Polyline([
            (172.610, -43.520), (172.630, -43.524), (172.650, -43.528),
            (172.670, -43.540), (172.690, -43.550)
        ]),
        {"ROUTE_ID": "S4", "NAME": "Riccarton - Sumner Link", "Type": "Suburban Link", "FREQUENCY_MIN": 15}
    )

    routes_renderer = UniqueValueRenderer(
        field="Type",
        color_map={
            "City Connector": "#059669",  # Green
            "Ferry": "#2563eb",           # Blue
            "Metro Line": "#4338ca",      # Dark Blue / Indigo
            "Suburban Link": "#db2777"    # Magenta / Deep Pink
        },
        default_fill="#475569"
    )

    # 3. Bus Stops (Points - Image 5)
    stops_layer = FeatureLayer("Bus Stops", geometry_type="Point")
    stops_data = [
        ("Cathedral Square Interchange", 172.636, -43.531, "Main Hub"),
        ("Christchurch Hospital", 172.625, -43.534, "Medical"),
        ("University of Canterbury", 172.580, -43.523, "Education"),
        ("Riccarton Mall Stop", 172.595, -43.534, "Commercial"),
        ("Linwood Transport Terminal", 172.672, -43.534, "Transfer Hub"),
        ("Hagley Park North", 172.618, -43.525, "Park"),
        ("New Brighton Pier Terminal", 172.730, -43.508, "Coastal"),
        ("Sumner Beach Terminal", 172.760, -43.565, "Coastal"),
        ("Lyttelton Port Interchange", 172.718, -43.602, "Ferry Hub"),
        ("Moorhouse Rail Interchange", 172.636, -43.542, "Rail/Bus"),
        ("Bealey Ave North Stop", 172.635, -43.518, "Suburban"),
        ("Eastgate Mall Stop", 172.675, -43.535, "Commercial"),
        ("Papanui North Stop", 172.605, -43.495, "Commercial"),
        ("Hornby Hub Stop", 172.525, -43.545, "Commercial"),
        ("Airport Terminal", 172.535, -43.488, "Airport")
    ]
    for name, lon, lat, cat in stops_data:
        stops_layer.add_feature(Point(lon, lat), {
            "NAME": name,
            "CATEGORY": cat,
            "SHELTER": "Yes",
            "ACCESSIBLE": "Yes"
        })

    stops_renderer = SimpleRenderer(fill="#10b981", stroke="#064e3b", point_radius=5.5)

    # 4. Meshblock Points (Census / Demographics)
    mesh_layer = FeatureLayer("MeshblockPoints", geometry_type="Point")
    mesh_coords = [
        ("MB 101", 172.628, -43.528, 450),
        ("MB 102", 172.642, -43.530, 620),
        ("MB 103", 172.638, -43.535, 510),
        ("MB 104", 172.621, -43.538, 380),
        ("MB 105", 172.650, -43.526, 740),
        ("MB 106", 172.660, -43.532, 590),
        ("MB 107", 172.632, -43.522, 680),
        ("MB 108", 172.645, -43.540, 420)
    ]
    for name, lon, lat, pop in mesh_coords:
        mesh_layer.add_feature(Point(lon, lat), {
            "NAME": name,
            "POPULATION": pop,
            "DENSITY": pop / 0.15
        })
    mesh_renderer = SimpleRenderer(fill="#6366f1", stroke="#312e81", point_radius=4.0)

    return {
        "project_name": "Christchurch Transportation.aprx",
        "map_name": "Christchurch Urban Area",
        "extent": Envelope(172.50, -43.62, 172.78, -43.47),
        "layers": [
            (urban_layer, urban_renderer),
            (routes_layer, routes_renderer),
            (stops_layer, stops_renderer),
            (mesh_layer, mesh_renderer)
        ]
    }


def load_brasil_project() -> Dict[str, Any]:
    """Generates the Brasil Geografico project."""
    zones = FeatureLayer("Macrorregiao_Sudeste", geometry_type="Polygon")
    sudeste_poly = Polygon([
        (-53.0, -25.5), (-39.5, -25.5), (-39.5, -14.5), (-53.0, -14.5)
    ])
    zones.add_feature(sudeste_poly, {"ZONE_NAME": "Macrorregiao Sudeste / Centro", "AREA_KM2": 924511})
    zones_renderer = SimpleRenderer(fill="#1e293b", stroke="#475569", stroke_width=2.0, opacity=0.35)

    cities = FeatureLayer("Capitais_Brasil", geometry_type="Point")
    city_data = [
        ("Sao Paulo", -46.6333, -23.5505, 12300000, "Sudeste"),
        ("Rio de Janeiro", -43.1729, -22.9068, 6700000, "Sudeste"),
        ("Belo Horizonte", -43.9378, -19.9208, 2500000, "Sudeste"),
        ("Brasilia", -47.8825, -15.7942, 3050000, "Centro-Oeste"),
        ("Curitiba", -49.2731, -25.4284, 1950000, "Sul"),
        ("Salvador", -38.5108, -12.9714, 2900000, "Nordeste"),
        ("Porto Alegre", -51.2177, -30.0346, 1490000, "Sul"),
        ("Recife", -34.8770, -8.0578, 1650000, "Nordeste"),
        ("Fortaleza", -38.5434, -3.7172, 2680000, "Nordeste"),
        ("Manaus", -60.0217, -3.1190, 2210000, "Norte"),
        ("Goiania", -49.2550, -16.6869, 1530000, "Centro-Oeste"),
        ("Cuiaba", -56.0967, -15.6014, 618000, "Centro-Oeste")
    ]
    for name, lon, lat, pop, reg in city_data:
        cities.add_feature(Point(lon, lat), {
            "NAME": name,
            "POP": pop,
            "REGION": reg,
            "STATUS": "Capital"
        })

    cities_renderer = UniqueValueRenderer(
        field="REGION",
        color_map={
            "Sudeste": "#ef4444",
            "Sul": "#10b981",
            "Centro-Oeste": "#f59e0b",
            "Nordeste": "#a855f7",
            "Norte": "#06b6d4"
        }
    )

    return {
        "project_name": "Brasil_Geografico.aprx",
        "map_name": "Brasil Geografico",
        "extent": Envelope(-60.0, -35.0, -35.0, 5.0),
        "layers": [
            (zones, zones_renderer),
            (cities, cities_renderer)
        ]
    }


def load_myproject_map() -> Dict[str, Any]:
    """
    Generates the exact ArcGIS Pro 3.x default project shown in user screenshot:
    - Project: MyProject
    - Map: Map
    - Layers:
        1. World Topographic Map
        2. World Hillshade
    - Viewport: South America / Brazil continent
    - Scale: 1:71.199.652
    """
    # 1. World Topographic Map Layer
    topo_layer = FeatureLayer("World Topographic Map", geometry_type="Polygon")

    # South American continent general outline
    sa_coast = [
        (-79.5, 9.0), (-74.2, 11.2), (-67.0, 10.5), (-60.5, 8.8), (-58.1, 6.8),
        (-55.2, 5.8), (-52.3, 4.9), (-51.2, 4.4), (-50.5, 0.0), (-48.5, -1.2),
        (-44.3, -2.5), (-38.5, -3.7), (-35.2, -5.3), (-34.8, -7.5), (-38.5, -13.0),
        (-39.0, -14.8), (-40.3, -20.3), (-42.0, -23.0), (-46.3, -24.0), (-48.5, -25.5),
        (-48.5, -27.6), (-51.2, -30.0), (-53.4, -33.7), (-56.2, -34.9), (-58.3, -34.6),
        (-57.5, -38.0), (-62.2, -38.7), (-65.0, -41.0), (-63.5, -42.5), (-67.5, -45.9),
        (-65.9, -47.7), (-69.2, -51.6), (-67.2, -55.9), (-68.5, -54.9), (-71.0, -53.5),
        (-73.5, -51.7), (-75.0, -47.0), (-73.8, -41.8), (-73.2, -39.8), (-73.0, -36.8),
        (-71.6, -33.0), (-71.3, -29.9), (-70.4, -23.6), (-70.1, -20.2), (-70.3, -18.5),
        (-72.0, -17.0), (-76.2, -13.7), (-77.0, -12.0), (-79.0, -8.1), (-81.2, -4.3),
        (-80.0, -2.2), (-80.7, -0.9), (-79.7, 0.9), (-77.1, 3.9), (-76.8, 8.4),
        (-79.5, 9.0)
    ]
    topo_layer.add_feature(Polygon(sa_coast), {
        "NAME": "South America Landmass",
        "TYPE": "Continent",
        "FILL_COLOR": "#e1ead9"
    })

    # Amazon Basin (Lush Green Lowlands)
    amazon_basin = [
        (-74.5, -3.5), (-71.0, 1.2), (-64.0, 2.5), (-56.0, 0.5), (-50.0, -1.0),
        (-48.5, -3.5), (-51.0, -8.0), (-56.0, -11.5), (-64.0, -12.0), (-69.5, -10.5),
        (-74.0, -7.0), (-74.5, -3.5)
    ]
    topo_layer.add_feature(Polygon(amazon_basin), {
        "NAME": "Amazon Basin",
        "TYPE": "Lowland",
        "FILL_COLOR": "#cee7bb"
    })

    # Brazilian Highlands (Planalto Central)
    brazil_highlands = [
        (-53.5, -12.5), (-45.0, -9.5), (-41.0, -13.5), (-41.5, -20.5),
        (-47.0, -23.5), (-52.0, -20.0), (-53.5, -12.5)
    ]
    topo_layer.add_feature(Polygon(brazil_highlands), {
        "NAME": "Brazilian Highlands",
        "TYPE": "Highland",
        "FILL_COLOR": "#e2dac5"
    })

    topo_renderer = UniqueValueRenderer(
        field="TYPE",
        color_map={
            "Continent": "#e1ead9",
            "Lowland": "#cee7bb",
            "Highland": "#e2dac5"
        },
        default_fill="#e1ead9"
    )

    # 2. World Hillshade Layer
    hillshade_layer = FeatureLayer("World Hillshade", geometry_type="Polygon")

    # Andes mountain shaded relief spine (Western South America)
    andes_spine = [
        (-76.5, 5.0), (-78.5, -0.5), (-76.0, -8.5), (-73.5, -14.5), (-69.0, -18.5),
        (-68.5, -24.0), (-70.0, -32.5), (-71.5, -42.0), (-73.0, -48.0), (-70.0, -53.5),
        (-67.5, -55.0), (-69.5, -53.0), (-71.0, -46.0), (-69.0, -38.0), (-67.0, -27.0),
        (-64.5, -18.0), (-70.0, -12.0), (-73.5, -4.5), (-75.0, 3.5), (-76.5, 5.0)
    ]
    hillshade_layer.add_feature(Polygon(andes_spine), {
        "NAME": "Andes Relief",
        "TYPE": "MountainRelief"
    })

    # Southern Patagonian Icefield / Hills
    patagonia_hills = [
        (-72.0, -46.0), (-70.0, -45.5), (-68.0, -48.5), (-70.5, -51.5), (-72.0, -46.0)
    ]
    hillshade_layer.add_feature(Polygon(patagonia_hills), {
        "NAME": "Patagonian Relief",
        "TYPE": "MountainRelief"
    })

    hillshade_renderer = SimpleRenderer(
        fill="#b8ab98",
        stroke="#9e917d",
        stroke_width=1.0,
        opacity=0.55
    )

    return {
        "project_name": "MyProject",
        "map_name": "Map",
        "extent": Envelope(-96.0, -58.0, -28.0, 15.0),
        "layers": [
            (topo_layer, topo_renderer),
            (hillshade_layer, hillshade_renderer)
        ]
    }

