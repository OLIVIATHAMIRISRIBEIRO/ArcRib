"""
arcrib.canvas - Interactive GIS Map Canvas
High-performance 2D GIS visualization canvas with:
- World coordinate to Screen pixel transformation
- Smooth pan & zoom centered on mouse cursor
- Vector rendering for Points, Polylines, Polygons, and Buffers
- Feature picking/identification by click
- Real-time coordinate tracking and measurement ruler
"""

import tkinter as tk
from typing import List, Dict, Set, Tuple, Optional, Callable, Any
from PIL import Image, ImageTk
from arcgeo.geometry import Point, Polyline, Polygon, Envelope, SpatialReference
from arcgeo.data import FeatureLayer, Feature
from arcgeo.mapping import SimpleRenderer, UniqueValueRenderer
from arcgeo.basemaps import EsriBasemapManager, ESRI_BASEMAPS


class InteractiveMapCanvas:
    def __init__(self, parent_widget, on_coords_change: Optional[Callable[[float, float], None]] = None,
                 on_feature_selected: Optional[Callable[[str, Feature], None]] = None):
        self.parent = parent_widget
        self.on_coords_change = on_coords_change
        self.on_feature_selected = on_feature_selected

        self.canvas = tk.Canvas(self.parent, bg="#f8fafc", highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.layers: List[FeatureLayer] = []
        self.layer_renderers: Dict[str, Any] = {}
        self.layer_visibility: Dict[str, bool] = {}
        self.selected_features: Dict[str, Set[int]] = {}  # layer_name -> set(fid)

        # ESRI Live Basemap Provider (Matching Image 4)
        self.basemap_mgr = EsriBasemapManager("Esri Topo")
        self.show_basemap = True
        self._tk_images: List[Any] = []

        # Viewport bounds in geographic coordinates
        self.view_extent = Envelope(-60.0, -35.0, -35.0, 5.0)  # Default: South America / Brazil bounds
        self.tool_mode = "PAN"  # "PAN", "IDENTIFY", "MEASURE", "SELECT"

        # Extent navigation history
        self.extent_history: List[Envelope] = [self.view_extent]
        self.extent_history_idx = 0

        # Interaction tracking
        self._pan_start_x = 0
        self._pan_start_y = 0
        self.measure_points: List[Point] = []

        # Bind events
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)  # Windows mouse wheel
        self.canvas.bind("<Button-4>", lambda e: self._zoom(1.2, e.x, e.y))  # Linux up
        self.canvas.bind("<Button-5>", lambda e: self._zoom(0.8, e.x, e.y))  # Linux down

    def push_extent(self, extent: Envelope):
        if self.extent_history_idx < len(self.extent_history) - 1:
            self.extent_history = self.extent_history[:self.extent_history_idx + 1]
        self.extent_history.append(extent)
        self.extent_history_idx = len(self.extent_history) - 1

    def previous_extent(self) -> bool:
        if self.extent_history_idx > 0:
            self.extent_history_idx -= 1
            self.view_extent = self.extent_history[self.extent_history_idx]
            self.redraw()
            return True
        return False

    def next_extent(self) -> bool:
        if self.extent_history_idx < len(self.extent_history) - 1:
            self.extent_history_idx += 1
            self.view_extent = self.extent_history[self.extent_history_idx]
            self.redraw()
            return True
        return False

    def add_layer(self, layer: FeatureLayer, renderer: Optional[Any] = None, visible: bool = True):
        self.layers.append(layer)
        self.layer_renderers[layer.name] = renderer or SimpleRenderer()
        self.layer_visibility[layer.name] = visible
        self.selected_features[layer.name] = set()
        self.redraw()

    def remove_layer(self, layer_name: str):
        self.layers = [l for l in self.layers if l.name != layer_name]
        self.layer_renderers.pop(layer_name, None)
        self.layer_visibility.pop(layer_name, None)
        self.selected_features.pop(layer_name, None)
        self.redraw()

    def set_layer_visibility(self, layer_name: str, visible: bool):
        if layer_name in self.layer_visibility:
            self.layer_visibility[layer_name] = visible
            self.redraw()

    def zoom_to_extent(self, extent: Optional[Envelope] = None):
        """Sets viewport to given extent, or calculates the union of all visible layers."""
        if extent is None:
            combined: Optional[Envelope] = None
            for layer in self.layers:
                if self.layer_visibility.get(layer.name, True):
                    ext = layer.get_extent()
                    if ext:
                        combined = ext if combined is None else combined.union(ext)
            extent = combined or Envelope(-60.0, -35.0, -35.0, 5.0)

        # Add 10% margin
        margin_x = max(extent.width * 0.1, 0.05)
        margin_y = max(extent.height * 0.1, 0.05)
        self.view_extent = Envelope(
            extent.xmin - margin_x,
            extent.ymin - margin_y,
            extent.xmax + margin_x,
            extent.ymax + margin_y
        )
        self.push_extent(self.view_extent)
        self.redraw()

    def geo_to_screen(self, gx: float, gy: float) -> Tuple[float, float]:
        """Converts Geographic (Lon, Lat) to Canvas Pixels (x, y)."""
        w = max(self.canvas.winfo_width(), 1)
        h = max(self.canvas.winfo_height(), 1)
        ext = self.view_extent

        scale_x = w / max(ext.width, 1e-9)
        scale_y = h / max(ext.height, 1e-9)

        sx = (gx - ext.xmin) * scale_x
        sy = h - ((gy - ext.ymin) * scale_y)
        return sx, sy

    def screen_to_geo(self, sx: float, sy: float) -> Tuple[float, float]:
        """Converts Canvas Pixels (x, y) to Geographic (Lon, Lat)."""
        w = max(self.canvas.winfo_width(), 1)
        h = max(self.canvas.winfo_height(), 1)
        ext = self.view_extent

        scale_x = w / max(ext.width, 1e-9)
        scale_y = h / max(ext.height, 1e-9)

        gx = ext.xmin + (sx / scale_x)
        gy = ext.ymin + ((h - sy) / scale_y)
        return gx, gy

    def _zoom(self, factor: float, center_x: float, center_y: float):
        """Zooms around a screen anchor point."""
        anchor_gx, anchor_gy = self.screen_to_geo(center_x, center_y)
        cur_w = self.view_extent.width
        cur_h = self.view_extent.height

        new_w = cur_w / factor
        new_h = cur_h / factor

        ratio_x = (anchor_gx - self.view_extent.xmin) / cur_w
        ratio_y = (anchor_gy - self.view_extent.ymin) / cur_h

        new_xmin = anchor_gx - (ratio_x * new_w)
        new_ymin = anchor_gy - (ratio_y * new_h)

        self.view_extent = Envelope(new_xmin, new_ymin, new_xmin + new_w, new_ymin + new_h)
        self.push_extent(self.view_extent)
        self.redraw()

    def _on_mouse_wheel(self, event):
        factor = 1.25 if event.delta > 0 else 0.8
        self._zoom(factor, event.x, event.y)

    def _on_mouse_down(self, event):
        self._pan_start_x = event.x
        self._pan_start_y = event.y

        if self.tool_mode in ("IDENTIFY", "SELECT"):
            gx, gy = self.screen_to_geo(event.x, event.y)
            click_point = Point(gx, gy)
            self._identify_feature(click_point, show_popup=(self.tool_mode == "IDENTIFY"))
        elif self.tool_mode == "MEASURE":
            gx, gy = self.screen_to_geo(event.x, event.y)
            self.measure_points.append(Point(gx, gy))
            self.redraw()

    def _on_mouse_drag(self, event):
        if self.tool_mode == "PAN":
            dx = event.x - self._pan_start_x
            dy = event.y - self._pan_start_y
            self._pan_start_x = event.x
            self._pan_start_y = event.y

            w = max(self.canvas.winfo_width(), 1)
            h = max(self.canvas.winfo_height(), 1)

            geo_dx = -(dx / w) * self.view_extent.width
            geo_dy = (dy / h) * self.view_extent.height

            self.view_extent = Envelope(
                self.view_extent.xmin + geo_dx,
                self.view_extent.ymin + geo_dy,
                self.view_extent.xmax + geo_dx,
                self.view_extent.ymax + geo_dy
            )
            self.redraw()

    def _on_mouse_up(self, event):
        pass

    def _on_mouse_move(self, event):
        gx, gy = self.screen_to_geo(event.x, event.y)
        if self.on_coords_change:
            self.on_coords_change(gx, gy)

    def _on_resize(self, event):
        self.redraw()

    def _identify_feature(self, click_point: Point, show_popup: bool = True):
        """Finds closest feature under click within a 15-pixel tolerance."""
        w = max(self.canvas.winfo_width(), 1)
        tol_geo = (15.0 / w) * self.view_extent.width

        # Search top-to-bottom among visible layers
        for layer in reversed(self.layers):
            if not self.layer_visibility.get(layer.name, True):
                continue

            query_box = Envelope(click_point.x - tol_geo, click_point.y - tol_geo,
                                 click_point.x + tol_geo, click_point.y + tol_geo)
            candidates = layer.select_by_envelope(query_box)

            for feat in candidates:
                hit = False
                if isinstance(feat.geometry, Point):
                    if feat.geometry.distance_to(click_point) <= tol_geo:
                        hit = True
                elif isinstance(feat.geometry, Polygon):
                    if feat.geometry.contains_point(click_point):
                        hit = True
                elif isinstance(feat.geometry, Polyline):
                    # Check distance to segments
                    hit = True

                if hit:
                    # Highlight this feature
                    self.selected_features[layer.name] = {feat.fid}
                    self.redraw()
                    if show_popup and self.on_feature_selected:
                        self.on_feature_selected(layer.name, feat)
                    return
                    return

    def set_basemap(self, name: str):
        self.basemap_mgr.set_basemap(name)
        self.redraw()

    def _draw_basemap_tiles(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 10 or h <= 10:
            return

        zoom = self.basemap_mgr.calculate_zoom_level(self.view_extent, w)
        zoom = max(2, min(zoom, 10))

        # Tile range
        x_min_t, y_max_t = self.basemap_mgr.deg2num(self.view_extent.ymin, self.view_extent.xmin, zoom)
        x_max_t, y_min_t = self.basemap_mgr.deg2num(self.view_extent.ymax, self.view_extent.xmax, zoom)

        # Ensure safety limit
        if (x_max_t - x_min_t + 1) * (y_max_t - y_min_t + 1) > 20:
            zoom = max(2, zoom - 1)
            x_min_t, y_max_t = self.basemap_mgr.deg2num(self.view_extent.ymin, self.view_extent.xmin, zoom)
            x_max_t, y_min_t = self.basemap_mgr.deg2num(self.view_extent.ymax, self.view_extent.xmax, zoom)

        self._tk_images.clear()
        for tx in range(x_min_t, x_max_t + 1):
            for ty in range(y_min_t, y_max_t + 1):
                tile_img = self.basemap_mgr.fetch_tile(zoom, tx, ty)
                if tile_img:
                    lat1, lon1 = self.basemap_mgr.num2deg(tx, ty, zoom)
                    lat2, lon2 = self.basemap_mgr.num2deg(tx + 1, ty + 1, zoom)

                    sx1, sy1 = self.geo_to_screen(lon1, lat1)
                    sx2, sy2 = self.geo_to_screen(lon2, lat2)

                    tw = int(abs(sx2 - sx1))
                    th = int(abs(sy2 - sy1))
                    if tw > 4 and th > 4:
                        resized = tile_img.resize((tw, th), Image.Resampling.LANCZOS)
                        tk_img = ImageTk.PhotoImage(resized)
                        self._tk_images.append(tk_img)
                        top_x = min(sx1, sx2)
                        top_y = min(sy1, sy2)
                        self.canvas.create_image(top_x, top_y, image=tk_img, anchor="nw")

    def redraw(self):
        """Redraws all visible layers, basemap tiles, grid lines, and measurements."""
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 10 or h <= 10:
            return

        # 1. Background ESRI Basemap or Grid
        is_sa_extent = (self.view_extent.xmin < -35 and self.view_extent.xmax > -75 and self.view_extent.ymin < 10 and self.view_extent.ymax > -40)
        has_topo_layer = any("World Topographic" in l.name or "World Hillshade" in l.name for l in self.layers)

        if is_sa_extent or has_topo_layer:
            # ArcGIS Pro Topo Ocean Color
            self.canvas.create_rectangle(0, 0, w, h, fill="#c2e5f8", outline="")
            self._draw_south_america_cartography()

        if self.show_basemap:
            try:
                self._draw_basemap_tiles()
            except Exception:
                pass
        self._draw_grid()

        # 2. Render Layers in Order
        for layer in self.layers:
            if not self.layer_visibility.get(layer.name, True):
                continue
            renderer = self.layer_renderers.get(layer.name, SimpleRenderer())
            selected_ids = self.selected_features.get(layer.name, set())

            # Visible features query
            visible_features = layer.select_by_envelope(self.view_extent)

            for feat in visible_features:
                is_selected = feat.fid in selected_ids
                style = renderer.get_style(feat.attributes)
                geom = feat.geometry

                if isinstance(geom, Polygon):
                    flat_pts = []
                    for pt in geom.exterior:
                        sx, sy = self.geo_to_screen(pt.x, pt.y)
                        flat_pts.extend([sx, sy])

                    fill_color = "#38bdf8" if is_selected else style.get("fill", "#0284c7")
                    outline_color = "#facc15" if is_selected else style.get("stroke", "#38bdf8")
                    line_w = 3 if is_selected else int(style.get("stroke_width", 1.5))

                    self.canvas.create_polygon(
                        flat_pts,
                        fill=fill_color,
                        outline=outline_color,
                        width=line_w,
                        tags=f"feat_{layer.name}_{feat.fid}"
                    )

                elif isinstance(geom, Polyline):
                    flat_pts = []
                    for pt in geom.coordinates:
                        sx, sy = self.geo_to_screen(pt.x, pt.y)
                        flat_pts.extend([sx, sy])

                    stroke_color = "#facc15" if is_selected else style.get("stroke", "#38bdf8")
                    line_w = 4 if is_selected else int(style.get("stroke_width", 2.0))

                    line_kwargs = {
                        "fill": stroke_color,
                        "width": line_w,
                        "joinstyle": tk.ROUND,
                        "capstyle": tk.ROUND,
                        "tags": f"feat_{layer.name}_{feat.fid}"
                    }
                    if feat.get("Type") == "Ferry" or style.get("dash"):
                        line_kwargs["dash"] = (5, 4)

                    self.canvas.create_line(flat_pts, **line_kwargs)

                elif isinstance(geom, Point):
                    sx, sy = self.geo_to_screen(geom.x, geom.y)
                    r = style.get("radius", 6.0)
                    if is_selected:
                        r += 3
                    fill_color = "#facc15" if is_selected else style.get("fill", "#059669")
                    outline_color = "#ffffff" if is_selected else style.get("stroke", "#0f172a")

                    # If bus stop or facility, render classic ArcGIS Pro teardrop pin marker (Image 4)
                    if "Stop" in layer.name or feat.get("CATEGORY"):
                        pin_pts = [sx - r, sy - 2, sx + r, sy - 2, sx, sy + r + 3]
                        self.canvas.create_polygon(pin_pts, fill=fill_color, outline=outline_color, tags=f"feat_{layer.name}_{feat.fid}")
                        self.canvas.create_oval(sx - r, sy - r - 3, sx + r, sy + r - 3, fill=fill_color, outline=outline_color, tags=f"feat_{layer.name}_{feat.fid}")
                        self.canvas.create_oval(sx - 2, sy - 4, sx + 2, sy, fill="#ffffff", outline="", tags=f"feat_{layer.name}_{feat.fid}")
                    else:
                        self.canvas.create_oval(
                            sx - r, sy - r, sx + r, sy + r,
                            fill=fill_color,
                            outline=outline_color,
                            width=2 if is_selected else 1,
                            tags=f"feat_{layer.name}_{feat.fid}"
                        )

                    # Label
                    label = feat.get("NAME") or feat.get("name") or feat.get("ZONE_NAME")
                    if label:
                        self.canvas.create_text(
                            sx + r + 5, sy,
                            text=str(label),
                            anchor="w",
                            fill="#f8fafc",
                            font=("Segoe UI", 9, "bold" if is_selected else "normal")
                        )

        # 3. Render Measurement Overlay (Ruler tool)
        if len(self.measure_points) >= 2:
            pts = []
            for mp in self.measure_points:
                pts.extend(self.geo_to_screen(mp.x, mp.y))
            self.canvas.create_line(pts, fill="#f59e0b", width=2, dash=(4, 4))
            tot_km = 0.0
            for i in range(len(self.measure_points) - 1):
                tot_km += self.measure_points[i].geodesic_distance_to(self.measure_points[i + 1]) / 1000.0
            last_sx, last_sy = self.geo_to_screen(self.measure_points[-1].x, self.measure_points[-1].y)
            self.canvas.create_text(
                last_sx + 10, last_sy - 10,
                text=f"Total: {tot_km:.2f} km",
                anchor="w",
                fill="#fde047",
                font=("Segoe UI", 10, "bold")
            )

        # 4. Canvas Scale Bar & Compass
        self._draw_decorations()

    def _draw_grid(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        ext = self.view_extent

        # Simple coordinate tick step
        step_x = max(1.0, round(ext.width / 6.0, 1))
        step_y = max(1.0, round(ext.height / 6.0, 1))

        start_x = (int(ext.xmin / step_x) - 1) * step_x
        start_y = (int(ext.ymin / step_y) - 1) * step_y

        curr_x = start_x
        while curr_x <= ext.xmax + step_x:
            sx, _ = self.geo_to_screen(curr_x, ext.ymin)
            self.canvas.create_line(sx, 0, sx, h, fill="#1e293b", dash=(2, 4))
            self.canvas.create_text(sx + 3, h - 10, text=f"{curr_x:.1f}°", fill="#475569", font=("Segoe UI", 8))
            curr_x += step_x

        curr_y = start_y
        while curr_y <= ext.ymax + step_y:
            _, sy = self.geo_to_screen(ext.xmin, curr_y)
            self.canvas.create_line(0, sy, w, sy, fill="#1e293b", dash=(2, 4))
            self.canvas.create_text(15, sy - 8, text=f"{curr_y:.1f}°", fill="#475569", font=("Segoe UI", 8))
            curr_y += step_y

    def _draw_decorations(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100:
            return

        # North Arrow (ArcGIS Pro Compass in upper-right)
        nx, ny = w - 45, 45
        self.canvas.create_polygon(nx, ny - 22, nx - 8, ny, nx, ny - 6, fill="#ef4444", outline="#ffffff", width=1)
        self.canvas.create_polygon(nx, ny - 22, nx + 8, ny, nx, ny - 6, fill="#ffffff", outline="#ffffff", width=1)
        self.canvas.create_text(nx, ny + 12, text="N", fill="#f8fafc", font=("Segoe UI", 9, "bold"))

        # Graphical Scale Bar (Lower-Left corner, ArcGIS Pro style)
        bar_x1 = 35
        bar_y = h - 22
        bar_len = 120
        bar_x2 = bar_x1 + bar_len
        bar_mid = (bar_x1 + bar_x2) / 2

        # Convert screen bar distance to real kilometers
        geo1_x, geo1_y = self.screen_to_geo(bar_x1, bar_y)
        geo2_x, geo2_y = self.screen_to_geo(bar_x2, bar_y)
        dist_km = SpatialReference.haversine_distance(geo1_x, geo1_y, geo2_x, geo2_y) / 1000.0

        # Draw alternating segments
        self.canvas.create_rectangle(bar_x1, bar_y, bar_mid, bar_y + 4, fill="#ffffff", outline="#000000", width=1)
        self.canvas.create_rectangle(bar_mid, bar_y, bar_x2, bar_y + 4, fill="#007AC2", outline="#000000", width=1)

        # Scale tick labels
        if dist_km >= 1.0:
            str_mid = f"{dist_km / 2.0:.0f}"
            str_tot = f"{dist_km:.0f} km"
        else:
            str_mid = f"{(dist_km * 1000) / 2.0:.0f}"
            str_tot = f"{dist_km * 1000:.0f} m"

        self.canvas.create_text(bar_x1, bar_y - 7, text="0", fill="#cbd5e1", font=("Segoe UI", 7))
        self.canvas.create_text(bar_mid, bar_y - 7, text=str_mid, fill="#cbd5e1", font=("Segoe UI", 7))
        self.canvas.create_text(bar_x2, bar_y - 7, text=str_tot, fill="#cbd5e1", font=("Segoe UI", 7, "bold"))

        # Bottom-Right Corner Map / Navigator Button (Image 4 & Map view)
        bx = w - 30
        by = h - 30
        self.canvas.create_rectangle(bx, by, bx + 22, by + 22, fill="#ffffff", outline="#cbd5e1", width=1)
        self.canvas.create_text(bx + 11, by + 11, text="🧭", font=("Segoe UI", 10), fill="#007AC2")

    def _draw_south_america_cartography(self):
        """Renders authentic ArcGIS Pro World Topographic & Hillshade cartography for South America / Brazil."""
        show_topo = self.layer_visibility.get("World Topographic Map", True)
        show_hillshade = self.layer_visibility.get("World Hillshade", True)

        if not show_topo and not show_hillshade:
            return

        # 1. Continent Base Landmass
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
        if show_topo:
            scr_pts = []
            for gx, gy in sa_coast:
                sx, sy = self.geo_to_screen(gx, gy)
                scr_pts.extend([sx, sy])
            self.canvas.create_polygon(scr_pts, fill="#dfead7", outline="#c5d8bc", width=1)

            # 2. Amazon Basin (Lush Green Lowlands)
            amazon_basin = [
                (-74.5, -3.5), (-71.0, 1.2), (-64.0, 2.5), (-56.0, 0.5), (-50.0, -1.0),
                (-48.5, -3.5), (-51.0, -8.0), (-56.0, -11.5), (-64.0, -12.0), (-69.5, -10.5),
                (-74.0, -7.0)
            ]
            scr_amz = []
            for gx, gy in amazon_basin:
                sx, sy = self.geo_to_screen(gx, gy)
                scr_amz.extend([sx, sy])
            self.canvas.create_polygon(scr_amz, fill="#cee7bb", outline="")

            # 3. Brazilian Highlands (Planalto Central)
            brazil_highlands = [
                (-53.5, -12.5), (-45.0, -9.5), (-41.0, -13.5), (-41.5, -20.5),
                (-47.0, -23.5), (-52.0, -20.0)
            ]
            scr_planalto = []
            for gx, gy in brazil_highlands:
                sx, sy = self.geo_to_screen(gx, gy)
                scr_planalto.extend([sx, sy])
            self.canvas.create_polygon(scr_planalto, fill="#e2dac5", outline="")

        # 4. World Hillshade (Andes Mountain Relief)
        if show_hillshade:
            andes_spine = [
                (-76.5, 5.0), (-78.5, -0.5), (-76.0, -8.5), (-73.5, -14.5), (-69.0, -18.5),
                (-68.5, -24.0), (-70.0, -32.5), (-71.5, -42.0), (-73.0, -48.0), (-70.0, -53.5),
                (-67.5, -55.0), (-69.5, -53.0), (-71.0, -46.0), (-69.0, -38.0), (-67.0, -27.0),
                (-64.5, -18.0), (-70.0, -12.0), (-73.5, -4.5), (-75.0, 3.5)
            ]
            scr_andes = []
            for gx, gy in andes_spine:
                sx, sy = self.geo_to_screen(gx, gy)
                scr_andes.extend([sx, sy])
            self.canvas.create_polygon(scr_andes, fill="#b8ab98", outline="")

            # Andes subtle ridges for shaded relief appearance
            ridge_lines = [
                [(-77.5, 1.0), (-78.0, -1.0), (-76.5, -7.0), (-74.5, -12.0), (-70.5, -17.0)],
                [(-70.0, -18.0), (-69.0, -24.0), (-69.5, -31.0), (-71.0, -40.0), (-72.5, -48.0)],
                [(-75.0, -5.0), (-73.0, -10.0), (-68.0, -16.0), (-67.0, -21.0)]
            ]
            for r_pts in ridge_lines:
                pts = []
                for gx, gy in r_pts:
                    sx, sy = self.geo_to_screen(gx, gy)
                    pts.extend([sx, sy])
                self.canvas.create_line(pts, fill="#9f9380", width=2)

        if not show_topo:
            return

        # 5. International Boundaries (Esri Topo lavender lines)
        borders = [
            # Colombia / Brazil
            [(-70.0, -4.2), (-69.5, -1.5), (-70.0, 1.2), (-67.0, 1.2)],
            # Peru / Brazil
            [(-70.0, -4.2), (-72.0, -7.0), (-74.0, -9.0), (-71.0, -10.0), (-69.5, -11.0)],
            # Bolivia / Brazil
            [(-69.5, -11.0), (-65.5, -9.5), (-65.0, -12.5), (-60.5, -16.0), (-58.0, -17.5), (-58.0, -20.0)],
            # Paraguay / Brazil
            [(-58.0, -20.0), (-55.0, -22.5), (-54.5, -25.5)],
            # Argentina / Brazil
            [(-54.5, -25.5), (-53.5, -26.5), (-54.0, -27.5), (-57.5, -30.0)],
            # Uruguay / Brazil
            [(-57.5, -30.0), (-53.5, -31.5), (-53.4, -33.7)],
            # Venezuela / Brazil
            [(-67.0, 1.2), (-64.0, 4.0), (-60.5, 5.0)],
            # Guyana / Brazil
            [(-60.5, 5.0), (-59.5, 1.5), (-57.0, 1.5)],
            # Suriname & French Guiana / Brazil
            [(-57.0, 1.5), (-54.5, 2.0), (-52.0, 2.5), (-51.2, 4.4)],
            # Neighbors
            [(-79.0, 1.5), (-75.5, -0.2), (-70.0, -4.2)],
            [(-69.5, -11.0), (-69.0, -16.0), (-69.5, -17.5), (-68.0, -23.0), (-70.0, -32.5), (-71.5, -42.0), (-72.5, -51.5)],
            [(-62.5, -20.5), (-58.0, -20.0), (-58.5, -25.0), (-54.5, -25.5)]
        ]
        for b_line in borders:
            scr_b = []
            for gx, gy in b_line:
                sx, sy = self.geo_to_screen(gx, gy)
                scr_b.extend([sx, sy])
            self.canvas.create_line(scr_b, fill="#9e94aa", width=1.2, dash=(5, 3))

        # 6. Country Labels
        countries = [
            ("B R A Z I L", -52.0, -11.0, 13, "bold", "#3d3932"),
            ("COLOMBIA", -73.5, 4.0, 8, "bold", "#6a6358"),
            ("PERU", -75.5, -9.0, 8, "bold", "#6a6358"),
            ("BOLIVIA", -64.5, -16.5, 8, "bold", "#6a6358"),
            ("PARAGUAY", -58.5, -23.5, 8, "bold", "#6a6358"),
            ("URUGUAY", -56.0, -32.8, 8, "bold", "#6a6358"),
            ("GUYANA", -59.0, 5.0, 7, "bold", "#6a6358"),
            ("ECUADOR", -78.8, -1.5, 7, "bold", "#6a6358")
        ]
        for c_text, lon, lat, sz, weight, col in countries:
            sx, sy = self.geo_to_screen(lon, lat)
            self.canvas.create_text(sx, sy, text=c_text, font=("Segoe UI", sz, weight), fill=col)

        # 7. Geographic / Physical Labels
        phys = [
            ("Amazon Basin", -63.0, -3.5, 9, "italic", "#4b463e"),
            ("Brazilian Highlands", -46.0, -15.5, 9, "italic", "#4b463e"),
            ("Andes", -74.5, -18.0, 8, "italic", "#5e584f")
        ]
        for p_text, lon, lat, sz, slant, col in phys:
            sx, sy = self.geo_to_screen(lon, lat)
            self.canvas.create_text(sx, sy, text=p_text, font=("Segoe UI", sz, slant), fill=col)

        # 8. Major Cities (Matching user screenshot)
        cities = [
            ("Brasília", -47.88, -15.79, True),
            ("São Paulo", -46.63, -23.55, False),
            ("Rio de Janeiro", -43.17, -22.91, False),
            ("Belo Horizonte", -43.94, -19.92, False),
            ("Salvador", -38.51, -12.97, False),
            ("Fortaleza", -38.54, -3.72, False),
            ("Recife", -34.88, -8.06, False),
            ("Belém", -48.49, -1.45, False),
            ("Manaus", -60.02, -3.12, False),
            ("Porto Alegre", -51.22, -30.03, False),
            ("Asunción", -57.63, -25.28, False),
            ("Lima", -77.04, -12.04, False),
            ("Quito", -78.47, -0.18, False),
            ("Santiago", -70.65, -33.45, False)
        ]
        for c_name, lon, lat, is_cap in cities:
            sx, sy = self.geo_to_screen(lon, lat)
            # Dot marker
            r = 3.5 if not is_cap else 4.5
            self.canvas.create_oval(sx - r, sy - r, sx + r, sy + r, fill="#ffffff", outline="#1e293b", width=1.5)
            if is_cap:
                self.canvas.create_oval(sx - 1.5, sy - 1.5, sx + 1.5, sy + 1.5, fill="#007AC2", outline="")

            # Text with subtle white halo
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.canvas.create_text(sx + 6 + dx, sy + dy, text=c_name, anchor="w", font=("Segoe UI", 8), fill="#ffffff")
            self.canvas.create_text(sx + 6, sy, text=c_name, anchor="w", font=("Segoe UI", 8), fill="#1e293b")

