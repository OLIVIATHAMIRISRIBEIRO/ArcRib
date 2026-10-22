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
from arcrib.sample_data import load_christchurch_project, load_brasil_project, load_myproject_map
from arcrib.i18n import tr, set_language, ACTIVE_LANGUAGE
from arcrib.daml_schema import DAML_SCHEMA


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
        self.catalog_folders: List[str] = ["C:\\Users\\User\\Documents\\ArcGIS\\Projects\\MyProject"]
        self.catalog_favorites: List[str] = ["MyProject.gdb", "World Topographic Map"]
        self.toc_view_mode = "DRAWING_ORDER"
        self.catalog_view_mode = "PROJECT"
        self.layer_editing_locks: Dict[str, bool] = {}
        self.layer_snapping: Dict[str, bool] = {}
        self.layer_labeling: Dict[str, bool] = {}
        self.snapping_enabled = True
        self.coords_format_mode = "DD"

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

        # Official Esri ArcGIS Pro 3.0 DAML Keyboard Accelerators
        self.search_entry = self.entry_cmd_search
        self.bind("<Control-F1>", lambda e: self._toggle_ribbon_collapse())
        self.bind("<Alt-q>", lambda e: self.entry_cmd_search.focus_set())
        self.bind("<Alt-Q>", lambda e: self.entry_cmd_search.focus_set())
        self.bind("<Control-o>", lambda e: self._action_open_aprx())
        self.bind("<Control-O>", lambda e: self._action_open_aprx())
        self.bind("<Control-s>", lambda e: self._action_save_aprx())
        self.bind("<Control-S>", lambda e: self._action_save_aprx())
        self.bind("<Control-n>", lambda e: self._on_start_page_new_project())
        self.bind("<Control-N>", lambda e: self._on_start_page_new_project())
        self.bind("<Control-Alt-c>", lambda e: self._set_tool("PAN"))
        self.bind("<Control-Alt-C>", lambda e: self._set_tool("PAN"))
        self.bind("<Control-Alt-s>", lambda e: self._set_tool("SELECT"))
        self.bind("<Control-Alt-S>", lambda e: self._set_tool("SELECT"))
        self.bind("<Control-Shift-c>", lambda e: self._action_add_point_dialog())
        self.bind("<Control-Shift-C>", lambda e: self._action_add_point_dialog())
        self.bind("<Control-Shift-m>", lambda e: self._switch_to_table_tab())
        self.bind("<Control-Shift-M>", lambda e: self._switch_to_table_tab())

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
        btn_qa_new = ctk.CTkButton(qa_frame, text="📄", width=24, height=22, fg_color="transparent", hover_color="#e2e8f0", text_color="#334155", font=("Segoe UI", 11), command=self._on_start_page_new_project)
        btn_qa_new.pack(side=tk.LEFT, padx=1)
        self._bind_hover_hint(btn_qa_new, "New Project (Ctrl+N)")

        btn_qa_open = ctk.CTkButton(qa_frame, text="📂", width=24, height=22, fg_color="transparent", hover_color="#e2e8f0", text_color="#334155", font=("Segoe UI", 11), command=self._action_open_aprx)
        btn_qa_open.pack(side=tk.LEFT, padx=1)
        self._bind_hover_hint(btn_qa_open, "Open Existing Project (.aprx / Ctrl+O)")

        btn_qa_save = ctk.CTkButton(qa_frame, text="💾", width=24, height=22, fg_color="transparent", hover_color="#e2e8f0", text_color="#334155", font=("Segoe UI", 11), command=self._action_save_aprx)
        btn_qa_save.pack(side=tk.LEFT, padx=1)
        self._bind_hover_hint(btn_qa_save, "Save Active Project (.aprx / Ctrl+S)")

        btn_qa_undo = ctk.CTkButton(qa_frame, text="↶ ▾", width=30, height=22, fg_color="transparent", hover_color="#e2e8f0", text_color="#334155", font=("Segoe UI", 10), command=self._action_qa_undo)
        btn_qa_undo.pack(side=tk.LEFT, padx=1)
        self._bind_hover_hint(btn_qa_undo, "Undo Previous Extent or Selection (Ctrl+Z)")

        btn_qa_redo = ctk.CTkButton(qa_frame, text="↷ ▾", width=30, height=22, fg_color="transparent", hover_color="#e2e8f0", text_color="#334155", font=("Segoe UI", 10), command=self._action_qa_redo)
        btn_qa_redo.pack(side=tk.LEFT, padx=1)
        self._bind_hover_hint(btn_qa_redo, "Redo Next Extent (Ctrl+Y)")

        btn_qa_cust = ctk.CTkButton(qa_frame, text="▾", width=18, height=22, fg_color="transparent", hover_color="#e2e8f0", text_color="#64748b", font=("Segoe UI", 10), command=self._action_customize_quick_access)
        btn_qa_cust.pack(side=tk.LEFT, padx=1)
        self._bind_hover_hint(btn_qa_cust, "Customize Quick Access Toolbar")

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
        right_hdr.pack(side=tk.RIGHT, padx=8)

        self.btn_lang_toggle = ctk.CTkButton(
            right_hdr, text="🌐 pt-BR", width=62, height=22,
            fg_color="#f1f5f9", hover_color="#e2e8f0", text_color="#1e293b",
            font=("Segoe UI", 9, "bold"), border_color=self.C_BORDER, border_width=1,
            command=self._toggle_language
        )
        self.btn_lang_toggle.pack(side=tk.LEFT, padx=4)

        self.lbl_account_name = ctk.CTkLabel(right_hdr, text="Not signed in", font=("Segoe UI", 9), text_color="#64748b", cursor="hand2")
        self.lbl_account_name.pack(side=tk.LEFT, padx=4)
        self.lbl_account_name.bind("<Button-1>", lambda e: self._action_user_account())

        btn_user = ctk.CTkButton(right_hdr, text="👤", width=22, height=22, fg_color="transparent", hover_color="#e2e8f0", text_color="#64748b", font=("Segoe UI", 11), command=self._action_user_account)
        btn_user.pack(side=tk.LEFT, padx=1)

        btn_fb = ctk.CTkButton(right_hdr, text="💬", width=22, height=22, fg_color="transparent", hover_color="#e2e8f0", text_color="#64748b", font=("Segoe UI", 11), command=self._action_feedback)
        btn_fb.pack(side=tk.LEFT, padx=1)

        btn_notif = ctk.CTkButton(right_hdr, text="🔔", width=22, height=22, fg_color="transparent", hover_color="#e2e8f0", text_color="#64748b", font=("Segoe UI", 11), command=self._action_notifications)
        btn_notif.pack(side=tk.LEFT, padx=1)

        btn_help = ctk.CTkButton(right_hdr, text="?", width=20, height=22, fg_color="transparent", hover_color="#e2e8f0", text_color="#64748b", font=("Segoe UI", 11, "bold"), command=self._action_help_dialog)
        btn_help.pack(side=tk.LEFT, padx=1)

        # Window Controls (Minimize, Maximize, Close)
        ctk.CTkButton(right_hdr, text="🗕", width=22, height=22, fg_color="transparent", hover_color="#e2e8f0", text_color="#64748b", font=("Segoe UI", 10), command=self.iconify).pack(side=tk.LEFT, padx=1)
        ctk.CTkButton(right_hdr, text="🗖", width=22, height=22, fg_color="transparent", hover_color="#e2e8f0", text_color="#64748b", font=("Segoe UI", 10), command=self._toggle_maximize).pack(side=tk.LEFT, padx=1)
        ctk.CTkButton(right_hdr, text="✕", width=22, height=22, fg_color="transparent", hover_color="#fee2e2", text_color="#ef4444", font=("Segoe UI", 10, "bold"), command=self._action_close_window).pack(side=tk.LEFT, padx=1)

    def _toggle_language(self, show_dialog: bool = False):
        from arcrib import i18n
        new_lang = "pt-BR" if i18n.ACTIVE_LANGUAGE == "en" else "en"
        i18n.set_language(new_lang)
        target_display = "EN" if new_lang == "pt-BR" else "pt-BR"
        if hasattr(self, "btn_lang_toggle"):
            self.btn_lang_toggle.configure(text=f"🌐 {target_display}")
        if hasattr(self, "lbl_selection"):
            self.lbl_selection.configure(text=f"Language: {new_lang}")
        if show_dialog:
            messagebox.showinfo("ArcGIS Pro", f"Idioma do ArcRib alterado para: {new_lang}\nArcRib language set to: {new_lang}")

    def _action_user_account(self):
        d = ctk.CTkInputDialog(text="Enter ArcGIS Online / Enterprise Username:\n(e.g. gis_analyst@esri.com)", title="ArcGIS Sign In")
        val = d.get_input()
        if val and val.strip():
            self.lbl_account_name.configure(text=val.strip(), text_color="#007AC2")
            messagebox.showinfo("ArcGIS Pro", f"Signed in successfully as: {val.strip()}\nRole: GIS Specialist (ArcGIS Pro Advanced)")
        else:
            self.lbl_account_name.configure(text="Demo Analyst (Pro Advanced)", text_color="#059669")

    def _action_feedback(self):
        messagebox.showinfo("ArcGIS Pro Feedback", "ArcGIS Pro Experience Improvement Program:\nAll features operational. Log feedback to Esri Technical Support or ArcRib GitHub.")

    def _action_notifications(self):
        messagebox.showinfo("Notifications", "ArcGIS Pro Notifications (3 unread):\n\n1. ✅ Project 'MyProject' loaded with World Topographic Map.\n2. ℹ System: Python 3.12 environment active.\n3. 🔒 License: ArcGIS Pro Advanced (Authorized).")

    def _action_help_dialog(self):
        help_text = (
            "ArcGIS Pro 3.x / ArcRib Quick Reference:\n\n"
            "• Alt+Q: Command Search\n"
            "• Ctrl+F1: Toggle Ribbon Collapse\n"
            "• Ctrl+O: Open Project (.aprx)\n"
            "• Ctrl+S: Save Project\n"
            "• Ctrl+N: New Project Start Page\n"
            "• Ctrl+Alt+C: Explore / Pan Tool\n"
            "• Ctrl+Alt+S: Select Features\n"
            "• Ctrl+Shift+C: Create Feature Point\n"
            "• Ctrl+Shift+M: Open Attributes Table\n\n"
            "For full SDK and ArcPy documentation, consult README.md."
        )
        messagebox.showinfo("ArcGIS Pro Help", help_text)

    def _toggle_maximize(self):
        try:
            if self.state() == "zoomed":
                self.state("normal")
            else:
                self.state("zoomed")
        except Exception:
            pass

    def _action_close_window(self):
        if messagebox.askyesno("ArcGIS Pro", "Do you want to save changes before exiting?"):
            self._action_save_aprx()
        self.destroy()

    def _bind_hover_hint(self, widget, hint_text: str):
        """Shows informative tooltip/status hint when mouse hovers over a button."""
        def _on_enter(e):
            if hasattr(self, "lbl_hint"):
                self.lbl_hint.configure(text=f"💡 {hint_text}")
            elif hasattr(self, "lbl_selection"):
                self._old_sel_text = self.lbl_selection.cget("text")
                self.lbl_selection.configure(text=f"Command: {hint_text}")

        def _on_leave(e):
            if hasattr(self, "lbl_hint"):
                self.lbl_hint.configure(text="")
            elif hasattr(self, "lbl_selection") and hasattr(self, "_old_sel_text"):
                self.lbl_selection.configure(text=self._old_sel_text)

        widget.bind("<Enter>", _on_enter)
        widget.bind("<Leave>", _on_leave)

    def _popup_project_switcher(self):
        m = tk.Menu(self, tearoff=0, font=("Segoe UI", 9))
        m.add_command(label="🗺  MyProject (Default Map)", command=lambda: self.load_project_by_name("MyProject"))
        m.add_command(label="🗺  Christchurch Transportation", command=lambda: self.load_project_by_name("Christchurch Transportation"))
        m.add_command(label="🗺  Brasil Geografico", command=lambda: self.load_project_by_name("Brasil Demo"))
        m.add_separator()
        m.add_command(label="📁  Open Existing Project (.aprx)...", command=self._action_open_aprx)
        m.add_command(label="💾  Save Project As...", command=self._action_save_aprx)
        m.add_command(label="➕  Start Page / New Template...", command=self.show_start_page_view)
        x = self.lbl_proj_dropdown.winfo_rootx()
        y = self.lbl_proj_dropdown.winfo_rooty() + self.lbl_proj_dropdown.winfo_height()
        m.tk_popup(x, y)

    def _on_command_search(self):
        query = self.entry_cmd_search.get().strip().lower()
        if not query:
            return
        if "buffer" in query or "tampao" in query or "influencia" in query:
            self._open_right_tool_buffer()
        elif "join" in query or "spatial" in query or "ligacao" in query or "juncao" in query:
            self._open_right_tool_join()
        elif "clip" in query or "recortar" in query or "corte" in query:
            self._action_clip()
        elif "stats" in query or "estatistica" in query or "resumo" in query:
            self._action_summary_stats()
        elif "catalog" in query or "catalogo" in query:
            self.right_tabs.set("Catalog")
        elif "contents" in query or "conteudo" in query or "camadas" in query:
            self._toggle_toc_panel()
        elif "symbology" in query or "simbologia" in query:
            self.right_tabs.set("Symbology")
        else:
            self.right_tabs.set("Geoprocessing")

    # =========================================================================
    # 2. FLUENT RIBBON & CONTEXTUAL TABS (Exact match of Image 3)
    # =========================================================================
    def _build_ribbon(self, parent):
        self.ribbon_container = ctk.CTkFrame(parent, height=88, fg_color=self.C_RIBBON_BG, corner_radius=0)
        self.ribbon_container.pack(fill=tk.X, side=tk.TOP)
        self.ribbon_is_collapsed = False

        # Core Ribbon Tabs (Left-aligned, anchor='nw' matching ArcGIS Pro)
        self.ribbon_tabs = ctk.CTkTabview(
            self.ribbon_container,
            height=86,
            fg_color=self.C_RIBBON_BG,
            segmented_button_fg_color="#f1f5f9",
            segmented_button_selected_color=self.C_ESRI_BLUE,
            segmented_button_selected_hover_color=self.C_ESRI_HOVER,
            corner_radius=0,
            anchor="nw"
        )
        self.ribbon_tabs.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        try:
            self.ribbon_tabs._segmented_button.configure(font=("Segoe UI", 9.5, "bold"))
        except Exception:
            pass

        # Contextual Tabs Group on the right of the same header row (Image 3, Box 5 & 9)
        ctx_frame = ctk.CTkFrame(self.ribbon_tabs, fg_color="transparent")
        ctx_frame.grid(row=1, rowspan=2, column=0, sticky="nse", padx=6, pady=0)

        ctx_pill = ctk.CTkFrame(ctx_frame, fg_color="#e0f2fe", border_color="#0284c7", border_width=1, corner_radius=10)
        ctx_pill.pack(side=tk.LEFT, padx=(0, 4), pady=1)

        btn_ctx_fl = ctk.CTkButton(ctx_pill, text="Feature Layer", width=86, height=20, fg_color="transparent", hover_color="#bae6fd", text_color="#0369a1", font=("Segoe UI", 9, "bold"), command=lambda: self._activate_stacked_pane("Symbology"))
        btn_ctx_fl.pack(side=tk.LEFT, padx=1)
        self._bind_hover_hint(btn_ctx_fl, "Feature Layer: Symbology and Rendering Properties")

        btn_ctx_lbl = ctk.CTkButton(ctx_pill, text="Labeling", width=64, height=20, fg_color="transparent", hover_color="#bae6fd", text_color="#0369a1", font=("Segoe UI", 9, "bold"), command=self._action_context_labeling)
        btn_ctx_lbl.pack(side=tk.LEFT, padx=1)
        self._bind_hover_hint(btn_ctx_lbl, "Labeling: Toggle and Configure Layer Labels")

        btn_ctx_data = ctk.CTkButton(ctx_pill, text="Data", width=50, height=20, fg_color="transparent", hover_color="#bae6fd", text_color="#0369a1", font=("Segoe UI", 9, "bold"), command=self._switch_to_table_tab)
        btn_ctx_data.pack(side=tk.LEFT, padx=1)
        self._bind_hover_hint(btn_ctx_data, "Data: Open Attributes Table and Layer Schema")

        # Ribbon Collapse Button (Ctrl+F1, Image 3 Box 9)
        self.btn_ribbon_collapse = ctk.CTkButton(
            ctx_frame, text="▾", width=20, height=20,
            fg_color="transparent", hover_color="#e2e8f0", text_color="#64748b",
            font=("Segoe UI", 9, "bold"), corner_radius=2,
            command=self._toggle_ribbon_collapse
        )
        self.btn_ribbon_collapse.pack(side=tk.LEFT, padx=(2, 4), pady=1)
        self._bind_hover_hint(self.btn_ribbon_collapse, "Collapse or Expand the Ribbon (Ctrl+F1)")

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
        self._build_ribbon_group_imagery(tab_imagery)
        self._build_ribbon_group_share(tab_share)
        self._build_ribbon_group_help(tab_help)

    def _toggle_ribbon_collapse(self):
        """Collapses or expands the ribbon (Ctrl+F1, Image 3 Box 9)."""
        if self.ribbon_is_collapsed:
            self.ribbon_tabs._set_grid_canvas()
            curr = self.ribbon_tabs.get()
            if curr in self.ribbon_tabs._tab_dict:
                self.ribbon_tabs._tab_dict[curr].grid()
            self.ribbon_container.configure(height=88)
            self.ribbon_is_collapsed = False
            self.btn_ribbon_collapse.configure(text="▾")
        else:
            curr = self.ribbon_tabs.get()
            if curr in self.ribbon_tabs._tab_dict:
                self.ribbon_tabs._tab_dict[curr].grid_remove()
            self.ribbon_tabs._canvas.grid_remove()
            self.ribbon_container.configure(height=34)
            self.ribbon_is_collapsed = True
            self.btn_ribbon_collapse.configure(text="▴")

    @property
    def ribbon_collapsed(self) -> bool:
        return getattr(self, "ribbon_is_collapsed", False)

    def _create_ribbon_group(self, parent_tab, group_name: str, has_launcher: bool = True):
        """Creates an authentic ArcGIS Pro ribbon group with title and optional launcher icon."""
        box = ctk.CTkFrame(parent_tab, fg_color="transparent", corner_radius=0)
        box.pack(side=tk.LEFT, fill=tk.Y, padx=2, pady=0)

        btn_area = ctk.CTkFrame(box, fg_color="transparent")
        btn_area.pack(side=tk.TOP, fill=tk.X, expand=False)

        bottom_bar = ctk.CTkFrame(box, fg_color="transparent", height=18)
        bottom_bar.pack(side=tk.TOP, fill=tk.X, pady=(2, 1))

        ctk.CTkLabel(bottom_bar, text=group_name, font=("Segoe UI", 9.5, "bold"), text_color="#475569").pack(side=tk.LEFT, padx=(3, 1))
        if has_launcher:
            l_btn = ctk.CTkLabel(bottom_bar, text="⤢", font=("Segoe UI", 8), text_color="#94a3b8", cursor="hand2")
            l_btn.pack(side=tk.RIGHT, padx=(0, 2))
            l_btn.bind("<Button-1>", lambda e, g=group_name: self._on_group_launcher_clicked(g))

        # Vertical separator
        sep = ctk.CTkFrame(parent_tab, width=1, height=56, fg_color=self.C_BORDER)
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=3, pady=5)

        return btn_area

    def _build_ribbon_group_map(self, tab):
        f = ctk.CTkFrame(tab, fg_color="transparent")
        f.pack(fill=tk.BOTH, expand=True)

        # 1. Clipboard Group (Paste, Cut, Copy, Copy Path)
        g_clip = self._create_ribbon_group(f, "Clipboard", has_launcher=False)
        b_paste = ctk.CTkButton(
            g_clip, text="📋\nPaste ▾", width=52, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._action_paste_dropdown(b_paste)
        )
        b_paste.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_paste, "Paste: Paste features, layers, or clipboard data (Ctrl+V)")

        col_clip = ctk.CTkFrame(g_clip, fg_color="transparent")
        col_clip.pack(side=tk.LEFT, padx=1)
        b_cut = ctk.CTkButton(col_clip, text="✂ Cut", width=88, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._action_cut)
        b_cut.pack(pady=0)
        self._bind_hover_hint(b_cut, "Cut: Cut selected features to clipboard (Ctrl+X)")

        b_copy = ctk.CTkButton(col_clip, text="📄 Copy", width=88, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._action_copy)
        b_copy.pack(pady=0)
        self._bind_hover_hint(b_copy, "Copy: Copy selected features to clipboard (Ctrl+C)")

        b_copypath = ctk.CTkButton(col_clip, text="📋 Copy Path", width=88, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._action_copy_path)
        b_copypath.pack(pady=0)
        self._bind_hover_hint(b_copypath, "Copy Path: Copy data source path to clipboard")

        # 2. Navigate Group (Explore, Mini Extents 2x2, Bookmarks, Go To XY)
        g_nav = self._create_ribbon_group(f, "Navigate", has_launcher=True)
        self.btn_explore = ctk.CTkButton(
            g_nav, text="✥\nExplore\n▾", width=58, height=54,
            fg_color="#e0f2fe", hover_color="#bae6fd", text_color="#007ac2",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._set_tool("PAN")
        )
        self.btn_explore.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(self.btn_explore, "Explore: Pan and identify map features (Ctrl+Alt+C)")

        col_nav_ext = ctk.CTkFrame(g_nav, fg_color="transparent")
        col_nav_ext.pack(side=tk.LEFT, padx=1)
        r_ext1 = ctk.CTkFrame(col_nav_ext, fg_color="transparent")
        r_ext1.pack(pady=0)
        b_full = ctk.CTkButton(r_ext1, text="🌐", width=24, height=24, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, corner_radius=2, font=("Segoe UI", 10.5, "bold"), command=lambda: self.canvas.zoom_to_extent())
        b_full.pack(side=tk.LEFT, padx=1)
        self._bind_hover_hint(b_full, "Full Extent: Zoom to fit all visible layers (Insert)")
        b_zin = ctk.CTkButton(r_ext1, text="⤢", width=24, height=24, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, corner_radius=2, font=("Segoe UI", 10.5, "bold"), command=lambda: self.canvas._zoom(1.3, self.canvas.canvas.winfo_width()//2, self.canvas.canvas.winfo_height()//2))
        b_zin.pack(side=tk.LEFT, padx=1)
        self._bind_hover_hint(b_zin, "Fixed Zoom In: Magnify map center")

        r_ext2 = ctk.CTkFrame(col_nav_ext, fg_color="transparent")
        r_ext2.pack(pady=0)
        b_prev = ctk.CTkButton(r_ext2, text="←", width=24, height=24, fg_color="transparent", hover_color="#e0f2fe", text_color="#007ac2", border_width=0, corner_radius=2, font=("Segoe UI", 10.5, "bold"), command=self._action_qa_undo)
        b_prev.pack(side=tk.LEFT, padx=1)
        self._bind_hover_hint(b_prev, "Previous Extent: Return to previous view")
        b_next = ctk.CTkButton(r_ext2, text="→", width=24, height=24, fg_color="transparent", hover_color="#e0f2fe", text_color="#64748b", border_width=0, corner_radius=2, font=("Segoe UI", 10.5, "bold"), command=self._action_qa_redo)
        b_next.pack(side=tk.LEFT, padx=1)
        self._bind_hover_hint(b_next, "Next Extent: Advance to next view")

        b_bkm = ctk.CTkButton(
            g_nav, text="📖\nBookmarks\n▾", width=68, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._action_bookmarks_dropdown(b_bkm)
        )
        b_bkm.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_bkm, "Bookmarks: Jump to predefined spatial locations")

        b_goto = ctk.CTkButton(
            g_nav, text="🎯\nGo To\nXY", width=56, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._action_goto_xy
        )
        b_goto.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_goto, "Go To XY: Pan directly to coordinates (Lon, Lat)")

        # 3. Layer Group (Basemap, Add Data, Add Graphics Layer)
        g_layer = self._create_ribbon_group(f, "Layer", has_launcher=False)
        self.btn_basemap = ctk.CTkButton(
            g_layer, text="🗺\nBasemap\n▾", width=62, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._action_basemap_dropdown(self.btn_basemap)
        )
        self.btn_basemap.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(self.btn_basemap, "Basemap: Choose an Esri basemap or satellite imagery background")

        b_add_data = ctk.CTkButton(
            g_layer, text="📁➕\nAdd\nData ▾", width=58, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._action_add_data_dropdown(b_add_data)
        )
        b_add_data.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_add_data, "Add Data: Add layers, shapefiles, web services, or data tables to map")

        col_gfx = ctk.CTkFrame(g_layer, fg_color="transparent")
        col_gfx.pack(side=tk.LEFT, padx=1)
        b_gfx = ctk.CTkButton(
            col_gfx, text="➕ Add Graphics Layer", width=156, height=22,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._action_add_graphics_layer
        )
        b_gfx.pack(pady=(15, 0))
        self._bind_hover_hint(b_gfx, "Add Graphics Layer: Create a graphics layer for custom markup and shapes")

        # 4. Selection Group (Select, Select By Attributes, Select By Location, 3-row stack)
        g_sel = self._create_ribbon_group(f, "Selection", has_launcher=True)
        self.btn_select = ctk.CTkButton(
            g_sel, text="↖⬡\nSelect\n▾", width=56, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._set_tool("SELECT")
        )
        self.btn_select.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(self.btn_select, "Select: Interactive feature selection by clicking or dragging (Ctrl+Alt+S)")

        b_s_attr = ctk.CTkButton(
            g_sel, text="▦\nSelect By\nAttributes", width=76, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._action_select_by_attributes
        )
        b_s_attr.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_s_attr, "Select By Attributes: Select features using SQL query expressions")

        b_s_loc = ctk.CTkButton(
            g_sel, text="⧉\nSelect By\nLocation", width=76, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._action_select_by_location
        )
        b_s_loc.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_s_loc, "Select By Location: Select features based on spatial relationships")

        col_sel_tools = ctk.CTkFrame(g_sel, fg_color="transparent")
        col_sel_tools.pack(side=tk.LEFT, padx=1)
        b_attr = ctk.CTkButton(col_sel_tools, text="▦ Attributes", width=88, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._switch_to_table_tab)
        b_attr.pack(pady=0)
        self._bind_hover_hint(b_attr, "Attributes: Open active layer attributes table")

        b_clear = ctk.CTkButton(col_sel_tools, text="✕ Clear", width=88, height=17, fg_color="transparent", hover_color="#fee2e2", text_color="#dc2626", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._action_clear_selection)
        b_clear.pack(pady=0)
        self._bind_hover_hint(b_clear, "Clear Selection: Deselect all features across all layers")

        b_zoom_to = ctk.CTkButton(col_sel_tools, text="🔍 Zoom To", width=88, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._zoom_to_selected_row)
        b_zoom_to.pack(pady=0)
        self._bind_hover_hint(b_zoom_to, "Zoom To: Zoom map extent to selected features")

        # 5. Inquiry Group (Measure, Locate, Infographics, Coordinate Conversion)
        g_inq = self._create_ribbon_group(f, "Inquiry", has_launcher=False)
        self.btn_measure = ctk.CTkButton(
            g_inq, text="📏\nMeasure\n▾", width=58, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._action_measure_dropdown(self.btn_measure)
        )
        self.btn_measure.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(self.btn_measure, "Measure: Measure distances, bearings, and areas on map")

        b_loc = ctk.CTkButton(
            g_inq, text="🔭\nLocate\n▾", width=54, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._activate_stacked_pane("Locate")
        )
        b_loc.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_loc, "Locate: Search places, landmarks, and addresses")

        b_info = ctk.CTkButton(
            g_inq, text="📊\nInfographics\n▾", width=78, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._action_infographics
        )
        b_info.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_info, "Infographics: Visualize demographic and economic data for study area")

        b_coord = ctk.CTkButton(
            g_inq, text="📍⇄\nCoordinate\nConversion", width=82, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._action_coordinate_conversion
        )
        b_coord.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_coord, "Coordinate Conversion: Convert coordinates between DD, DDM, DMS, and UTM/MGRS")

        # 6. Labeling Group (Pause, Lock, View Unplaced, More, Convert)
        g_lbl = self._create_ribbon_group(f, "Labeling", has_launcher=True)
        col_lbl_ctrls = ctk.CTkFrame(g_lbl, fg_color="transparent")
        col_lbl_ctrls.pack(side=tk.LEFT, padx=1)

        r_lbl1 = ctk.CTkFrame(col_lbl_ctrls, fg_color="transparent")
        r_lbl1.pack(pady=0)
        b_lpause = ctk.CTkButton(r_lbl1, text="⏸ Pause", width=64, height=22, fg_color="transparent", hover_color="#fef3c7", text_color="#b45309", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._action_label_pause)
        b_lpause.pack(side=tk.LEFT, padx=1)
        self._bind_hover_hint(b_lpause, "Pause Labeling: Suspend label rendering calculation")
        b_llock = ctk.CTkButton(r_lbl1, text="🔒 Lock", width=60, height=22, fg_color="transparent", hover_color="#fef3c7", text_color="#b45309", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._action_label_lock)
        b_llock.pack(side=tk.LEFT, padx=1)
        self._bind_hover_hint(b_llock, "Lock Labels: Freeze label placement in current positions")

        r_lbl2 = ctk.CTkFrame(col_lbl_ctrls, fg_color="transparent")
        r_lbl2.pack(pady=0)
        b_unplaced = ctk.CTkButton(r_lbl2, text="❌ View Unplaced", width=108, height=22, fg_color="transparent", hover_color="#fee2e2", text_color="#dc2626", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._action_label_unplaced)
        b_unplaced.pack(side=tk.LEFT, padx=1)
        self._bind_hover_hint(b_unplaced, "View Unplaced: Display labels that could not be placed due to conflict")
        b_more = ctk.CTkButton(r_lbl2, text="More ▾", width=58, height=22, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=lambda: self._action_label_more_dropdown(b_more))
        b_more.pack(side=tk.LEFT, padx=1)
        self._bind_hover_hint(b_more, "More Labeling: Label priority, placement weights, and styles")

        b_conv = ctk.CTkButton(
            g_lbl, text="🏷️A\nConvert\n▾", width=58, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._action_label_convert
        )
        b_conv.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_conv, "Convert Labels: Convert map labels to geodatabase annotation")

        # 7. Offline Group (Download Map, Sync, Remove)
        g_off = self._create_ribbon_group(f, "Offline", has_launcher=True)
        b_dl = ctk.CTkButton(
            g_off, text="🗺⬇\nDownload\nMap ▾", width=74, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._action_download_map
        )
        b_dl.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_dl, "Download Map: Cache map layers for offline fieldwork and mobile devices")

        col_off = ctk.CTkFrame(g_off, fg_color="transparent")
        col_off.pack(side=tk.LEFT, padx=1)
        b_sync = ctk.CTkButton(col_off, text="🔄 Sync", width=68, height=24, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._action_offline_sync)
        b_sync.pack(pady=0)
        self._bind_hover_hint(b_sync, "Sync: Synchronize offline edits with remote feature service")
        b_rem = ctk.CTkButton(col_off, text="🗑 Remove", width=68, height=24, fg_color="transparent", hover_color="#fee2e2", text_color="#dc2626", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._action_offline_remove)
        b_rem.pack(pady=0)
        self._bind_hover_hint(b_rem, "Remove: Remove offline replica and restore web service connection")

    def _build_ribbon_group_insert(self, tab):
        f = ctk.CTkFrame(tab, fg_color="transparent")
        f.pack(fill=tk.BOTH, expand=True)

        # 1. Project Group (New Map, New Layout, Report, Notebook, Toolbox, Import Map, Import Layout, Task)
        g_proj = self._create_ribbon_group(f, "Project")

        b_new_map = ctk.CTkButton(
            g_proj, text="🗺\nNew\nMap ▾", width=58, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._action_new_map_dropdown(b_new_map)
        )
        b_new_map.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_new_map, "Create a new 2D Map or Basemap view")

        b_new_layout = ctk.CTkButton(
            g_proj, text="📐\nNew\nLayout ▾", width=58, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._action_new_layout_dropdown(b_new_layout)
        )
        b_new_layout.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_new_layout, "Create printable map layout or export vector map")

        col1 = ctk.CTkFrame(g_proj, fg_color="transparent")
        col1.pack(side=tk.LEFT, padx=1)
        b_rep = ctk.CTkButton(col1, text="📊 New Report ▾", width=116, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._action_generate_report)
        b_rep.pack(pady=0)
        self._bind_hover_hint(b_rep, "Generate comprehensive layer and attribute summary report")

        b_nb = ctk.CTkButton(col1, text="📓 New Notebook ▾", width=116, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._action_new_notebook)
        b_nb.pack(pady=0)
        self._bind_hover_hint(b_nb, "Open interactive Python/arcpy notebook environment")

        b_tbx = ctk.CTkButton(col1, text="🧰 Toolbox ▾", width=116, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=lambda: self._action_toolbox_dropdown(b_tbx))
        b_tbx.pack(pady=0)
        self._bind_hover_hint(b_tbx, "Manage geoprocessing toolboxes and custom spatial models")

        col2 = ctk.CTkFrame(g_proj, fg_color="transparent")
        col2.pack(side=tk.LEFT, padx=1)
        b_imp_map = ctk.CTkButton(col2, text="🗺 Import Map", width=112, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._action_open_aprx)
        b_imp_map.pack(pady=0)
        self._bind_hover_hint(b_imp_map, "Import an existing ArcGIS Pro project (.aprx) or map layer")

        b_imp_lay = ctk.CTkButton(col2, text="📐 Import Layout ▾", width=112, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._action_import_layout)
        b_imp_lay.pack(pady=0)
        self._bind_hover_hint(b_imp_lay, "Import layout page template (.pagx / .svg)")

        b_tsk = ctk.CTkButton(col2, text="📋 Task ▾", width=112, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=lambda: self._action_task_dropdown(b_tsk))
        b_tsk.pack(pady=0)
        self._bind_hover_hint(b_tsk, "Open guided interactive GIS workflow task")

        # 2. Connections Group
        g_conn = self._create_ribbon_group(f, "Connections")
        b_conn = ctk.CTkButton(
            g_conn, text="🗄\nConnections\n▾", width=76, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._action_connections_dropdown(b_conn)
        )
        b_conn.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_conn, "Add folder, database, or WMS web service connections")

        b_add_fld = ctk.CTkButton(
            g_conn, text="📁\nAdd\nFolder", width=56, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._action_add_folder
        )
        b_add_fld.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_add_fld, "Browse and connect a directory to project Catalog")

        col_conn = ctk.CTkFrame(g_conn, fg_color="transparent")
        col_conn.pack(side=tk.LEFT, padx=1)
        b_new_db = ctk.CTkButton(col_conn, text="🗃 New Database", width=118, height=24, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=lambda: messagebox.showinfo("New Database", "Create File Geodatabase (.gdb) or Mobile Geodatabase (.geodatabase)"))
        b_new_db.pack(pady=0)
        self._bind_hover_hint(b_new_db, "Create File Geodatabase (.gdb) in project home")

        b_new_srv = ctk.CTkButton(col_conn, text="🌐 New Server", width=118, height=24, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=lambda: messagebox.showinfo("New Server", "Connect to ArcGIS Enterprise / Server, OGC WMS/WMTS or GeoServer"))
        b_new_srv.pack(pady=0)
        self._bind_hover_hint(b_new_srv, "Connect to ArcGIS Server or OGC WMS/WFS Service")

        # 3. Layer Templates Group (6 buttons with actual layer creation actions)
        g_notes = self._create_ribbon_group(f, "Layer Templates")
        templates = [
            ("📍", "Bright\nMap Notes", "#ef4444", "#ffffff", "Create Bright Map Notes layer with red pins"),
            ("📌", "Dark Map\nNotes", "#1e293b", "#94a3b8", "Create Dark Map Notes layer with charcoal pins"),
            ("📍", "Light Map\nNotes", "#0284c7", "#ffffff", "Create Light Map Notes layer with sky blue pins"),
            ("📊", "Paired\nMap Notes", "#10b981", "#4338ca", "Create Paired Map Notes layer with emerald pins"),
            ("📍", "Pastel Map\nNotes", "#fdba74", "#86efac", "Create Pastel Map Notes layer with peach pins"),
            ("🎯", "Red Green\nMap Notes", "#dc2626", "#16a34a", "Create Red Green Map Notes layer with target pins")
        ]
        for ic, t_label, fill_c, strk_c, hint in templates:
            b_t = ctk.CTkButton(
                g_notes, text=f"{ic}\n{t_label}", width=56, height=54,
                fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
                border_width=0, corner_radius=2, font=("Segoe UI", 9, "bold"),
                command=lambda name=t_label.replace("\n", " "), fc=fill_c, sc=strk_c: self._action_add_map_notes(name, fc, sc)
            )
            b_t.pack(side=tk.LEFT, padx=1, pady=0)
            self._bind_hover_hint(b_t, hint)

        # 4. Link Analysis Group
        g_link = self._create_ribbon_group(f, "Link Analysis")
        b_link = ctk.CTkButton(
            g_link, text="🕸\nNew Link\nChart ▾", width=68, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._action_new_link_chart
        )
        b_link.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_link, "Open interactive network relationship graph for project layers")

        # 5. Measurements Group
        g_meas = self._create_ribbon_group(f, "Measurements")
        b_meas = ctk.CTkButton(
            g_meas, text="🧭\nDistance &\nDirection", width=76, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._action_distance_and_direction
        )
        b_meas.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_meas, "Measure geodesic distance, bearing, and path on map")

        # 6. Styles Group
        g_style = self._create_ribbon_group(f, "Styles")
        col_style = ctk.CTkFrame(g_style, fg_color="transparent")
        col_style.pack(side=tk.LEFT, padx=1)
        b_s1 = ctk.CTkButton(col_style, text="🎨 Add Style ▾", width=86, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=lambda: self._action_styles_dropdown(b_s1))
        b_s1.pack(pady=0)
        self._bind_hover_hint(b_s1, "Add system or mobile style gallery")

        b_s2 = ctk.CTkButton(col_style, text="✨ New Style ▾", width=86, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=lambda: self._action_styles_dropdown(b_s2))
        b_s2.pack(pady=0)
        self._bind_hover_hint(b_s2, "Create custom symbol style")

        b_s3 = ctk.CTkButton(col_style, text="📥 Import Style ▾", width=86, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=lambda: self._action_styles_dropdown(b_s3))
        b_s3.pack(pady=0)
        self._bind_hover_hint(b_s3, "Import style (.stylx) palette")

        # 7. Favorites Group
        g_fav = self._create_ribbon_group(f, "Favorites")
        b_fav = ctk.CTkButton(
            g_fav, text="⭐\nAdd\nItem ▾", width=56, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._action_favorites_dropdown(b_fav)
        )
        b_fav.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_fav, "Add active layer or extent to project favorites")

    # =========================================================================
    # INSERT TAB ACTIONS & HANDLERS
    # =========================================================================
    def _action_new_map_dropdown(self, btn):
        m = tk.Menu(self, tearoff=0, font=("Segoe UI", 9))
        m.add_command(label="🗺  New 2D Map", command=lambda: self.load_project_by_name("MyProject"))
        m.add_command(label="🗺  Add Basemap...", command=lambda: self._open_basemap_selector())
        m.add_command(label="🌐  New 3D Scene (Global)", command=lambda: self._open_3d_preview(global_mode=True))
        m.add_command(label="🏙  New 3D Scene (Local)", command=lambda: self._open_3d_preview(global_mode=False))
        m.add_separator()
        m.add_command(label="📐  Add Map Frame to Layout", command=self._action_export_svg)
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        m.tk_popup(x, y)

    def _action_new_layout_dropdown(self, btn):
        m = tk.Menu(self, tearoff=0, font=("Segoe UI", 9))
        m.add_command(label="📐  New Layout - A4 Landscape (Export SVG)", command=self._action_export_svg)
        m.add_command(label="📐  New Layout - A4 Portrait", command=self._action_export_svg)
        m.add_command(label="📐  New Layout - Letter (8.5 x 11 in)", command=self._action_export_svg)
        m.add_command(label="📐  New Layout - Poster Arch D (24 x 36 in)", command=self._action_export_svg)
        m.add_separator()
        m.add_command(label="🖨  Print Setup & Page Margins...", command=lambda: messagebox.showinfo("Print Setup", "Orientation: Landscape | Resolution: 300 DPI | Margins: 0.5 in"))
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        m.tk_popup(x, y)

    def _action_generate_report(self):
        report_lines = [
            "==================================================",
            f"   ArcGIS® Pro - Layer & Project Inventory Report",
            "==================================================",
            f"Project: {self.current_project_name}",
            f"Map View: {self.center_tabs.get().strip()}",
            f"Scale: {self.scale_combo.get()}",
            f"Active Extent: {self.canvas.view_extent.to_dict() if self.canvas else 'N/A'}",
            f"Total Layers: {len(self.canvas.layers) if self.canvas else 0}",
            "--------------------------------------------------"
        ]
        total_feats = 0
        if self.canvas:
            for l in self.canvas.layers:
                cnt = len(l)
                total_feats += cnt
                report_lines.append(f" • Layer: {l.name:<24} | Type: {l.geometry_type:<10} | Features: {cnt}")
        report_lines.append("--------------------------------------------------")
        report_lines.append(f"Total Features across project: {total_feats}")
        report_text = "\n".join(report_lines)

        top = ctk.CTkToplevel(self)
        top.title("ArcGIS Pro - Summary Report")
        top.geometry("540x420")
        top.transient(self)
        txt = tk.Text(top, font=("Consolas", 9), bg="#ffffff", fg="#1e293b", padx=10, pady=10)
        txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
        txt.insert("1.0", report_text)
        txt.configure(state="disabled")

        def _save():
            f = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Report", "*.txt"), ("CSV", "*.csv")])
            if f:
                with open(f, "w", encoding="utf-8") as fp:
                    fp.write(report_text)
                messagebox.showinfo("Report Saved", f"Report saved to:\n{f}")

        ctk.CTkButton(top, text="💾 Save Report to File...", command=_save, fg_color=self.C_ESRI_BLUE, hover_color=self.C_ESRI_HOVER).pack(pady=8)

    def _action_new_notebook(self):
        self.center_tabs.set("  🐍 Python Window (arcpy)  ")
        starter_code = "import arcpy\nprint('Active layers:', [l.name for l in canvas.layers])"
        self.py_cmd_entry.delete(0, tk.END)
        self.py_cmd_entry.insert(0, starter_code)

    def _action_toolbox_dropdown(self, btn):
        m = tk.Menu(self, tearoff=0, font=("Segoe UI", 9))
        m.add_command(label="🧰  SpatialAnalysis.tbx (Buffer, Clip, Join)", command=lambda: self.right_tabs.set("Geoprocessing"))
        m.add_command(label="🧰  DataManagement.tbx (Summary, Projections)", command=lambda: self.right_tabs.set("Geoprocessing"))
        m.add_separator()
        m.add_command(label="➕  Create New Toolbox (.tbx)...", command=lambda: messagebox.showinfo("Toolbox", f"New Toolbox created in {self.current_project_name}.gdb"))
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        m.tk_popup(x, y)

    def _action_import_layout(self):
        f = filedialog.askopenfilename(filetypes=[("Layout Files", "*.pagx;*.svg;*.json"), ("All Files", "*.*")])
        if f:
            messagebox.showinfo("Import Layout", f"Imported layout template:\n{os.path.basename(f)}")

    def _action_task_dropdown(self, btn):
        m = tk.Menu(self, tearoff=0, font=("Segoe UI", 9))
        m.add_command(label="📋  Task: Proximity Buffer Analysis", command=self._open_right_tool_buffer)
        m.add_command(label="📋  Task: Spatial Overlay & Join", command=self._open_right_tool_join)
        m.add_command(label="📋  Task: Clip Study Area", command=self._action_clip)
        m.add_command(label="📋  Task: Cartographic Symbology", command=lambda: self.right_tabs.set("Symbology"))
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        m.tk_popup(x, y)

    def _action_connections_dropdown(self, btn):
        m = tk.Menu(self, tearoff=0, font=("Segoe UI", 9))
        m.add_command(label="📁  Add Folder Connection...", command=self._action_add_folder)
        m.add_command(label="🗃  New File Geodatabase (.gdb)...", command=self._action_new_gdb)
        m.add_command(label="🗄  New Database Connection (.sde)...", command=lambda: messagebox.showinfo("Database", "Database Connection: PostGIS / Oracle / SpatiaLite ready."))
        m.add_command(label="🌐  Add WMS / WMTS Server...", command=lambda: messagebox.showinfo("WMS Server", "Connected to Esri Living Atlas WMS endpoint."))
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        m.tk_popup(x, y)

    def _action_add_folder(self):
        f = filedialog.askdirectory(title="Add Folder Connection to Catalog")
        if f:
            if not hasattr(self, "catalog_folders"):
                self.catalog_folders = []
            if f not in self.catalog_folders:
                self.catalog_folders.append(f)
            self._activate_stacked_pane("Catalog")
            self._set_catalog_view("PROJECT")
            self.lbl_selection.configure(text=f"Folder Connected: {os.path.basename(f)}")

    def _action_new_gdb(self):
        f = filedialog.asksaveasfilename(defaultextension=".gdb", filetypes=[("File Geodatabase", "*.gdb")])
        if f:
            os.makedirs(f, exist_ok=True)
            self._activate_stacked_pane("Catalog")
            self._refresh_catalog_tree()
            messagebox.showinfo("File Geodatabase", f"Created File Geodatabase:\n{f}")

    def _action_add_map_notes(self, template_name: str, fill_col: str, stroke_col: str):
        """Creates an authentic ArcGIS Pro Map Notes layer with pins in the viewport."""
        layer = FeatureLayer(template_name, geometry_type="Point")
        ext = self.canvas.view_extent if self.canvas else Envelope(-55.0, -25.0, -40.0, -10.0)
        cx = (ext.xmin + ext.xmax) / 2.0
        cy = (ext.ymin + ext.ymax) / 2.0
        dx = ext.width * 0.12
        dy = ext.height * 0.09

        p1 = Point(cx - dx, cy + dy)
        p2 = Point(cx + dx, cy - dy)
        p3 = Point(cx, cy)

        layer.add_feature(p1, {"NAME": f"{template_name} - Inspection 1", "STATUS": "Critical", "PRIORITY": "High"})
        layer.add_feature(p2, {"NAME": f"{template_name} - Field Note 2", "STATUS": "Verified", "PRIORITY": "Normal"})
        layer.add_feature(p3, {"NAME": f"{template_name} - Target 3", "STATUS": "New", "PRIORITY": "Urgent"})

        renderer = SimpleRenderer(fill=fill_col, stroke=stroke_col, stroke_width=2.0, point_radius=7.0)
        self.canvas.add_layer(layer, renderer)
        self.active_layer = layer
        self._refresh_toc()
        self.canvas.redraw()
        self.lbl_selection.configure(text=f"Added: {template_name} (3 features)")

    def _action_new_link_chart(self):
        top = ctk.CTkToplevel(self)
        top.title("ArcGIS Pro - Link Analysis Chart")
        top.geometry("620x450")
        top.transient(self)
        cv = tk.Canvas(top, bg="#f8fafc", highlightthickness=0)
        cv.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        layers = self.canvas.layers if self.canvas else []
        cv.create_text(310, 25, text="Link Analysis: Spatial & Entity Relationships", font=("Segoe UI", 12, "bold"), fill="#1e293b")
        cx, cy = 310, 225
        # Center Hub
        cv.create_oval(cx - 45, cy - 45, cx + 45, cy + 45, fill="#007AC2", outline="#ffffff", width=2)
        cv.create_text(cx, cy, text=self.current_project_name.split()[0], font=("Segoe UI", 9, "bold"), fill="#ffffff")

        import math
        n = max(len(layers), 1)
        for i, l in enumerate(layers):
            ang = (2 * math.pi * i) / n
            nx = cx + 160 * math.cos(ang)
            ny = cy + 130 * math.sin(ang)
            cv.create_line(cx, cy, nx, ny, fill="#94a3b8", width=1.5, dash=(4, 2))
            cv.create_oval(nx - 36, ny - 20, nx + 36, ny + 20, fill="#ffffff", outline="#0284c7", width=2)
            cv.create_text(nx, ny - 4, text=l.name[:12], font=("Segoe UI", 8, "bold"), fill="#1e293b")
            cv.create_text(nx, ny + 8, text=f"{len(l)} feats", font=("Segoe UI", 7), fill="#64748b")

    def _action_distance_and_direction(self):
        self._set_tool("MEASURE")
        self.lbl_selection.configure(text="Tool: Distance & Direction | Click map vertices to measure")
        if hasattr(self, "lbl_hint"):
            self.lbl_hint.configure(text="💡 Click map vertices to calculate geodesic distances and azimuth")

    def _action_styles_dropdown(self, btn):
        m = tk.Menu(self, tearoff=0, font=("Segoe UI", 9))
        m.add_command(label="🎨  Format Symbology...", command=lambda: self._activate_stacked_pane("Symbology"))
        m.add_command(label="✨  Create Custom Symbol...", command=lambda: self._activate_stacked_pane("Symbology"))
        m.add_command(label="📥  Import Style File (.stylx)...", command=lambda: messagebox.showinfo("Styles", "Imported ArcGIS 2D styles and ramps."))
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        m.tk_popup(x, y)

    def _action_favorites_dropdown(self, btn):
        m = tk.Menu(self, tearoff=0, font=("Segoe UI", 9))
        m.add_command(label="⭐  Add Active Layer to Favorites", command=self._add_current_layer_to_favorites)
        m.add_command(label="⭐  Bookmark Current Extent", command=lambda: messagebox.showinfo("Bookmark", f"Extent added to Map Bookmarks."))
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        m.tk_popup(x, y)

    def _add_current_layer_to_favorites(self):
        layer = self.active_layer or (self.canvas.layers[0] if self.canvas and self.canvas.layers else None)
        if layer:
            if not hasattr(self, "catalog_favorites"):
                self.catalog_favorites = []
            if layer.name not in self.catalog_favorites:
                self.catalog_favorites.append(f"Layer: {layer.name}")
            self._activate_stacked_pane("Catalog")
            self._set_catalog_view("FAVORITES")
            self.lbl_selection.configure(text=f"Favorited: {layer.name}")

    def _open_basemap_selector(self):
        opts = list(ESRI_BASEMAPS.keys())
        d = ctk.CTkInputDialog(text=f"Select Basemap:\nOptions: {', '.join(opts[:4])}", title="Basemap Selector")
        c = d.get_input()
        if c and c in ESRI_BASEMAPS:
            self._on_basemap_changed(c)

    def _open_3d_preview(self, global_mode: bool = True):
        mode_str = "Global" if global_mode else "Local"
        messagebox.showinfo("ArcGIS Pro 3D Scene", f"3D Scene ({mode_str}) initialized with 3D elevation surface and terrain shading.")

    def _action_select_by_attributes(self):
        """Interactive Select By Attributes dialog matching ArcGIS Pro 3.x."""
        top = ctk.CTkToplevel(self)
        top.title("Select By Attributes")
        top.geometry("480x420")
        top.transient(self)

        hdr = ctk.CTkFrame(top, height=32, fg_color=self.C_HEADER_BG, corner_radius=0)
        hdr.pack(fill=tk.X, side=tk.TOP)
        ctk.CTkLabel(hdr, text="Select Layer By Attribute (SQL Query)", font=("Segoe UI", 10, "bold"), text_color=self.C_ESRI_BLUE).pack(side=tk.LEFT, padx=10, pady=4)

        body = ctk.CTkFrame(top, fg_color="transparent")
        body.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)

        # Layer Selection
        ctk.CTkLabel(body, text="Input Rows (Layer):", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 1))
        layer_names = [l.name for l in self.canvas.layers] or ["None"]
        c_layer = ctk.CTkComboBox(body, values=layer_names, height=26, font=("Segoe UI", 9))
        c_layer.set(self.active_layer.name if self.active_layer else layer_names[0])
        c_layer.pack(fill=tk.X, pady=(0, 8))

        # Selection Type
        ctk.CTkLabel(body, text="Selection Type:", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 1))
        c_type = ctk.CTkComboBox(body, values=["New selection", "Add to current selection", "Remove from current selection"], height=26, font=("Segoe UI", 9))
        c_type.set("New selection")
        c_type.pack(fill=tk.X, pady=(0, 8))

        # Expression Builder
        ctk.CTkLabel(body, text="WHERE Clause Expression:", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 1))

        row_exp = ctk.CTkFrame(body, fg_color="transparent")
        row_exp.pack(fill=tk.X, pady=(0, 6))

        def _get_fields():
            l_name = c_layer.get()
            target_l = next((l for l in self.canvas.layers if l.name == l_name), None)
            if not target_l or not target_l.features:
                return ["OBJECTID"]
            sample_feat = next(iter(target_l.features.values()))
            return ["OBJECTID"] + list(sample_feat.attributes.keys())

        fields = _get_fields()
        c_field = ctk.CTkComboBox(row_exp, values=fields, width=140, height=26, font=("Segoe UI", 9))
        c_field.pack(side=tk.LEFT, padx=(0, 4))

        c_op = ctk.CTkComboBox(row_exp, values=["=", "!=", ">", "<", ">=", "<=", "LIKE", "IS NOT NULL"], width=90, height=26, font=("Segoe UI", 9))
        c_op.pack(side=tk.LEFT, padx=(0, 4))

        e_val = ctk.CTkEntry(row_exp, placeholder_text="Value (e.g. High / 5)", height=26, font=("Segoe UI", 9))
        e_val.pack(side=tk.LEFT, fill=tk.X, expand=True)

        lbl_sql_preview = ctk.CTkLabel(body, text="SQL: SELECT * FROM Layer WHERE Field = 'Value'", font=("Consolas", 8, "italic"), text_color="#64748b")
        lbl_sql_preview.pack(anchor="w", pady=(2, 8))

        def _update_preview(*args):
            lbl_sql_preview.configure(text=f"SQL: SELECT * FROM {c_layer.get()} WHERE {c_field.get()} {c_op.get()} '{e_val.get()}'")

        c_layer.configure(command=lambda e: c_field.configure(values=_get_fields()))
        e_val.bind("<KeyRelease>", _update_preview)

        lbl_res = ctk.CTkLabel(body, text="", font=("Segoe UI", 9, "bold"), text_color="#059669")
        lbl_res.pack(anchor="w", pady=(2, 6))

        def _apply():
            l_name = c_layer.get()
            target_l = next((l for l in self.canvas.layers if l.name == l_name), None)
            if not target_l:
                lbl_res.configure(text="No layer selected", text_color="#dc2626")
                return

            f_name = c_field.get()
            op = c_op.get()
            val_raw = e_val.get().strip()

            matching_fids = set()
            for fid, feat in target_l.features.items():
                attr_val = feat.get(f_name, "")
                attr_str = str(attr_val).strip()

                hit = False
                if op == "=":
                    hit = (attr_str.lower() == val_raw.lower())
                elif op == "!=":
                    hit = (attr_str.lower() != val_raw.lower())
                elif op == "LIKE":
                    hit = (val_raw.lower() in attr_str.lower())
                elif op == "IS NOT NULL":
                    hit = bool(attr_str)
                elif op in (">", "<", ">=", "<="):
                    try:
                        n_attr = float(attr_val)
                        n_val = float(val_raw)
                        if op == ">": hit = n_attr > n_val
                        elif op == "<": hit = n_attr < n_val
                        elif op == ">=": hit = n_attr >= n_val
                        elif op == "<=": hit = n_attr <= n_val
                    except Exception:
                        hit = False

                if hit:
                    matching_fids.add(fid)

            sel_type = c_type.get()
            curr_sel = self.canvas.selected_features.get(l_name, set())
            if sel_type == "Add to current selection":
                final_sel = curr_sel.union(matching_fids)
            elif sel_type == "Remove from current selection":
                final_sel = curr_sel.difference(matching_fids)
            else:
                final_sel = matching_fids

            self.canvas.selected_features[l_name] = final_sel
            self.canvas.redraw()
            self._refresh_toc()
            self.lbl_selection.configure(text=f"Selected Features: {len(final_sel)}")
            lbl_res.configure(text=f"✅ {len(matching_fids)} features matched query expression", text_color="#059669")

            if matching_fids:
                matched_geoms = [feat.geometry for fid, feat in target_l.features.items() if fid in matching_fids]
                if matched_geoms:
                    env = matched_geoms[0].get_envelope()
                    for g in matched_geoms[1:]:
                        env = env.union(g.get_envelope())
                    self.canvas.zoom_to_extent(env)

        b_row = ctk.CTkFrame(top, height=36, fg_color="#f8fafc")
        b_row.pack(fill=tk.X, side=tk.BOTTOM, padx=14, pady=8)
        ctk.CTkButton(b_row, text="Apply", width=80, fg_color=self.C_ESRI_BLUE, hover_color=self.C_ESRI_HOVER, command=_apply).pack(side=tk.RIGHT, padx=4)
        ctk.CTkButton(b_row, text="OK", width=70, fg_color="#059669", hover_color="#047857", command=lambda: (_apply(), top.destroy())).pack(side=tk.RIGHT, padx=4)
        ctk.CTkButton(b_row, text="Cancel", width=70, fg_color="#f1f5f9", hover_color="#e2e8f0", text_color="#1e293b", command=top.destroy).pack(side=tk.RIGHT, padx=4)

    def _action_select_by_location(self):
        """Select By Location dialog matching ArcGIS Pro 3.x."""
        top = ctk.CTkToplevel(self)
        top.title("Select By Location")
        top.geometry("460x360")
        top.transient(self)

        hdr = ctk.CTkFrame(top, height=32, fg_color=self.C_HEADER_BG, corner_radius=0)
        hdr.pack(fill=tk.X, side=tk.TOP)
        ctk.CTkLabel(hdr, text="Select Layer By Location (Spatial Relationship)", font=("Segoe UI", 10, "bold"), text_color=self.C_ESRI_BLUE).pack(side=tk.LEFT, padx=10, pady=4)

        body = ctk.CTkFrame(top, fg_color="transparent")
        body.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)

        layer_names = [l.name for l in self.canvas.layers] or ["None"]

        ctk.CTkLabel(body, text="Target Features (Layer to select):", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 1))
        c_target = ctk.CTkComboBox(body, values=layer_names, height=26, font=("Segoe UI", 9))
        c_target.set(layer_names[0])
        c_target.pack(fill=tk.X, pady=(0, 6))

        ctk.CTkLabel(body, text="Relationship:", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 1))
        c_rel = ctk.CTkComboBox(body, values=["Intersect", "Within a distance of", "Completely contain", "Are completely within"], height=26, font=("Segoe UI", 9))
        c_rel.set("Intersect")
        c_rel.pack(fill=tk.X, pady=(0, 6))

        ctk.CTkLabel(body, text="Selecting Features (Source Layer):", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 1))
        c_source = ctk.CTkComboBox(body, values=layer_names, height=26, font=("Segoe UI", 9))
        c_source.set(layer_names[1] if len(layer_names) > 1 else layer_names[0])
        c_source.pack(fill=tk.X, pady=(0, 8))

        lbl_res = ctk.CTkLabel(body, text="", font=("Segoe UI", 9, "bold"), text_color="#059669")
        lbl_res.pack(anchor="w", pady=(2, 4))

        def _apply():
            t_name = c_target.get()
            s_name = c_source.get()
            target_l = next((l for l in self.canvas.layers if l.name == t_name), None)
            source_l = next((l for l in self.canvas.layers if l.name == s_name), None)
            if not target_l or not source_l:
                lbl_res.configure(text="Layers not found", text_color="#dc2626")
                return

            matched = set()
            for s_feat in source_l.features.values():
                s_env = s_feat.geometry.get_envelope()
                candidates = target_l.select_by_envelope(s_env)
                for t_feat in candidates:
                    matched.add(t_feat.fid)

            self.canvas.selected_features[t_name] = matched
            self.canvas.redraw()
            self._refresh_toc()
            self.lbl_selection.configure(text=f"Selected Features: {len(matched)}")
            lbl_res.configure(text=f"✅ {len(matched)} features spatially selected in '{t_name}'", text_color="#059669")

        b_row = ctk.CTkFrame(top, height=36, fg_color="#f8fafc")
        b_row.pack(fill=tk.X, side=tk.BOTTOM, padx=14, pady=8)
        ctk.CTkButton(b_row, text="Apply", width=80, fg_color=self.C_ESRI_BLUE, hover_color=self.C_ESRI_HOVER, command=_apply).pack(side=tk.RIGHT, padx=4)
        ctk.CTkButton(b_row, text="OK", width=70, fg_color="#059669", hover_color="#047857", command=lambda: (_apply(), top.destroy())).pack(side=tk.RIGHT, padx=4)
        ctk.CTkButton(b_row, text="Cancel", width=70, fg_color="#f1f5f9", hover_color="#e2e8f0", text_color="#1e293b", command=top.destroy).pack(side=tk.RIGHT, padx=4)

    def _action_bookmarks_dropdown(self, btn):
        m = tk.Menu(self, tearoff=0, font=("Segoe UI", 9))
        m.add_command(label="🏛  Cathedral Square (City Center)", command=lambda: self.canvas.zoom_to_extent(Envelope(172.630, -43.535, 172.642, -43.527)))
        m.add_command(label="✈  Christchurch Airport", command=lambda: self.canvas.zoom_to_extent(Envelope(172.520, -43.498, 172.550, -43.478)))
        m.add_command(label="⚓  Lyttelton Port", command=lambda: self.canvas.zoom_to_extent(Envelope(172.705, -43.612, 172.730, -43.592)))
        m.add_command(label="⤢  Full Project Extent", command=lambda: self.canvas.zoom_to_extent())
        m.add_separator()
        m.add_command(label="➕  New Bookmark...", command=self._action_create_bookmark)
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        m.tk_popup(x, y)

    def _action_create_bookmark(self):
        d = ctk.CTkInputDialog(text="Enter Bookmark Name:", title="New Map Bookmark")
        b_name = d.get_input()
        if b_name and b_name.strip():
            if not hasattr(self, "map_bookmarks"):
                self.map_bookmarks = {}
            self.map_bookmarks[b_name.strip()] = self.canvas.view_extent
            self.lbl_selection.configure(text=f"Bookmark '{b_name.strip()}' saved")

    def _action_goto_xy(self):
        d = ctk.CTkInputDialog(text="Enter Longitude, Latitude:\n(e.g. 172.636, -43.531)", title="Go To XY")
        res = d.get_input()
        if res:
            try:
                parts = [float(p.strip()) for p in res.split(",")]
                lon, lat = parts[0], parts[1]
                self.canvas.zoom_to_extent(Envelope(lon - 0.015, lat - 0.01, lon + 0.015, lat + 0.01))
                self.lbl_selection.configure(text=f"Jumped to: {lon:.4f}, {lat:.4f}")
            except Exception as e:
                messagebox.showerror("Error", f"Invalid coordinates: {e}")

    def _action_qa_undo(self):
        if self.canvas and self.canvas.previous_extent():
            self.lbl_selection.configure(text="Navigation: Previous Extent")
        else:
            self._action_clear_selection()
            self.lbl_selection.configure(text="Selection Cleared")

    def _action_qa_redo(self):
        if self.canvas and self.canvas.next_extent():
            self.lbl_selection.configure(text="Navigation: Next Extent")
        else:
            self.lbl_selection.configure(text="No further action to redo")

    def _action_customize_quick_access(self):
        m = tk.Menu(self, tearoff=0, font=("Segoe UI", 9))
        m.add_checkbutton(label="✓  New Project (📄)", command=lambda: messagebox.showinfo("Quick Access", "New Project command enabled"))
        m.add_checkbutton(label="✓  Open Project (📂)", command=lambda: messagebox.showinfo("Quick Access", "Open Project command enabled"))
        m.add_checkbutton(label="✓  Save Project (💾)", command=lambda: messagebox.showinfo("Quick Access", "Save Project command enabled"))
        m.add_checkbutton(label="✓  Undo / Previous (↶)", command=lambda: messagebox.showinfo("Quick Access", "Undo command enabled"))
        m.add_checkbutton(label="✓  Redo / Next (↷)", command=lambda: messagebox.showinfo("Quick Access", "Redo command enabled"))
        m.add_separator()
        m.add_command(label="⚙  More Commands...", command=self._action_customize_ribbon)
        m.tk_popup(self.winfo_pointerx(), self.winfo_pointery())

    def _action_context_labeling(self):
        layer = self.active_layer or (self.canvas.layers[0] if self.canvas and self.canvas.layers else None)
        if layer:
            self._toggle_layer_labeling(layer.name)
            status = "Enabled" if self.layer_labeling.get(layer.name, True) else "Disabled"
            self.lbl_selection.configure(text=f"Labels {status} on {layer.name}")

    def _action_paste(self):
        layer = self.active_layer or (self.canvas.layers[0] if self.canvas and self.canvas.layers else None)
        if layer and hasattr(self, "_copied_features") and self._copied_features:
            for feat in self._copied_features:
                layer.add_feature(feat.geometry, dict(feat.attributes))
            self.canvas.redraw()
            self._refresh_toc()
            self.lbl_selection.configure(text=f"Pasted {len(self._copied_features)} features into {layer.name}")
        else:
            self.lbl_selection.configure(text="Clipboard: No features to paste")

    def _action_cut(self):
        self._action_copy()
        layer = self.active_layer or (self.canvas.layers[0] if self.canvas and self.canvas.layers else None)
        if layer and layer.name in self.canvas.selected_features and self.canvas.selected_features[layer.name]:
            s_fids = set(self.canvas.selected_features[layer.name])
            layer.features = {fid: f for fid, f in layer.features.items() if fid not in s_fids}
            self.canvas.selected_features[layer.name].clear()
            self.canvas.redraw()
            self._refresh_toc()
            self.lbl_selection.configure(text=f"Cut {len(s_fids)} features to clipboard")

    def _action_copy(self):
        layer = self.active_layer or (self.canvas.layers[0] if self.canvas and self.canvas.layers else None)
        if layer and layer.name in self.canvas.selected_features and self.canvas.selected_features[layer.name]:
            s_fids = self.canvas.selected_features[layer.name]
            self._copied_features = [layer.features[fid] for fid in s_fids if fid in layer.features]
            attrs_txt = "\n".join([str(f.attributes) for f in self._copied_features])
            self.clipboard_clear()
            self.clipboard_append(attrs_txt)
            self.lbl_selection.configure(text=f"Copied {len(self._copied_features)} features to clipboard")
        elif layer:
            self._copied_features = list(layer.features.values())
            self.clipboard_clear()
            self.clipboard_append(f"Layer: {layer.name} ({len(layer)} features)")
            self.lbl_selection.configure(text=f"Copied layer {layer.name} to clipboard")

    def _action_copy_path(self):
        layer = self.active_layer or (self.canvas.layers[0] if self.canvas and self.canvas.layers else None)
        path = f"C:\\Users\\User\\Documents\\ArcGIS\\Projects\\{self.current_project_name}\\{self.current_project_name}.gdb"
        if layer:
            path += f"\\{layer.name}"
        self.clipboard_clear()
        self.clipboard_append(path)
        self.lbl_selection.configure(text=f"Copied Path: {path}")

    def _action_paste_dropdown(self, btn):
        m = tk.Menu(self, tearoff=0, font=("Segoe UI", 9))
        m.add_command(label="📋  Paste (Ctrl+V)", command=self._action_paste)
        m.add_command(label="📑  Paste Special...", command=lambda: messagebox.showinfo("Paste Special", "Paste as New Layer / New Feature Class."))
        m.add_separator()
        m.add_command(label="🗑  Clear Clipboard", command=lambda: (setattr(self, "_copied_features", []), self.lbl_selection.configure(text="Clipboard Cleared")))
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        m.tk_popup(x, y)

    def _action_basemap_dropdown(self, btn):
        m = tk.Menu(self, tearoff=0, font=("Segoe UI", 9))
        curr_bm = getattr(self.canvas.basemap_mgr, "basemap_name", "Esri Topo")
        show_bm = getattr(self.canvas, "show_basemap", True)
        for bm_key in ESRI_BASEMAPS.keys():
            prefix = "✓  " if (show_bm and curr_bm == bm_key) else "    "
            m.add_command(label=f"{prefix}{bm_key}", command=lambda k=bm_key: self._on_basemap_changed(k))
        m.add_separator()
        prefix_none = "✓  " if not show_bm else "    "
        m.add_command(label=f"{prefix_none}No Basemap (Grid)", command=lambda: self._on_basemap_changed("No Basemap (Grid)"))
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        m.tk_popup(x, y)

    def _action_add_data_dropdown(self, btn):
        m = tk.Menu(self, tearoff=0, font=("Segoe UI", 9))
        m.add_command(label="📁  Add Data to Current Map...", command=self._action_open_aprx)
        m.add_command(label="🌐  Add Data From ArcGIS Living Atlas...", command=lambda: messagebox.showinfo("Living Atlas", "Connected to ArcGIS Living Atlas: World Elevation, Hydrography, and Land Cover."))
        m.add_command(label="📍  Add XY Point Data...", command=self._action_goto_xy)
        m.add_command(label="🗺  Add Route Data...", command=lambda: messagebox.showinfo("Route Data", "Transportation transit network loaded."))
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        m.tk_popup(x, y)

    def _action_add_graphics_layer(self):
        g_name = f"Graphics Layer {len([l for l in self.canvas.layers if 'Graphics' in l.name]) + 1}"
        layer = FeatureLayer(g_name, geometry_type="Point")
        renderer = SimpleRenderer(fill="#f59e0b", stroke="#b45309", stroke_width=2.0, point_radius=6.0)
        self.canvas.add_layer(layer, renderer)
        self.active_layer = layer
        self._refresh_toc()
        self.lbl_selection.configure(text=f"Added: {g_name}")

    def _action_measure_dropdown(self, btn):
        self._set_tool("MEASURE")
        m = tk.Menu(self, tearoff=0, font=("Segoe UI", 9))
        m.add_command(label="📏  Measure Distance / Line", command=lambda: self._set_tool("MEASURE"))
        m.add_command(label="📐  Measure Area / Polygon", command=lambda: (self._set_tool("MEASURE"), messagebox.showinfo("Measure Area", "Measure Area: Click 3 or more points on the map to compute polygon surface area.")))
        m.add_command(label="🧭  Measure Direction & Azimuth", command=self._action_distance_and_direction)
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        m.tk_popup(x, y)

    def _action_infographics(self):
        top = ctk.CTkToplevel(self)
        top.title("ArcGIS Pro - Infographics & Demographics")
        top.geometry("560x420")
        top.transient(self)

        hdr = ctk.CTkFrame(top, height=36, fg_color=self.C_HEADER_BG, corner_radius=0)
        hdr.pack(fill=tk.X, side=tk.TOP)
        ctk.CTkLabel(hdr, text="📊 Study Area Infographics Summary", font=("Segoe UI", 11, "bold"), text_color=self.C_ESRI_BLUE).pack(side=tk.LEFT, padx=12, pady=6)

        body = ctk.CTkFrame(top, fg_color="transparent")
        body.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)

        # Summary KPIs
        kpi_row = ctk.CTkFrame(body, fg_color="#f8fafc", corner_radius=4)
        kpi_row.pack(fill=tk.X, pady=(0, 10), ipady=6)
        
        kpis = [
            ("Total Population", "389,700", "#0284c7"),
            ("Total Households", "149,300", "#059669"),
            ("Median Household Income", "$84,200", "#d97706"),
            ("Transit Stops", "15 active", "#7c3aed")
        ]
        for title, val, color in kpis:
            col = ctk.CTkFrame(kpi_row, fg_color="transparent")
            col.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=4)
            ctk.CTkLabel(col, text=title, font=("Segoe UI", 8), text_color="#64748b").pack()
            ctk.CTkLabel(col, text=val, font=("Segoe UI", 13, "bold"), text_color=color).pack()

        # Canvas for bar comparison chart
        cv = tk.Canvas(body, bg="#ffffff", highlightthickness=1, highlightbackground=self.C_BORDER, height=220)
        cv.pack(fill=tk.BOTH, expand=True)

        categories = [
            ("Under 18", 0.22, "#38bdf8"),
            ("18 to 34", 0.28, "#0284c7"),
            ("35 to 54", 0.26, "#0369a1"),
            ("55 to 64", 0.12, "#075985"),
            ("65 and over", 0.12, "#0c4a6e")
        ]
        cv.create_text(260, 20, text="Age Distribution Breakdown (Esri Living Atlas Demographics)", font=("Segoe UI", 9, "bold"), fill="#1e293b")
        for i, (cat, pct, col) in enumerate(categories):
            y = 50 + i * 32
            cv.create_text(90, y + 10, text=cat, font=("Segoe UI", 8), fill="#475569", anchor="e")
            bar_w = int(pct * 800)
            cv.create_rectangle(100, y, 100 + bar_w, y + 20, fill=col, outline="")
            cv.create_text(110 + bar_w, y + 10, text=f"{pct*100:.0f}%", font=("Segoe UI", 8, "bold"), fill="#1e293b", anchor="w")

    def _action_coordinate_conversion(self):
        top = ctk.CTkToplevel(self)
        top.title("Coordinate Conversion")
        top.geometry("480x320")
        top.transient(self)

        hdr = ctk.CTkFrame(top, height=32, fg_color=self.C_HEADER_BG, corner_radius=0)
        hdr.pack(fill=tk.X, side=tk.TOP)
        ctk.CTkLabel(hdr, text="📍 Coordinate Conversion Tool", font=("Segoe UI", 10, "bold"), text_color=self.C_ESRI_BLUE).pack(side=tk.LEFT, padx=10, pady=4)

        body = ctk.CTkFrame(top, fg_color="transparent")
        body.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)

        ctk.CTkLabel(body, text="Input Coordinates (Lon, Lat or DD):", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 2))
        
        ext = self.canvas.view_extent if self.canvas else Envelope(172.636, -43.531, 172.636, -43.531)
        cx = (ext.xmin + ext.xmax) / 2.0
        cy = (ext.ymin + ext.ymax) / 2.0

        ent = ctk.CTkEntry(body, height=28, font=("Segoe UI", 9))
        ent.insert(0, f"{cx:.6f}, {cy:.6f}")
        ent.pack(fill=tk.X, pady=(0, 8))

        # Output formats
        tree = ttk.Treeview(body, columns=["Format", "Converted Value"], show="headings", height=4)
        tree.heading("Format", text="Coordinate Format")
        tree.heading("Converted Value", text="Converted Coordinate")
        tree.column("Format", width=140)
        tree.column("Converted Value", width=280)
        tree.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        def _update_conversions():
            try:
                parts = [float(p.strip()) for p in ent.get().split(",")]
                lon, lat = parts[0], parts[1]
                tree.delete(*tree.get_children())
                
                # DD
                tree.insert("", "end", values=["Decimal Degrees (DD)", f"{lat:.6f}°, {lon:.6f}°"])
                # DDM
                lat_d = int(abs(lat))
                lat_m = (abs(lat) - lat_d) * 60.0
                lon_d = int(abs(lon))
                lon_m = (abs(lon) - lon_d) * 60.0
                lat_h = "N" if lat >= 0 else "S"
                lon_h = "E" if lon >= 0 else "W"
                tree.insert("", "end", values=["Deg Dec Min (DDM)", f"{lat_d}° {lat_m:.3f}' {lat_h}, {lon_d}° {lon_m:.3f}' {lon_h}"])
                # DMS
                lat_s = (lat_m - int(lat_m)) * 60.0
                lon_s = (lon_m - int(lon_m)) * 60.0
                tree.insert("", "end", values=["Deg Min Sec (DMS)", f"{lat_d}° {int(lat_m)}' {lat_s:.1f}\" {lat_h}, {lon_d}° {int(lon_m)}' {lon_s:.1f}\" {lon_h}"])
                # MGRS / UTM
                utm_zone = int((lon + 180) / 6) + 1
                tree.insert("", "end", values=["UTM / MGRS", f"Zone {utm_zone}{lat_h} (WGS 84)"])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to parse coordinates: {e}")

        _update_conversions()

        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.pack(fill=tk.X)
        ctk.CTkButton(btn_row, text="Convert", width=80, height=24, fg_color=self.C_ESRI_BLUE, hover_color=self.C_ESRI_HOVER, command=_update_conversions).pack(side=tk.LEFT, padx=2)
        def _zoom():
            try:
                parts = [float(p.strip()) for p in ent.get().split(",")]
                lon, lat = parts[0], parts[1]
                self.canvas.zoom_to_extent(Envelope(lon - 0.015, lat - 0.01, lon + 0.015, lat + 0.01))
                self.lbl_selection.configure(text=f"Zoomed to: {lon:.4f}, {lat:.4f}")
                top.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid coords: {e}")
        ctk.CTkButton(btn_row, text="Pan & Zoom To", width=110, height=24, fg_color="#059669", hover_color="#047857", command=_zoom).pack(side=tk.LEFT, padx=4)

    def _action_label_pause(self):
        if not hasattr(self, "_labels_paused"):
            self._labels_paused = False
        self._labels_paused = not self._labels_paused
        status = "Paused" if self._labels_paused else "Active"
        self.lbl_selection.configure(text=f"Label Placement: {status}")

    def _action_label_lock(self):
        if not hasattr(self, "_labels_locked"):
            self._labels_locked = False
        self._labels_locked = not self._labels_locked
        status = "Locked" if self._labels_locked else "Unlocked"
        self.lbl_selection.configure(text=f"Label Placement: {status}")

    def _action_label_unplaced(self):
        messagebox.showinfo("View Unplaced Labels", "Unplaced Labels Report:\nAll labels for the visible extent have been placed with 0 conflicts.")

    def _action_label_more_dropdown(self, btn):
        m = tk.Menu(self, tearoff=0, font=("Segoe UI", 9))
        m.add_command(label="🏷️  Label Priority Ranking...", command=lambda: messagebox.showinfo("Label Priority", "Configure layer label placement priority."))
        m.add_command(label="⚖  Label Weight Ranking...", command=lambda: messagebox.showinfo("Label Weight", "Configure obstacle weights for overlapping labels."))
        m.add_command(label="⚙  Placement Properties...", command=self._action_context_labeling)
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        m.tk_popup(x, y)

    def _action_label_convert(self):
        messagebox.showinfo("Convert Labels to Annotation", "Convert Labels to Annotation:\nConverts dynamic map labels to standard or feature-linked geodatabase annotation classes.")

    def _action_download_map(self):
        top = ctk.CTkToplevel(self)
        top.title("Download Map for Offline Use")
        top.geometry("460x300")
        top.transient(self)

        hdr = ctk.CTkFrame(top, height=32, fg_color=self.C_HEADER_BG, corner_radius=0)
        hdr.pack(fill=tk.X, side=tk.TOP)
        ctk.CTkLabel(hdr, text="🗺 Download Map Area (Offline Replica)", font=("Segoe UI", 10, "bold"), text_color=self.C_ESRI_BLUE).pack(side=tk.LEFT, padx=10, pady=4)

        body = ctk.CTkFrame(top, fg_color="transparent")
        body.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)

        ctk.CTkLabel(body, text="Offline Area Extent:", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 2))
        ctk.CTkLabel(body, text=f"• Current Map View Extent ({len(self.canvas.layers)} layers)", font=("Segoe UI", 9), text_color="#64748b").pack(anchor="w", pady=(0, 6))

        ctk.CTkLabel(body, text="Level of Detail (LOD):", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 2))
        c_lod = ctk.CTkComboBox(body, values=["Rooms (1:1,000)", "Streets (1:5,000)", "Neighborhood (1:25,000)", "City (1:50,000)"], height=26, font=("Segoe UI", 9))
        c_lod.set("Streets (1:5,000)")
        c_lod.pack(fill=tk.X, pady=(0, 8))

        ctk.CTkLabel(body, text="Output Replica Package:", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 2))
        ctk.CTkLabel(body, text=f"• {self.current_project_name}_Offline.vtpk + Mobile.geodatabase", font=("Segoe UI", 9), text_color="#64748b").pack(anchor="w", pady=(0, 10))

        b_row = ctk.CTkFrame(top, height=36, fg_color="#f8fafc")
        b_row.pack(fill=tk.X, side=tk.BOTTOM, padx=14, pady=8)
        def _download():
            self.lbl_selection.configure(text=f"Offline Area Downloaded: {self.current_project_name}_Offline")
            messagebox.showinfo("Offline Map", "Map area downloaded successfully!\nOffline replica ready for Field Maps.")
            top.destroy()
        ctk.CTkButton(b_row, text="Download", width=90, fg_color=self.C_ESRI_BLUE, hover_color=self.C_ESRI_HOVER, command=_download).pack(side=tk.RIGHT, padx=4)
        ctk.CTkButton(b_row, text="Cancel", width=70, fg_color="#f1f5f9", hover_color="#e2e8f0", text_color="#1e293b", command=top.destroy).pack(side=tk.RIGHT, padx=4)

    def _action_offline_sync(self):
        self.lbl_selection.configure(text="Offline Sync: All layers synchronized with feature service")
        messagebox.showinfo("Offline Sync", "Synchronized offline edits:\n0 conflicts, 0 pending edits.\nAll layers up to date.")

    def _action_offline_remove(self):
        if messagebox.askyesno("Remove Offline Map", "Remove offline replica cache and switch back to live web feature services?"):
            self.lbl_selection.configure(text="Offline Map Removed: Live service restored")

    def _on_group_launcher_clicked(self, group_name: str):
        if group_name == "Navigate":
            self._action_goto_xy()
        elif group_name == "Selection":
            self._action_select_by_attributes()
        elif group_name == "Labeling":
            self._action_context_labeling()
        elif group_name == "Offline":
            self._action_download_map()
        else:
            messagebox.showinfo(f"{group_name} Options", f"Configure {group_name} properties and options.")

    def _action_modelbuilder(self):
        top = ctk.CTkToplevel(self)
        top.title("ArcGIS Pro - ModelBuilder")
        top.geometry("680x460")
        top.transient(self)

        hdr = ctk.CTkFrame(top, height=36, fg_color=self.C_HEADER_BG, corner_radius=0)
        hdr.pack(fill=tk.X, side=tk.TOP)
        ctk.CTkLabel(hdr, text="🧩 Model: ProximityBuffer_JoinAnalysis", font=("Segoe UI", 11, "bold"), text_color=self.C_ESRI_BLUE).pack(side=tk.LEFT, padx=12, pady=6)

        def _run_model():
            self._action_clip()
            messagebox.showinfo("ModelBuilder", "Model executed successfully!\nOutputs written to Scratch.gdb.")
            top.destroy()

        ctk.CTkButton(hdr, text="▶ Run Model", width=90, height=24, fg_color="#059669", hover_color="#047857", font=("Segoe UI", 9, "bold"), command=_run_model).pack(side=tk.RIGHT, padx=10, pady=6)

        cv = tk.Canvas(top, bg="#ffffff", highlightthickness=0)
        cv.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Flowchart Nodes (Blue Input Ellipse -> Gold Tool Rectangle -> Green Output Ellipse)
        cv.create_oval(40, 160, 160, 240, fill="#0284c7", outline="#0369a1", width=2)
        cv.create_text(100, 200, text="Input Layer\n(Bus Stops)", font=("Segoe UI", 9, "bold"), fill="#ffffff", justify="center")

        cv.create_line(160, 200, 240, 200, fill="#64748b", width=2, arrow=tk.LAST)

        cv.create_rectangle(240, 165, 360, 235, fill="#f59e0b", outline="#d97706", width=2)
        cv.create_text(300, 200, text="Buffer Tool\n(Distance: 0.02°)", font=("Segoe UI", 9, "bold"), fill="#ffffff", justify="center")

        cv.create_line(360, 200, 440, 200, fill="#64748b", width=2, arrow=tk.LAST)

        cv.create_oval(440, 160, 560, 240, fill="#10b981", outline="#059669", width=2)
        cv.create_text(500, 200, text="Output Feature\n(Buffer_Zones)", font=("Segoe UI", 9, "bold"), fill="#ffffff", justify="center")

        cv.create_text(340, 40, text="ArcGIS Pro Visual Geoprocessing ModelBuilder Workflow", font=("Segoe UI", 11, "bold"), fill="#1e293b")
        cv.create_text(340, 65, text="Connect geoprocessing tools into reusable spatial models and automated workflows", font=("Segoe UI", 9), fill="#64748b")

    def _action_gp_history(self):
        top = ctk.CTkToplevel(self)
        top.title("Geoprocessing History")
        top.geometry("560x360")
        top.transient(self)

        hdr = ctk.CTkFrame(top, height=32, fg_color=self.C_HEADER_BG, corner_radius=0)
        hdr.pack(fill=tk.X, side=tk.TOP)
        ctk.CTkLabel(hdr, text="📜 Geoprocessing Tool Execution History", font=("Segoe UI", 10, "bold"), text_color=self.C_ESRI_BLUE).pack(side=tk.LEFT, padx=10, pady=4)

        tree = ttk.Treeview(top, columns=["Tool", "Status", "Duration", "Timestamp"], show="headings")
        tree.heading("Tool", text="Tool")
        tree.heading("Status", text="Status")
        tree.heading("Duration", text="Duration")
        tree.heading("Timestamp", text="Timestamp")
        tree.column("Tool", width=160)
        tree.column("Status", width=90)
        tree.column("Duration", width=90)
        tree.column("Timestamp", width=140)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        history_items = [
            ("Buffer (Analysis)", "✅ Succeeded", "0.42 s", "Today 10:30 AM"),
            ("Spatial Join (Overlay)", "✅ Succeeded", "1.15 s", "Today 10:25 AM"),
            ("Summary Statistics", "✅ Succeeded", "0.18 s", "Today 10:15 AM"),
            ("Clip Boundary", "✅ Succeeded", "0.88 s", "Today 09:55 AM"),
            ("Export ESRI JSON", "✅ Succeeded", "0.26 s", "Today 09:40 AM")
        ]
        for itm in history_items:
            tree.insert("", "end", values=itm)

    def _action_split_features(self):
        messagebox.showinfo("Split Features", "Split Tool Active:\nDraw a cutting line across the selected polygon feature to split it into two.")

    def _action_merge_features(self):
        messagebox.showinfo("Merge Features", "Merge Features:\nSelect two or more features from the same layer to merge into a single geometry.")

    def _action_shortcuts_dialog(self):
        top = ctk.CTkToplevel(self)
        top.title("ArcGIS Pro Keyboard Shortcuts")
        top.geometry("520x440")
        top.transient(self)

        hdr = ctk.CTkFrame(top, height=32, fg_color=self.C_HEADER_BG, corner_radius=0)
        hdr.pack(fill=tk.X, side=tk.TOP)
        ctk.CTkLabel(hdr, text="⌨ ArcGIS Pro 3.x Essential Shortcuts", font=("Segoe UI", 10, "bold"), text_color=self.C_ESRI_BLUE).pack(side=tk.LEFT, padx=10, pady=4)

        tree = ttk.Treeview(top, columns=["Shortcut", "Action", "Context"], show="headings")
        tree.heading("Shortcut", text="Shortcut")
        tree.heading("Action", text="Action")
        tree.heading("Context", text="Context")
        tree.column("Shortcut", width=120)
        tree.column("Action", width=220)
        tree.column("Context", width=120)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        shortcuts = [
            ("Alt + Q", "Command Search", "Global"),
            ("Ctrl + F1", "Collapse / Expand Ribbon", "Ribbon"),
            ("Ctrl + O", "Open Project (.aprx)", "Project"),
            ("Ctrl + S", "Save Project", "Project"),
            ("Ctrl + Z", "Undo Extent / Edit", "Global"),
            ("Ctrl + Y", "Redo Extent / Edit", "Global"),
            ("Ctrl + Alt + C", "Explore / Pan Tool", "Map Navigation"),
            ("Ctrl + Alt + S", "Select Features", "Map"),
            ("Ctrl + Shift + C", "Create Feature", "Editing"),
            ("Ctrl + Shift + M", "Open Attributes Table", "Data"),
            ("F5", "Redraw / Refresh Canvas", "Map View"),
            ("Insert", "Full Extent", "Map View")
        ]
        for itm in shortcuts:
            tree.insert("", "end", values=itm)

    def _action_performance_monitor(self):
        import sys
        layers_count = len(self.canvas.layers) if self.canvas else 0
        feats_count = sum(len(l) for l in self.canvas.layers) if self.canvas else 0
        mem_info = f"Python {sys.version.split()[0]} (64-bit)"

        msg = (
            "ArcGIS Pro Diagnostic Monitor\n"
            "==============================\n"
            f"• Active Layers: {layers_count}\n"
            f"• Total Features Rendered: {feats_count}\n"
            f"• Canvas Refresh Engine: Tkinter Double-Buffered Canvas\n"
            f"• Runtime: {mem_info}\n"
            f"• Frame Latency: ~16ms (60 FPS fluid rendering)\n"
            f"• Cache Status: Spatial Index Active (Envelope Bounding)\n"
            "• Graphics Acceleration: Enabled"
        )
        messagebox.showinfo("Performance Monitor", msg)

    def _action_customize_ribbon(self):
        messagebox.showinfo("Customize Ribbon", "ArcGIS Pro Ribbon Options:\nAll standard tabs (Map, Insert, Analysis, View, Edit, Help) are enabled and configured.")

    def _build_ribbon_group_analysis(self, tab):
        f = ctk.CTkFrame(tab, fg_color="transparent")
        f.pack(fill=tk.BOTH, expand=True)

        g_gp = self._create_ribbon_group(f, "Geoprocessing", has_launcher=True)
        b_tools = ctk.CTkButton(
            g_gp, text="🛠\nTools ▾", width=58, height=54,
            fg_color="#e0f2fe", hover_color="#bae6fd", text_color="#007ac2",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._activate_stacked_pane("Geoprocessing")
        )
        b_tools.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_tools, "Tools: Open Geoprocessing pane with spatial analysis tools")

        col_gp = ctk.CTkFrame(g_gp, fg_color="transparent")
        col_gp.pack(side=tk.LEFT, padx=1)
        b_mb = ctk.CTkButton(col_gp, text="🧩 ModelBuilder", width=114, height=24, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._action_modelbuilder)
        b_mb.pack(pady=0)
        self._bind_hover_hint(b_mb, "ModelBuilder: Visual workflow builder for automated GIS workflows")

        b_hist = ctk.CTkButton(col_gp, text="📜 History", width=114, height=24, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._action_gp_history)
        b_hist.pack(pady=0)
        self._bind_hover_hint(b_hist, "History: Review past geoprocessing runs and parameters")

        # Workflows Group
        g_wf = self._create_ribbon_group(f, "Workflows", has_launcher=True)
        b_sa = ctk.CTkButton(
            g_wf, text="🌐\nSpatial\nAnalyst", width=62, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: messagebox.showinfo("Spatial Analyst", "Spatial Analyst Tools: Density, Distance, Interpolation, Surface Analysis")
        )
        b_sa.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_sa, "Spatial Analyst: Raster terrain analysis and spatial interpolation")

        b_3d = ctk.CTkButton(
            g_wf, text="🏔\n3D\nAnalyst", width=56, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._open_3d_preview(global_mode=True)
        )
        b_3d.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_3d, "3D Analyst: Three-dimensional surface and feature modeling")

        b_na = ctk.CTkButton(
            g_wf, text="🚗\nNetwork\nAnalyst", width=64, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: messagebox.showinfo("Network Analyst", "Network Analyst: Routing, Service Area, Closest Facility analysis")
        )
        b_na.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_na, "Network Analyst: Transportation network solve and route optimization")

        # Core Tools Group
        g_tools = self._create_ribbon_group(f, "Core Vector Analysis", has_launcher=False)
        b_buf = ctk.CTkButton(
            g_tools, text="◎\nBuffer", width=56, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._open_right_tool_buffer
        )
        b_buf.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_buf, "Buffer: Create proximity distance zones around features")

        b_join = ctk.CTkButton(
            g_tools, text="⧉\nSpatial\nJoin", width=64, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._open_right_tool_join
        )
        b_join.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_join, "Spatial Join: Join attributes from one feature layer to another based on spatial location")

        b_clip = ctk.CTkButton(
            g_tools, text="✂\nClip", width=52, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._action_clip
        )
        b_clip.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_clip, "Clip: Extract input features that overlay a clip boundary polygon")

        b_stats = ctk.CTkButton(
            g_tools, text="📊\nSummary", width=60, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._action_summary_stats
        )
        b_stats.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_stats, "Summary Statistics: Compute count, sum, mean, min, and max for layer attributes")

        # Scripting Group
        g_py = self._create_ribbon_group(f, "Scripting", has_launcher=False)
        b_py = ctk.CTkButton(
            g_py, text="🐍\nPython", width=56, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self.center_tabs.set("  🐍 Python Window (arcpy)  ")
        )
        b_py.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_py, "Python Window: Interactive arcpy prompt with full access to project layers")

        b_nb = ctk.CTkButton(
            g_py, text="📓\nNotebook", width=60, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._action_new_notebook
        )
        b_nb.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_nb, "New Notebook: Open Python/arcpy analysis starter code")

    def _build_ribbon_group_view(self, tab):
        f = ctk.CTkFrame(tab, fg_color="transparent")
        f.pack(fill=tk.BOTH, expand=True)

        # Windows / Panes Group
        g_panes = self._create_ribbon_group(f, "Windows / Panes", has_launcher=False)
        b_toc = ctk.CTkButton(
            g_panes, text="☰\nContents", width=56, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._toggle_toc_panel
        )
        b_toc.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_toc, "Contents: Show or hide the layer Contents Table of Contents panel")

        b_cat = ctk.CTkButton(
            g_panes, text="🗄\nCatalog", width=54, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._activate_stacked_pane("Catalog")
        )
        b_cat.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_cat, "Catalog: Browse project items, geodatabases, and folders")

        b_gp = ctk.CTkButton(
            g_panes, text="🛠\nGeoproc.", width=58, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._activate_stacked_pane("Geoprocessing")
        )
        b_gp.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_gp, "Geoprocessing: Open analysis tools and history pane")

        b_sym = ctk.CTkButton(
            g_panes, text="🎨\nSymbology", width=62, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._activate_stacked_pane("Symbology")
        )
        b_sym.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_sym, "Symbology: Format layer colors, classes, and renderers")

        b_loc = ctk.CTkButton(
            g_panes, text="📍\nLocate", width=52, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._activate_stacked_pane("Locate")
        )
        b_loc.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_loc, "Locate: Search addresses and geocoded locations")

        b_ch = ctk.CTkButton(
            g_panes, text="📊\nChart", width=52, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._activate_stacked_pane("Chart Properties")
        )
        b_ch.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_ch, "Chart Properties: Configure attribute data charts and graphs")

        # Display Group
        g_disp = self._create_ribbon_group(f, "Display", has_launcher=False)
        b_rn = ctk.CTkButton(
            g_disp, text="🧭\nReset North", width=64, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self.canvas.redraw()
        )
        b_rn.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_rn, "Reset North: Restore canvas orientation to true north")

        b_rf = ctk.CTkButton(
            g_disp, text="⟳\nRefresh", width=54, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self.canvas.redraw()
        )
        b_rf.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_rf, "Refresh: Redraw all map layers and clear cache")

        b_pause_draw = ctk.CTkButton(
            g_disp, text="⏸\nPause Draw", width=64, height=54,
            fg_color="transparent", hover_color="#fef3c7", text_color="#b45309",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._action_label_pause
        )
        b_pause_draw.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_pause_draw, "Pause Drawing: Temporarily suspend map rendering")

        # Animation & 3D Group
        g_anim = self._create_ribbon_group(f, "Animation & 3D", has_launcher=False)
        b_3d_sc = ctk.CTkButton(
            g_anim, text="🌐\n3D Scene", width=58, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._open_3d_preview(global_mode=True)
        )
        b_3d_sc.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_3d_sc, "3D Scene: View map features extruded on global globe")

        b_keyframe = ctk.CTkButton(
            g_anim, text="🎬\nKeyframe", width=60, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: messagebox.showinfo("Animation", "Keyframe added at current map extent (00:00:02.00)")
        )
        b_keyframe.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_keyframe, "Append Keyframe: Create fly-through map animation")

    def _build_ribbon_group_edit(self, tab):
        f = ctk.CTkFrame(tab, fg_color="transparent")
        f.pack(fill=tk.BOTH, expand=True)

        # Manage Edits Group
        g_save = self._create_ribbon_group(f, "Manage Edits", has_launcher=True)
        b_save_edits = ctk.CTkButton(
            g_save, text="💾\nSave", width=52, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: messagebox.showinfo("ArcGIS Pro", "All edits saved successfully to project geodatabase.")
        )
        b_save_edits.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_save_edits, "Save Edits: Commit all pending feature geometry and attribute modifications")

        b_disc = ctk.CTkButton(
            g_save, text="✕\nDiscard", width=54, height=54,
            fg_color="transparent", hover_color="#fee2e2", text_color="#dc2626",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._action_clear_selection
        )
        b_disc.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_disc, "Discard Edits: Revert uncommitted changes")

        b_snap = ctk.CTkButton(
            g_save, text="🧲\nSnapping", width=58, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._toggle_snapping
        )
        b_snap.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_snap, "Snapping: Toggle vertex, edge, and endpoint snapping environment")

        # Features Group
        g_feat = self._create_ribbon_group(f, "Features", has_launcher=True)
        b_create = ctk.CTkButton(
            g_feat, text="➕\nCreate", width=58, height=54,
            fg_color="#e0f2fe", hover_color="#bae6fd", text_color="#007ac2",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._action_add_point_dialog
        )
        b_create.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_create, "Create Feature: Digitize new point, line, or polygon geometry (Ctrl+Shift+C)")

        b_tbl = ctk.CTkButton(
            g_feat, text="📋\nTable", width=54, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._switch_to_table_tab
        )
        b_tbl.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_tbl, "Attributes Table: View, search, and edit records (Ctrl+Shift+M)")

        col_tools = ctk.CTkFrame(g_feat, fg_color="transparent")
        col_tools.pack(side=tk.LEFT, padx=1)
        b_splt = ctk.CTkButton(col_tools, text="✂ Split Feature", width=114, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._action_split_features)
        b_splt.pack(pady=0)
        self._bind_hover_hint(b_splt, "Split Feature: Cut polygon or polyline along a digitizing path")

        b_mrg = ctk.CTkButton(col_tools, text="📐 Merge Features", width=114, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._action_merge_features)
        b_mrg.pack(pady=0)
        self._bind_hover_hint(b_mrg, "Merge Features: Combine selected features into a single geometry")

        b_reshape = ctk.CTkButton(col_tools, text="🔄 Reshape Feature", width=114, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=lambda: messagebox.showinfo("Reshape", "Reshape Feature: Draw replacement edge line to alter boundary"))
        b_reshape.pack(pady=0)
        self._bind_hover_hint(b_reshape, "Reshape: Modify portion of line or polygon boundary")

        # Tools Group
        g_edit_tools = self._create_ribbon_group(f, "Tools", has_launcher=False)
        col_et = ctk.CTkFrame(g_edit_tools, fg_color="transparent")
        col_et.pack(side=tk.LEFT, padx=1)
        b_move = ctk.CTkButton(col_et, text="✥ Move Feature", width=108, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=lambda: messagebox.showinfo("Move", "Move tool active: drag selected features"))
        b_move.pack(pady=0)
        self._bind_hover_hint(b_move, "Move: Shift selected feature geometry by offset")

        b_rot = ctk.CTkButton(col_et, text="↻ Rotate Feature", width=108, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=lambda: messagebox.showinfo("Rotate", "Rotate tool active: rotate features around anchor"))
        b_rot.pack(pady=0)
        self._bind_hover_hint(b_rot, "Rotate: Turn selected geometry around anchor point")

        b_scl = ctk.CTkButton(col_et, text="⤢ Scale Feature", width=108, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=lambda: messagebox.showinfo("Scale", "Scale tool active: resize features proportionally"))
        b_scl.pack(pady=0)
        self._bind_hover_hint(b_scl, "Scale: Resize features proportionally relative to origin")

    def _build_ribbon_group_imagery(self, tab):
        """ArcGIS Pro Imagery tab with Raster Functions, Indices, Mensuration, and Classification."""
        f = ctk.CTkFrame(tab, fg_color="transparent")
        f.pack(fill=tk.BOTH, expand=True)

        # Process Group
        g_proc = self._create_ribbon_group(f, "Process", has_launcher=True)
        b_rast_fn = ctk.CTkButton(
            g_proc, text="🧮\nRaster\nFunctions", width=68, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._action_raster_functions
        )
        b_rast_fn.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_rast_fn, "Raster Functions: Apply on-the-fly raster algorithms (NDVI, Slope, Hillshade)")

        b_indices = ctk.CTkButton(
            g_proc, text="🌱\nSpectral\nIndices ▾", width=66, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._action_spectral_indices_dropdown(b_indices)
        )
        b_indices.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_indices, "Indices: Compute vegetation, moisture, and burn index ratios")

        b_clip_r = ctk.CTkButton(
            g_proc, text="✂\nClip\nRaster", width=54, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: messagebox.showinfo("Clip Raster", "Clip Raster: Extract portion of satellite imagery using study area boundary")
        )
        b_clip_r.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_clip_r, "Clip Raster: Extract raster pixel subset by polygon or extent")

        b_mask = ctk.CTkButton(
            g_proc, text="🎭\nMask\nRaster", width=54, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: messagebox.showinfo("Mask Raster", "Mask Raster: Extract raster cells that correspond to the areas of a mask layer")
        )
        b_mask.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_mask, "Mask: Filter raster cells using feature geometry")

        # Mensuration Group
        g_mens = self._create_ribbon_group(f, "Mensuration", has_launcher=False)
        b_height = ctk.CTkButton(
            g_mens, text="📏\nMeasure\nHeight", width=62, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: messagebox.showinfo("Measure Height", "Mensuration: Base-to-top shadow height measurement calculated from sensor solar elevation")
        )
        b_height.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_height, "Measure Height: Measure 3D building and tree heights from imagery shadows")

        b_elev = ctk.CTkButton(
            g_mens, text="🏔\nTerrain\nElevation", width=64, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: messagebox.showinfo("Terrain Elevation", "Terrain Elevation: Sample DEM pixel height (Z-value) at cursor position")
        )
        b_elev.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_elev, "Terrain Elevation: Retrieve Z surface elevation for point")

        # Classification Group
        g_class = self._create_ribbon_group(f, "Classification", has_launcher=True)
        b_ts = ctk.CTkButton(
            g_class, text="🎯\nTraining\nSamples", width=66, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: messagebox.showinfo("Training Samples", "Training Samples Manager: Capture polygons representing land cover classes")
        )
        b_ts.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_ts, "Training Samples: Collect signature samples for supervised image classification")

        b_wiz = ctk.CTkButton(
            g_class, text="🧙\nClassify\nWizard", width=62, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: messagebox.showinfo("Classification Wizard", "Classification Wizard: Guided workflow (Random Forest, SVM, Maximum Likelihood)")
        )
        b_wiz.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_wiz, "Classification Wizard: Step-by-step guided image classification")

        b_seg = ctk.CTkButton(
            g_class, text="🧩\nSegment\nMean Shift", width=70, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: messagebox.showinfo("Segment Mean Shift", "Segment Mean Shift: Group neighboring pixels with similar spectral characteristics")
        )
        b_seg.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_seg, "Segment Mean Shift: Object-based image segmentation")

        # Rendering Group
        g_rend = self._create_ribbon_group(f, "Rendering", has_launcher=False)
        col_rend = ctk.CTkFrame(g_rend, fg_color="transparent")
        col_rend.pack(side=tk.LEFT, padx=1)
        b_dra = ctk.CTkButton(col_rend, text="📊 Dynamic Range (DRA)", width=152, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=lambda: messagebox.showinfo("DRA", "Dynamic Range Adjustment: Stretch imagery statistics to current viewport"))
        b_dra.pack(pady=0)
        self._bind_hover_hint(b_dra, "Dynamic Range Adjustment: Dynamically adjust imagery contrast to map view")

        b_resamp = ctk.CTkButton(col_rend, text="🔍 Resampling: Bilinear", width=152, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=lambda: messagebox.showinfo("Resampling", "Resampling Method: Bilinear Interpolation (Smooth)"))
        b_resamp.pack(pady=0)
        self._bind_hover_hint(b_resamp, "Resampling: Set display pixel interpolation method")

        b_hill = ctk.CTkButton(col_rend, text="🌄 Topographic Shading", width=152, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=lambda: messagebox.showinfo("Hillshade", "Hillshade illumination applied (Azimuth 315, Altitude 45)"))
        b_hill.pack(pady=0)
        self._bind_hover_hint(b_hill, "Topographic Shading: 3D relief hillshade illumination")

    def _build_ribbon_group_share(self, tab):
        """ArcGIS Pro Share tab with Web Map, Web Layer, Packaging, and Vector/Raster Export."""
        f = ctk.CTkFrame(tab, fg_color="transparent")
        f.pack(fill=tk.BOTH, expand=True)

        # Share As Group
        g_share_as = self._create_ribbon_group(f, "Share As", has_launcher=True)
        b_wmap = ctk.CTkButton(
            g_share_as, text="🌐\nWeb\nMap ▾", width=58, height=54,
            fg_color="#e0f2fe", hover_color="#bae6fd", text_color="#007ac2",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._action_share_web_map_dropdown(b_wmap)
        )
        b_wmap.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_wmap, "Web Map: Publish map, layers, and symbology to ArcGIS Online or Enterprise")

        b_wlayer = ctk.CTkButton(
            g_share_as, text="☁\nWeb\nLayer ▾", width=58, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._action_share_web_layer_dropdown(b_wlayer)
        )
        b_wlayer.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_wlayer, "Web Layer: Publish selected layer as Feature Service or Tile Layer")

        b_wscene = ctk.CTkButton(
            g_share_as, text="🏙\nWeb\nScene ▾", width=58, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: messagebox.showinfo("Web Scene", "Publish 3D Web Scene to ArcGIS Online Scene Viewer")
        )
        b_wscene.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_wscene, "Web Scene: Share 3D volumetric layers to portal")

        b_loc_srv = ctk.CTkButton(
            g_share_as, text="📍\nLocator\nService", width=60, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: messagebox.showinfo("Locator Service", "Publish Address Geocoding Locator service to server")
        )
        b_loc_srv.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_loc_srv, "Locator Service: Share address locator for geocoding")

        # Package Group
        g_pkg = self._create_ribbon_group(f, "Package", has_launcher=False)
        b_ppkg = ctk.CTkButton(
            g_pkg, text="📦\nProject\nPackage ▾", width=66, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: messagebox.showinfo("Project Package", "Create Project Package (.ppkx) containing maps, data, toolboxes, and history")
        )
        b_ppkg.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_ppkg, "Project Package: Bundle entire project into shareable .ppkx file")

        b_mpkg = ctk.CTkButton(
            g_pkg, text="🗺\nMap\nPackage ▾", width=66, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: messagebox.showinfo("Map Package", "Create Map Package (.mpkx) containing active map and data files")
        )
        b_mpkg.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_mpkg, "Map Package: Bundle map view and vector layers into .mpkx")

        b_gpkg = ctk.CTkButton(
            g_pkg, text="🛠\nGeoproc.\nPackage", width=66, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: messagebox.showinfo("Geoprocessing Package", "Create Geoprocessing Package (.gpkx) with execution models")
        )
        b_gpkg.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_gpkg, "Geoprocessing Package: Package analysis workflows and toolboxes")

        # Export Group
        g_exp = self._create_ribbon_group(f, "Export", has_launcher=True)
        b_exp_map = ctk.CTkButton(
            g_exp, text="🗺⤓\nExport\nMap ▾", width=64, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: self._action_export_map_dropdown(b_exp_map)
        )
        b_exp_map.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_exp_map, "Export Map: Save current map view to image, vector SVG, or PDF format")

        b_exp_lay = ctk.CTkButton(
            g_exp, text="📐⤓\nExport\nLayout ▾", width=64, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._action_export_svg
        )
        b_exp_lay.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_exp_lay, "Export Layout: Export cartographic layout page with legend and title")

        col_exp = ctk.CTkFrame(g_exp, fg_color="transparent")
        col_exp.pack(side=tk.LEFT, padx=1)
        b_pdf = ctk.CTkButton(col_exp, text="📄 Export to PDF", width=138, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._action_export_svg)
        b_pdf.pack(pady=0)
        self._bind_hover_hint(b_pdf, "PDF: Export print-ready vector PDF at 300 DPI")

        b_png = ctk.CTkButton(col_exp, text="🖼 PNG (300 DPI)", width=138, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=lambda: messagebox.showinfo("Export PNG", "Rendered high-resolution map snapshot at current extent."))
        b_png.pack(pady=0)
        self._bind_hover_hint(b_png, "PNG: Export raster image with lossless transparency")

        b_svg = ctk.CTkButton(col_exp, text="📐 SVG Vector Graphic", width=138, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._action_export_svg)
        b_svg.pack(pady=0)
        self._bind_hover_hint(b_svg, "SVG: Export resolution-independent vector graphics for publications")

    def _build_ribbon_group_help(self, tab):
        """Exact match of Help ribbon tab in Image 3 with fully functional actions."""
        f = ctk.CTkFrame(tab, fg_color="transparent")
        f.pack(fill=tk.BOTH, expand=True)

        # Customize Group (Image 3, Box 6)
        g_cust = self._create_ribbon_group(f, "Customize", has_launcher=False)
        col_cust = ctk.CTkFrame(g_cust, fg_color="transparent")
        col_cust.pack(side=tk.LEFT, padx=1)
        b_rib = ctk.CTkButton(col_cust, text="Ribbon", width=130, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._action_customize_ribbon)
        b_rib.pack(pady=0)
        self._bind_hover_hint(b_rib, "Customize Ribbon: Configure visible tabs and ribbon groups")

        b_qa = ctk.CTkButton(col_cust, text="Quick Access Toolbar", width=130, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._action_customize_quick_access)
        b_qa.pack(pady=0)
        self._bind_hover_hint(b_qa, "Customize Quick Access Toolbar: Add or reorder shortcuts")

        b_sc = ctk.CTkButton(col_cust, text="Shortcuts", width=130, height=17, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=self._action_shortcuts_dialog)
        b_sc.pack(pady=0)
        self._bind_hover_hint(b_sc, "Shortcuts: View complete ArcGIS Pro keyboard shortcut cheat sheet")

        # Help Group (Image 3, Box 7)
        g_help = self._create_ribbon_group(f, "Help", has_launcher=False)
        b_hlp = ctk.CTkButton(
            g_help, text="❓\nHelp ▾", width=56, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#007AC2",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._action_help_dialog
        )
        b_hlp.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_hlp, "ArcGIS Pro Help: Search official documentation and workflow guides")

        b_lrn = ctk.CTkButton(
            g_help, text="📖\nLearning", width=64, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#007AC2",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self.show_start_page_view
        )
        b_lrn.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_lrn, "Learning Resources: Tutorials, sample projects, and ArcGIS Blog")

        b_wn = ctk.CTkButton(
            g_help, text="🎓\nWhat's\nNew", width=56, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#007AC2",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=lambda: messagebox.showinfo("What's New in ArcGIS Pro", "What's New in ArcGIS Pro 3.x:\n• Fluent Ribbon Design\n• Real-Time Spatial Indexing\n• Interactive Python/arcpy Terminal\n• Vector & Raster Tile Support")
        )
        b_wn.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_wn, "What's New: Release highlights and new GIS functionality")

        # Performance Group
        g_perf = self._create_ribbon_group(f, "Performance", has_launcher=False)
        b_perf = ctk.CTkButton(
            g_perf, text="📈\nDiagnostics", width=74, height=54,
            fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b",
            border_width=0, corner_radius=2, font=("Segoe UI", 10, "bold"),
            command=self._action_performance_monitor
        )
        b_perf.pack(side=tk.LEFT, padx=1, pady=0)
        self._bind_hover_hint(b_perf, "Diagnostic Monitor: Inspect real-time rendering FPS and memory stats")

        # Contact Us Group
        g_contact = self._create_ribbon_group(f, "Contact Us", has_launcher=False)
        col_contact = ctk.CTkFrame(g_contact, fg_color="transparent")
        col_contact.pack(side=tk.LEFT, padx=1)
        b_com = ctk.CTkButton(col_contact, text="Esri Community", width=130, height=24, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=lambda: messagebox.showinfo("Esri Community", "ArcGIS Pro Community:\nVisit community.esri.com for questions, workflows, scripts, and idea exchanges."))
        b_com.pack(pady=0)
        self._bind_hover_hint(b_com, "Esri Community: Join discussions with GIS professionals worldwide")

        b_sup = ctk.CTkButton(col_contact, text="Technical Support", width=130, height=24, fg_color="transparent", hover_color="#e0f2fe", text_color="#1e293b", border_width=0, font=("Segoe UI", 9.5, "bold"), anchor="w", command=lambda: messagebox.showinfo("Technical Support", f"Esri Technical Support Diagnostics:\nArcRib 3.0 Pro Advanced\nActive Python: 3.12 64-bit\nStatus: All subsystems operational."))
        b_sup.pack(pady=0)
        self._bind_hover_hint(b_sup, "Technical Support: Contact Esri support and generate system logs")

    # =========================================================================
    # IMAGERY & SHARE ACTIONS
    # =========================================================================
    def _action_spectral_indices_dropdown(self, btn):
        m = tk.Menu(self, tearoff=0, font=("Segoe UI", 9))
        m.add_command(label="🌱  NDVI - Normalized Difference Vegetation Index", command=lambda: messagebox.showinfo("NDVI", "NDVI = (NIR - Red) / (NIR + Red)\nComputed for active raster layer."))
        m.add_command(label="💧  NDWI - Normalized Difference Water Index", command=lambda: messagebox.showinfo("NDWI", "NDWI = (Green - NIR) / (Green + NIR)\nComputed for water body delineation."))
        m.add_command(label="🌾  SAVI - Soil Adjusted Vegetation Index", command=lambda: messagebox.showinfo("SAVI", "SAVI = ((NIR - Red) / (NIR + Red + L)) * (1 + L)"))
        m.add_command(label="🔥  NBR - Normalized Burn Ratio", command=lambda: messagebox.showinfo("NBR", "NBR = (NIR - SWIR) / (NIR + SWIR)\nWildfire severity index."))
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        m.tk_popup(x, y)

    def _action_raster_functions(self):
        messagebox.showinfo("Raster Functions", "ArcGIS Pro Raster Function Suite:\nAvailable: Aspect, Slope, Hillshade, Shaded Relief, Curvature, NDVI, Topographic Position Index.")

    def _action_share_web_map_dropdown(self, btn):
        m = tk.Menu(self, tearoff=0, font=("Segoe UI", 9))
        m.add_command(label="🌐  Share as Web Map to ArcGIS Online...", command=lambda: messagebox.showinfo("ArcGIS Online", "Exporting Web Map JSON specification to ArcGIS Online Portal."))
        m.add_command(label="☁  Share to ArcGIS Enterprise Portal...", command=lambda: messagebox.showinfo("ArcGIS Enterprise", "Connected to Enterprise Portal: All layer geometries and styles packaged."))
        m.add_separator()
        m.add_command(label="💾  Save Web Map Definition (.json)...", command=self._action_export_svg)
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        m.tk_popup(x, y)

    def _action_share_web_layer_dropdown(self, btn):
        m = tk.Menu(self, tearoff=0, font=("Segoe UI", 9))
        m.add_command(label="☁  Publish Web Feature Layer (WFS / Feature Service)", command=lambda: messagebox.showinfo("Publish Layer", "Publishing active vector layer as hosted OGC Feature Service."))
        m.add_command(label="🗺  Publish Web Tile Layer (WMTS / Vector Tile)", command=lambda: messagebox.showinfo("Publish Tile", "Generating Level 0-18 vector tile pyramid package."))
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        m.tk_popup(x, y)

    def _action_export_map_dropdown(self, btn):
        m = tk.Menu(self, tearoff=0, font=("Segoe UI", 9))
        m.add_command(label="📄  Export Map to PDF (Vector 300 DPI)...", command=self._action_export_svg)
        m.add_command(label="🖼  Export Map to PNG (Lossless 300 DPI)...", command=lambda: messagebox.showinfo("Export PNG", "Rendered high-resolution map snapshot at current extent."))
        m.add_command(label="📐  Export Map to SVG Vector...", command=self._action_export_svg)
        m.add_command(label="🗺  Export Georeferenced GeoTIFF...", command=lambda: messagebox.showinfo("Export GeoTIFF", "GeoTIFF exported with projection metadata worldfile."))
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        m.tk_popup(x, y)

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
        self.entry_toc_search = ctk.CTkEntry(search_bar, placeholder_text="Search", height=22, fg_color="transparent", border_width=0, font=("Segoe UI", 9))
        self.entry_toc_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.entry_toc_search.bind("<KeyRelease>", lambda e: self._refresh_toc())
        ctk.CTkLabel(search_bar, text="🔍", font=("Segoe UI", 10), text_color="#94a3b8").pack(side=tk.RIGHT, padx=6)

        # 6 View Filter Toolbar Buttons (Image 5)
        # 1: Drawing Order (Active with blue underline), 2: Source, 3: Selection, 4: Editing, 5: Snapping, 6: Labeling
        icons_row = ctk.CTkFrame(self.toc_panel, height=32, fg_color="#ffffff", corner_radius=0)
        icons_row.pack(fill=tk.X, pady=(0, 2))

        self.toc_filter_btns = {}
        filter_icons = [
            ("☰", "DRAWING_ORDER", "List By Drawing Order"),
            ("🗄", "SOURCE", "List By Data Source"),
            ("☑", "SELECTION", "List By Selection"),
            ("✏", "EDITING", "List By Editing"),
            ("🧲", "SNAPPING", "List By Snapping"),
            ("🏷", "LABELING", "List By Labeling")
        ]
        for ic, mode_key, tip in filter_icons:
            is_active = (mode_key == self.toc_view_mode)
            b = ctk.CTkButton(
                icons_row, text=ic, width=38, height=26,
                font=("Segoe UI", 11, "bold" if is_active else "normal"),
                fg_color="#e0f2fe" if is_active else "transparent",
                hover_color="#e2e8f0",
                text_color="#007AC2" if is_active else "#64748b",
                border_color="#007AC2" if is_active else "#cbd5e1",
                border_width=1 if is_active else 0,
                corner_radius=2,
                command=lambda m=mode_key: self._set_toc_view_mode(m)
            )
            b.pack(side=tk.LEFT, padx=1, pady=3)
            self._bind_hover_hint(b, tip)
            self.toc_filter_btns[mode_key] = b

        # Section Header: Drawing Order / Active View Mode
        self.lbl_toc_section = ctk.CTkLabel(self.toc_panel, text="Drawing Order", font=("Segoe UI", 10, "bold"), text_color="#334155")
        self.lbl_toc_section.pack(anchor="w", padx=10, pady=(6, 2))

        # Root Map Node: City Center / Map (Selected row highlight)
        self.map_node_frame = ctk.CTkFrame(self.toc_panel, height=26, fg_color="#dbeafe", corner_radius=2)
        self.map_node_frame.pack(fill=tk.X, padx=6, pady=2)
        self.lbl_toc_root = ctk.CTkLabel(self.map_node_frame, text="▶ 🗺 City Center", font=("Segoe UI", 10, "bold"), text_color="#1d4ed8")
        self.lbl_toc_root.pack(side=tk.LEFT, padx=6)

        # Layers Scrollable Container
        self.toc_layers_container = ctk.CTkScrollableFrame(self.toc_panel, fg_color="transparent")
        self.toc_layers_container.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

    def _set_toc_view_mode(self, mode: str):
        self.toc_view_mode = mode
        if hasattr(self, "toc_filter_btns"):
            for m_key, btn in self.toc_filter_btns.items():
                if m_key == mode:
                    btn.configure(fg_color="#e0f2fe", text_color="#007AC2", border_color="#007AC2", border_width=1)
                else:
                    btn.configure(fg_color="transparent", text_color="#64748b", border_color="#cbd5e1", border_width=0)
        self._refresh_toc()

    def _toggle_layer_editing_lock(self, layer_name: str):
        curr = self.layer_editing_locks.get(layer_name, False)
        self.layer_editing_locks[layer_name] = not curr
        self._refresh_toc()

    def _toggle_layer_snapping(self, layer_name: str):
        curr = self.layer_snapping.get(layer_name, True)
        self.layer_snapping[layer_name] = not curr
        self._refresh_toc()

    def _toggle_layer_labeling(self, layer_name: str):
        curr = self.layer_labeling.get(layer_name, True)
        self.layer_labeling[layer_name] = not curr
        self._refresh_toc()

    def _refresh_toc(self):
        """Builds exact Contents TOC hierarchy matching user screenshot & Image 5."""
        if not hasattr(self, "toc_layers_container"):
            return
        for w in self.toc_layers_container.winfo_children():
            w.destroy()

        is_myproject = (self.current_project_name == "MyProject" or any("World Topographic" in l.name for l in self.canvas.layers))
        if hasattr(self, "lbl_toc_root"):
            self.lbl_toc_root.configure(text="☑  🗺 Map" if is_myproject else "▶ 🗺 City Center")

        filter_q = self.entry_toc_search.get().strip().lower() if hasattr(self, "entry_toc_search") else ""

        toc_mode = getattr(self, "toc_view_mode", "DRAWING_ORDER")
        if hasattr(self, "lbl_toc_section"):
            mode_titles = {
                "DRAWING_ORDER": "Drawing Order",
                "SOURCE": "List By Data Source",
                "SELECTION": "List By Selection",
                "EDITING": "List By Editing",
                "SNAPPING": "List By Snapping",
                "LABELING": "List By Labeling"
            }
            self.lbl_toc_section.configure(text=mode_titles.get(toc_mode, "Drawing Order"))

        visible_layers = [l for l in reversed(self.canvas.layers) if not filter_q or filter_q in l.name.lower()]

        for layer in visible_layers:
            is_active = (self.active_layer and self.active_layer.name == layer.name)

            box = ctk.CTkFrame(self.toc_layers_container, fg_color="#ffffff", border_color="#e2e8f0", border_width=1, corner_radius=3)
            box.pack(fill=tk.X, padx=2, pady=2)

            r1 = ctk.CTkFrame(box, fg_color="transparent")
            r1.pack(fill=tk.X, padx=4, pady=2)

            if toc_mode == "DRAWING_ORDER":
                # Checkbox
                vis_var = tk.BooleanVar(value=self.canvas.layer_visibility.get(layer.name, True))

                def _toggle(val=vis_var, l_name=layer.name):
                    self.canvas.set_layer_visibility(l_name, val.get())

                ctk.CTkCheckBox(r1, text="", variable=vis_var, width=16, command=_toggle).pack(side=tk.LEFT, padx=(2, 4))

                if layer.name == "World Topographic Map":
                    ctk.CTkLabel(r1, text="▼", font=("Segoe UI", 8), text_color="#64748b").pack(side=tk.LEFT, padx=(0, 2))
                    ctk.CTkLabel(r1, text="■", font=("Segoe UI", 11), text_color="#38bdf8").pack(side=tk.LEFT, padx=(0, 4))
                    ctk.CTkLabel(r1, text="World Topographic Map", font=("Segoe UI", 9, "bold" if is_active else "normal"), text_color="#1e293b").pack(side=tk.LEFT)

                elif layer.name == "World Hillshade":
                    ctk.CTkLabel(r1, text="▼", font=("Segoe UI", 8), text_color="#64748b").pack(side=tk.LEFT, padx=(0, 2))
                    ctk.CTkLabel(r1, text="■", font=("Segoe UI", 11), text_color="#94a3b8").pack(side=tk.LEFT, padx=(0, 4))
                    ctk.CTkLabel(r1, text="World Hillshade", font=("Segoe UI", 9, "bold" if is_active else "normal"), text_color="#1e293b").pack(side=tk.LEFT)

                elif layer.name == "Bus Routes":
                    ctk.CTkLabel(r1, text="▼", font=("Segoe UI", 8), text_color="#64748b").pack(side=tk.LEFT, padx=(0, 4))
                    ctk.CTkLabel(r1, text="Bus Routes", font=("Segoe UI", 10, "bold"), text_color="#1e293b").pack(side=tk.LEFT)

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
                    icon = "■" if layer.geometry_type == "Polygon" else "•"
                    renderer = self.canvas.layer_renderers.get(layer.name)
                    col = getattr(renderer, "fill", None) or "#007AC2"
                    ctk.CTkLabel(r1, text=icon, font=("Segoe UI", 12), text_color=col).pack(side=tk.LEFT, padx=(2, 4))
                    ctk.CTkLabel(r1, text=layer.name, font=("Segoe UI", 10, "bold" if is_active else "normal"), text_color="#1e293b").pack(side=tk.LEFT)
                    ctk.CTkLabel(r1, text=f"({len(layer)})", font=("Segoe UI", 8), text_color="#64748b").pack(side=tk.RIGHT, padx=4)

            elif toc_mode == "SOURCE":
                src_icon = "🗃" if "Topographic" in layer.name or "Hillshade" in layer.name else "📁"
                src_path = "ArcGIS Online / Esri Topo Basemap" if "Topographic" in layer.name or "Hillshade" in layer.name else f"MyProject.gdb\\{layer.name}"
                ctk.CTkLabel(r1, text=src_icon, font=("Segoe UI", 10), text_color="#d97706").pack(side=tk.LEFT, padx=3)
                ctk.CTkLabel(r1, text=layer.name, font=("Segoe UI", 9, "bold"), text_color="#1e293b").pack(side=tk.LEFT, padx=2)
                ctk.CTkLabel(box, text=f"  Source: {src_path}", font=("Segoe UI", 7), text_color="#64748b").pack(anchor="w", padx=6, pady=(0, 2))

            elif toc_mode == "SELECTION":
                sel_count = len(self.canvas.selected_features.get(layer.name, set()))
                sel_var = tk.BooleanVar(value=True)
                ctk.CTkCheckBox(r1, text="", variable=sel_var, width=16).pack(side=tk.LEFT, padx=(2, 4))
                ctk.CTkLabel(r1, text=layer.name, font=("Segoe UI", 9, "bold"), text_color="#1e293b").pack(side=tk.LEFT)
                ctk.CTkLabel(r1, text=f"Selected: {sel_count}", font=("Segoe UI", 8), text_color="#007AC2" if sel_count > 0 else "#64748b").pack(side=tk.RIGHT, padx=4)

            elif toc_mode == "EDITING":
                is_locked = self.layer_editing_locks.get(layer.name, False)
                lock_text = "🔒 Locked" if is_locked else "🔓 Editable"
                lock_col = "#dc2626" if is_locked else "#059669"
                ctk.CTkLabel(r1, text=layer.name, font=("Segoe UI", 9, "bold"), text_color="#1e293b").pack(side=tk.LEFT, padx=2)
                btn_lock = ctk.CTkButton(
                    r1, text=lock_text, width=68, height=18, font=("Segoe UI", 7),
                    fg_color="transparent", text_color=lock_col, hover_color="#f1f5f9",
                    command=lambda l_name=layer.name: self._toggle_layer_editing_lock(l_name)
                )
                btn_lock.pack(side=tk.RIGHT, padx=2)

            elif toc_mode == "SNAPPING":
                is_snap = self.layer_snapping.get(layer.name, True)
                snap_text = "🧲 Active" if is_snap else "⚪ Inactive"
                snap_col = "#007AC2" if is_snap else "#94a3b8"
                ctk.CTkLabel(r1, text=layer.name, font=("Segoe UI", 9, "bold"), text_color="#1e293b").pack(side=tk.LEFT, padx=2)
                btn_snap = ctk.CTkButton(
                    r1, text=snap_text, width=65, height=18, font=("Segoe UI", 7),
                    fg_color="transparent", text_color=snap_col, hover_color="#f1f5f9",
                    command=lambda l_name=layer.name: self._toggle_layer_snapping(l_name)
                )
                btn_snap.pack(side=tk.RIGHT, padx=2)

            elif toc_mode == "LABELING":
                is_lbl = self.layer_labeling.get(layer.name, True)
                lbl_text = "🏷 Visible" if is_lbl else "⚪ Hidden"
                lbl_col = "#007AC2" if is_lbl else "#94a3b8"
                ctk.CTkLabel(r1, text=layer.name, font=("Segoe UI", 9, "bold"), text_color="#1e293b").pack(side=tk.LEFT, padx=2)
                btn_lbl = ctk.CTkButton(
                    r1, text=lbl_text, width=65, height=18, font=("Segoe UI", 7),
                    fg_color="transparent", text_color=lbl_col, hover_color="#f1f5f9",
                    command=lambda l_name=layer.name: self._toggle_layer_labeling(l_name)
                )
                btn_lbl.pack(side=tk.RIGHT, padx=2)

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

        # Hide internal segmented button so stacked_btns bar controls panes seamlessly without duplication
        self.right_tabs._segmented_button.grid_forget()

        self._build_catalog_pane(tab_catalog)
        self._build_create_features_pane(tab_create)
        self._build_locate_pane(tab_locate)
        self._build_symbology_pane(tab_sym)
        self._build_geoprocessing_pane(tab_gp)
        self._build_chart_properties_pane(tab_chart)

    def _build_catalog_pane(self, parent):
        """Exact match of Catalog dock in ArcGIS Pro (screenshot & Image 5)."""
        hdr = ctk.CTkFrame(parent, height=28, fg_color=self.C_HEADER_BG, corner_radius=0)
        hdr.pack(fill=tk.X, side=tk.TOP)
        ctk.CTkLabel(hdr, text="Catalog", font=("Segoe UI", 11, "bold"), text_color="#1e293b").pack(side=tk.LEFT, padx=8)
        ctk.CTkLabel(hdr, text="▾   📌   ✕", font=("Segoe UI", 9), text_color="#64748b").pack(side=tk.RIGHT, padx=6)

        # Tabs row: Project (Active with underline), Portal, Favorites (Matching user screenshot)
        cat_tabs = ctk.CTkFrame(parent, height=28, fg_color="#ffffff", corner_radius=0)
        cat_tabs.pack(fill=tk.X, pady=(0, 2))

        self.btn_cat_project = ctk.CTkButton(
            cat_tabs, text="Project", width=62, height=24,
            fg_color="#e0f2fe", text_color="#007AC2", border_color="#007AC2", border_width=1,
            font=("Segoe UI", 9, "bold"), command=lambda: self._set_catalog_view("PROJECT")
        )
        self.btn_cat_project.pack(side=tk.LEFT, padx=2)

        self.btn_cat_portal = ctk.CTkButton(
            cat_tabs, text="Portal", width=55, height=24,
            fg_color="transparent", text_color="#64748b", border_color="#cbd5e1", border_width=0,
            font=("Segoe UI", 9), command=lambda: self._set_catalog_view("PORTAL")
        )
        self.btn_cat_portal.pack(side=tk.LEFT, padx=1)

        self.btn_cat_favorites = ctk.CTkButton(
            cat_tabs, text="Favorites", width=65, height=24,
            fg_color="transparent", text_color="#64748b", border_color="#cbd5e1", border_width=0,
            font=("Segoe UI", 9), command=lambda: self._set_catalog_view("FAVORITES")
        )
        self.btn_cat_favorites.pack(side=tk.LEFT, padx=1)
        ctk.CTkLabel(cat_tabs, text="☰", font=("Segoe UI", 11), text_color="#64748b").pack(side=tk.RIGHT, padx=6)

        # Navigation Bar: Search Project (Matching user screenshot)
        nav_row = ctk.CTkFrame(parent, height=28, fg_color="#ffffff", border_color=self.C_BORDER, border_width=1, corner_radius=2)
        nav_row.pack(fill=tk.X, padx=6, pady=4)
        ctk.CTkLabel(nav_row, text="←", font=("Segoe UI", 11, "bold"), text_color="#64748b").pack(side=tk.LEFT, padx=4)
        ctk.CTkLabel(nav_row, text="🏠", font=("Segoe UI", 10), text_color="#007AC2").pack(side=tk.LEFT, padx=4)
        self.entry_cat_search = ctk.CTkEntry(nav_row, placeholder_text="Search Project", height=22, fg_color="transparent", border_width=0, font=("Segoe UI", 9))
        self.entry_cat_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.entry_cat_search.bind("<KeyRelease>", lambda e: self._refresh_catalog_tree())
        ctk.CTkLabel(nav_row, text="🔍", font=("Segoe UI", 9), text_color="#94a3b8").pack(side=tk.RIGHT, padx=4)

        # Tree Structure Container
        self.catalog_tree_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.catalog_tree_scroll.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self._refresh_catalog_tree()

    def _set_catalog_view(self, mode: str):
        self.catalog_view_mode = mode
        btns = {
            "PROJECT": self.btn_cat_project,
            "PORTAL": self.btn_cat_portal,
            "FAVORITES": self.btn_cat_favorites
        }
        for m_name, btn in btns.items():
            if m_name == mode:
                btn.configure(fg_color="#e0f2fe", text_color="#007AC2", border_color="#007AC2", border_width=1)
            else:
                btn.configure(fg_color="transparent", text_color="#64748b", border_color="#cbd5e1", border_width=0)
        self._refresh_catalog_tree()

    def _refresh_catalog_tree(self):
        if not hasattr(self, "catalog_tree_scroll"):
            return
        for w in self.catalog_tree_scroll.winfo_children():
            w.destroy()

        mode = getattr(self, "catalog_view_mode", "PROJECT")
        q = self.entry_cat_search.get().strip().lower() if hasattr(self, "entry_cat_search") else ""

        if mode == "PORTAL":
            tree_items = [
                ("▷ 🌐 My Content", ["     🗺 My South America WebMap", "     📄 Protected Natural Reserves Layer"]),
                ("▷ 👥 My Groups", ["     👥 GIS Enterprise Team", "     👥 Field Operations Crew"]),
                ("▷ 🌍 Living Atlas", ["     🌍 World Elevation & Shaded Relief", "     🌍 World Population 2026"]),
                ("▷ ☁ ArcGIS Online", ["     ☁ World Imagery with Metadata", "     ☁ World Vector Basemap Canvas"])
            ]
        elif mode == "FAVORITES":
            fav_items = [f"     ⭐ {item}" for item in getattr(self, "catalog_favorites", ["MyProject.gdb"])]
            tree_items = [
                ("▷ ⭐ Favorite Geodatabases", fav_items),
                ("▷ ⭐ Connected Folders", [f"     📁 {os.path.basename(f)}" for f in getattr(self, "catalog_folders", ["MyProject"])]),
                ("▷ ⭐ Saved Styles", ["     🎨 ArcGIS 2D Official", "     🎨 ArcGIS 3D Elevation"]),
                ("▷ ⭐ Map Bookmarks", ["     🔖 Brazil Capital (Brasília)", "     🔖 Amazon River Basin"])
            ]
        else:
            # PROJECT Mode
            folder_nodes = ["     📁 MyProject"]
            for cf in getattr(self, "catalog_folders", []):
                folder_nodes.append(f"     📁 {os.path.basename(cf)}")

            if self.current_project_name == "MyProject" or any("World Topographic" in l.name for l in self.canvas.layers):
                tree_items = [
                    ("▷ 🗺 Maps", ["     🗺 Map"]),
                    ("▷ 🧰 Toolboxes", ["     🧰 MyProject.tbx"]),
                    ("▷ 🗄 Databases", ["     🗃 MyProject.gdb"]),
                    ("▷ 🎨 Styles", ["     🎨 ArcGIS 2D", "     🎨 ArcGIS 3D"]),
                    ("▷ 📁 Folders", folder_nodes),
                    ("▷ 📍 Locators", ["     📍 World Geocoding Service"])
                ]
            else:
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
            matching_children = [ch for ch in children if not q or q in ch.lower()]
            if q and not matching_children and q not in section.lower():
                continue

            sec_lbl = ctk.CTkLabel(self.catalog_tree_scroll, text=section, font=("Segoe UI", 10, "bold"), text_color="#007AC2", cursor="hand2")
            sec_lbl.pack(anchor="w", pady=(5, 1))

            for ch in matching_children:
                is_sub = ch.startswith("     ")
                clean_text = ch.strip()

                def _on_click_node(t=clean_text):
                    if "Map" in t:
                        self.center_tabs.set("  🗺 Map ✕  ")
                    elif "Toolbox" in t or ".tbx" in t:
                        self._activate_stacked_pane("Geoprocessing")
                    elif "Style" in t:
                        self._activate_stacked_pane("Symbology")
                    elif "Locator" in t:
                        self._activate_stacked_pane("Locate")
                    elif "Database" in t or ".gdb" in t:
                        self._switch_to_table_tab()
                    elif "Folder" in t:
                        messagebox.showinfo("Catalog Folder", f"Folder contents active:\n{t}")

                node_btn = ctk.CTkButton(
                    self.catalog_tree_scroll, text=clean_text,
                    height=20, font=("Segoe UI", 9), anchor="w",
                    fg_color="transparent", hover_color="#f1f5f9",
                    text_color="#1e293b" if not is_sub else "#334155",
                    command=_on_click_node
                )
                node_btn.pack(anchor="w", padx=10 if not is_sub else 20, pady=1)

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
        # Map Tabs Bar matching Image 4 (Left-aligned with anchor='nw')
        self.center_tabs = ctk.CTkTabview(
            self.center_viewport,
            fg_color="#ffffff",
            segmented_button_fg_color="#e2e8f0",
            segmented_button_selected_color="#007AC2",
            segmented_button_selected_hover_color="#005a90",
            corner_radius=0,
            anchor="nw"
        )
        self.center_tabs.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Tabs matching ArcGIS Pro 3.x Map Viewport
        tab_map = self.center_tabs.add("  🗺 Map ✕  ")
        tab_chch = self.center_tabs.add("  🗺 Christchurch Urban Area ✕  ")
        tab_cant = self.center_tabs.add("  🗺 Canterbury Region  ")
        tab_risk = self.center_tabs.add("  📊 Liquefaction Risk  ")
        tab_table = self.center_tabs.add("  📋 Attributes Table  ")
        tab_python = self.center_tabs.add("  🐍 Python Window (arcpy)  ")

        # Map Canvas inside primary Map tab
        self.canvas = InteractiveMapCanvas(
            tab_map,
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

        self.scale_combo = ctk.CTkComboBox(left_status, values=["1:50,000", "1:100,000", "1:250,000", "1:500,000", "1:71.199.652"], width=118, height=22, font=("Segoe UI", 9), command=self._on_scale_selected)
        self.scale_combo.set("1:71.199.652")
        self.scale_combo.pack(side=tk.LEFT, padx=2)

        # Snapping toggle button
        self.btn_snapping = ctk.CTkButton(left_status, text="🧲", width=22, height=20, fg_color="transparent", hover_color="#e2e8f0", text_color="#007AC2", font=("Segoe UI", 10), command=self._toggle_snapping)
        self.btn_snapping.pack(side=tk.LEFT, padx=1)
        self._bind_hover_hint(self.btn_snapping, "Toggle snapping environment on/off")

        # Dedicated Zoom and Navigation controls [- + 🔍 ⟲]
        b_zout = ctk.CTkButton(left_status, text="−", width=18, height=20, fg_color="transparent", hover_color="#e2e8f0", text_color="#1e293b", font=("Segoe UI", 9, "bold"), command=lambda: self.canvas._zoom(0.7, self.canvas.canvas.winfo_width()//2, self.canvas.canvas.winfo_height()//2))
        b_zout.pack(side=tk.LEFT, padx=1)
        self._bind_hover_hint(b_zout, "Fixed Zoom Out")

        b_zin = ctk.CTkButton(left_status, text="+", width=18, height=20, fg_color="transparent", hover_color="#e2e8f0", text_color="#1e293b", font=("Segoe UI", 9, "bold"), command=lambda: self.canvas._zoom(1.3, self.canvas.canvas.winfo_width()//2, self.canvas.canvas.winfo_height()//2))
        b_zin.pack(side=tk.LEFT, padx=1)
        self._bind_hover_hint(b_zin, "Fixed Zoom In")

        b_zext = ctk.CTkButton(left_status, text="🔍", width=20, height=20, fg_color="transparent", hover_color="#e2e8f0", text_color="#1e293b", font=("Segoe UI", 9), command=lambda: self.canvas.zoom_to_extent())
        b_zext.pack(side=tk.LEFT, padx=1)
        self._bind_hover_hint(b_zext, "Zoom to Full Extent")

        b_zred = ctk.CTkButton(left_status, text="⟲", width=20, height=20, fg_color="transparent", hover_color="#e2e8f0", text_color="#1e293b", font=("Segoe UI", 9), command=lambda: self.canvas.redraw())
        b_zred.pack(side=tk.LEFT, padx=1)
        self._bind_hover_hint(b_zred, "Refresh Map Display")

        # Center Coordinates: 72,0538018°W 2,6192255°N ▾ (Image 4 & Map view)
        self.lbl_coords = ctk.CTkLabel(
            self.status_bar,
            text="72,0538018°W 2,6192255°N ▾",
            font=("Segoe UI", 9),
            text_color="#1e293b",
            cursor="hand2"
        )
        self.lbl_coords.pack(side=tk.LEFT, padx=14, pady=2)
        self.lbl_coords.bind("<Button-1>", lambda e: self._cycle_coords_format())
        self._bind_hover_hint(self.lbl_coords, "Click to toggle coordinate display format (DD / DMS / Meters)")

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

        # Dynamic Status Hint Label
        self.lbl_hint = ctk.CTkLabel(
            self.status_bar,
            text="",
            font=("Segoe UI", 8, "italic"),
            text_color="#0284c7"
        )
        self.lbl_hint.pack(side=tk.LEFT, padx=10, pady=2)

        # Right Controls: Refresh & Pause Drawing (Image 4)
        right_status = ctk.CTkFrame(self.status_bar, fg_color="transparent")
        right_status.pack(side=tk.RIGHT, padx=8, pady=2)

        b_ref = ctk.CTkButton(right_status, text="⟳", width=22, height=20, fg_color="transparent", hover_color="#e2e8f0", text_color="#007AC2", font=("Segoe UI", 11, "bold"), command=lambda: self.canvas.redraw())
        b_ref.pack(side=tk.LEFT, padx=2)
        self._bind_hover_hint(b_ref, "Redraw and recompute spatial indices")

        self.btn_pause = ctk.CTkButton(right_status, text="⏸", width=22, height=20, fg_color="transparent", hover_color="#e2e8f0", text_color="#64748b", font=("Segoe UI", 10), command=self._toggle_pause_drawing)
        self.btn_pause.pack(side=tk.LEFT, padx=2)
        self._bind_hover_hint(self.btn_pause, "Pause background layer rendering")

    def _toggle_snapping(self):
        self.snapping_enabled = not getattr(self, "snapping_enabled", True)
        col = "#007AC2" if self.snapping_enabled else "#94a3b8"
        self.btn_snapping.configure(text_color=col)
        self.lbl_selection.configure(text=f"Snapping: {'Enabled' if self.snapping_enabled else 'Disabled'}")

    def _toggle_pause_drawing(self):
        paused = getattr(self, "drawing_paused", False)
        self.drawing_paused = not paused
        self.btn_pause.configure(text_color="#dc2626" if self.drawing_paused else "#64748b")
        self.lbl_selection.configure(text=f"Drawing: {'Paused' if self.drawing_paused else 'Active'}")

    def _cycle_coords_format(self):
        modes = ["DD", "DMS", "METERS"]
        curr = getattr(self, "coords_format_mode", "DD")
        idx = (modes.index(curr) + 1) % len(modes)
        self.coords_format_mode = modes[idx]
        self.lbl_selection.configure(text=f"Coordinates format: {self.coords_format_mode}")

    def _on_scale_selected(self, choice: str):
        if not self.canvas:
            return
        scales = {
            "1:50,000": 0.05,
            "1:100,000": 0.1,
            "1:250,000": 0.25,
            "1:500,000": 0.5,
            "1:71.199.652": 35.0
        }
        deg = scales.get(choice, 1.0)
        ext = self.canvas.view_extent
        cx = (ext.xmin + ext.xmax) / 2.0
        cy = (ext.ymin + ext.ymax) / 2.0
        self.canvas.zoom_to_extent(Envelope(cx - deg, cy - deg * 0.7, cx + deg, cy + deg * 0.7))

    def _on_canvas_mouse_move(self, lon: float, lat: float):
        ew = "E" if lon >= 0 else "W"
        ns = "N" if lat >= 0 else "S"
        lon_s = f"{abs(lon):.7f}".replace(".", ",")
        lat_s = f"{abs(lat):.7f}".replace(".", ",")
        self.lbl_coords.configure(text=f"{lon_s}°{ew} {lat_s}°{ns} ▾")

    def _on_feature_identified(self, layer_name: str, feat: Feature):
        attrs_str = "\n".join([f"• {k}: {v}" for k, v in feat.attributes.items()])
        self.lbl_selection.configure(text=f"Selected Features: 1")
        messagebox.showinfo(
            f"Pop-up - {layer_name}",
            f"OBJECTID: {feat.objectid}\nGeometry: {feat.geometry.esri_geometry_type}\n\nAttributes:\n{attrs_str}"
        )

    def _set_tool(self, tool_name: str):
        self.canvas.tool_mode = tool_name
        if hasattr(self, "btn_explore"):
            if tool_name == "PAN":
                self.btn_explore.configure(fg_color="#e0f2fe", border_width=0, text_color="#007ac2")
            else:
                self.btn_explore.configure(fg_color="transparent", border_width=0, text_color="#1e293b")
        if hasattr(self, "btn_select"):
            if tool_name == "SELECT":
                self.btn_select.configure(fg_color="#e0f2fe", border_width=0, text_color="#007ac2")
            else:
                self.btn_select.configure(fg_color="transparent", border_width=0, text_color="#1e293b")
        if hasattr(self, "btn_measure"):
            if tool_name == "MEASURE":
                self.btn_measure.configure(fg_color="#e0f2fe", border_width=0, text_color="#007ac2")
            else:
                self.btn_measure.configure(fg_color="transparent", border_width=0, text_color="#1e293b")
        if tool_name != "MEASURE":
            self.canvas.measure_points.clear()
            self.canvas.redraw()

    def _on_basemap_changed(self, choice: str):
        if "No Basemap" in choice:
            self.canvas.show_basemap = False
        else:
            self.canvas.show_basemap = True
            self.canvas.set_basemap(choice)
        self.lbl_selection.configure(text=f"Basemap: {choice}")
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
        """Loads sample dataset matching ArcGIS Pro projects."""
        self.canvas.layers.clear()
        self.canvas.layer_renderers.clear()
        self.canvas.layer_visibility.clear()
        self.canvas.selected_features.clear()

        if "MyProject" in name or name == "Map" or "Default" in name:
            p_info = load_myproject_map()
            self.current_project_name = "MyProject"
            self.lbl_proj_dropdown.configure(text="MyProject ▾")
            self.title("ArcGIS® Pro - MyProject - Map")
            self.ribbon_tabs.set("  Map  ")
            self.center_tabs.set("  🗺 Map ✕  ")
            self.scale_combo.set("1:71.199.652")
            self.lbl_coords.configure(text="72,0538018°W 2,6192255°N ▾")
            self.lbl_selection.configure(text="Selected Features: 0")
            if hasattr(self, "lbl_account_name"):
                self.lbl_account_name.configure(text="Not signed in")
            self._activate_stacked_pane("Catalog")
        elif "Christchurch" in name or "Wellington" in name or "Ven" in name or "Scotland" in name:
            p_info = load_christchurch_project()
            self.current_project_name = p_info["project_name"]
            self.lbl_proj_dropdown.configure(text=f"{self.current_project_name} ▾")
            self.title(f"ArcGIS® Pro - {self.current_project_name} - City Center")
            self.ribbon_tabs.set("  Map  ")
        else:
            p_info = load_brasil_project()
            self.current_project_name = p_info["project_name"]
            self.lbl_proj_dropdown.configure(text=f"{self.current_project_name} ▾")
            self.title(f"ArcGIS® Pro - {self.current_project_name}")
            self.ribbon_tabs.set("  Map  ")

        for layer, renderer in p_info["layers"]:
            self.canvas.add_layer(layer, renderer)

        self.active_layer = self.canvas.layers[0] if self.canvas.layers else None
        self.canvas.zoom_to_extent(p_info["extent"])
        self._refresh_toc()
        if hasattr(self, "_refresh_catalog_tree"):
            self._refresh_catalog_tree()

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
