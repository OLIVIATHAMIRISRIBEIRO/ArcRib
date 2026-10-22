"""
arcgeo.basemaps - Live ArcGIS Online Basemap Service Provider
Fetches, caches, and renders official ESRI Basemap tile services:
- Esri World Imagery (Satellite)
- Esri World Topo Map (Topographic)
- Esri World Street Map (Streets)
- Esri World Dark Gray Canvas (Dark)
"""

import os
import math
import urllib.request
from typing import Dict, Tuple, List, Optional
from PIL import Image, ImageTk
from arcgeo.geometry import Envelope


ESRI_BASEMAPS = {
    "Esri Imagem de Satélite": "https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    "Esri Topográfico": "https://services.arcgisonline.com/arcgis/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
    "Esri Ruas": "https://services.arcgisonline.com/arcgis/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    "Esri Dark Canvas": "https://services.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
    "Esri Topo": "https://services.arcgisonline.com/arcgis/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
    "World Topographic Map": "https://services.arcgisonline.com/arcgis/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
    "World Hillshade": "https://services.arcgisonline.com/arcgis/rest/services/Elevation/World_Hillshade/MapServer/tile/{z}/{y}/{x}",
    "Esri Hillshade": "https://services.arcgisonline.com/arcgis/rest/services/Elevation/World_Hillshade/MapServer/tile/{z}/{y}/{x}",
    "Esri Streets": "https://services.arcgisonline.com/arcgis/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    "Esri Satellite": "https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
}

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", ".cache", "esri_tiles")
os.makedirs(CACHE_DIR, exist_ok=True)


class EsriBasemapManager:
    def __init__(self, basemap_name: str = "Esri Dark Canvas"):
        self.current_basemap = basemap_name
        self._tile_cache: Dict[str, Image.Image] = {}

    def set_basemap(self, name: str):
        if name in ESRI_BASEMAPS:
            self.current_basemap = name
            self._tile_cache.clear()

    @staticmethod
    def deg2num(lat_deg: float, lon_deg: float, zoom: int) -> Tuple[int, int]:
        """Converts (lat, lon) to tile (x, y) at given zoom level."""
        lat_rad = math.radians(max(min(lat_deg, 85.0511), -85.0511))
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return xtile, ytile

    @staticmethod
    def num2deg(xtile: int, ytile: int, zoom: int) -> Tuple[float, float]:
        """Converts tile coordinates (x, y) to top-left (lat, lon)."""
        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
        lat_deg = math.degrees(lat_rad)
        return lat_deg, lon_deg

    def calculate_zoom_level(self, extent: Envelope, screen_width: int) -> int:
        """Determines best tile zoom level (0 to 18) for current extent."""
        span_deg = max(extent.width, 0.001)
        # 360 degrees / span * (screen_width / 256)
        scale = (360.0 / span_deg) * (screen_width / 256.0)
        zoom = int(math.log2(max(scale, 1.0)))
        return max(0, min(zoom, 16))

    def fetch_tile(self, zoom: int, x: int, y: int) -> Optional[Image.Image]:
        """Fetches a tile from disk cache or ESRI REST API."""
        key = f"{self.current_basemap}_{zoom}_{x}_{y}"
        if key in self._tile_cache:
            return self._tile_cache[key]

        safe_bm_name = self.current_basemap.replace(" ", "_")
        tile_path = os.path.join(CACHE_DIR, f"{safe_bm_name}_{zoom}_{x}_{y}.png")

        if os.path.exists(tile_path):
            try:
                img = Image.open(tile_path).convert("RGBA")
                self._tile_cache[key] = img
                return img
            except Exception:
                pass

        url_template = ESRI_BASEMAPS.get(self.current_basemap)
        if not url_template:
            return None

        url = url_template.format(z=zoom, x=x, y=y)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ArcRib-GIS/1.0"})
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                data = resp.read()
                with open(tile_path, "wb") as f:
                    f.write(data)
                img = Image.open(tile_path).convert("RGBA")
                self._tile_cache[key] = img
                return img
        except Exception:
            return None
