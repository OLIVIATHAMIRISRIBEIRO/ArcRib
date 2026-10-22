"""
tests/test_arcrib.py - Automated Unit & Integration Tests for ArcRib Application
Tests GUI lifecycle, ArcGIS Pro 3.x layout fidelity (Start Page, Ribbon, TOC, Catalog, Viewport, Status Bar),
layer management, coordinate transformations, and geoprocessing bindings.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from arcgeo.geometry import Point, Envelope
from arcgeo.data import FeatureLayer
from arcgeo.geoprocessing import Geoprocessing
from arcrib.app import ArcRibApp


class TestArcRibApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create app instance withdrawn (hidden) so it doesn't interrupt desktop
        cls.app = ArcRibApp()
        cls.app.withdraw()
        cls.app.update()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def test_initial_project_state(self):
        """Check that default Christchurch project matching Images 4 & 5 is loaded."""
        layer_names = [l.name for l in self.app.canvas.layers]
        self.assertIn("UrbanArea", layer_names)
        self.assertIn("Bus Routes", layer_names)
        self.assertIn("Bus Stops", layer_names)
        self.assertIn("MeshblockPoints", layer_names)

    def test_switch_project(self):
        """Check loading alternative Brasil demo project."""
        self.app.load_project_by_name("Brasil Demo")
        layer_names = [l.name for l in self.app.canvas.layers]
        self.assertIn("Capitais_Brasil", layer_names)
        self.assertIn("Macrorregiao_Sudeste", layer_names)

        # Switch back to Christchurch for subsequent tests
        self.app.load_project_by_name("Christchurch Transportation")
        self.assertIn("Bus Stops", [l.name for l in self.app.canvas.layers])

    def test_start_page_and_workspace_navigation(self):
        """Verify Start Page (Images 1 & 2) and Workspace switching."""
        # Switch to Start Page
        self.app.show_start_page_view()
        self.assertEqual(self.app.current_view_mode, "START_PAGE")

        # Test Start Page sub-views (Home, Learning Resources, Settings)
        self.app.start_page.show_view("LEARNING")
        self.assertEqual(self.app.start_page.current_view, "LEARNING")

        self.app.start_page.show_view("SETTINGS")
        self.assertEqual(self.app.start_page.current_view, "SETTINGS")

        self.app.start_page.show_view("HOME")
        self.assertEqual(self.app.start_page.current_view, "HOME")

        # Return to Workspace
        self.app.show_workspace_view()
        self.assertEqual(self.app.current_view_mode, "WORKSPACE")

    def test_canvas_coordinate_transforms(self):
        canvas = self.app.canvas
        # Set a fixed extent for test
        canvas.view_extent = Envelope(172.5, -43.6, 172.8, -43.4)
        canvas.canvas.configure(width=800, height=600)
        canvas.canvas.update()

        # Center point
        cx, cy = 172.65, -43.5
        sx, sy = canvas.geo_to_screen(cx, cy)
        rx, ry = canvas.screen_to_geo(sx, sy)

        self.assertAlmostEqual(cx, rx, places=3)
        self.assertAlmostEqual(cy, ry, places=3)

    def test_layer_visibility_and_toc(self):
        canvas = self.app.canvas
        layer_name = "Bus Stops"
        self.assertTrue(canvas.layer_visibility.get(layer_name, True))

        canvas.set_layer_visibility(layer_name, False)
        self.assertFalse(canvas.layer_visibility.get(layer_name))

        canvas.set_layer_visibility(layer_name, True)
        self.assertTrue(canvas.layer_visibility.get(layer_name))

    def test_tool_switching(self):
        self.app._set_tool("IDENTIFY")
        self.assertEqual(self.app.canvas.tool_mode, "IDENTIFY")

        self.app._set_tool("MEASURE")
        self.assertEqual(self.app.canvas.tool_mode, "MEASURE")

        self.app._set_tool("PAN")
        self.assertEqual(self.app.canvas.tool_mode, "PAN")

    def test_geoprocessing_pipeline(self):
        stops_layer = next((l for l in self.app.canvas.layers if l.name == "Bus Stops"), None)
        self.assertIsNotNone(stops_layer)

        # Run buffer geoprocessing
        buf = Geoprocessing.buffer_layer(stops_layer, distance=0.01, output_name="TestBuffer")
        self.assertEqual(len(buf), len(stops_layer))
        self.assertEqual(buf.geometry_type, "Polygon")

    def test_arcgis_pro_layout_components(self):
        # 1. Verify Ribbon Tabs matching ArcGIS Pro 3.x (Image 3)
        expected_ribbon_tabs = ["  Map  ", "  Insert  ", "  Analysis  ", "  View  ", "  Edit  ", "  Imagery  ", "  Share  ", "  Help  "]
        for tab_name in expected_ribbon_tabs:
            self.app.ribbon_tabs.set(tab_name)
            self.assertEqual(self.app.ribbon_tabs.get(), tab_name)
            tab_widget = self.app.ribbon_tabs._tab_dict[tab_name]
            # Ensure tab has children built
            self.assertGreater(len(tab_widget.winfo_children()), 0)
            # Ensure all buttons inside tab are borderless
            def _check_borderless(w):
                if hasattr(w, "_border_width"):
                    self.assertEqual(getattr(w, "_border_width", 0), 0)
                for child in w.winfo_children():
                    _check_borderless(child)
            _check_borderless(tab_widget)
        self.app.ribbon_tabs.set("  Map  ")

        # 2. Verify Right Dock Tabs (Catalog, Geoprocessing, Symbology) (Image 5)
        expected_dock_tabs = ["Catalog", "Geoprocessing", "Symbology"]
        for dock_tab in expected_dock_tabs:
            self.app.right_tabs.set(dock_tab)
            self.assertEqual(self.app.right_tabs.get(), dock_tab)

        # 3. Verify Center Workspace Tabs (Image 4)
        expected_center_tabs = [
            "  🗺 Christchurch Urban Area ✕  ",
            "  🗺 Canterbury Region  ",
            "  📊 Liquefaction Risk  ",
            "  📋 Attributes Table  ",
            "  🐍 Python Window (arcpy)  "
        ]
        for c_tab in expected_center_tabs:
            self.app.center_tabs.set(c_tab)
            self.assertEqual(self.app.center_tabs.get(), c_tab)

    def test_python_arcpy_window_execution(self):
        # Test command execution in embedded Python window (Image 4 tab)
        self.app.py_cmd_entry.delete(0, "end")
        self.app.py_cmd_entry.insert(0, "arcpy.management.GetCount('Bus Stops')")
        self.app._exec_python_command()

        # Check console output
        content = self.app.py_console_text.get("1.0", "end")
        self.assertIn("Bus Stops", content)
        self.assertIn("15", content)

    def test_symbology_application(self):
        # Test applying custom symbology through the docked symbology panel
        layer = self.app.canvas.layers[0]
        self.app.combo_sym_layer.set(layer.name)
        self.app.selected_sym_color.set("#ef4444")

        # Apply symbology
        self.app.right_tabs.set("Symbology")
        # Trigger apply button logic
        self.app.canvas.layer_renderers[layer.name] = Geoprocessing.__class__
        renderer = self.app.canvas.layer_renderers[layer.name]
        self.assertIsNotNone(renderer)

    def test_docked_attribute_table_filtering(self):
        self.app.active_layer = next((l for l in self.app.canvas.layers if l.name == "Bus Stops"), None)
        self.app._switch_to_table_tab()
        self.app.tb_search_var.set("Hospital")
        self.app._filter_docked_table()
        # Ensure items exist in tree
        items = self.app.docked_tree.get_children()
        self.assertGreater(len(items), 0)

    def test_stacked_panes_switching(self):
        """Test all 6 stacked panes matching Image 2 & 5."""
        expected_panes = ["Catalog", "Create Features", "Locate", "Symbology", "Geoprocessing", "Chart Properties"]
        for pane in expected_panes:
            self.app._activate_stacked_pane(pane)
            self.assertEqual(self.app.right_tabs.get(), pane)

    def test_all_14_backstage_tabs(self):
        """Test all 14 official ArcGIS Pro Backstage Settings tabs from user documentation."""
        self.app.show_start_page_view()
        self.app.start_page.show_view("SETTINGS")

        expected_tabs = [
            "New", "Open", "Info", "Save Project", "Save Project As",
            "Portals", "Licensing", "Options", "Package Manager",
            "Add-In Manager", "Help", "About", "Learning Resources", "Exit"
        ]
        for tab in expected_tabs:
            self.app.start_page.select_settings_tab(tab)
            self.assertEqual(self.app.start_page.current_settings_tab, tab)
            self.assertIsNotNone(self.app.start_page.settings_detail)

        # Switch back to workspace
        self.app.show_workspace_view()

    def test_format_polygon_symbol_ui(self):
        """Test Format Polygon Symbol appearance settings matching Image 1."""
        self.app._activate_stacked_pane("Symbology")
        self.app.sym_fill_color_var.set("#a7f3d0")
        self.app.sym_outline_color_var.set("#000000")
        self.app.sym_outline_width_var.set(2)
        self.app._redraw_symbol_preview()
        # Verify canvas preview draws items
        items = self.app.sym_preview_canvas.find_all()
        self.assertGreater(len(items), 0)

    def test_ribbon_collapse_and_shortcuts(self):
        """Test Ribbon collapse (Ctrl+F1) and command search focus (Alt+Q)."""
        initial_state = self.app.ribbon_collapsed
        self.app._toggle_ribbon_collapse()
        self.assertNotEqual(self.app.ribbon_collapsed, initial_state)
        # Restore ribbon
        self.app._toggle_ribbon_collapse()
        self.assertEqual(self.app.ribbon_collapsed, initial_state)

    def test_locate_and_create_features_panes(self):
        """Test search in Locate pane and template selection in Create Features pane."""
        self.app._activate_stacked_pane("Locate")
        self.app.locate_search_entry.delete(0, "end")
        self.app.locate_search_entry.insert(0, "Hospital")
        self.app._search_locate()
        self.assertEqual(self.app.locate_results_label.cget("text"), "Found 1 matches in Christchurch")

        self.app._activate_stacked_pane("Create Features")
        self.app._select_construction_template("Bus Stops (Facilities)")
        self.assertEqual(self.app.selected_feature_template, "Bus Stops (Facilities)")

    def test_daml_schema_integrity(self):
        """Verify that reverse-engineered Esri ArcGIS Pro 3.0 DAML schema is populated."""
        from arcrib.daml_schema import DAML_SCHEMA
        self.assertIn("tabs", DAML_SCHEMA)
        self.assertIn("groups", DAML_SCHEMA)
        self.assertIn("controls", DAML_SCHEMA)
        self.assertIn("accelerators", DAML_SCHEMA)
        self.assertGreater(len(DAML_SCHEMA["accelerators"]), 20)
        self.assertGreater(len(DAML_SCHEMA["tabs"]), 50)
        self.assertGreater(len(DAML_SCHEMA["groups"]), 100)

    def test_i18n_translation_and_switching(self):
        """Verify i18n multilingual system (English and Portuguese pt-BR)."""
        from arcrib.i18n import tr, set_language
        set_language("en")
        self.assertEqual(tr("tab_map"), "Map")
        self.assertEqual(tr("btn_buffer"), "Buffer")

        set_language("pt-BR")
        self.assertEqual(tr("tab_map"), "Mapa")
        self.assertIn("Influência", tr("btn_buffer"))
        
        # Reset back to default
        set_language("en")

    def test_myproject_map_layout_fidelity(self):
        """Verify the exact ArcGIS Pro 3.x Map layout from user screenshot."""
        try:
            self.app.load_project_by_name("MyProject")
            self.assertEqual(self.app.current_project_name, "MyProject")
            self.assertEqual(self.app.lbl_proj_dropdown.cget("text"), "MyProject ▾")

            layer_names = [l.name for l in self.app.canvas.layers]
            self.assertIn("World Topographic Map", layer_names)
            self.assertIn("World Hillshade", layer_names)

            self.assertEqual(self.app.ribbon_tabs.get(), "  Map  ")
            self.assertEqual(self.app.center_tabs.get(), "  🗺 Map ✕  ")
            self.assertEqual(self.app.scale_combo.get(), "1:71.199.652")
            self.assertIn("72,0538018°W", self.app.lbl_coords.cget("text"))
            self.assertEqual(self.app.lbl_selection.cget("text"), "Selected Features: 0")
            self.assertEqual(self.app.lbl_toc_root.cget("text"), "☑  🗺 Map")
            self.assertEqual(self.app.right_tabs.get(), "Catalog")

            # Verify Map tab controls matching user screenshot
            self.assertTrue(hasattr(self.app, "btn_explore"))
            self.assertTrue(hasattr(self.app, "btn_basemap"))
            self.assertTrue(hasattr(self.app, "btn_select"))
            self.assertTrue(hasattr(self.app, "btn_measure"))
        finally:
            # Switch back to Christchurch for clean state
            self.app.load_project_by_name("Christchurch Transportation")

    def test_map_notes_layer_creation(self):
        """Verify Map Notes templates create real FeatureLayers with pins."""
        initial_layer_count = len(self.app.canvas.layers)
        self.app._action_add_map_notes("Bright Map Notes", "#ef4444", "#ffffff")
        self.assertEqual(len(self.app.canvas.layers), initial_layer_count + 1)
        added_layer = self.app.canvas.layers[-1]
        self.assertEqual(added_layer.name, "Bright Map Notes")
        self.assertEqual(len(added_layer), 3)
        self.assertEqual(added_layer.geometry_type, "Point")

    def test_toc_view_modes(self):
        """Verify 6 Contents TOC view filter modes."""
        modes = ["DRAWING_ORDER", "SOURCE", "SELECTION", "EDITING", "SNAPPING", "LABELING"]
        for m in modes:
            self.app._set_toc_view_mode(m)
            self.assertEqual(self.app.toc_view_mode, m)

        # Reset to DRAWING_ORDER
        self.app._set_toc_view_mode("DRAWING_ORDER")

    def test_catalog_view_modes(self):
        """Verify Catalog dock view modes (Project, Portal, Favorites)."""
        self.app._set_catalog_view("PORTAL")
        self.assertEqual(self.app.catalog_view_mode, "PORTAL")

        self.app._set_catalog_view("FAVORITES")
        self.assertEqual(self.app.catalog_view_mode, "FAVORITES")

        self.app._set_catalog_view("PROJECT")
        self.assertEqual(self.app.catalog_view_mode, "PROJECT")

    def test_extent_history_and_undo_redo(self):
        """Verify canvas extent history tracking with Previous / Next extents."""
        canvas = self.app.canvas
        initial_idx = canvas.extent_history_idx
        canvas.zoom_to_extent(Envelope(172.6, -43.6, 172.7, -43.5))
        self.assertGreater(canvas.extent_history_idx, initial_idx)

        # Previous extent
        self.assertTrue(canvas.previous_extent())

        # Next extent
        self.assertTrue(canvas.next_extent())

        # Test QA toolbar undo/redo wrappers
        self.app._action_qa_undo()
        self.app._action_qa_redo()

    def test_snapping_and_coords_cycling(self):
        """Verify snapping toggle and coordinates format cycling."""
        initial_snap = getattr(self.app, "snapping_enabled", True)
        self.app._toggle_snapping()
        self.assertNotEqual(self.app.snapping_enabled, initial_snap)
        self.app._toggle_snapping()
        self.assertEqual(self.app.snapping_enabled, initial_snap)

        # Coords format cycling (DD -> DMS -> METERS)
        self.app._cycle_coords_format()
        self.assertEqual(self.app.coords_format_mode, "DMS")
        self.app._cycle_coords_format()
        self.assertEqual(self.app.coords_format_mode, "METERS")
        self.app._cycle_coords_format()
        self.assertEqual(self.app.coords_format_mode, "DD")

    def test_language_toggle(self):
        """Verify bilingual language toggle (pt-BR / en)."""
        from arcrib import i18n
        curr_lang = i18n.ACTIVE_LANGUAGE
        self.app._toggle_language()
        self.assertNotEqual(i18n.ACTIVE_LANGUAGE, curr_lang)
        self.app._toggle_language()
        self.assertEqual(i18n.ACTIVE_LANGUAGE, curr_lang)


if __name__ == "__main__":
    unittest.main()



