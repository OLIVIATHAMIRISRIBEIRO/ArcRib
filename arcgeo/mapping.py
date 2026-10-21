"""
arcgeo.mapping - Map Presentation and Rendering Subsystem
Corresponds to ArcGIS.Desktop.Mapping.dll
Provides:
- Map: container for layers, active extent, and coordinate frame.
- Symbology Renderers: SimpleRenderer, UniqueValueRenderer.
- Vector SVG Exporter: Renders crisp SVG vector graphics for web/visual inspection.
"""

from typing import List, Dict, Any, Optional
from arcgeo.geometry import Envelope, Point, Polyline, Polygon
from arcgeo.data import FeatureLayer


class SimpleRenderer:
    """Applies uniform styling to all features in a layer."""
    def __init__(self, fill: str = "#3b82f6", stroke: str = "#1d4ed8", stroke_width: float = 1.5, opacity: float = 0.8, point_radius: float = 5.0):
        self.fill = fill
        self.stroke = stroke
        self.stroke_width = stroke_width
        self.opacity = opacity
        self.point_radius = point_radius

    def get_style(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "fill": self.fill,
            "stroke": self.stroke,
            "stroke_width": self.stroke_width,
            "opacity": self.opacity,
            "radius": self.point_radius
        }


class UniqueValueRenderer:
    """Styles features based on a discrete attribute field."""
    def __init__(self, field: str, color_map: Dict[Any, str], default_fill: str = "#9ca3af"):
        self.field = field
        self.color_map = color_map
        self.default_fill = default_fill

    def get_style(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        val = attributes.get(self.field)
        color = self.color_map.get(val, self.default_fill)
        return {
            "fill": color,
            "stroke": "#1f2937",
            "stroke_width": 1.5,
            "opacity": 0.85,
            "radius": 5.0
        }


class Map:
    """Represents a 2D Map containing an ordered stack of FeatureLayers."""
    def __init__(self, name: str = "Map"):
        self.name = name
        self.layers: List[FeatureLayer] = []
        self.renderers: Dict[str, Any] = {}

    def add_layer(self, layer: FeatureLayer, renderer: Optional[Any] = None):
        self.layers.append(layer)
        self.renderers[layer.name] = renderer or SimpleRenderer()

    def get_full_extent(self) -> Optional[Envelope]:
        extent = None
        for layer in self.layers:
            layer_ext = layer.get_extent()
            if layer_ext:
                extent = layer_ext if extent is None else extent.union(layer_ext)
        return extent

    def export_svg(self, width: int = 800, height: int = 600, padding: int = 40) -> str:
        """
        Renders the map into SVG format.
        Calculates affine transformation from geographic coordinates to canvas pixel coordinates.
        """
        extent = self.get_full_extent()
        if not extent or extent.width == 0 or extent.height == 0:
            return f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg"><text x="20" y="40">Empty Map</text></svg>'

        # Add 10% margin around extent
        margin_x = extent.width * 0.08
        margin_y = extent.height * 0.08
        xmin = extent.xmin - margin_x
        xmax = extent.xmax + margin_x
        ymin = extent.ymin - margin_y
        ymax = extent.ymax + margin_y

        draw_w = width - 2 * padding
        draw_h = height - 2 * padding

        scale_x = draw_w / (xmax - xmin)
        scale_y = draw_h / (ymax - ymin)
        scale = min(scale_x, scale_y)

        # Coordinate transformation: GIS Y goes UP, SVG Y goes DOWN
        def to_screen(gx: float, gy: float):
            sx = padding + (gx - xmin) * scale
            sy = height - padding - (gy - ymin) * scale
            return sx, sy

        svg_parts = [
            f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="background:#0f172a;font-family:sans-serif;">',
            f'<defs><filter id="glow"><feGaussianBlur stdDeviation="2" result="coloredBlur"/><feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>',
            f'<text x="{padding}" y="28" fill="#e2e8f0" font-size="18" font-weight="bold">{self.name}</text>',
            f'<rect x="{padding}" y="{padding}" width="{width - 2*padding}" height="{height - 2*padding}" fill="#1e293b" stroke="#334155" rx="6" />'
        ]

        # Render layers from bottom to top
        for layer in self.layers:
            renderer = self.renderers.get(layer.name, SimpleRenderer())
            for feat in layer.features.values():
                style = renderer.get_style(feat.attributes)
                geom = feat.geometry

                if isinstance(geom, Polygon):
                    points_str = " ".join([f"{to_screen(p.x, p.y)[0]:.1f},{to_screen(p.x, p.y)[1]:.1f}" for p in geom.exterior])
                    svg_parts.append(
                        f'<polygon points="{points_str}" fill="{style["fill"]}" stroke="{style["stroke"]}" stroke-width="{style["stroke_width"]}" fill-opacity="{style["opacity"]}" />'
                    )

                elif isinstance(geom, Polyline):
                    points_str = " ".join([f"{to_screen(p.x, p.y)[0]:.1f},{to_screen(p.x, p.y)[1]:.1f}" for p in geom.coordinates])
                    svg_parts.append(
                        f'<polyline points="{points_str}" fill="none" stroke="{style["stroke"]}" stroke-width="{style["stroke_width"]}" stroke-linecap="round" />'
                    )

                elif isinstance(geom, Point):
                    sx, sy = to_screen(geom.x, geom.y)
                    svg_parts.append(
                        f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{style["radius"]}" fill="{style["fill"]}" stroke="{style["stroke"]}" stroke-width="{style["stroke_width"]}" />'
                    )
                    # Label if available
                    label = feat.get("NAME") or feat.get("name")
                    if label:
                        svg_parts.append(
                            f'<text x="{sx + 8:.1f}" y="{sy + 4:.1f}" fill="#f1f5f9" font-size="11">{label}</text>'
                        )

        svg_parts.append('</svg>')
        return "\n".join(svg_parts)
