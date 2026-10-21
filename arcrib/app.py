"""
arcrib.app - ArcRib Desktop GIS Application
Faithful reproduction of Esri ArcGIS Pro 3.0:
- Image 1 & 2: Start Page & Backstage Landing Screen (New Project Templates, Recent Projects, Learning Resources)
- Image 3: Ribbon & Title Bar (Quick Access, Project Dropdown, Command Search, Contextual Tabs [Feature Layer | Labeling | Data])
- Image 4: Map Viewport & Status Bar (Map tabs, Christchurch Urban Hazard Layers, Status Bar with 1:100,000, Snapping, Lat/Lon)
- Image 5: Contents (TOC) & Catalog Panes (6 View Filter icons, City Center, Bus Routes legend, Christchurch Transportation.gdb)
- Geoprocessing Tools Suite (Buffer, Spatial Join, Clip, Summary Stats, Select by Attribute)
"""

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from typing import Optional, Dict, List, Any

from arcgeo.geometry import Point, Polyline, Polygon, Envelope, SpatialReference
from arcgeo.data import FeatureLayer, Feature
from arcgeo.geoprocessing import Geoprocessing
from arcgeo.mapping import SimpleRenderer, UniqueValueRenderer
from arcgeo.basemaps import ESRI_BASEMAPS
from arcrib.canvas import InteractiveMapCanvas
from arcrib.start_page import ArcGISProStartPage
from arcrib.sample_data import load_christchurch_project, load_brasil_project


class ArcRibApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("ArcGIS® Pro - Christchurch Transportation - City Center")
        self.geometry("1420x900")
        self.minsize(1080, 700)

        # ArcGIS Pro Light Theme by default (matching user screenshots)
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

        # Color Tokens matching ArcGIS Pro 3.0 Light UI
        self.C_ESRI_BLUE = "#007AC2"
        self.C_ESRI_HOVER = "#005a90"
        self.C_TOP_BG = "#ffffff"
        self.C_RIBBON_BG = "#ffffff"
        self.C_PANEL_BG = "#f8fafc"
        self.C_HEADER_BG = "#f1f5f9"
        self.C_BORDER = "#e2e8f0"
        self.C_TEXT = "#1e293b"
        self.C_TEXT_MUTED = "#64748b"
        self.C_TAB_ACTIVE = "#e1f0fa"

        # App State
        self.canvas = None
        self.current_project_name = "Christchurch Transportation"
        self.active_layer: Optional[FeatureLayer] = None
        self.selected_feature_template = None
        self.current_view_mode = "WORKSPACE"  # "START_PAGE" or "WORKSPACE"

        # Main Root Container for Switching Views
        self.root_container = ctk.CTkFrame(self, fg_color="#f3f4f6", corner_radius=0)
        self.root_container.pack(fill=tk.BOTH, expand=True)

        # Build Project Workspace Frame
        self.workspace_frame = ctk.CTkFrame(self.root_container, fg_color="#f8fafc", corner_radius=0)

        # Build Start Page Frame (Images 1 & 2)
        self.start_page = ArcGISProStartPage(
            self.root_container,
            on_open_project=self._on_start_page_open_project,
            on_new_project=self._on_start_page_new_project,
            on_save_project=self._action_save_aprx,
            on_save_project_as=self._action_save_aprx,
            on_exit=self.destroy,
            get_project_info=self._get_project_info_dict
        )

        # Construct Project Workspace UI (Images 3, 4, 5)
        self._build_title_bar(self.workspace_frame)
        self._build_ribbon(self.workspace_frame)
        self._build_status_bar(self.workspace_frame)
        self._build_docked_workspace(self.workspace_frame)

        # Load Default Christchurch Project (Images 4 & 5)
        self.load_project_by_name("Christchurch Transportation")

        # Global Keyboard Shortcuts (Ctrl+F1 for Ribbon, Alt+Q for Command Search)
        self.bind("<Control-F1>", lambda e: self._toggle_ribbon_collapse())
        self.bind("<Alt-q>", lambda e: self.search_entry.focus_set())
        self.bind("<Alt-Q>", lambda e: self.search_entry.focus_set())

        # By default, ArcGIS Pro opens to a start page.
        self.show_start_page_view()

    def _get_project_info_dict(self) -> dict:
        return {
            "name": f"{self.current_project_name}.aprx",
            "path": f"C:\\Users\\User\\Documents\\ArcGIS\\Projects\\{self.current_project_name}\\{self.current_project_name}.aprx",
            "version": "ArcGIS Pro 3.5.0",
            "gdb": f"{self.current_project_name}.gdb",
            "crs": "WGS 1984 (WKID: 4326)"
        }

    # =========================================================================
    # VIEW SWITCHING (Start Page vs Project Workspace)
    # =========================================================================
    def show_start_page_view(self):
        """Displays the ArcGIS Pro Start Page (Image 1 & 2)."""
        self.current_view_mode = "START_PAGE"
        self.workspace_frame.pack_forget()
        self.start_page.pack(fill=tk.BOTH, expand=True)
        self.title("ArcGIS® Pro")

    def show_workspace_view(self):
        """Displays the active Project Workspace (Image 3, 4 & 5)."""
        self.current_view_mode = "WORKSPACE"
        self.start_page.pack_forget()
        self.workspace_frame.pack(fill=tk.BOTH, expand=True)
        self.title(f"ArcGIS® Pro - {self.current_project_name} - City Center")

    def _on_start_page_open_project(self, project_name: str):
        self.load_project_by_name(project_name)
        self.show_workspace_view()

    def _on_start_page_new_project(self):
        self.canvas.layers.clear()
        self.canvas.layer_renderers.clear()
        self.canvas.layer_visibility.clear()
        self.canvas.selected_features.clear()
        self.current_project_name = "Untitled"
        self.lbl_proj_dropdown.configure(text="Untitled ▾")
        self._refresh_toc()
        self.canvas.redraw()
        self.show_workspace_view()

    # =========================================================================
    # 1. TOP TITLE BAR & QUICK ACCESS (Exact match of Image 3)
    # =========================================================================
    def _build_title_bar(self, parent):
        title_bar = ctk.CTkFrame(parent, height=36, fg_color=self.C_TOP_BG, corner_radius=0)
        title_bar.pack(fill=tk.X, side=tk.TOP)

        # Quick Access Toolbar (Image 3, Box 1)
        qa_frame = ctk.CTkFrame(title_bar, fg_color="transparent")
        qa_frame.pack(side=tk.LEFT, padx=(8, 4), pady=4)

        # Blue Backstage Button 'Project'
        btn_project = ctk.CTkButton(
            qa_frame, text="Project", width=62, height=24,
            fg_color=self.C_ESRI_BLUE, hover_color=self.C_ESRI_HOVER,
            font=("Segoe UI", 10, "bold"), corner_radius=2,
            command=self.show_start_page_view
        )
        btn_project.pack(side=tk.LEFT, padx=(0, 6))

        # Quick Access Icons: New, Open, Save, Undo, Redo, Customize
        ctk.CTkButton(qa_frame, text="📄", width=24, height=22, fg_color="transparent", hover_color="#e2e8f0", text_color="#334155", font=("Segoe UI", 11), command=self._on_start_page_new_project).pack(side=tk.LEFT, padx=1)
        ctk.CTkButton(qa_frame, text="📂", width=24, height=22, fg_color="transparent", hover_color="#e2e8f0", text_color="#334155", font=("Segoe UI", 11), command=self._action_open_aprx).pack(side=tk.LEFT, padx=1)
        ctk.CTkButton(qa_frame, text="💾", width=24, height=22, fg_color="transparent", hover_color="#e2e8f0", text_color="#334155", font=("Segoe UI", 11), command=self._action_save_aprx).pack(side=tk.LEFT, padx=1)
        ctk.CTkButton(qa_frame, text="↶ ▾", width=30, height=22, fg_color="transparent", hover_color="#e2e8f0", text_color="#334155", font=("Segoe UI", 10), command=self._action_clear_selection).pack(side=tk.LEFT, padx=1)
        ctk.CTkButton(qa_frame, text="↷ ▾", width=30, height=22, fg_color="transparent", hover_color="#e2e8f0", text_color="#334155", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=1)
        ctk.CTkButton(qa_frame, text="▾", width=18, height=22, fg_color="transparent", hover_color="#e2e8f0", text_color="#64748b", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=1)

        # Vertical Divider
        ctk.CTkFrame(title_bar, width=1, height=18, fg_color=self.C_BORDER).pack(side=tk.LEFT, padx=8)

        # Project Dropdown Selector (Image 3, Box 2)
        self.lbl_proj_dropdown = ctk.CTkButton(
            title_bar, text=f"{self.current_project_name} ▾", width=190, height=24,
            fg_color="transparent", hover_color="#f1f5f9", text_color="#1e293b",
            font=("Segoe UI", 10, "bold"), anchor="w",
            command=self._popup_project_switcher
        )
        self.lbl_proj_dropdown.pack(side=tk.LEFT, padx=2)

        # Command Search Bar (Image 3, Box 3)
        search_frame = ctk.CTkFrame(title_bar, fg_color="transparent")
        search_frame.pack(side=tk.LEFT, padx=18)
        self.entry_cmd_search = ctk.CTkEntry(
            search_frame, placeholder_text="🔍 Command Search (Alt+Q)",
            width=260, height=24, font=("Segoe UI", 9)
        )
        self.entry_cmd_search.pack()
        self.entry_cmd_search.bind("<Return>", lambda e: self._on_command_search())

        # Right-side Account, Notifications & Window Controls
        right_hdr = ctk.CTkFrame(title_bar, fg_color="transparent")
        right_hdr.pack(side=tk.RIGHT, padx=10)

        ctk.CTkLabel(right_hdr, text="Your Name - Your Organization", font=("Segoe UI", 9, "bold"), text_color="#334155").pack(side=tk.LEFT, padx=4)
        ctk.CTkLabel(right_hdr, text="YN", width=22, height=22, fg_color="#a3e635", text_color="#14532d", font=("Segoe UI", 9, "bold"), corner_radius=11).pack(side=tk.LEFT, padx=4)
        ctk.CTkLabel(right_hdr, text="🔔   ?", font=("Segoe UI", 11), text_color="#64748b").pack(side=tk.LEFT, padx=6)

    def _popup_project_switcher(self):
        opts = ["Christchurch Transportation", "Brasil Geografico", "Wellington Buildings", "Scotland Medical Facilities"]
        # Cycle through
        idx = opts.index(self.current_project_name) if self.current_project_name in opts else -1
        nxt = opts[(idx + 1) % len(opts)]
        self.load_project_by_name(nxt)

    def _on_command_search(self):
        query = self.entry_cmd_search.get().strip().lower()
        if not query:
            return
        if "buffer" in query:
            self._open_right_tool_buffer()
        elif "join" in query or "spatial" in query:
            self._open_right_tool_join()
        elif "clip" in query:
            self._action_clip()
        elif "catalog" in query or "catalogo" in query:
            self.right_tabs.set("Catalog")
        elif "contents" in query or "conteudo" in query:
            self._toggle_toc_panel()
        else:
            self.right_tabs.set("Geoprocessing")

    # =========================================================================
    # 2. FLUENT RIBBON & CONTEXTUAL TABS (Exact match of Image 3)
    # =========================================================================
    def _build_ribbon(self, parent):
        self.ribbon_container = ctk.CTkFrame(parent, height=118, fg_color=self.C_RIBBON_BG, corner_radius=0)
        self.ribbon_container.pack(fill=tk.X, side=tk.TOP)
        self.ribbon_is_collapsed = False

        # Tab Strip Header with Contextual Tabs
        tab_header_strip = ctk.CTkFrame(self.ribbon_container, height=28, fg_color="#f8fafc", corner_radius=0)
        tab_header_strip.pack(fill=tk.X, side=tk.TOP)

        # Ribbon Collapse Button (Image 3, Box 9 & Ctrl+F1)
        self.btn_ribbon_collapse = ctk.CTkButton(
            tab_header_strip, text="▾", width=22, height=22,
            fg_color="transparent", hover_color="#e2e8f0", text_color="#64748b",
            font=("Segoe UI", 9, "bold"), corner_radius=2,
            command=self._toggle_ribbon_collapse
        )
        self.btn_ribbon_collapse.pack(side=tk.RIGHT, padx=(0, 8), pady=2)

        # Contextual Tabs Group on the right (Image 3, Box 5)
        ctx_frame = ctk.CTkFrame(tab_header_strip, fg_color="transparent")
        ctx_frame.pack(side=tk.RIGHT, padx=8, pady=2)

        ctx_pill = ctk.CTkFrame(ctx_frame, fg_color="#e0f2fe", border_color="#0284c7", border_width=1, corner_radius=12)
        ctx_pill.pack(side=tk.RIGHT)

        ctk.CTkButton(ctx_pill, text="Feature Layer", width=85, height=22, fg_color="transparent", hover_color="#bae6fd", text_color="#0369a1", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(ctx_pill, text="Labeling", width=65, height=22, fg_color="transparent", hover_color="#bae6fd", text_color="#0369a1", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(ctx_pill, text="Data", width=55, height=22, fg_color="transparent", hover_color="#bae6fd", text_color="#0369a1", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=2)

        # Core Ribbon Tabs
        self.ribbon_tabs = ctk.CTkTabview(
            self.ribbon_container,
            height=90,
            fg_color=self.C_RIBBON_BG,
            segmented_button_fg_color="#f1f5f9",
            segmented_button_selected_color=self.C_ESRI_BLUE,
            segmented_button_selected_hover_color=self.C_ESRI_HOVER,
            corner_radius=0
        )
        self.ribbon_tabs.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Ribbon Tabs as seen in Image 3
        tab_map = self.ribbon_tabs.add("  Map  ")
        tab_insert = self.ribbon_tabs.add("  Insert  ")
        tab_analysis = self.ribbon_tabs.add("  Analysis  ")
        tab_view = self.ribbon_tabs.add("  View  ")
        tab_edit = self.ribbon_tabs.add("  Edit  ")
        tab_imagery = self.ribbon_tabs.add("  Imagery  ")
        tab_share = self.ribbon_tabs.add("  Share  ")
        tab_help = self.ribbon_tabs.add("  Help  ")

        self._build_ribbon_group_map(tab_map)
        self._build_ribbon_group_insert(tab_insert)
        self._build_ribbon_group_analysis(tab_analysis)
        self._build_ribbon_group_view(tab_view)
        self._build_ribbon_group_edit(tab_edit)
        self._build_ribbon_group_help(tab_help)

    def _toggle_ribbon_collapse(self):
        """Collapses or expands the ribbon (Ctrl+F1, Image 3 Box 9)."""
        if self.ribbon_is_collapsed:
            self.ribbon_tabs.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
            self.ribbon_container.configure(height=118)
            self.ribbon_is_collapsed = False
            self.btn_ribbon_collapse.configure(text="▾")
        else:
            self.ribbon_tabs.pack_forget()
            self.ribbon_container.configure(height=28)
            self.ribbon_is_collapsed = True
            self.btn_ribbon_collapse.configure(text="▴")

    @property
    def ribbon_collapsed(self) -> bool:
        return getattr(self, "ribbon_is_collapsed", False)

    def _create_ribbon_group(self, parent_tab, group_name: str):
        """Creates an authentic ArcGIS Pro ribbon group with title and launcher icon (Image 3, 6/7/8)."""
        box = ctk.CTkFrame(parent_tab, fg_color="transparent", corner_radius=0)
        box.pack(side=tk.LEFT, fill=tk.Y, padx=3, pady=1)

        btn_area = ctk.CTkFrame(box, fg_color="transparent")
        btn_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        bottom_bar = ctk.CTkFrame(box, fg_color="transparent")
        bottom_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(1, 2))

        ctk.CTkLabel(bottom_bar, text=group_name, font=("Segoe UI", 8), text_color="#64748b").pack(side=tk.LEFT, padx=(4, 2))
        # Dialog launcher button (Image 3, Box 8)
        ctk.CTkLabel(bottom_bar, text="⤢", font=("Segoe UI", 8), text_color="#94a3b8", cursor="hand2").pack(side=tk.RIGHT, padx=(0, 2))

        # Vertical separator
        sep = ctk.CTkFrame(parent_tab, width=1, fg_color=self.C_BORDER)
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=2, pady=6)

        return btn_area

    def _build_ribbon_group_map(self, tab):
        f = ctk.CTkFrame(tab, fg_color="transparent")
        f.pack(fill=tk.BOTH, expand=True)

        # Navigate Group
        g_nav = self._create_ribbon_group(f, "Navigate")
        ctk.CTkButton(g_nav, text="✋ Explore", width=72, height=32, fg_color=self.C_ESRI_BLUE, hover_color=self.C_ESRI_HOVER, font=("Segoe UI", 9, "bold"), command=lambda: self._set_tool("PAN")).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(g_nav, text="⤢ Full Extent", width=80, height=32, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 9), command=lambda: self.canvas.zoom_to_extent()).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(g_nav, text="+", width=28, height=32, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, command=lambda: self.canvas._zoom(1.3, self.canvas.canvas.winfo_width()//2, self.canvas.canvas.winfo_height()//2)).pack(side=tk.LEFT, padx=1)
        ctk.CTkButton(g_nav, text="-", width=28, height=32, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, command=lambda: self.canvas._zoom(0.7, self.canvas.canvas.winfo_width()//2, self.canvas.canvas.winfo_height()//2)).pack(side=tk.LEFT, padx=1)

        # Layer & Basemap Group
        g_layer = self._create_ribbon_group(f, "Layer")
        basemap_options = list(ESRI_BASEMAPS.keys()) + ["No Basemap (Grid)"]
        self.combo_basemap = ctk.CTkComboBox(g_layer, values=basemap_options, width=155, height=28, font=("Segoe UI", 9), command=self._on_basemap_changed)
        self.combo_basemap.set("Esri Topo")
        self.combo_basemap.pack(side=tk.LEFT, padx=3, pady=2)
        ctk.CTkButton(g_layer, text="➕ Add Data", width=75, height=28, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 9), command=self._action_open_aprx).pack(side=tk.LEFT, padx=2)

        # Selection & Inquiry Group
        g_inq = self._create_ribbon_group(f, "Selection & Inquiry")
        ctk.CTkButton(g_inq, text="ℹ Pop-up", width=70, height=30, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 9), command=lambda: self._set_tool("IDENTIFY")).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(g_inq, text="📏 Measure", width=70, height=30, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 9), command=lambda: self._set_tool("MEASURE")).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(g_inq, text="Clear", width=55, height=30, fg_color="#fef2f2", hover_color="#fee2e2", text_color="#991b1b", border_color="#fca5a5", border_width=1, font=("Segoe UI", 9), command=self._action_clear_selection).pack(side=tk.LEFT, padx=2)

    def _build_ribbon_group_insert(self, tab):
        f = ctk.CTkFrame(tab, fg_color="transparent")
        f.pack(fill=tk.BOTH, expand=True)

        g_proj = self._create_ribbon_group(f, "Project")
        ctk.CTkButton(g_proj, text="🗺 New Map", width=85, height=30, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 9), command=lambda: messagebox.showinfo("ArcGIS Pro", "New Map 2D created.")).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(g_proj, text="📐 New Layout", width=95, height=30, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 9), command=self._action_export_svg).pack(side=tk.LEFT, padx=2)

        g_conn = self._create_ribbon_group(f, "Connections")
        ctk.CTkButton(g_conn, text="📁 Add Folder", width=95, height=30, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 9), command=lambda: self.right_tabs.set("Catalog")).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(g_conn, text="🗄 Add Database", width=105, height=30, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 9), command=lambda: self.right_tabs.set("Catalog")).pack(side=tk.LEFT, padx=2)

    def _build_ribbon_group_analysis(self, tab):
        f = ctk.CTkFrame(tab, fg_color="transparent")
        f.pack(fill=tk.BOTH, expand=True)

        g_gp = self._create_ribbon_group(f, "Geoprocessing")
        ctk.CTkButton(g_gp, text="🛠 Tools", width=75, height=30, fg_color=self.C_ESRI_BLUE, hover_color=self.C_ESRI_HOVER, font=("Segoe UI", 9, "bold"), command=lambda: self.right_tabs.set("Geoprocessing")).pack(side=tk.LEFT, padx=2)

        g_tools = self._create_ribbon_group(f, "Core Vector Analysis")
        ctk.CTkButton(g_tools, text="◎ Buffer", width=75, height=30, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 9), command=self._open_right_tool_buffer).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(g_tools, text="⧉ Spatial Join", width=95, height=30, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 9), command=self._open_right_tool_join).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(g_tools, text="✂ Clip", width=65, height=30, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 9), command=self._action_clip).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(g_tools, text="📊 Summary Stats", width=110, height=30, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 9), command=self._action_summary_stats).pack(side=tk.LEFT, padx=2)

        g_py = self._create_ribbon_group(f, "Scripting")
        ctk.CTkButton(g_py, text="🐍 Python Window", width=120, height=30, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 9), command=lambda: self.center_tabs.set("  🐍 Python Window (arcpy)  ")).pack(side=tk.LEFT, padx=2)

    def _build_ribbon_group_view(self, tab):
        f = ctk.CTkFrame(tab, fg_color="transparent")
        f.pack(fill=tk.BOTH, expand=True)

        g_panes = self._create_ribbon_group(f, "Windows / Panes")
        ctk.CTkButton(g_panes, text="☰ Contents", width=85, height=30, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 9), command=self._toggle_toc_panel).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(g_panes, text="🛠 Geoprocessing", width=115, height=30, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 9), command=lambda: self.right_tabs.set("Geoprocessing")).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(g_panes, text="🗄 Catalog", width=80, height=30, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 9), command=lambda: self.right_tabs.set("Catalog")).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(g_panes, text="🎨 Symbology", width=95, height=30, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 9), command=lambda: self.right_tabs.set("Symbology")).pack(side=tk.LEFT, padx=2)

    def _build_ribbon_group_edit(self, tab):
        f = ctk.CTkFrame(tab, fg_color="transparent")
        f.pack(fill=tk.BOTH, expand=True)

        g_feat = self._create_ribbon_group(f, "Features")
        ctk.CTkButton(g_feat, text="➕ Create Feature", width=110, height=30, fg_color=self.C_ESRI_BLUE, hover_color=self.C_ESRI_HOVER, font=("Segoe UI", 9, "bold"), command=self._action_add_point_dialog).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(g_feat, text="📋 Attributes Table", width=120, height=30, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 9), command=self._switch_to_table_tab).pack(side=tk.LEFT, padx=2)

        g_save = self._create_ribbon_group(f, "Manage Edits")
        ctk.CTkButton(g_save, text="💾 Save", width=65, height=30, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 9), command=lambda: messagebox.showinfo("ArcGIS Pro", "Edits saved.")).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(g_save, text="Discard", width=65, height=30, fg_color="#ffffff", hover_color="#fee2e2", text_color="#991b1b", border_color="#fca5a5", border_width=1, font=("Segoe UI", 9), command=self._action_clear_selection).pack(side=tk.LEFT, padx=2)

    def _build_ribbon_group_help(self, tab):
        """Exact match of Help ribbon tab in Image 3."""
        f = ctk.CTkFrame(tab, fg_color="transparent")
        f.pack(fill=tk.BOTH, expand=True)

        # Customize Group (Image 3, Box 6)
        g_cust = self._create_ribbon_group(f, "Customize")
        ctk.CTkButton(g_cust, text="Ribbon", width=65, height=28, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=1)
        ctk.CTkButton(g_cust, text="Quick Access Toolbar", width=125, height=28, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=1)
        ctk.CTkButton(g_cust, text="Shortcuts", width=65, height=28, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=1)

        # Help Group (Image 3, Box 7)
        g_help = self._create_ribbon_group(f, "Help")
        ctk.CTkButton(g_help, text="❓ Help ▾", width=75, height=32, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#007AC2", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(g_help, text="📖 Learning Resources", width=135, height=32, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#007AC2", border_color="#007AC2", border_width=1, font=("Segoe UI", 9, "bold"), command=self.show_start_page_view).pack(side=tk.LEFT, padx=2)

        # Performance Group
        g_perf = self._create_ribbon_group(f, "Performance")
        ctk.CTkButton(g_perf, text="📈 Diagnostic Monitor", width=130, height=28, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=2)

        # Contact Us Group
        g_contact = self._create_ribbon_group(f, "Contact Us")
        ctk.CTkButton(g_contact, text="Esri Community", width=105, height=28, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=1)
        ctk.CTkButton(g_contact, text="Technical Support", width=115, height=28, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=1)

    # =========================================================================
    # 3. DOCKED WORKSPACE (Left TOC | Center Map Viewport | Right Catalog)
    # =========================================================================
    def _build_docked_workspace(self, parent):
        workspace = ctk.CTkFrame(parent, fg_color="#f1f5f9", corner_radius=0)
        workspace.pack(fill=tk.BOTH, expand=True)

        # LEFT TOC: Contents Pane (Image 5)
        self.toc_panel = ctk.CTkFrame(workspace, width=280, fg_color=self.C_PANEL_BG, corner_radius=0)
        self.toc_panel.pack(fill=tk.Y, side=tk.LEFT, padx=(0, 1))

        # RIGHT DOCK: Catalog & Geoprocessing (Image 5)
        self.right_panel = ctk.CTkFrame(workspace, width=320, fg_color=self.C_PANEL_BG, corner_radius=0)
        self.right_panel.pack(fill=tk.Y, side=tk.RIGHT, padx=(1, 0))

        # CENTER: Map Viewport Tabs (Image 4)
        self.center_viewport = ctk.CTkFrame(workspace, fg_color="#ffffff", corner_radius=0)
        self.center_viewport.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Build center first so self.canvas is ready
        self._build_center_tabbed_view()
        self._build_toc_contents()
        self._build_right_dock_panel()

    # =========================================================================
    # 4. LEFT TOC: CONTENTS PANE (Exact match of Image 5)
    # =========================================================================
    def _build_toc_contents(self):
        # Pane Header with Dropdown, Pin, and Close (Image 5)
        hdr = ctk.CTkFrame(self.toc_panel, height=28, fg_color=self.C_HEADER_BG, corner_radius=0)
        hdr.pack(fill=tk.X, side=tk.TOP)

        ctk.CTkLabel(hdr, text="Contents", font=("Segoe UI", 11, "bold"), text_color="#1e293b").pack(side=tk.LEFT, padx=8)
        ctk.CTkLabel(hdr, text="▾   📌   ✕", font=("Segoe UI", 9), text_color="#64748b").pack(side=tk.RIGHT, padx=6)

        # Search Bar with Filter Funnel (Image 5)
        search_bar = ctk.CTkFrame(self.toc_panel, height=28, fg_color="#ffffff", border_color=self.C_BORDER, border_width=1, corner_radius=2)
        search_bar.pack(fill=tk.X, padx=6, pady=4)

        ctk.CTkLabel(search_bar, text="Y", font=("Segoe UI", 10, "bold"), text_color="#64748b").pack(side=tk.LEFT, padx=(6, 2))
        e_toc = ctk.CTkEntry(search_bar, placeholder_text="Search", height=22, fg_color="transparent", border_width=0, font=("Segoe UI", 9))
        e_toc.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ctk.CTkLabel(search_bar, text="🔍", font=("Segoe UI", 10), text_color="#94a3b8").pack(side=tk.RIGHT, padx=6)

        # 6 View Filter Toolbar Buttons (Image 5)
        # 1: Drawing Order (Active with blue underline), 2: Source, 3: Selection, 4: Editing, 5: Snapping, 6: Labeling
        icons_row = ctk.CTkFrame(self.toc_panel, height=32, fg_color="#ffffff", corner_radius=0)
        icons_row.pack(fill=tk.X, pady=(0, 2))

        filter_icons = [
            ("☰", "List By Drawing Order", True),
            ("🗄", "List By Data Source", False),
            ("☑", "List By Selection", False),
            ("✏", "List By Editing", False),
            ("🧲", "List By Snapping", False),
            ("🏷", "List By Labeling", False)
        ]
        for ic, tip, is_active in filter_icons:
            b = ctk.CTkButton(
                icons_row, text=ic, width=38, height=26,
                font=("Segoe UI", 11, "bold" if is_active else "normal"),
                fg_color="#e0f2fe" if is_active else "transparent",
                hover_color="#e2e8f0",
                text_color="#007AC2" if is_active else "#64748b",
                border_color="#007AC2" if is_active else "#cbd5e1",
                border_width=1 if is_active else 0,
                corner_radius=2
            )
            b.pack(side=tk.LEFT, padx=1, pady=3)

        # Section Header: Drawing Order
        ctk.CTkLabel(self.toc_panel, text="Drawing Order", font=("Segoe UI", 10, "bold"), text_color="#334155").pack(anchor="w", padx=10, pady=(6, 2))

        # Root Map Node: City Center (Selected row highlight)
        self.map_node_frame = ctk.CTkFrame(self.toc_panel, height=26, fg_color="#dbeafe", corner_radius=2)
        self.map_node_frame.pack(fill=tk.X, padx=6, pady=2)
        ctk.CTkLabel(self.map_node_frame, text="▶ 🗺 City Center", font=("Segoe UI", 10, "bold"), text_color="#1d4ed8").pack(side=tk.LEFT, padx=6)

        # Layers Scrollable Container
        self.toc_layers_container = ctk.CTkScrollableFrame(self.toc_panel, fg_color="transparent")
        self.toc_layers_container.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

    def _refresh_toc(self):
        """Builds exact Contents TOC hierarchy matching Image 5."""
        for w in self.toc_layers_container.winfo_children():
            w.destroy()

        for layer in reversed(self.canvas.layers):
            is_active = (self.active_layer and self.active_layer.name == layer.name)

            box = ctk.CTkFrame(self.toc_layers_container, fg_color="#ffffff", border_color="#e2e8f0", border_width=1, corner_radius=3)
            box.pack(fill=tk.X, padx=2, pady=2)

            r1 = ctk.CTkFrame(box, fg_color="transparent")
            r1.pack(fill=tk.X, padx=4, pady=2)

            # Checkbox
            vis_var = tk.BooleanVar(value=self.canvas.layer_visibility.get(layer.name, True))

            def _toggle(val=vis_var, l_name=layer.name):
                self.canvas.set_layer_visibility(l_name, val.get())

            ctk.CTkCheckBox(r1, text="", variable=vis_var, width=16, command=_toggle).pack(side=tk.LEFT, padx=(2, 4))

            # Expand arrow & Symbol Swatch
            if layer.name == "Bus Routes":
                ctk.CTkLabel(r1, text="▼", font=("Segoe UI", 8), text_color="#64748b").pack(side=tk.LEFT, padx=(0, 4))
                ctk.CTkLabel(r1, text="Bus Routes", font=("Segoe UI", 10, "bold"), text_color="#1e293b").pack(side=tk.LEFT)

                # Legend Category: Type (Image 5)
                sub_legend = ctk.CTkFrame(box, fg_color="transparent")
                sub_legend.pack(fill=tk.X, padx=22, pady=(2, 4))
                ctk.CTkLabel(sub_legend, text="Type", font=("Segoe UI", 9, "bold"), text_color="#64748b").pack(anchor="w")

                legend_items = [
                    ("━", "#059669", "City Connector"),
                    ("┅", "#2563eb", "Ferry"),
                    ("━", "#4338ca", "Metro Line"),
                    ("━", "#db2777", "Suburban Link")
                ]
                for sym, col, l_title in legend_items:
                    item_row = ctk.CTkFrame(sub_legend, fg_color="transparent")
                    item_row.pack(fill=tk.X, pady=1)
                    ctk.CTkLabel(item_row, text=sym, font=("Segoe UI", 11, "bold"), text_color=col).pack(side=tk.LEFT, padx=(0, 6))
                    ctk.CTkLabel(item_row, text=l_title, font=("Segoe UI", 9), text_color="#334155").pack(side=tk.LEFT)

            elif layer.name == "Bus Stops":
                ctk.CTkLabel(r1, text="•", font=("Segoe UI", 14, "bold"), text_color="#059669").pack(side=tk.LEFT, padx=(2, 4))
                ctk.CTkLabel(r1, text="Bus Stops", font=("Segoe UI", 10, "bold" if is_active else "normal"), text_color="#1e293b").pack(side=tk.LEFT)
                ctk.CTkLabel(r1, text=f"({len(layer)})", font=("Segoe UI", 8), text_color="#64748b").pack(side=tk.RIGHT, padx=4)

            else:
                # Default layer row
                icon = "■" if layer.geometry_type == "Polygon" else "•"
                renderer = self.canvas.layer_renderers.get(layer.name)
                col = getattr(renderer, "fill", None) or "#007AC2"
                ctk.CTkLabel(r1, text=icon, font=("Segoe UI", 12), text_color=col).pack(side=tk.LEFT, padx=(2, 4))
                ctk.CTkLabel(r1, text=layer.name, font=("Segoe UI", 10, "bold" if is_active else "normal"), text_color="#1e293b").pack(side=tk.LEFT)
                ctk.CTkLabel(r1, text=f"({len(layer)})", font=("Segoe UI", 8), text_color="#64748b").pack(side=tk.RIGHT, padx=4)

    def _toggle_toc_panel(self):
        if self.toc_panel.winfo_ismapped():
            self.toc_panel.pack_forget()
        else:
            self.toc_panel.pack(fill=tk.Y, side=tk.LEFT, padx=(0, 1), before=self.center_viewport)

    def _activate_stacked_pane(self, p_name: str):
        """Activates one of the 6 stacked panes (Catalog, Create Features, Locate, Symbology, Geoprocessing, Chart Properties)."""
        self.right_tabs.set(p_name)
        if hasattr(self, "stacked_btns"):
            for name, b in self.stacked_btns.items():
                if name == p_name:
                    b.configure(fg_color="#e0f2fe", text_color="#007AC2", border_color="#007AC2", border_width=1)
                else:
                    b.configure(fg_color="transparent", text_color="#64748b", border_color="#cbd5e1", border_width=0)

    # =========================================================================
    # 5. RIGHT PANEL: STACKED PANES, CATALOG & GEOPROCESSING (Images 1, 2, 5)
    # =========================================================================
    def _build_right_dock_panel(self):
        # 1. Stacked Panes Strip (Image 2)
        stacked_bar = ctk.CTkFrame(self.right_panel, height=28, fg_color="#f1f5f9", corner_radius=0)
        stacked_bar.pack(fill=tk.X, side=tk.TOP, pady=(0, 2))

        self.stacked_btns = {}
        pane_items = [
            ("Catalog", "📁 C..."),
            ("Create Features", "📝 C..."),
            ("Locate", "🔍 L..."),
            ("Symbology", "🖌 S..."),
            ("Geoprocessing", "💼 G..."),
            ("Chart Properties", "📊 C...")
        ]

        for p_name, short_label in pane_items:
            b = ctk.CTkButton(
                stacked_bar, text=short_label, width=44, height=24,
                font=("Segoe UI", 9),
                fg_color="#e0f2fe" if p_name == "Catalog" else "transparent",
                hover_color="#e2e8f0",
                text_color="#007AC2" if p_name == "Catalog" else "#64748b",
                border_color="#007AC2" if p_name == "Catalog" else "#cbd5e1",
                border_width=1 if p_name == "Catalog" else 0,
                corner_radius=2,
                command=lambda p=p_name: self._activate_stacked_pane(p)
            )
            b.pack(side=tk.LEFT, padx=1, pady=2)
            self.stacked_btns[p_name] = b

        # Dropdown menu button '▾' (Image 2)
        def _show_stacked_menu():
            m = tk.Menu(self, tearoff=0, font=("Segoe UI", 9))
            m.add_command(label="📁  Catalog", command=lambda: self._activate_stacked_pane("Catalog"))
            m.add_command(label="📝  Create Features", command=lambda: self._activate_stacked_pane("Create Features"))
            m.add_command(label="🔍  Locate", command=lambda: self._activate_stacked_pane("Locate"))
            m.add_command(label="🖌  Symbology", command=lambda: self._activate_stacked_pane("Symbology"))
            m.add_command(label="💼  Geoprocessing", command=lambda: self._activate_stacked_pane("Geoprocessing"))
            m.add_command(label="📊  Chart Properties", command=lambda: self._activate_stacked_pane("Chart Properties"))
            x = btn_menu.winfo_rootx()
            y = btn_menu.winfo_rooty() + btn_menu.winfo_height()
            m.tk_popup(x, y)

        btn_menu = ctk.CTkButton(
            stacked_bar, text="▾", width=22, height=24,
            font=("Segoe UI", 10, "bold"),
            fg_color="transparent", hover_color="#e2e8f0", text_color="#334155",
            corner_radius=2,
            command=_show_stacked_menu
        )
        btn_menu.pack(side=tk.LEFT, padx=2, pady=2)

        # 2. Tabview with all 6 Stacked Panes
        self.right_tabs = ctk.CTkTabview(
            self.right_panel,
            fg_color=self.C_PANEL_BG,
            segmented_button_fg_color="#f1f5f9",
            segmented_button_selected_color=self.C_ESRI_BLUE,
            segmented_button_selected_hover_color=self.C_ESRI_HOVER,
            corner_radius=0
        )
        self.right_tabs.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        tab_catalog = self.right_tabs.add("Catalog")
        tab_create = self.right_tabs.add("Create Features")
        tab_locate = self.right_tabs.add("Locate")
        tab_sym = self.right_tabs.add("Symbology")
        tab_gp = self.right_tabs.add("Geoprocessing")
        tab_chart = self.right_tabs.add("Chart Properties")

        self._build_catalog_pane(tab_catalog)
        self._build_create_features_pane(tab_create)
        self._build_locate_pane(tab_locate)
        self._build_symbology_pane(tab_sym)
        self._build_geoprocessing_pane(tab_gp)
        self._build_chart_properties_pane(tab_chart)

    def _build_catalog_pane(self, parent):
        """Exact match of Catalog dock in Image 5."""
        hdr = ctk.CTkFrame(parent, height=28, fg_color=self.C_HEADER_BG, corner_radius=0)
        hdr.pack(fill=tk.X, side=tk.TOP)
        ctk.CTkLabel(hdr, text="Catalog", font=("Segoe UI", 11, "bold"), text_color="#1e293b").pack(side=tk.LEFT, padx=8)
        ctk.CTkLabel(hdr, text="▾   📌   ✕", font=("Segoe UI", 9), text_color="#64748b").pack(side=tk.RIGHT, padx=6)

        # Tabs row: Project (Active with underline), Portal, Computer, Favorites, Menu (Image 5)
        cat_tabs = ctk.CTkFrame(parent, height=28, fg_color="#ffffff", corner_radius=0)
        cat_tabs.pack(fill=tk.X, pady=(0, 2))

        ctk.CTkButton(cat_tabs, text="Project", width=55, height=24, fg_color="#e0f2fe", text_color="#007AC2", border_color="#007AC2", border_width=1, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(cat_tabs, text="Portal", width=50, height=24, fg_color="transparent", text_color="#64748b", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=1)
        ctk.CTkButton(cat_tabs, text="Computer", width=65, height=24, fg_color="transparent", text_color="#64748b", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=1)
        ctk.CTkButton(cat_tabs, text="Favorites", width=60, height=24, fg_color="transparent", text_color="#64748b", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=1)
        ctk.CTkLabel(cat_tabs, text="☰", font=("Segoe UI", 11), text_color="#64748b").pack(side=tk.RIGHT, padx=6)

        # Navigation Bar: Back arrow, Home icon, Search Project (Image 5)
        nav_row = ctk.CTkFrame(parent, height=28, fg_color="#ffffff", border_color=self.C_BORDER, border_width=1, corner_radius=2)
        nav_row.pack(fill=tk.X, padx=6, pady=4)
        ctk.CTkLabel(nav_row, text="←", font=("Segoe UI", 11, "bold"), text_color="#64748b").pack(side=tk.LEFT, padx=4)
        ctk.CTkLabel(nav_row, text="🏠", font=("Segoe UI", 10), text_color="#007AC2").pack(side=tk.LEFT, padx=4)
        ctk.CTkEntry(nav_row, placeholder_text="Search Project", height=22, fg_color="transparent", border_width=0, font=("Segoe UI", 9)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ctk.CTkLabel(nav_row, text="🔍", font=("Segoe UI", 9), text_color="#94a3b8").pack(side=tk.RIGHT, padx=4)

        # Tree Structure matching Image 5
        tree_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        tree_scroll.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        tree_items = [
            ("▼ 📁 Maps", ["🗺 City Center", "🗺 Neighborhoods", "🏛 Routes 3D"]),
            ("▶ 🧰 Toolboxes", ["SpatialAnalysis.tbx"]),
            ("▼ 🗄 Databases", [
                "▼ 🗃 Christchurch Transportation.gdb",
                "     ━ BusRoutes",
                "     • BusStops",
                "     • MeshblockPoints",
                "     ■ UrbanArea",
                "▶ 🗃 ChristchurchData.gdb"
            ]),
            ("▼ 📄 Layouts", ["📐 Christchurch Transportation"])
        ]

        for section, children in tree_items:
            ctk.CTkLabel(tree_scroll, text=section, font=("Segoe UI", 10, "bold"), text_color="#007AC2").pack(anchor="w", pady=(6, 2))
            for ch in children:
                is_sub = ch.startswith("     ")
                ctk.CTkLabel(tree_scroll, text=ch, font=("Segoe UI", 9), text_color="#334155" if not is_sub else "#64748b").pack(anchor="w", padx=10 if not is_sub else 20, pady=1)

    def _build_geoprocessing_pane(self, parent):
        hdr = ctk.CTkFrame(parent, height=28, fg_color=self.C_HEADER_BG, corner_radius=0)
        hdr.pack(fill=tk.X, side=tk.TOP)
        ctk.CTkLabel(hdr, text="Geoprocessing", font=("Segoe UI", 11, "bold"), text_color="#1e293b").pack(side=tk.LEFT, padx=8)

        search_f = ctk.CTkEntry(parent, placeholder_text="🔍 Find Tools", height=26, font=("Segoe UI", 9))
        search_f.pack(fill=tk.X, padx=8, pady=6)

        ctk.CTkLabel(parent, text="Favorites", font=("Segoe UI", 10, "bold"), text_color="#334155").pack(anchor="w", padx=10, pady=(6, 2))

        tools = [
            ("◎ Buffer (Proximity)", self._open_right_tool_buffer),
            ("⧉ Spatial Join (Overlay)", self._open_right_tool_join),
            ("✂ Clip (Extract)", self._action_clip),
            ("📊 Summary Statistics", self._action_summary_stats),
            ("🗂 Export to ESRI JSON", self._action_export_esri_json)
        ]
        for t_name, t_cmd in tools:
            ctk.CTkButton(
                parent, text=f"  {t_name}", anchor="w",
                font=("Segoe UI", 9), height=28,
                fg_color="#ffffff", hover_color="#f1f5f9", text_color="#1e293b",
                border_color=self.C_BORDER, border_width=1,
                command=t_cmd
            ).pack(fill=tk.X, padx=8, pady=2)

        # Dynamic Parameters Container
        self.gp_param_container = ctk.CTkFrame(parent, fg_color="#ffffff", border_color=self.C_BORDER, border_width=1, corner_radius=4)
        self.gp_param_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self._show_gp_welcome()

    def _show_gp_welcome(self):
        for w in self.gp_param_container.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.gp_param_container, text="Select a geoprocessing tool above\nto configure parameters and run.", font=("Segoe UI", 9), text_color="#64748b").pack(expand=True, pady=30)

    def _open_right_tool_buffer(self):
        self.right_tabs.set("Geoprocessing")
        for w in self.gp_param_container.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.gp_param_container, text="Buffer (Analysis Tools)", font=("Segoe UI", 10, "bold"), text_color="#007AC2").pack(anchor="w", padx=8, pady=(8, 4))

        ctk.CTkLabel(self.gp_param_container, text="Input Features:", font=("Segoe UI", 9)).pack(anchor="w", padx=8, pady=(4, 1))
        layer_names = [l.name for l in self.canvas.layers] or ["None"]
        c_combo = ctk.CTkComboBox(self.gp_param_container, values=layer_names, height=26, font=("Segoe UI", 9))
        c_combo.pack(fill=tk.X, padx=8, pady=(0, 6))

        ctk.CTkLabel(self.gp_param_container, text="Distance (Decimal Degrees / Radius):", font=("Segoe UI", 9)).pack(anchor="w", padx=8, pady=(4, 1))
        e_dist = ctk.CTkEntry(self.gp_param_container, height=26, font=("Segoe UI", 9))
        e_dist.insert(0, "0.015")
        e_dist.pack(fill=tk.X, padx=8, pady=(0, 6))

        ctk.CTkLabel(self.gp_param_container, text="Output Feature Class:", font=("Segoe UI", 9)).pack(anchor="w", padx=8, pady=(4, 1))
        e_out = ctk.CTkEntry(self.gp_param_container, height=26, font=("Segoe UI", 9))
        e_out.insert(0, "Buffer_Output")
        e_out.pack(fill=tk.X, padx=8, pady=(0, 10))

        def _run():
            target = next((l for l in self.canvas.layers if l.name == c_combo.get()), None)
            if not target:
                messagebox.showerror("Error", "Select a valid input layer.")
                return
            try:
                dist = float(e_dist.get().replace(",", "."))
            except ValueError:
                messagebox.showerror("Error", "Invalid buffer distance.")
                return
            out_layer = Geoprocessing.buffer_layer(target, distance=dist, output_name=e_out.get().strip() or "Buffer_Output")
            self.canvas.add_layer(out_layer, SimpleRenderer(fill="#007AC2", stroke="#38bdf8", opacity=0.35))
            self._refresh_toc()
            messagebox.showinfo("Geoprocessing", f"Buffer succeeded! Created '{out_layer.name}'.")

        ctk.CTkButton(self.gp_param_container, text="▶ Run", height=30, fg_color=self.C_ESRI_BLUE, hover_color=self.C_ESRI_HOVER, font=("Segoe UI", 10, "bold"), command=_run).pack(fill=tk.X, padx=8, pady=8)

    def _open_right_tool_join(self):
        self.right_tabs.set("Geoprocessing")
        for w in self.gp_param_container.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.gp_param_container, text="Spatial Join (Analysis Tools)", font=("Segoe UI", 10, "bold"), text_color="#007AC2").pack(anchor="w", padx=8, pady=(8, 4))
        pts_layers = [l.name for l in self.canvas.layers if l.geometry_type == "Point"] or ["None"]
        poly_layers = [l.name for l in self.canvas.layers if l.geometry_type == "Polygon"] or ["None"]

        ctk.CTkLabel(self.gp_param_container, text="Target Features (Points):", font=("Segoe UI", 9)).pack(anchor="w", padx=8, pady=(4, 1))
        c_target = ctk.CTkComboBox(self.gp_param_container, values=pts_layers, height=26, font=("Segoe UI", 9))
        c_target.pack(fill=tk.X, padx=8, pady=(0, 6))

        ctk.CTkLabel(self.gp_param_container, text="Join Features (Polygons):", font=("Segoe UI", 9)).pack(anchor="w", padx=8, pady=(4, 1))
        c_join = ctk.CTkComboBox(self.gp_param_container, values=poly_layers, height=26, font=("Segoe UI", 9))
        c_join.pack(fill=tk.X, padx=8, pady=(0, 6))

        def _run():
            target = next((l for l in self.canvas.layers if l.name == c_target.get()), None)
            join = next((l for l in self.canvas.layers if l.name == c_join.get()), None)
            if not target or not join:
                messagebox.showerror("Error", "Select valid target and join layers.")
                return
            out_layer = Geoprocessing.spatial_join(target, join, "SpatialJoin_Output")
            self.canvas.add_layer(out_layer, SimpleRenderer(fill="#059669", stroke="#064e3b", point_radius=6.5))
            self._refresh_toc()
            messagebox.showinfo("Geoprocessing", f"Spatial Join succeeded! Created '{out_layer.name}'.")

        ctk.CTkButton(self.gp_param_container, text="▶ Run", height=30, fg_color=self.C_ESRI_BLUE, hover_color=self.C_ESRI_HOVER, font=("Segoe UI", 10, "bold"), command=_run).pack(fill=tk.X, padx=8, pady=12)

    # =========================================================================
    # SYMBOLOGY PANE (Exact match of Image 1: Format Polygon Symbol)
    # =========================================================================
    def _build_symbology_pane(self, parent):
        # 1. Header (Image 1, Points 1 & 5)
        hdr = ctk.CTkFrame(parent, height=32, fg_color=self.C_HEADER_BG, corner_radius=0)
        hdr.pack(fill=tk.X, side=tk.TOP)

        ctk.CTkButton(
            hdr, text="←", width=24, height=24, fg_color="transparent",
            hover_color="#e2e8f0", text_color="#334155", font=("Segoe UI", 11, "bold"),
            command=lambda: self.right_tabs.set("Catalog")
        ).pack(side=tk.LEFT, padx=(6, 2))

        self.lbl_sym_title = ctk.CTkLabel(hdr, text="Format Polygon Symbol", font=("Segoe UI", 10, "bold"), text_color="#1e293b")
        self.lbl_sym_title.pack(side=tk.LEFT, padx=4)
        ctk.CTkLabel(hdr, text="☰", font=("Segoe UI", 10), text_color="#64748b").pack(side=tk.LEFT, padx=4)
        ctk.CTkLabel(hdr, text="▾   □   ✕", font=("Segoe UI", 9), text_color="#64748b").pack(side=tk.RIGHT, padx=6)

        # Layer Subheader: Symbology - <Layer Name>
        sub_hdr = ctk.CTkFrame(parent, height=24, fg_color="#f8fafc", corner_radius=0)
        sub_hdr.pack(fill=tk.X, side=tk.TOP)
        self.lbl_sym_layer_banner = ctk.CTkLabel(sub_hdr, text="Symbology - Urban Area", font=("Segoe UI", 9, "bold"), text_color="#007AC2")
        self.lbl_sym_layer_banner.pack(side=tk.LEFT, padx=10)

        # 2. Primary Tabs: Gallery | Properties (Image 1, Point 2)
        prim_tabs = ctk.CTkFrame(parent, height=26, fg_color="#ffffff", corner_radius=0)
        prim_tabs.pack(fill=tk.X, side=tk.TOP)
        ctk.CTkButton(prim_tabs, text="Gallery", width=65, height=22, fg_color="transparent", text_color="#64748b", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=6)
        ctk.CTkButton(prim_tabs, text="Properties", width=75, height=22, fg_color="#e0f2fe", text_color="#007AC2", border_color="#007AC2", border_width=1, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=2)

        # 3. Secondary Graphical Tabs: 🖌 Appearance | 📑 Layers | 🔧 Structure (Image 1, Point 3)
        sec_tabs = ctk.CTkFrame(parent, height=28, fg_color="#f8fafc", corner_radius=0)
        sec_tabs.pack(fill=tk.X, side=tk.TOP, pady=(2, 2))
        ctk.CTkButton(sec_tabs, text="🖌", width=34, height=22, fg_color="#e0f2fe", text_color="#007AC2", border_color="#007AC2", border_width=1, font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=6)
        ctk.CTkButton(sec_tabs, text="📑", width=34, height=22, fg_color="transparent", text_color="#64748b", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(sec_tabs, text="🔧", width=34, height=22, fg_color="transparent", text_color="#64748b", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=2)

        # Scrollable Properties Body
        body = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        body.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

        # 4. Expander Section: [v] Appearance (Image 1, Point 4)
        exp_hdr = ctk.CTkFrame(body, height=24, fg_color="#ffffff", corner_radius=3)
        exp_hdr.pack(fill=tk.X, pady=(2, 4))
        ctk.CTkLabel(exp_hdr, text="☑ Appearance", font=("Segoe UI", 9, "bold"), text_color="#1e293b").pack(side=tk.LEFT, padx=8)

        app_form = ctk.CTkFrame(body, fg_color="#ffffff", border_color="#e2e8f0", border_width=1, corner_radius=4)
        app_form.pack(fill=tk.X, pady=(0, 6), padx=2)

        # Layer selector row
        canvas = getattr(self, "canvas", None)
        layer_names = [l.name for l in canvas.layers] if canvas else ["UrbanArea", "Bus Routes", "Bus Stops"]
        r_layer = ctk.CTkFrame(app_form, fg_color="transparent")
        r_layer.pack(fill=tk.X, padx=8, pady=4)
        ctk.CTkLabel(r_layer, text="Layer:", width=90, anchor="w", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        self.combo_sym_layer = ctk.CTkComboBox(r_layer, values=layer_names, height=24, font=("Segoe UI", 9), command=self._on_sym_layer_changed)
        if layer_names:
            self.combo_sym_layer.set(layer_names[0])
        self.combo_sym_layer.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Color row (Fill Color)
        self.selected_sym_color = tk.StringVar(value="#bbf7d0")
        self.sym_fill_color = self.selected_sym_color  # Alias for compatibility
        self.sym_fill_color_var = self.selected_sym_color
        r_color = ctk.CTkFrame(app_form, fg_color="transparent")
        r_color.pack(fill=tk.X, padx=8, pady=4)
        ctk.CTkLabel(r_color, text="Color", width=90, anchor="w", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.btn_sym_fill_preview = ctk.CTkButton(
            r_color, text="  ▾", width=60, height=24,
            fg_color=self.sym_fill_color.get(), hover_color="#86efac", text_color="#000000",
            border_color="#94a3b8", border_width=1, corner_radius=2,
            command=self._choose_sym_fill_color
        )
        self.btn_sym_fill_preview.pack(side=tk.RIGHT)

        # Outline Color row
        self.sym_outline_color = tk.StringVar(value="#000000")
        self.sym_outline_color_var = self.sym_outline_color
        r_outline = ctk.CTkFrame(app_form, fg_color="transparent")
        r_outline.pack(fill=tk.X, padx=8, pady=4)
        ctk.CTkLabel(r_outline, text="Outline color", width=90, anchor="w", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.btn_sym_outline_preview = ctk.CTkButton(
            r_outline, text="  ▾", width=60, height=24,
            fg_color=self.sym_outline_color.get(), hover_color="#334155", text_color="#ffffff",
            border_color="#94a3b8", border_width=1, corner_radius=2,
            command=self._choose_sym_outline_color
        )
        self.btn_sym_outline_preview.pack(side=tk.RIGHT)

        # Outline Width spinbox row
        self.sym_outline_width = tk.DoubleVar(value=1.0)
        self.sym_outline_width_var = self.sym_outline_width
        r_width = ctk.CTkFrame(app_form, fg_color="transparent")
        r_width.pack(fill=tk.X, padx=8, pady=4)
        ctk.CTkLabel(r_width, text="Outline width", width=90, anchor="w", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        spin_f = ctk.CTkFrame(r_width, fg_color="#ffffff", border_color="#cbd5e1", border_width=1, corner_radius=2)
        spin_f.pack(side=tk.RIGHT)
        self.lbl_sym_width = ctk.CTkLabel(spin_f, text=f"{self.sym_outline_width.get():.0f} pt", width=36, font=("Segoe UI", 9))
        self.lbl_sym_width.pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(spin_f, text="▲", width=14, height=10, fg_color="transparent", text_color="#334155", font=("Segoe UI", 6), command=lambda: self._adjust_sym_width(0.5)).pack(side=tk.TOP)
        ctk.CTkButton(spin_f, text="▼", width=14, height=10, fg_color="transparent", text_color="#334155", font=("Segoe UI", 6), command=lambda: self._adjust_sym_width(-0.5)).pack(side=tk.BOTTOM)

        # Enable scale-based sizing
        r_scale = ctk.CTkFrame(app_form, fg_color="transparent")
        r_scale.pack(fill=tk.X, padx=8, pady=3)
        ctk.CTkCheckBox(r_scale, text="Enable scale-based sizing", font=("Segoe UI", 8), corner_radius=2).pack(anchor="w")

        # Angle alignment
        r_align = ctk.CTkFrame(app_form, fg_color="transparent")
        r_align.pack(fill=tk.X, padx=8, pady=4)
        ctk.CTkLabel(r_align, text="Angle alignment", width=90, anchor="w", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        ctk.CTkComboBox(r_align, values=["Map", "Display"], height=22, font=("Segoe UI", 9), width=90).pack(side=tk.RIGHT)

        # 5. Resizer Handle (Image 1, Point 6)
        div_frame = ctk.CTkFrame(body, height=16, fg_color="transparent")
        div_frame.pack(fill=tk.X, pady=(4, 2))
        ctk.CTkFrame(div_frame, height=1, fg_color="#cbd5e1").pack(fill=tk.X, side=tk.TOP, pady=7)
        ctk.CTkLabel(div_frame, text="···", font=("Segoe UI", 11, "bold"), text_color="#94a3b8", fg_color="#ffffff", corner_radius=4, width=28, height=14).place(relx=0.5, rely=0.5, anchor="center")

        # 6. Live Symbol Preview Canvas Box (Image 1)
        prev_box = ctk.CTkFrame(body, height=110, fg_color="#e5e7eb", border_color="#cbd5e1", border_width=1, corner_radius=4)
        prev_box.pack(fill=tk.X, padx=2, pady=4)
        self.sym_preview_canvas = tk.Canvas(prev_box, height=100, bg="#f1f5f9", highlightthickness=0)
        self.sym_preview_canvas.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # 7. Bottom Controls: 100% ▾ | Auto Apply toggle | Apply | Cancel (Image 1)
        bottom_bar = ctk.CTkFrame(parent, height=36, fg_color=self.C_HEADER_BG, corner_radius=0)
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM)

        ctk.CTkLabel(bottom_bar, text="100% ▾", font=("Segoe UI", 9), text_color="#64748b").pack(side=tk.LEFT, padx=6)
        ctk.CTkButton(bottom_bar, text="▬", width=22, height=22, fg_color="transparent", hover_color="#e2e8f0", text_color="#475569", command=self._redraw_sym_preview).pack(side=tk.LEFT, padx=2)

        self.auto_apply_var = tk.BooleanVar(value=True)
        ctk.CTkSwitch(bottom_bar, text="Auto Apply", variable=self.auto_apply_var, font=("Segoe UI", 8), width=36).pack(side=tk.LEFT, padx=6)

        ctk.CTkButton(bottom_bar, text="Cancel", width=50, height=24, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, font=("Segoe UI", 9)).pack(side=tk.RIGHT, padx=4)
        ctk.CTkButton(bottom_bar, text="Apply", width=50, height=24, fg_color=self.C_ESRI_BLUE, hover_color=self.C_ESRI_HOVER, text_color="#ffffff", font=("Segoe UI", 9, "bold"), command=self._apply_current_symbology).pack(side=tk.RIGHT, padx=2)

        self._redraw_sym_preview()

    def _choose_sym_fill_color(self):
        palette = ["#bbf7d0", "#dc2626", "#f59e0b", "#fef08a", "#86efac", "#38bdf8", "#007AC2", "#059669", "#312e81", "#db2777", "#ffffff", "#000000"]
        curr = self.sym_fill_color.get()
        idx = (palette.index(curr) + 1) % len(palette) if curr in palette else 0
        new_c = palette[idx]
        self.sym_fill_color.set(new_c)
        self.btn_sym_fill_preview.configure(fg_color=new_c)
        self._redraw_sym_preview()
        if self.auto_apply_var.get():
            self._apply_current_symbology()

    def _choose_sym_outline_color(self):
        palette = ["#000000", "#ffffff", "#94a3b8", "#dc2626", "#007AC2", "#059669"]
        curr = self.sym_outline_color.get()
        idx = (palette.index(curr) + 1) % len(palette) if curr in palette else 0
        new_c = palette[idx]
        self.sym_outline_color.set(new_c)
        self.btn_sym_outline_preview.configure(fg_color=new_c)
        self._redraw_sym_preview()
        if self.auto_apply_var.get():
            self._apply_current_symbology()

    def _adjust_sym_width(self, delta: float):
        w = max(0.5, min(10.0, self.sym_outline_width.get() + delta))
        self.sym_outline_width.set(w)
        self.lbl_sym_width.configure(text=f"{w:.0f} pt" if w.is_integer() else f"{w:.1f} pt")
        self._redraw_sym_preview()
        if self.auto_apply_var.get():
            self._apply_current_symbology()

    def _on_sym_layer_changed(self, layer_name: str):
        self.lbl_sym_layer_banner.configure(text=f"Symbology - {layer_name}")
        target = next((l for l in self.canvas.layers if l.name == layer_name), None) if self.canvas else None
        if target:
            if target.geometry_type == "Polygon":
                self.lbl_sym_title.configure(text="Format Polygon Symbol")
            elif target.geometry_type == "Polyline":
                self.lbl_sym_title.configure(text="Format Line Symbol")
            else:
                self.lbl_sym_title.configure(text="Format Point Symbol")
        self._redraw_sym_preview()

    def _redraw_sym_preview(self):
        if not hasattr(self, "sym_preview_canvas"):
            return
        self.sym_preview_canvas.delete("all")
        w = max(self.sym_preview_canvas.winfo_width(), 200)
        h = max(self.sym_preview_canvas.winfo_height(), 100)
        fill = self.sym_fill_color.get()
        outline = self.sym_outline_color.get()
        stroke_w = max(1, int(self.sym_outline_width.get()))

        l_name = self.combo_sym_layer.get() if hasattr(self, "combo_sym_layer") else "UrbanArea"
        target = next((l for l in self.canvas.layers if l.name == l_name), None) if self.canvas else None
        g_type = target.geometry_type if target else "Polygon"

        if g_type == "Polygon":
            x1, y1 = w // 2 - 45, h // 2 - 25
            x2, y2 = w // 2 + 45, h // 2 + 25
            self.sym_preview_canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=stroke_w)
        elif g_type == "Polyline":
            self.sym_preview_canvas.create_line(30, h // 2, w - 30, h // 2, fill=fill, width=stroke_w + 1)
        else:
            r = 10 + stroke_w
            self.sym_preview_canvas.create_oval(w // 2 - r, h // 2 - r, w // 2 + r, h // 2 + r, fill=fill, outline=outline, width=stroke_w)

    def _redraw_symbol_preview(self):
        """Public alias for redrawing the Format Symbol preview."""
        self._redraw_sym_preview()

    def _apply_current_symbology(self):
        l_name = self.combo_sym_layer.get() if hasattr(self, "combo_sym_layer") else ""
        target = next((l for l in self.canvas.layers if l.name == l_name), None) if self.canvas else None
        if target:
            stroke_w = max(1, int(self.sym_outline_width.get()))
            self.canvas.layer_renderers[target.name] = SimpleRenderer(
                fill=self.sym_fill_color.get(),
                stroke=self.sym_outline_color.get(),
                point_radius=5.5 + stroke_w
            )
            self.canvas.redraw()
            self._refresh_toc()

    # =========================================================================
    # CREATE FEATURES PANE (Stacked Pane from Image 2)
    # =========================================================================
    def _select_construction_template(self, template_name: str):
        self.selected_feature_template = template_name

    def _build_create_features_pane(self, parent):
        hdr = ctk.CTkFrame(parent, height=28, fg_color=self.C_HEADER_BG, corner_radius=0)
        hdr.pack(fill=tk.X, side=tk.TOP)
        ctk.CTkLabel(hdr, text="Create Features", font=("Segoe UI", 11, "bold"), text_color="#1e293b").pack(side=tk.LEFT, padx=8)
        ctk.CTkLabel(hdr, text="📌   ✕", font=("Segoe UI", 9), text_color="#64748b").pack(side=tk.RIGHT, padx=6)

        body = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        body.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        ctk.CTkLabel(body, text="Feature Templates:", font=("Segoe UI", 10, "bold"), text_color="#334155").pack(anchor="w", pady=(4, 6))

        templates = [
            ("UrbanArea (Hazard Zone)", "Polygon", "▨", ["Polygon", "Rectangle", "Circle", "Freehand"]),
            ("Bus Routes (Transit Network)", "Polyline", "〰", ["Line", "Two-Point Line", "Freehand"]),
            ("Bus Stops (Facilities)", "Point", "📍", ["Point", "Along Line", "End of Line"])
        ]

        for t_title, g_type, ic, tools in templates:
            card = ctk.CTkFrame(body, fg_color="#ffffff", border_color="#e2e8f0", border_width=1, corner_radius=4)
            card.pack(fill=tk.X, pady=4)
            ctk.CTkLabel(card, text=f"{ic}  {t_title}", font=("Segoe UI", 10, "bold"), text_color="#007AC2").pack(anchor="w", padx=8, pady=(6, 2))
            ctk.CTkLabel(card, text=f"Type: {g_type}", font=("Segoe UI", 8), text_color="#64748b").pack(anchor="w", padx=8, pady=(0, 4))

            tool_row = ctk.CTkFrame(card, fg_color="transparent")
            tool_row.pack(fill=tk.X, padx=8, pady=(0, 6))
            for t_btn in tools:
                ctk.CTkButton(
                    tool_row, text=t_btn, height=22, font=("Segoe UI", 8),
                    fg_color="#f1f5f9", hover_color="#e2e8f0", text_color="#334155",
                    command=lambda t=t_btn, lay=t_title: messagebox.showinfo("Create Features", f"Active tool: {t} on layer {lay}.\nClick on the map to digitize.")
                ).pack(side=tk.LEFT, padx=1)

    # =========================================================================
    # LOCATE PANE (Stacked Pane from Image 2)
    # =========================================================================
    def _search_locate(self):
        query = self.locate_search_entry.get().strip().lower()
        if not query:
            return
        matches = [p for p in getattr(self, "locate_places", []) if query in p[0].lower()]
        count = len(matches)
        if hasattr(self, "locate_results_label"):
            self.locate_results_label.configure(text=f"Found {count} matches in Christchurch")
        if matches and self.canvas:
            p_name, p_lon, p_lat = matches[0]
            self.canvas.zoom_to_extent(Envelope(p_lon - 0.015, p_lat - 0.01, p_lon + 0.015, p_lat + 0.01))
            self.lbl_selection.configure(text=f"Located: {p_name}")

    def _build_locate_pane(self, parent):
        hdr = ctk.CTkFrame(parent, height=28, fg_color=self.C_HEADER_BG, corner_radius=0)
        hdr.pack(fill=tk.X, side=tk.TOP)
        ctk.CTkLabel(hdr, text="Locate", font=("Segoe UI", 11, "bold"), text_color="#1e293b").pack(side=tk.LEFT, padx=8)
        ctk.CTkLabel(hdr, text="📌   ✕", font=("Segoe UI", 9), text_color="#64748b").pack(side=tk.RIGHT, padx=6)

        body = ctk.CTkFrame(parent, fg_color="transparent")
        body.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        ctk.CTkLabel(body, text="Provider:", font=("Segoe UI", 9, "bold"), text_color="#334155").pack(anchor="w", pady=(2, 2))
        c_prov = ctk.CTkComboBox(body, values=["ArcGIS World Geocoding Service", "Project Feature Layers", "Canterbury Regional Gazette"], height=24, font=("Segoe UI", 9))
        c_prov.pack(fill=tk.X, pady=(0, 6))

        s_box = ctk.CTkFrame(body, fg_color="#ffffff", border_color=self.C_BORDER, border_width=1, corner_radius=3)
        s_box.pack(fill=tk.X, pady=(0, 4))
        self.locate_search_entry = ctk.CTkEntry(s_box, placeholder_text="Search Christchurch places or coordinates...", height=24, font=("Segoe UI", 9), border_width=0, fg_color="transparent")
        self.locate_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        ctk.CTkButton(s_box, text="🔍", width=24, height=24, fg_color="transparent", hover_color="#e2e8f0", text_color="#007AC2", font=("Segoe UI", 9), command=self._search_locate).pack(side=tk.RIGHT, padx=2)

        self.locate_results_label = ctk.CTkLabel(body, text="", font=("Segoe UI", 8), text_color="#059669")
        self.locate_results_label.pack(anchor="w", padx=2, pady=(0, 4))

        ctk.CTkLabel(body, text="Quick Locations (Christchurch):", font=("Segoe UI", 9, "bold"), text_color="#334155").pack(anchor="w", pady=(4, 4))
        places = [
            ("Cathedral Square Interchange", 172.636, -43.531),
            ("Christchurch Hospital", 172.625, -43.534),
            ("University of Canterbury", 172.580, -43.523),
            ("New Brighton Pier", 172.730, -43.508),
            ("Lyttelton Port Terminal", 172.718, -43.602),
            ("Christchurch Airport", 172.535, -43.488)
        ]
        self.locate_places = places

        def _zoom_to_place(lon, lat, name):
            if self.canvas:
                self.canvas.zoom_to_extent(Envelope(lon - 0.015, lat - 0.01, lon + 0.015, lat + 0.01))
                self.lbl_selection.configure(text=f"Located: {name}")

        for p_name, p_lon, p_lat in places:
            r = ctk.CTkFrame(body, fg_color="#ffffff", border_color="#e2e8f0", border_width=1, corner_radius=3)
            r.pack(fill=tk.X, pady=2)
            ctk.CTkLabel(r, text=f"📍 {p_name}", font=("Segoe UI", 9), text_color="#1e293b").pack(side=tk.LEFT, padx=6, pady=4)
            ctk.CTkButton(r, text="Go to", width=45, height=20, font=("Segoe UI", 8), fg_color="#007AC2", command=lambda lon=p_lon, lat=p_lat, n=p_name: _zoom_to_place(lon, lat, n)).pack(side=tk.RIGHT, padx=6)

    # =========================================================================
    # CHART PROPERTIES PANE (Stacked Pane from Image 2)
    # =========================================================================
    def _build_chart_properties_pane(self, parent):
        hdr = ctk.CTkFrame(parent, height=28, fg_color=self.C_HEADER_BG, corner_radius=0)
        hdr.pack(fill=tk.X, side=tk.TOP)
        ctk.CTkLabel(hdr, text="Chart Properties - Urban Area", font=("Segoe UI", 11, "bold"), text_color="#1e293b").pack(side=tk.LEFT, padx=8)
        ctk.CTkLabel(hdr, text="📌   ✕", font=("Segoe UI", 9), text_color="#64748b").pack(side=tk.RIGHT, padx=6)

        body = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        body.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        ctk.CTkLabel(body, text="Chart Type:", font=("Segoe UI", 9, "bold"), text_color="#334155").pack(anchor="w", pady=(2, 2))
        ctk.CTkComboBox(body, values=["Bar Chart 📊", "Histogram 📉", "Box Plot 📦", "Scatter Plot 📈"], height=24, font=("Segoe UI", 9)).pack(fill=tk.X, pady=(0, 6))

        ctk.CTkLabel(body, text="Category (X-axis):", font=("Segoe UI", 9, "bold"), text_color="#334155").pack(anchor="w", pady=(2, 2))
        ctk.CTkComboBox(body, values=["RISK_LEVEL", "ZONE_NAME", "AREA_HA"], height=24, font=("Segoe UI", 9)).pack(fill=tk.X, pady=(0, 6))

        ctk.CTkLabel(body, text="Aggregation:", font=("Segoe UI", 9, "bold"), text_color="#334155").pack(anchor="w", pady=(2, 2))
        ctk.CTkComboBox(body, values=["Count of Features", "Sum (AREA_HA)", "Average (AREA_HA)"], height=24, font=("Segoe UI", 9)).pack(fill=tk.X, pady=(0, 10))

        # Chart Visual Preview Canvas
        ctk.CTkLabel(body, text="Chart Preview:", font=("Segoe UI", 9, "bold"), text_color="#334155").pack(anchor="w", pady=(4, 2))
        c_box = ctk.CTkFrame(body, height=130, fg_color="#ffffff", border_color="#cbd5e1", border_width=1, corner_radius=4)
        c_box.pack(fill=tk.X, pady=4)

        chart_cv = tk.Canvas(c_box, height=120, bg="#ffffff", highlightthickness=0)
        chart_cv.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        bars = [
            ("High", 3, "#dc2626"),
            ("Mod", 2, "#f59e0b"),
            ("Low", 4, "#fef08a"),
            ("Park", 1, "#86efac"),
            ("Water", 1, "#38bdf8")
        ]
        max_v = 4
        bw = 26
        spacing = 36
        base_y = 95
        for i, (name, val, color) in enumerate(bars):
            bx = 18 + i * spacing
            bh = int((val / max_v) * 65)
            chart_cv.create_rectangle(bx, base_y - bh, bx + bw, base_y, fill=color, outline="#334155", width=1)
            chart_cv.create_text(bx + bw // 2, base_y - bh - 6, text=str(val), font=("Segoe UI", 8, "bold"), fill="#1e293b")
            chart_cv.create_text(bx + bw // 2, base_y + 10, text=name, font=("Segoe UI", 7), fill="#64748b")

    # =========================================================================
    # 6. CENTER MAP VIEWPORT & STATUS BAR (Exact match of Image 4)
    # =========================================================================
    def _build_center_tabbed_view(self):
        # Map Tabs Bar matching Image 4
        self.center_tabs = ctk.CTkTabview(
            self.center_viewport,
            fg_color="#ffffff",
            segmented_button_fg_color="#e2e8f0",
            segmented_button_selected_color="#007AC2",
            segmented_button_selected_hover_color="#005a90",
            corner_radius=0
        )
        self.center_tabs.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Tabs matching Image 4
        tab_chch = self.center_tabs.add("  🗺 Christchurch Urban Area ✕  ")
        tab_cant = self.center_tabs.add("  🗺 Canterbury Region  ")
        tab_risk = self.center_tabs.add("  📊 Liquefaction Risk  ")
        tab_table = self.center_tabs.add("  📋 Attributes Table  ")
        tab_python = self.center_tabs.add("  🐍 Python Window (arcpy)  ")

        # Map Canvas inside Christchurch tab
        self.canvas = InteractiveMapCanvas(
            tab_chch,
            on_coords_change=self._on_canvas_mouse_move,
            on_feature_selected=self._on_feature_identified
        )

        # Embedded Attributes Table
        self._build_docked_attribute_table(tab_table)

        # Embedded Python Window
        self._build_python_window(tab_python)

    def _build_status_bar(self, parent):
        """Exact status bar matching Image 4."""
        self.status_bar = ctk.CTkFrame(parent, height=28, fg_color="#f8fafc", border_color=self.C_BORDER, border_width=1, corner_radius=0)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # Left Controls: Scale Dropdown, Snap, Grid, Fixed Zoom, North indicator (Image 4)
        left_status = ctk.CTkFrame(self.status_bar, fg_color="transparent")
        left_status.pack(side=tk.LEFT, padx=6, pady=2)

        self.scale_combo = ctk.CTkComboBox(left_status, values=["1:50,000", "1:100,000", "1:250,000", "1:500,000"], width=105, height=22, font=("Segoe UI", 9))
        self.scale_combo.set("1:100,000")
        self.scale_combo.pack(side=tk.LEFT, padx=2)

        # Snapping, Grid, Fixed Zoom buttons
        ctk.CTkLabel(left_status, text="🧲", font=("Segoe UI", 10), text_color="#007AC2", cursor="hand2").pack(side=tk.LEFT, padx=3)
        ctk.CTkLabel(left_status, text="▦", font=("Segoe UI", 11), text_color="#64748b", cursor="hand2").pack(side=tk.LEFT, padx=3)
        ctk.CTkLabel(left_status, text="↑ N ▾", font=("Segoe UI", 9, "bold"), text_color="#1e293b", cursor="hand2").pack(side=tk.LEFT, padx=5)

        # Center Coordinates: 172.8417259°E 43.5364396°S ▾ (Image 4)
        self.lbl_coords = ctk.CTkLabel(
            self.status_bar,
            text="172.6360000°E  43.5310000°S ▾",
            font=("Segoe UI", 9),
            text_color="#1e293b"
        )
        self.lbl_coords.pack(side=tk.LEFT, padx=16, pady=2)

        # Vertical Divider
        ctk.CTkLabel(self.status_bar, text="|", font=("Segoe UI", 10), text_color="#cbd5e1").pack(side=tk.LEFT, padx=4)

        # Selection Status (Image 4)
        self.lbl_selection = ctk.CTkLabel(
            self.status_bar,
            text="Selected Features: 0",
            font=("Segoe UI", 9),
            text_color="#64748b"
        )
        self.lbl_selection.pack(side=tk.LEFT, padx=6, pady=2)

        # Right Controls: Refresh & Pause Drawing (Image 4)
        right_status = ctk.CTkFrame(self.status_bar, fg_color="transparent")
        right_status.pack(side=tk.RIGHT, padx=8, pady=2)

        ctk.CTkButton(right_status, text="⟳", width=22, height=20, fg_color="transparent", hover_color="#e2e8f0", text_color="#007AC2", font=("Segoe UI", 11, "bold"), command=lambda: self.canvas.redraw()).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(right_status, text="⏸", width=22, height=20, fg_color="transparent", hover_color="#e2e8f0", text_color="#64748b", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=2)

    def _on_canvas_mouse_move(self, lon: float, lat: float):
        ew = "E" if lon >= 0 else "W"
        ns = "N" if lat >= 0 else "S"
        self.lbl_coords.configure(text=f"{abs(lon):.7f}°{ew}  {abs(lat):.7f}°{ns} ▾")

    def _on_feature_identified(self, layer_name: str, feat: Feature):
        attrs_str = "\n".join([f"• {k}: {v}" for k, v in feat.attributes.items()])
        self.lbl_selection.configure(text=f"Selected Features: 1")
        messagebox.showinfo(
            f"Pop-up - {layer_name}",
            f"OBJECTID: {feat.objectid}\nGeometry: {feat.geometry.esri_geometry_type}\n\nAttributes:\n{attrs_str}"
        )

    def _set_tool(self, tool_name: str):
        self.canvas.tool_mode = tool_name
        if tool_name != "MEASURE":
            self.canvas.measure_points.clear()
            self.canvas.redraw()

    def _on_basemap_changed(self, choice: str):
        if "No Basemap" in choice:
            self.canvas.show_basemap = False
        else:
            self.canvas.show_basemap = True
            self.canvas.set_basemap(choice)
        self.canvas.redraw()

    # =========================================================================
    # 7. ATTRIBUTES TABLE & PYTHON CONSOLE
    # =========================================================================
    def _build_docked_attribute_table(self, parent):
        tb_toolbar = ctk.CTkFrame(parent, height=36, fg_color=self.C_HEADER_BG, corner_radius=0)
        tb_toolbar.pack(fill=tk.X, side=tk.TOP)

        self.lbl_table_header = ctk.CTkLabel(tb_toolbar, text="Active Layer: None", font=("Segoe UI", 10, "bold"), text_color=self.C_ESRI_BLUE)
        self.lbl_table_header.pack(side=tk.LEFT, padx=12, pady=4)

        ctk.CTkButton(tb_toolbar, text="⤢ Zoom to Selection", width=125, height=24, font=("Segoe UI", 9), fg_color="#ffffff", hover_color="#e2e8f0", text_color="#1e293b", border_color=self.C_BORDER, border_width=1, command=self._zoom_to_selected_row).pack(side=tk.LEFT, padx=6)
        ctk.CTkButton(tb_toolbar, text="Clear", width=55, height=24, font=("Segoe UI", 9), fg_color="#fef2f2", hover_color="#fee2e2", text_color="#991b1b", border_color="#fca5a5", border_width=1, command=self._action_clear_selection).pack(side=tk.LEFT, padx=2)

        self.tb_search_var = tk.StringVar()
        self.tb_search_var.trace_add("write", lambda *args: self._filter_docked_table())
        entry = ctk.CTkEntry(tb_toolbar, placeholder_text="Filter attributes...", textvariable=self.tb_search_var, width=220, height=24, font=("Segoe UI", 9))
        entry.pack(side=tk.RIGHT, padx=10, pady=4)

        t_frame = ctk.CTkFrame(parent, fg_color="transparent")
        t_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("ProLight.Treeview", background="#ffffff", foreground="#1e293b", fieldbackground="#ffffff", rowheight=24, font=("Segoe UI", 9))
        style.configure("ProLight.Treeview.Heading", background="#f1f5f9", foreground="#007AC2", font=("Segoe UI", 9, "bold"))
        style.map("ProLight.Treeview", background=[("selected", self.C_ESRI_BLUE)], foreground=[("selected", "#ffffff")])

        self.docked_tree = ttk.Treeview(t_frame, columns=[], show="headings", style="ProLight.Treeview")
        vsb = ttk.Scrollbar(t_frame, orient="vertical", command=self.docked_tree.yview)
        hsb = ttk.Scrollbar(t_frame, orient="horizontal", command=self.docked_tree.xview)
        self.docked_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.docked_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        t_frame.grid_rowconfigure(0, weight=1)
        t_frame.grid_columnconfigure(0, weight=1)

        self.docked_tree.bind("<<TreeviewSelect>>", self._on_docked_row_select)

    def _switch_to_table_tab(self):
        layer = self.active_layer or (self.canvas.layers[0] if self.canvas.layers else None)
        if not layer:
            return
        self.center_tabs.set("  📋 Attributes Table  ")
        self.lbl_table_header.configure(text=f"Table: {layer.name} ({len(layer)} records)")

        sample_attrs = {}
        for f in layer.features.values():
            sample_attrs.update(f.attributes)

        cols = ["OBJECTID", "SHAPE"] + sorted([k for k in sample_attrs.keys() if k != "OBJECTID"])
        self.docked_tree.configure(columns=cols)

        for col in cols:
            self.docked_tree.heading(col, text=col)
            self.docked_tree.column(col, width=120, anchor="center")

        self.docked_table_cols = cols
        self._filter_docked_table()

    def _filter_docked_table(self):
        layer = self.active_layer or (self.canvas.layers[0] if self.canvas.layers else None)
        if not layer or not hasattr(self, "docked_table_cols"):
            return

        self.docked_tree.delete(*self.docked_tree.get_children())
        query = self.tb_search_var.get().strip().lower()

        for feat in layer.features.values():
            row = [feat.objectid, feat.geometry.esri_geometry_type]
            match = (query == "") or (query in str(feat.objectid))

            for col in self.docked_table_cols[2:]:
                val = feat.get(col, "")
                row.append(val)
                if query in str(val).lower():
                    match = True

            if match:
                self.docked_tree.insert("", "end", values=row, iid=str(feat.fid))

    def _on_docked_row_select(self, event):
        sel = self.docked_tree.selection()
        if sel and self.active_layer:
            fid = int(sel[0])
            self.canvas.selected_features[self.active_layer.name] = {fid}
            feat = self.active_layer.get_feature(fid)
            if feat:
                self.canvas.zoom_to_extent(feat.geometry.get_envelope())
            self.canvas.redraw()
            self.lbl_selection.configure(text="Selected Features: 1")

    def _zoom_to_selected_row(self):
        sel = self.docked_tree.selection()
        if sel and self.active_layer:
            fid = int(sel[0])
            feat = self.active_layer.get_feature(fid)
            if feat:
                self.center_tabs.set("  🗺 Christchurch Urban Area ✕  ")
                self.canvas.zoom_to_extent(feat.geometry.get_envelope())

    def _build_python_window(self, parent):
        top_bar = ctk.CTkFrame(parent, height=36, fg_color=self.C_HEADER_BG, corner_radius=0)
        top_bar.pack(fill=tk.X, side=tk.TOP)
        ctk.CTkLabel(top_bar, text="ArcGIS Pro Python Interactive Window (arcpy 3.0)", font=("Segoe UI", 10, "bold"), text_color=self.C_ESRI_BLUE).pack(side=tk.LEFT, padx=12, pady=4)

        self.py_console_text = tk.Text(parent, bg="#ffffff", fg="#1e293b", insertbackground="#007AC2", font=("Consolas", 10), wrap="word", relief="flat", padx=10, pady=10)
        self.py_console_text.pack(fill=tk.BOTH, expand=True, padx=6, pady=(4, 0))

        welcome_banner = (
            "ArcGIS Pro Python Interactive Prompt\n"
            "Environment: Python 3.12 (64-bit) | Library: arcpy\n"
            "Type Python commands or arcpy geoprocessing scripts.\n"
            "Examples:\n"
            "  >>> [l.name for l in canvas.layers]\n"
            "  >>> arcpy.management.GetCount('Bus Stops')\n"
            "--------------------------------------------------------------------------\n"
        )
        self.py_console_text.insert(tk.END, welcome_banner)
        self.py_console_text.configure(state="disabled")

        input_frame = ctk.CTkFrame(parent, height=40, fg_color="#f1f5f9", corner_radius=0)
        input_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=6, pady=6)

        ctk.CTkLabel(input_frame, text=">>>", font=("Consolas", 11, "bold"), text_color=self.C_ESRI_BLUE).pack(side=tk.LEFT, padx=(8, 4))
        self.py_cmd_entry = ctk.CTkEntry(input_frame, placeholder_text="Enter arcpy or Python command...", font=("Consolas", 10), height=30)
        self.py_cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        self.py_cmd_entry.bind("<Return>", lambda e: self._exec_python_command())

        ctk.CTkButton(input_frame, text="Run", width=80, height=30, fg_color=self.C_ESRI_BLUE, hover_color=self.C_ESRI_HOVER, font=("Segoe UI", 10, "bold"), command=self._exec_python_command).pack(side=tk.RIGHT, padx=6)

    def _exec_python_command(self):
        cmd = self.py_cmd_entry.get().strip()
        if not cmd:
            return
        self.py_cmd_entry.delete(0, tk.END)

        import sys
        import io
        import arcpy

        self.py_console_text.configure(state="normal")
        self.py_console_text.insert(tk.END, f"\n>>> {cmd}\n")

        arcpy.env.active_layers = self.canvas.layers

        exec_globals = {
            "arcpy": arcpy,
            "canvas": self.canvas,
            "layers": self.canvas.layers,
            "app": self
        }

        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output

        try:
            try:
                res = eval(cmd, exec_globals)
                if res is not None:
                    print(repr(res))
            except SyntaxError:
                exec(cmd, exec_globals)
            out_str = redirected_output.getvalue()
            if out_str:
                self.py_console_text.insert(tk.END, out_str)
        except Exception as err:
            self.py_console_text.insert(tk.END, f"Error: {err}\n")
        finally:
            sys.stdout = old_stdout

        self.py_console_text.see(tk.END)
        self.py_console_text.configure(state="disabled")
        self._refresh_toc()

    # =========================================================================
    # 8. GEOPROCESSING & PROJECT ACTIONS
    # =========================================================================
    def _action_clip(self):
        if len(self.canvas.layers) < 2:
            messagebox.showwarning("Geoprocessing", "At least two layers are required to perform a Clip.")
            return
        input_layer = self.active_layer or self.canvas.layers[0]
        poly_layer = next((l for l in self.canvas.layers if l.geometry_type == "Polygon" and l != input_layer), None)
        if not poly_layer or not poly_layer.features:
            messagebox.showwarning("Geoprocessing", "Select a polygon layer to serve as the clip boundary.")
            return

        first_poly = next((f.geometry for f in poly_layer.features.values() if isinstance(f.geometry, Polygon)), None)
        if not first_poly:
            return

        clipped = Geoprocessing.clip_layer(input_layer, first_poly, f"{input_layer.name}_Clip")
        self.canvas.add_layer(clipped, SimpleRenderer(fill="#f59e0b", stroke="#d97706"))
        self._refresh_toc()
        messagebox.showinfo("Geoprocessing", f"Clip completed! {len(clipped)} features preserved.")

    def _action_summary_stats(self):
        layer = self.active_layer or (self.canvas.layers[0] if self.canvas.layers else None)
        if not layer:
            return
        fields = set()
        for f in layer.features.values():
            for k, v in f.attributes.items():
                if isinstance(v, (int, float)) and k != "OBJECTID":
                    fields.add(k)
        if not fields:
            messagebox.showinfo("Statistics", f"Layer '{layer.name}' has no numerical fields.")
            return
        target_f = sorted(list(fields))[0]
        stats = Geoprocessing.summary_statistics(layer, target_f)
        msg = f"Field Statistics for '{target_f}':\n• Count: {stats['count']}\n• Sum: {stats['sum']:,.2f}\n• Mean: {stats['mean']:,.2f}\n• Min: {stats['min']}\n• Max: {stats['max']}"
        messagebox.showinfo("Summary Statistics", msg)

    def _action_clear_selection(self):
        for l in self.canvas.layers:
            self.canvas.selected_features[l.name].clear()
        self.canvas.measure_points.clear()
        self.canvas.redraw()
        self.lbl_selection.configure(text="Selected Features: 0")

    def _action_add_point_dialog(self):
        dialog = ctk.CTkInputDialog(text="Enter Lon, Lat, Name (e.g. 172.63, -43.53, Cathedral Stop):", title="Create Feature")
        res = dialog.get_input()
        if res:
            try:
                parts = [p.strip() for p in res.split(",")]
                lon = float(parts[0])
                lat = float(parts[1])
                name = parts[2] if len(parts) > 2 else "New Point"
                layer = self.active_layer or self.canvas.layers[0]
                layer.add_feature(Point(lon, lat), {"NAME": name})
                self.canvas.redraw()
                self._refresh_toc()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid format: {e}")

    def _action_save_aprx(self):
        f = filedialog.asksaveasfilename(defaultextension=".aprx", filetypes=[("ArcGIS Pro Project", "*.aprx")])
        if f:
            pdata = {
                "aprxVersion": "3.0.0",
                "name": os.path.splitext(os.path.basename(f))[0],
                "layers": [l.to_esri_json() for l in self.canvas.layers]
            }
            with open(f, "w", encoding="utf-8") as fp:
                json.dump(pdata, fp, indent=2)
            messagebox.showinfo("ArcGIS Pro", f"Project saved to {f}")

    def _action_open_aprx(self):
        f = filedialog.askopenfilename(filetypes=[("ArcGIS Pro Project", "*.aprx"), ("JSON", "*.json")])
        if f:
            self._load_aprx_file(f)

    def _action_export_esri_json(self):
        layer = self.active_layer or (self.canvas.layers[0] if self.canvas.layers else None)
        if not layer:
            return
        f = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("ESRI FeatureSet JSON", "*.json")])
        if f:
            with open(f, "w", encoding="utf-8") as fp:
                json.dump(layer.to_esri_json(), fp, indent=2)
            messagebox.showinfo("Export", f"Exported {layer.name} to {f}")

    def _action_export_svg(self):
        f = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=[("SVG Vector Map", "*.svg")])
        if f:
            from arcgeo.mapping import Map
            m = Map(self.current_project_name)
            for l in self.canvas.layers:
                m.add_layer(l, self.canvas.layer_renderers.get(l.name))
            svg = m.export_svg(width=1200, height=800)
            with open(f, "w", encoding="utf-8") as fp:
                fp.write(svg)
            messagebox.showinfo("Export", f"Vector map exported to {f}")

    # =========================================================================
    # 9. PROJECT LOADING (Christchurch & Brasil)
    # =========================================================================
    def load_project_by_name(self, name: str):
        """Loads sample dataset matching ArcGIS Pro Tutorial projects."""
        self.canvas.layers.clear()
        self.canvas.layer_renderers.clear()
        self.canvas.layer_visibility.clear()
        self.canvas.selected_features.clear()

        if "Christchurch" in name or "Wellington" in name or "Ven" in name or "Scotland" in name:
            p_info = load_christchurch_project()
        else:
            p_info = load_brasil_project()

        self.current_project_name = p_info["project_name"]
        self.lbl_proj_dropdown.configure(text=f"{self.current_project_name} ▾")

        for layer, renderer in p_info["layers"]:
            self.canvas.add_layer(layer, renderer)

        self.active_layer = self.canvas.layers[0] if self.canvas.layers else None
        self.canvas.zoom_to_extent(p_info["extent"])
        self._refresh_toc()

    def _load_aprx_file(self, file_path: str):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                pdata = json.load(f)
            self.canvas.layers.clear()
            self.canvas.layer_renderers.clear()
            self.canvas.layer_visibility.clear()
            self.canvas.selected_features.clear()

            for ld in pdata.get("layers", []):
                g_type_esri = ld.get("geometryType", "esriGeometryPoint")
                g_type = "Polygon" if "Polygon" in g_type_esri else ("Polyline" if "Polyline" in g_type_esri else "Point")
                layer = FeatureLayer(ld.get("name", "Layer"), geometry_type=g_type)
                for f in ld.get("features", []):
                    geom_data = f.get("geometry", {})
                    attrs = f.get("attributes", {})
                    if "x" in geom_data and "y" in geom_data:
                        layer.add_feature(Point(geom_data["x"], geom_data["y"]), attrs)
                    elif "rings" in geom_data and geom_data["rings"]:
                        layer.add_feature(Polygon(geom_data["rings"][0]), attrs)
                    elif "paths" in geom_data and geom_data["paths"]:
                        layer.add_feature(Polyline(geom_data["paths"][0]), attrs)
                self.canvas.add_layer(layer)

            self.current_project_name = os.path.basename(file_path)
            self.lbl_proj_dropdown.configure(text=f"{self.current_project_name} ▾")
            self.active_layer = self.canvas.layers[0] if self.canvas.layers else None
            self._refresh_toc()
            self.canvas.zoom_to_extent()
            messagebox.showinfo("ArcGIS Pro", f"Loaded {self.current_project_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open aprx: {e}")


def main():
    app = ArcRibApp()
    app.mainloop()


if __name__ == "__main__":
    main()
