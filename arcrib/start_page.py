"""
arcrib.start_page - ArcGIS Pro Start Screen & Backstage Landing Interface
Exact reproduction of:
- Image 1: ArcGIS Pro Home Page (New Project templates, Recent Projects cards, Learning Resources box)
- Image 2: ArcGIS Pro Learning Resources Page (Quick-start tutorials, Tutorial Series, ArcMap migration)
- Settings tab with Light/Dark appearance and ArcGIS Online portal settings
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from typing import Callable, Optional
from PIL import Image, ImageDraw, ImageTk


class ArcGISProStartPage(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        on_open_project: Callable[[str], None],
        on_new_project: Callable[[], None],
        on_save_project: Optional[Callable[[], None]] = None,
        on_save_project_as: Optional[Callable[[], None]] = None,
        on_exit: Optional[Callable[[], None]] = None,
        get_project_info: Optional[Callable[[], dict]] = None
    ):
        super().__init__(parent, fg_color="#f3f4f6", corner_radius=0)
        self.on_open_project = on_open_project
        self.on_new_project = on_new_project
        self.on_save_project = on_save_project
        self.on_save_project_as = on_save_project_as
        self.on_exit = on_exit
        self.get_project_info = get_project_info

        self._pil_thumbnails = {}
        self._generate_synthetic_thumbnails()

        # Build Top Bar
        self._build_top_bar()

        # Build Main Body with Left Navigation
        self.body_container = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.body_container.pack(fill=tk.BOTH, expand=True)

        self._build_left_nav()

        # Right Content Area (switches between Home, Learning Resources, Settings)
        self.content_area = ctk.CTkFrame(self.body_container, fg_color="#f8fafc", corner_radius=0)
        self.content_area.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Current view state
        self.current_view = "HOME"

        # Show Home view by default (Image 1)
        self._show_home_view()

    def show_view(self, view_name: str):
        """Programmatically switch view: 'HOME', 'LEARNING', 'SETTINGS'."""
        v = view_name.upper()
        if "LEARN" in v:
            self._show_learning_view()
        elif "SETTING" in v:
            self._show_settings_view()
        else:
            self._show_home_view()

    def _generate_synthetic_thumbnails(self):
        """Generates realistic synthetic preview thumbnails matching Image 1 & Image 2."""
        # 1. Wellington Buildings (Cityscape 3D)
        im_wellington = Image.new("RGB", (220, 110), color="#64748b")
        d = ImageDraw.Draw(im_wellington)
        d.rectangle([(0, 0), (220, 45)], fill="#93c5fd")  # Sky / Sea
        d.polygon([(0, 45), (140, 40), (220, 55), (220, 110), (0, 110)], fill="#334155")  # Land
        # Buildings
        for x in range(25, 200, 24):
            h = 25 + (x % 35)
            d.rectangle([(x, 90 - h), (x + 18, 95)], fill="#1e293b", outline="#cbd5e1")
        self._pil_thumbnails["wellington"] = ctk.CTkImage(light_image=im_wellington, size=(220, 110))

        # 2. Scotland Medical Facilities (Scotland shape simulation)
        im_scotland = Image.new("RGB", (220, 110), color="#3b82f6")  # Blue sea
        d = ImageDraw.Draw(im_scotland)
        d.polygon([
            (70, 15), (130, 20), (150, 45), (135, 75), (145, 95), (90, 105), (65, 80), (80, 50)
        ], fill="#15803d")  # Green land
        d.ellipse([(110, 60), (120, 70)], fill="#ef4444", outline="#ffffff")
        d.ellipse([(95, 75), (105, 85)], fill="#ef4444", outline="#ffffff")
        self._pil_thumbnails["scotland"] = ctk.CTkImage(light_image=im_scotland, size=(220, 110))

        # 3. Ven (Harbor & boats)
        im_ven = Image.new("RGB", (220, 110), color="#0284c7")
        d = ImageDraw.Draw(im_ven)
        d.rectangle([(0, 0), (220, 50)], fill="#e2e8f0")  # Sky
        d.polygon([(0, 50), (160, 45), (220, 70), (220, 110), (0, 110)], fill="#475569")  # Harbor
        # Houses
        for x in range(30, 180, 32):
            d.rectangle([(x, 50), (x + 22, 75)], fill="#dc2626" if x % 2 == 0 else "#f59e0b", outline="#1e293b")
            d.polygon([(x, 50), (x + 11, 40), (x + 22, 50)], fill="#1e293b")
        self._pil_thumbnails["ven"] = ctk.CTkImage(light_image=im_ven, size=(220, 110))

        # 4. Christchurch Urban Area
        im_chch = Image.new("RGB", (220, 110), color="#fef08a")
        d = ImageDraw.Draw(im_chch)
        d.rectangle([(160, 0), (220, 110)], fill="#93c5fd")  # Ocean
        d.polygon([(50, 30), (140, 25), (150, 80), (70, 85)], fill="#fed7aa")  # Orange hazard
        d.polygon([(80, 45), (125, 40), (130, 65), (90, 70)], fill="#fca5a5")  # Red hazard
        d.line([(40, 50), (160, 52)], fill="#0284c7", width=3)  # River
        self._pil_thumbnails["christchurch"] = ctk.CTkImage(light_image=im_chch, size=(220, 110))

    # =========================================================================
    # TOP HEADER BAR (Logo, User Avatar, Sign out, Portal Link)
    # =========================================================================
    def _build_top_bar(self):
        top_bar = ctk.CTkFrame(self, height=52, fg_color="#ffffff", corner_radius=0)
        top_bar.pack(fill=tk.X, side=tk.TOP)

        # Left Logo
        logo_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        logo_frame.pack(side=tk.LEFT, padx=18, pady=8)

        lbl_logo_icon = ctk.CTkLabel(logo_frame, text="🌎", font=("Segoe UI", 20), text_color="#007AC2")
        lbl_logo_icon.pack(side=tk.LEFT, padx=(0, 6))

        lbl_logo_text = ctk.CTkLabel(logo_frame, text="ArcGIS® Pro", font=("Segoe UI", 16, "bold"), text_color="#1e293b")
        lbl_logo_text.pack(side=tk.LEFT)

        # Right User & Account Area
        user_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        user_frame.pack(side=tk.RIGHT, padx=16, pady=6)

        # Circle Avatar 'YN'
        avatar_lbl = ctk.CTkLabel(
            user_frame, text="YN", width=28, height=28,
            fg_color="#a3e635", text_color="#14532d",
            font=("Segoe UI", 10, "bold"), corner_radius=14
        )
        avatar_lbl.pack(side=tk.LEFT, padx=(0, 8))

        user_info = ctk.CTkFrame(user_frame, fg_color="transparent")
        user_info.pack(side=tk.LEFT)

        name_lbl = ctk.CTkLabel(user_info, text="Your Name • ArcGIS Pro Tutorials", font=("Segoe UI", 10, "bold"), text_color="#1e293b")
        name_lbl.pack(anchor="w")

        link_row = ctk.CTkFrame(user_info, fg_color="transparent")
        link_row.pack(anchor="w")
        ctk.CTkLabel(link_row, text="Sign out", font=("Segoe UI", 9, "underline"), text_color="#007AC2", cursor="hand2").pack(side=tk.LEFT, padx=(0, 6))
        ctk.CTkLabel(link_row, text="https://www.arcgis.com/", font=("Segoe UI", 9), text_color="#64748b").pack(side=tk.LEFT)

        # Help & Window Controls
        ctrls = ctk.CTkFrame(top_bar, fg_color="transparent")
        ctrls.pack(side=tk.RIGHT, padx=12)
        ctk.CTkLabel(ctrls, text="?   ─   □   ✕", font=("Segoe UI", 11), text_color="#94a3b8").pack(side=tk.RIGHT, padx=4)

    # =========================================================================
    # LEFT NAVIGATION MENU (Home, Learning Resources, Settings)
    # =========================================================================
    def _build_left_nav(self):
        self.nav_frame = ctk.CTkFrame(self.body_container, width=190, fg_color="#f1f5f9", corner_radius=0)
        self.nav_frame.pack(fill=tk.Y, side=tk.LEFT)

        self.btn_nav_home = ctk.CTkButton(
            self.nav_frame, text="  🏠  Home", anchor="w",
            height=38, font=("Segoe UI", 11, "bold"),
            fg_color="#e1f0fa", hover_color="#d0e7f7", text_color="#007AC2",
            corner_radius=4, command=self._show_home_view
        )
        self.btn_nav_home.pack(fill=tk.X, padx=10, pady=(16, 4))

        self.btn_nav_learning = ctk.CTkButton(
            self.nav_frame, text="  📖  Learning Resources", anchor="w",
            height=38, font=("Segoe UI", 11),
            fg_color="transparent", hover_color="#e2e8f0", text_color="#334155",
            corner_radius=4, command=self._show_learning_view
        )
        self.btn_nav_learning.pack(fill=tk.X, padx=10, pady=4)

        self.btn_nav_settings = ctk.CTkButton(
            self.nav_frame, text="  ⚙  Settings", anchor="w",
            height=38, font=("Segoe UI", 11),
            fg_color="transparent", hover_color="#e2e8f0", text_color="#334155",
            corner_radius=4, command=self._show_settings_view
        )
        self.btn_nav_settings.pack(fill=tk.X, padx=10, pady=4)

    def _update_nav_highlight(self, active_btn):
        for btn in [self.btn_nav_home, self.btn_nav_learning, self.btn_nav_settings]:
            if btn == active_btn:
                btn.configure(fg_color="#e1f0fa", text_color="#007AC2", font=("Segoe UI", 11, "bold"))
            else:
                btn.configure(fg_color="transparent", text_color="#334155", font=("Segoe UI", 11))

    # =========================================================================
    # VIEW 1: HOME PAGE (Exact match of Image 1)
    # =========================================================================
    def _show_home_view(self):
        self.current_view = "HOME"
        self._update_nav_highlight(self.btn_nav_home)
        for w in self.content_area.winfo_children():
            w.destroy()

        scroll_frame = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent")
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)

        # -------------------------------------------------------------
        # 1. NEW PROJECT SECTION (Image 1, Point 1)
        # -------------------------------------------------------------
        ctk.CTkLabel(scroll_frame, text="New Project", font=("Segoe UI", 13, "bold"), text_color="#1e293b").pack(anchor="w", pady=(0, 8))

        template_container = ctk.CTkFrame(scroll_frame, fg_color="#ffffff", border_color="#e2e8f0", border_width=1, corner_radius=6)
        template_container.pack(fill=tk.X, pady=(0, 20))

        t_row = ctk.CTkFrame(template_container, fg_color="transparent")
        t_row.pack(fill=tk.X, padx=16, pady=14)

        templates = [
            ("🗺", "Map", lambda: self.on_open_project("MyProject")),
            ("📁", "Catalog", self.on_new_project),
            ("🌐", "Global Scene", lambda: self.on_open_project("Brasil Geografico")),
            ("🏙", "Local Scene", lambda: self.on_open_project("Christchurch Transportation")),
            ("↗", "Start without a template", self.on_new_project)
        ]

        for icon, title, cmd in templates:
            col = ctk.CTkFrame(t_row, fg_color="transparent")
            col.pack(side=tk.LEFT, expand=True, padx=8)

            btn_box = ctk.CTkButton(
                col, text=icon, width=64, height=54,
                font=("Segoe UI", 24), fg_color="#f8fafc", hover_color="#e1f0fa",
                border_color="#cbd5e1", border_width=1, corner_radius=4,
                command=cmd
            )
            btn_box.pack(pady=(0, 4))
            ctk.CTkLabel(col, text=title, font=("Segoe UI", 10), text_color="#334155").pack()

        # -------------------------------------------------------------
        # 2. MAIN SPLIT: RECENT PROJECTS (Left) & RESOURCES (Right)
        # -------------------------------------------------------------
        two_col_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        two_col_frame.pack(fill=tk.BOTH, expand=True)

        left_col = ctk.CTkFrame(two_col_frame, fg_color="transparent")
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 16))

        right_col = ctk.CTkFrame(two_col_frame, width=280, fg_color="transparent")
        right_col.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Recent Projects Header & Filter (Image 1, Point 2 & 3) ---
        rp_bar = ctk.CTkFrame(left_col, fg_color="transparent")
        rp_bar.pack(fill=tk.X, pady=(0, 8))

        ctk.CTkLabel(rp_bar, text="Recent Projects", font=("Segoe UI", 13, "bold"), text_color="#1e293b").pack(side=tk.LEFT, padx=(0, 12))

        search_entry = ctk.CTkEntry(rp_bar, placeholder_text="Find", width=180, height=26, font=("Segoe UI", 10))
        search_entry.pack(side=tk.LEFT, padx=4)

        ctk.CTkButton(rp_bar, text="⇅", width=26, height=26, fg_color="#ffffff", hover_color="#e2e8f0", text_color="#475569", border_color="#cbd5e1", border_width=1).pack(side=tk.LEFT, padx=2)

        # Open another project button
        def _open_another():
            f = filedialog.askopenfilename(filetypes=[("ArcGIS Pro Project", "*.aprx"), ("JSON", "*.json")])
            if f:
                self.on_open_project(f)

        btn_open_another = ctk.CTkButton(
            rp_bar, text="📁 Open another project", width=160, height=26,
            fg_color="transparent", hover_color="#e2e8f0", text_color="#334155",
            font=("Segoe UI", 10), command=_open_another
        )
        btn_open_another.pack(side=tk.RIGHT, padx=4)

        btn_grid_view = ctk.CTkButton(rp_bar, text="▦", width=28, height=26, fg_color="#e1f0fa", text_color="#007AC2", border_color="#007AC2", border_width=1)
        btn_grid_view.pack(side=tk.RIGHT, padx=2)
        btn_list_view = ctk.CTkButton(rp_bar, text="☰", width=28, height=26, fg_color="#ffffff", text_color="#64748b", border_color="#cbd5e1", border_width=1)
        btn_list_view.pack(side=tk.RIGHT, padx=2)

        # --- Recent Projects Cards Grid (Image 1, Point 2) ---
        cards_grid = ctk.CTkFrame(left_col, fg_color="transparent")
        cards_grid.pack(fill=tk.X, pady=4)

        project_cards = [
            ("Wellington Buildings", "11/18/2022 11:23 AM", "C:/Users/timo/Documents/ArcGIS/Projects/Wellington...", "wellington", lambda: self.on_open_project("Christchurch Transportation")),
            ("Scotland Medical Facilities", "11/18/2022 11:21 AM", "C:/Users/timo/Documents/ArcGIS/Projects/Scotland...", "scotland", lambda: self.on_open_project("Christchurch Transportation")),
            ("Ven", "11/18/2022 11:06 AM", "C:/Users/timo/Documents/ArcGIS/Projects/Ven/Ven.aprx", "ven", lambda: self.on_open_project("Christchurch Transportation")),
            ("Christchurch Transportation", "11/18/2022 10:45 AM", "C:/Users/timo/Documents/ArcGIS/Projects/Christchurch...", "christchurch", lambda: self.on_open_project("Christchurch Transportation"))
        ]

        for p_title, p_mod, p_path, thumb_key, p_cmd in project_cards:
            card = ctk.CTkFrame(cards_grid, fg_color="#ffffff", border_color="#e2e8f0", border_width=1, corner_radius=6)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=4)

            # Thumbnail Image
            thumb_lbl = ctk.CTkLabel(card, text="", image=self._pil_thumbnails[thumb_key], cursor="hand2")
            thumb_lbl.pack(fill=tk.X, padx=6, pady=(6, 4))
            thumb_lbl.bind("<Button-1>", lambda e, c=p_cmd: c())

            # Text block
            title_btn = ctk.CTkButton(
                card, text=p_title, anchor="w",
                font=("Segoe UI", 11, "bold"), text_color="#007AC2",
                fg_color="transparent", hover_color="#f1f5f9", height=24,
                command=p_cmd
            )
            title_btn.pack(fill=tk.X, padx=6, pady=(2, 1))

            ctk.CTkLabel(card, text=f"Modified: {p_mod}", font=("Segoe UI", 9), text_color="#64748b").pack(anchor="w", padx=10)
            ctk.CTkLabel(card, text=f"Path: {p_path}", font=("Segoe UI", 8), text_color="#94a3b8").pack(anchor="w", padx=10, pady=(0, 8))

        # --- Right Column: Learning Resources & Templates (Image 1, Point 4) ---
        box_lr = ctk.CTkFrame(right_col, fg_color="#ffffff", border_color="#e2e8f0", border_width=1, corner_radius=6)
        box_lr.pack(fill=tk.X, pady=(0, 16))

        ctk.CTkLabel(box_lr, text="📖", font=("Segoe UI", 32), text_color="#007AC2").pack(pady=(16, 4))
        ctk.CTkButton(
            box_lr, text="Learning Resources", font=("Segoe UI", 12, "bold"),
            fg_color="transparent", hover_color="#e1f0fa", text_color="#007AC2",
            command=self._show_learning_view
        ).pack(pady=(0, 12))

        # Recent Templates Header
        ctk.CTkLabel(right_col, text="Recent Templates", font=("Segoe UI", 11, "bold"), text_color="#1e293b").pack(anchor="w", pady=(4, 2))
        btn_tmpl = ctk.CTkButton(right_col, text="📂 Start with another template", font=("Segoe UI", 9), fg_color="transparent", text_color="#007AC2", anchor="w")
        btn_tmpl.pack(anchor="w", pady=(0, 6))

        # Template Item
        tmpl_card = ctk.CTkFrame(right_col, fg_color="#ffffff", border_color="#e2e8f0", border_width=1, corner_radius=4)
        tmpl_card.pack(fill=tk.X, pady=4)
        ctk.CTkLabel(tmpl_card, text="💼  Wellington_Template", font=("Segoe UI", 10, "bold"), text_color="#334155").pack(anchor="w", padx=8, pady=(6, 1))
        ctk.CTkLabel(tmpl_card, text="C:/Users/timo/Documents/ArcGIS/OnlinePr...", font=("Segoe UI", 8), text_color="#94a3b8").pack(anchor="w", padx=8, pady=(0, 6))

        ctk.CTkLabel(right_col, text="Learn more about creating project templates", font=("Segoe UI", 9, "underline"), text_color="#007AC2", cursor="hand2").pack(anchor="w", pady=10)

    # =========================================================================
    # VIEW 2: LEARNING RESOURCES (Exact match of Image 2)
    # =========================================================================
    def _show_learning_view(self):
        self.current_view = "LEARNING"
        self._update_nav_highlight(self.btn_nav_learning)
        for w in self.content_area.winfo_children():
            w.destroy()

        scroll_frame = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent")
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)

        two_col = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        two_col.pack(fill=tk.BOTH, expand=True)

        left_side = ctk.CTkFrame(two_col, fg_color="transparent")
        left_side.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))

        right_side = ctk.CTkFrame(two_col, width=280, fg_color="transparent")
        right_side.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Section 1: Quick-start tutorials (Image 2, Point 1) ---
        ctk.CTkLabel(left_side, text="Quick-start tutorials", font=("Segoe UI", 13, "bold"), text_color="#1e293b").pack(anchor="w", pady=(0, 2))
        ctk.CTkLabel(left_side, text="These step-by-step tutorials with companion videos present essential ArcGIS Pro functionality and workflows", font=("Segoe UI", 9), text_color="#64748b").pack(anchor="w", pady=(0, 10))

        tut_row = ctk.CTkFrame(left_side, fg_color="transparent")
        tut_row.pack(fill=tk.X, pady=(0, 12))

        tutorials = [
            ("Create a project", "Create a project, and add data to a map of endangered species habitats", "🗺"),
            ("Explore data", "Display, query, summarize, and chart livestock data in New Zealand", "📊"),
            ("Symbolize map layers", "Choose and customize map symbols for an urban transportation network", "🎨"),
            ("Make a layout", "Arrange maps, a legend, scale bar, and text to show solar energy potential", "📐"),
            ("Use geoprocessing tools", "Quantify the presence of an invasive grass species near campgrounds", "🛠")
        ]

        for t_title, t_desc, t_icon in tutorials:
            card = ctk.CTkFrame(tut_row, fg_color="#ffffff", border_color="#e2e8f0", border_width=1, corner_radius=6)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

            # Simulated preview box
            p_box = ctk.CTkFrame(card, height=65, fg_color="#f1f5f9", corner_radius=4)
            p_box.pack(fill=tk.X, padx=6, pady=6)
            ctk.CTkLabel(p_box, text=t_icon, font=("Segoe UI", 24)).place(relx=0.5, rely=0.5, anchor="center")

            ctk.CTkLabel(card, text=t_title, font=("Segoe UI", 10, "bold"), text_color="#007AC2").pack(anchor="w", padx=8, pady=(2, 2))
            ctk.CTkLabel(card, text=t_desc, font=("Segoe UI", 8), text_color="#64748b", wraplength=120, justify="left").pack(anchor="w", padx=8, pady=(0, 8))

        ctk.CTkLabel(left_side, text="More Tutorials →", font=("Segoe UI", 9, "bold"), text_color="#007AC2", cursor="hand2").pack(anchor="e", pady=(0, 16))

        # --- Section 3: Tutorial Series (Image 2, Point 3) ---
        ctk.CTkLabel(left_side, text="Tutorial Series", font=("Segoe UI", 13, "bold"), text_color="#1e293b").pack(anchor="w", pady=(0, 2))
        ctk.CTkLabel(left_side, text="Explore ArcGIS Pro through curated collections of tutorials, blog posts, and videos", font=("Segoe UI", 9), text_color="#64748b").pack(anchor="w", pady=(0, 10))

        series_row = ctk.CTkFrame(left_side, fg_color="transparent")
        series_row.pack(fill=tk.X, pady=(0, 8))

        series = [
            ("Mapping and visualization", "Learn essential techniques of map design and data visualization", "📍"),
            ("Analysis and modeling", "Use geoprocessing tools, build analytical models, and apply spatial statistics", "📈"),
            ("Raster data and imagery", "Visualize and analyze raster data and satellite imagery", "🛰"),
            ("3D perspective", "Explore, analyze, and symbolize your data in 3D views", "🏙"),
            ("Data management", "Organize, enhance, and edit data to facilitate project management", "🗄")
        ]

        for s_title, s_desc, s_icon in series:
            card = ctk.CTkFrame(series_row, fg_color="#ffffff", border_color="#e2e8f0", border_width=1, corner_radius=6)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

            p_box = ctk.CTkFrame(card, height=65, fg_color="#f8fafc", corner_radius=4)
            p_box.pack(fill=tk.X, padx=6, pady=6)
            ctk.CTkLabel(p_box, text=s_icon, font=("Segoe UI", 24)).place(relx=0.5, rely=0.5, anchor="center")

            ctk.CTkLabel(card, text=s_title, font=("Segoe UI", 10, "bold"), text_color="#007AC2").pack(anchor="w", padx=8, pady=(2, 2))
            ctk.CTkLabel(card, text=s_desc, font=("Segoe UI", 8), text_color="#64748b", wraplength=120, justify="left").pack(anchor="w", padx=8, pady=(0, 8))

        ctk.CTkLabel(left_side, text="More Tutorial Series →", font=("Segoe UI", 9, "bold"), text_color="#007AC2", cursor="hand2").pack(anchor="e")

        # --- Section 2 & 4: Right Links & ArcMap Migration (Image 2, Point 2 & 4) ---
        side_links = [
            ("What's New", "See what's new and improved in ArcGIS Pro", "✨"),
            ("Help", "Access our comprehensive product documentation", "❓"),
            ("More Tutorials", "Follow guided tutorials based on real-world problems", "📚"),
            ("Esri Academy", "Find instructor-led courses, MOOCs, web courses, videos...", "🎓"),
            ("ArcGIS Blog", "Get insider info from the ArcGIS Pro product team", "📰"),
            ("Esri Community", "Share ideas, solve problems, and build relationships", "👥")
        ]

        grid_links = ctk.CTkFrame(right_side, fg_color="transparent")
        grid_links.pack(fill=tk.X, pady=(0, 16))

        for l_title, l_desc, l_ic in side_links:
            b_card = ctk.CTkFrame(grid_links, fg_color="#ffffff", border_color="#e2e8f0", border_width=1, corner_radius=4)
            b_card.pack(fill=tk.X, pady=3)
            r = ctk.CTkFrame(b_card, fg_color="transparent")
            r.pack(fill=tk.X, padx=8, pady=6)
            ctk.CTkLabel(r, text=l_ic, font=("Segoe UI", 14)).pack(side=tk.LEFT, padx=(0, 8))
            sub = ctk.CTkFrame(r, fg_color="transparent")
            sub.pack(side=tk.LEFT)
            ctk.CTkLabel(sub, text=l_title, font=("Segoe UI", 10, "bold"), text_color="#007AC2").pack(anchor="w")
            ctk.CTkLabel(sub, text=l_desc, font=("Segoe UI", 8), text_color="#64748b", wraplength=180, justify="left").pack(anchor="w")

        # Coming from ArcMap?
        ctk.CTkLabel(right_side, text="Coming from ArcMap?", font=("Segoe UI", 11, "bold"), text_color="#1e293b").pack(anchor="w", pady=(8, 4))
        ctk.CTkLabel(right_side, text="📄  Import an ArcMap document", font=("Segoe UI", 9), text_color="#007AC2", cursor="hand2").pack(anchor="w", pady=2)
        ctk.CTkLabel(right_side, text="🔀  ArcGIS Pro Migration Guide", font=("Segoe UI", 9), text_color="#007AC2", cursor="hand2").pack(anchor="w", pady=2)
        ctk.CTkLabel(right_side, text="👥  For ArcMap users", font=("Segoe UI", 9), text_color="#007AC2", cursor="hand2").pack(anchor="w", pady=2)

    # =========================================================================
    # VIEW 3: SETTINGS (Backstage Settings with 14 Official ArcGIS Pro Tabs)
    # =========================================================================
    def _show_settings_view(self, initial_tab: str = "Options"):
        self.current_view = "SETTINGS"
        self._update_nav_highlight(self.btn_nav_settings)
        for w in self.content_area.winfo_children():
            w.destroy()

        container = ctk.CTkFrame(self.content_area, fg_color="transparent", corner_radius=0)
        container.pack(fill=tk.BOTH, expand=True)

        # Settings Left Sub-Navigation Bar
        settings_nav = ctk.CTkFrame(container, width=175, fg_color="#f1f5f9", corner_radius=0)
        settings_nav.pack(fill=tk.Y, side=tk.LEFT)

        # Vertical Divider
        ctk.CTkFrame(container, width=1, fg_color="#e2e8f0").pack(fill=tk.Y, side=tk.LEFT)

        # Settings Detail Content Container
        self.settings_detail = ctk.CTkScrollableFrame(container, fg_color="#ffffff", corner_radius=0)
        self.settings_detail.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=0, pady=0)

        self._settings_nav_btns = {}

        tabs = [
            ("New", "📄", self._settings_render_new),
            ("Open", "📂", self._settings_render_open),
            ("Info", "ℹ", self._settings_render_info),
            ("Save Project", "💾", self._settings_render_save),
            ("Save Project As", "📑", self._settings_render_save_as),
            ("Portals", "🌐", self._settings_render_portals),
            ("Licensing", "🔑", self._settings_render_licensing),
            ("Options", "⚙", self._settings_render_options),
            ("Package Manager", "📦", self._settings_render_package_manager),
            ("Add-In Manager", "🧩", self._settings_render_addin_manager),
            ("Help", "❓", self._settings_render_help),
            ("About", "ℹ", self._settings_render_about),
            ("Learning Resources", "📖", self._show_learning_view),
            ("Exit", "🚪", self._settings_render_exit)
        ]

        self._settings_tab_map = {n: f for n, _, f in tabs}

        def _select_subtab(name: str, render_fn=None):
            if render_fn is None:
                render_fn = self._settings_tab_map.get(name, self._settings_render_options)
            self.current_settings_tab = name
            for t_name, btn in self._settings_nav_btns.items():
                if t_name == name:
                    btn.configure(fg_color="#e1f0fa", text_color="#007AC2", font=("Segoe UI", 10, "bold"))
                else:
                    btn.configure(fg_color="transparent", text_color="#334155", font=("Segoe UI", 10))
            for w in self.settings_detail.winfo_children():
                w.destroy()
            render_fn()

        self._select_settings_tab_fn = _select_subtab

        ctk.CTkLabel(settings_nav, text="Project & Options", font=("Segoe UI", 10, "bold"), text_color="#64748b").pack(anchor="w", padx=12, pady=(12, 6))

        for name, icon, fn in tabs:
            btn = ctk.CTkButton(
                settings_nav,
                text=f"  {icon}  {name}",
                anchor="w",
                height=30,
                font=("Segoe UI", 10),
                fg_color="transparent",
                hover_color="#e2e8f0",
                text_color="#334155",
                corner_radius=2,
                command=lambda n=name, f=fn: _select_subtab(n, f)
            )
            btn.pack(fill=tk.X, padx=6, pady=1)
            self._settings_nav_btns[name] = btn

        _select_subtab(initial_tab, next((f for n, _, f in tabs if n == initial_tab), self._settings_render_options))

    def select_settings_tab(self, name: str):
        """Programmatically switches between the 14 Backstage Settings tabs."""
        if self.current_view != "SETTINGS":
            self._show_settings_view(initial_tab=name)
        elif hasattr(self, "_select_settings_tab_fn"):
            self._select_settings_tab_fn(name)

    # --- Backstage Subviews ---
    def _settings_render_new(self):
        ctk.CTkLabel(self.settings_detail, text="Create a New Project", font=("Segoe UI", 14, "bold"), text_color="#1e293b").pack(anchor="w", padx=20, pady=(16, 8))
        ctk.CTkLabel(self.settings_detail, text="Select a project template to create a new map or catalog document:", font=("Segoe UI", 9), text_color="#64748b").pack(anchor="w", padx=20, pady=(0, 16))

        grid = ctk.CTkFrame(self.settings_detail, fg_color="transparent")
        grid.pack(anchor="w", padx=20, pady=8)
        for t_name, ic in [("Map", "🗺"), ("Catalog", "🗄"), ("Global Scene", "🌐"), ("Local Scene", "🏙")]:
            b = ctk.CTkButton(grid, text=f"{ic}\n{t_name}", width=120, height=80, fg_color="#f8fafc", hover_color="#e2e8f0", text_color="#1e293b", border_color="#cbd5e1", border_width=1, command=self.on_new_project)
            b.pack(side=tk.LEFT, padx=6)

    def _settings_render_open(self):
        ctk.CTkLabel(self.settings_detail, text="Open an Existing Project", font=("Segoe UI", 14, "bold"), text_color="#1e293b").pack(anchor="w", padx=20, pady=(16, 8))
        ctk.CTkButton(self.settings_detail, text="📁 Browse (.aprx)...", width=160, height=32, fg_color="#007AC2", hover_color="#005a90", text_color="#ffffff", font=("Segoe UI", 10, "bold"), command=lambda: self.on_open_project("Christchurch Transportation")).pack(anchor="w", padx=20, pady=10)

        ctk.CTkLabel(self.settings_detail, text="Recent Projects:", font=("Segoe UI", 11, "bold"), text_color="#334155").pack(anchor="w", padx=20, pady=(12, 6))
        for p_name in ["Christchurch Transportation", "Wellington Buildings", "Scotland Medical Facilities", "Ven", "Brasil Demo"]:
            row = ctk.CTkFrame(self.settings_detail, fg_color="#f8fafc", border_color="#e2e8f0", border_width=1, corner_radius=3)
            row.pack(fill=tk.X, padx=20, pady=3)
            ctk.CTkLabel(row, text=f"🗺  {p_name}", font=("Segoe UI", 10, "bold"), text_color="#1e293b").pack(side=tk.LEFT, padx=10, pady=6)
            ctk.CTkButton(row, text="Open", width=60, height=24, fg_color="#007AC2", text_color="#ffffff", font=("Segoe UI", 9), command=lambda p=p_name: self.on_open_project(p)).pack(side=tk.RIGHT, padx=8)

    def _settings_render_info(self):
        info = self.get_project_info() if self.get_project_info else {
            "name": "Christchurch Transportation.aprx",
            "path": "C:\\Users\\User\\Documents\\ArcGIS\\Projects\\Christchurch\\Christchurch Transportation.aprx",
            "version": "ArcGIS Pro 3.5.0",
            "gdb": "Christchurch Transportation.gdb",
            "crs": "WGS 1984 (WKID: 4326)"
        }
        ctk.CTkLabel(self.settings_detail, text="Project Information", font=("Segoe UI", 14, "bold"), text_color="#1e293b").pack(anchor="w", padx=20, pady=(16, 8))
        card = ctk.CTkFrame(self.settings_detail, fg_color="#f8fafc", border_color="#e2e8f0", border_width=1, corner_radius=6)
        card.pack(fill=tk.X, padx=20, pady=8)

        for label, val in [
            ("Project Name:", info.get("name", "Christchurch Transportation.aprx")),
            ("File Location:", info.get("path", "C:\\Users\\User\\Documents\\ArcGIS\\Projects\\Christchurch.aprx")),
            ("Created With:", info.get("version", "ArcGIS Pro 3.5.0")),
            ("Default Geodatabase:", info.get("gdb", "Christchurch Transportation.gdb")),
            ("Spatial Reference:", info.get("crs", "WGS 1984 (WKID: 4326)"))
        ]:
            r = ctk.CTkFrame(card, fg_color="transparent")
            r.pack(fill=tk.X, padx=12, pady=4)
            ctk.CTkLabel(r, text=label, width=140, anchor="w", font=("Segoe UI", 9, "bold"), text_color="#475569").pack(side=tk.LEFT)
            ctk.CTkLabel(r, text=str(val), font=("Segoe UI", 9), text_color="#1e293b").pack(side=tk.LEFT)

    def _settings_render_save(self):
        ctk.CTkLabel(self.settings_detail, text="Save Project", font=("Segoe UI", 14, "bold"), text_color="#1e293b").pack(anchor="w", padx=20, pady=(16, 8))
        card = ctk.CTkFrame(self.settings_detail, fg_color="#f8fafc", border_color="#e2e8f0", border_width=1, corner_radius=6)
        card.pack(fill=tk.X, padx=20, pady=8)
        ctk.CTkLabel(card, text="Save all current changes, map layers, symbology, and connections to the active project file (.aprx):", font=("Segoe UI", 9), text_color="#475569").pack(anchor="w", padx=14, pady=(12, 6))
        ctk.CTkButton(card, text="💾 Save Current Project", width=160, fg_color="#007AC2", hover_color="#005a90", text_color="#ffffff", font=("Segoe UI", 10, "bold"), command=lambda: self.on_save_project() if self.on_save_project else None).pack(anchor="w", padx=14, pady=(0, 12))

    def _settings_render_save_as(self):
        ctk.CTkLabel(self.settings_detail, text="Save Project As", font=("Segoe UI", 14, "bold"), text_color="#1e293b").pack(anchor="w", padx=20, pady=(16, 8))
        ctk.CTkLabel(self.settings_detail, text="Save a copy of the current project with maps, layers, and toolbox connections:", font=("Segoe UI", 9), text_color="#64748b").pack(anchor="w", padx=20, pady=(0, 12))
        e = ctk.CTkEntry(self.settings_detail, width=320)
        e.insert(0, "Christchurch_Backup_2026.aprx")
        e.pack(anchor="w", padx=20, pady=(0, 12))
        ctk.CTkButton(self.settings_detail, text="💾 Save Copy", width=120, fg_color="#007AC2", hover_color="#005a90", command=lambda: messagebox.showinfo("ArcGIS Pro", f"Project copy '{e.get()}' saved.")).pack(anchor="w", padx=20)

    def _settings_render_portals(self):
        ctk.CTkLabel(self.settings_detail, text="Manage Portal Connections", font=("Segoe UI", 14, "bold"), text_color="#1e293b").pack(anchor="w", padx=20, pady=(16, 8))
        card = ctk.CTkFrame(self.settings_detail, fg_color="#f8fafc", border_color="#e2e8f0", border_width=1, corner_radius=6)
        card.pack(fill=tk.X, padx=20, pady=8)
        ctk.CTkLabel(card, text="● https://www.arcgis.com/ (Active • Signed in as Your Name)", font=("Segoe UI", 10, "bold"), text_color="#0284c7").pack(anchor="w", padx=12, pady=10)

        ctk.CTkLabel(self.settings_detail, text="Add New Portal URL:", font=("Segoe UI", 10, "bold"), text_color="#334155").pack(anchor="w", padx=20, pady=(12, 4))
        p_entry = ctk.CTkEntry(self.settings_detail, width=320, placeholder_text="https://enterprise.yourdomain.com/arcgis/")
        p_entry.pack(anchor="w", padx=20, pady=(0, 8))
        ctk.CTkButton(self.settings_detail, text="Connect Portal", width=130, fg_color="#007AC2").pack(anchor="w", padx=20, pady=4)

    def _settings_render_licensing(self):
        ctk.CTkLabel(self.settings_detail, text="ArcGIS Pro Licensing", font=("Segoe UI", 14, "bold"), text_color="#1e293b").pack(anchor="w", padx=20, pady=(16, 8))
        card = ctk.CTkFrame(self.settings_detail, fg_color="#f8fafc", border_color="#e2e8f0", border_width=1, corner_radius=6)
        card.pack(fill=tk.X, padx=20, pady=8)

        for k, v in [
            ("License Type:", "Named User License"),
            ("Product Level:", "ArcGIS Pro Advanced"),
            ("Authorized User:", "Your Name (tutorials@arcgis.com)"),
            ("Core Extensions:", "Spatial Analyst, 3D Analyst, Network Analyst, Geostatistical Analyst"),
            ("Status:", "Licensed and Authorized")
        ]:
            r = ctk.CTkFrame(card, fg_color="transparent")
            r.pack(fill=tk.X, padx=12, pady=4)
            ctk.CTkLabel(r, text=k, width=150, anchor="w", font=("Segoe UI", 9, "bold"), text_color="#475569").pack(side=tk.LEFT)
            ctk.CTkLabel(r, text=v, font=("Segoe UI", 9), text_color="#1e293b").pack(side=tk.LEFT)

    def _settings_render_options(self):
        ctk.CTkLabel(self.settings_detail, text="Options & General Preferences", font=("Segoe UI", 14, "bold"), text_color="#1e293b").pack(anchor="w", padx=20, pady=(16, 8))

        box = ctk.CTkFrame(self.settings_detail, fg_color="#f8fafc", border_color="#e2e8f0", border_width=1, corner_radius=6)
        box.pack(fill=tk.X, padx=20, pady=8)

        ctk.CTkLabel(box, text="Application Theme (Aparência):", font=("Segoe UI", 10, "bold"), text_color="#334155").pack(anchor="w", padx=16, pady=(10, 2))
        theme_combo = ctk.CTkComboBox(box, values=["Light", "Dark"], width=200, command=lambda m: ctk.set_appearance_mode(m))
        theme_combo.set("Light")
        theme_combo.pack(anchor="w", padx=16, pady=(0, 10))

        ctk.CTkLabel(box, text="Coordinate Display Format:", font=("Segoe UI", 10, "bold"), text_color="#334155").pack(anchor="w", padx=16, pady=(6, 2))
        unit_combo = ctk.CTkComboBox(box, values=["Decimal Degrees", "Degrees Minutes Seconds (DMS)", "Web Mercator Meters"], width=260)
        unit_combo.pack(anchor="w", padx=16, pady=(0, 10))

        ctk.CTkLabel(box, text="Snapping Tolerance:", font=("Segoe UI", 10, "bold"), text_color="#334155").pack(anchor="w", padx=16, pady=(6, 2))
        e_snap = ctk.CTkEntry(box, width=120)
        e_snap.insert(0, "10 pixels")
        e_snap.pack(anchor="w", padx=16, pady=(0, 14))

        ctk.CTkButton(box, text="Save Preferences", width=140, fg_color="#007AC2", hover_color="#005a90", command=lambda: messagebox.showinfo("Options", "Preferences saved successfully.")).pack(anchor="w", padx=16, pady=(0, 12))

    def _settings_render_package_manager(self):
        ctk.CTkLabel(self.settings_detail, text="Package Manager (Python & Conda)", font=("Segoe UI", 14, "bold"), text_color="#1e293b").pack(anchor="w", padx=20, pady=(16, 8))
        card = ctk.CTkFrame(self.settings_detail, fg_color="#f8fafc", border_color="#e2e8f0", border_width=1, corner_radius=6)
        card.pack(fill=tk.X, padx=20, pady=8)

        ctk.CTkLabel(card, text="Active Environment: arcgispro-py3 (Python 3.12 64-bit)", font=("Segoe UI", 10, "bold"), text_color="#0284c7").pack(anchor="w", padx=12, pady=(10, 4))
        ctk.CTkLabel(card, text="Location: C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3", font=("Segoe UI", 8), text_color="#64748b").pack(anchor="w", padx=12, pady=(0, 8))

        ctk.CTkLabel(self.settings_detail, text="Installed Packages:", font=("Segoe UI", 10, "bold"), text_color="#334155").pack(anchor="w", padx=20, pady=(8, 4))
        packages = [
            ("arcpy", "3.5.0", "Esri ArcGIS Python Geoprocessing & Spatial Analysis"),
            ("arcgeo", "1.0.0", "Native High-Performance Vector GIS & QuadTree Index"),
            ("customtkinter", "5.2.2", "Modern High-DPI Desktop Widget System"),
            ("pillow", "10.4.0", "Python Imaging Library & Tile Rendering"),
            ("shapely", "2.0.6", "Planar Geometric Calculations"),
            ("pyproj", "3.6.1", "Cartographic Projections and Coordinate Transformations")
        ]
        for p, v, desc in packages:
            r = ctk.CTkFrame(self.settings_detail, fg_color="#ffffff", border_color="#e2e8f0", border_width=1, corner_radius=3)
            r.pack(fill=tk.X, padx=20, pady=2)
            ctk.CTkLabel(r, text=p, width=120, anchor="w", font=("Segoe UI", 9, "bold"), text_color="#007AC2").pack(side=tk.LEFT, padx=8, pady=4)
            ctk.CTkLabel(r, text=v, width=80, anchor="w", font=("Segoe UI", 9), text_color="#475569").pack(side=tk.LEFT, padx=4)
            ctk.CTkLabel(r, text=desc, font=("Segoe UI", 8), text_color="#64748b").pack(side=tk.LEFT, padx=4)

    def _settings_render_addin_manager(self):
        ctk.CTkLabel(self.settings_detail, text="Add-In Manager", font=("Segoe UI", 14, "bold"), text_color="#1e293b").pack(anchor="w", padx=20, pady=(16, 8))
        card = ctk.CTkFrame(self.settings_detail, fg_color="#f8fafc", border_color="#e2e8f0", border_width=1, corner_radius=6)
        card.pack(fill=tk.X, padx=20, pady=8)
        ctk.CTkLabel(card, text="🧩 ArcRib Studio Extension (v1.0.0) • Active", font=("Segoe UI", 10, "bold"), text_color="#15803d").pack(anchor="w", padx=12, pady=6)
        ctk.CTkLabel(card, text="🧩 Christchurch Hazard Geoprocessing Add-In (v2.1) • Active", font=("Segoe UI", 10, "bold"), text_color="#15803d").pack(anchor="w", padx=12, pady=6)

    def _settings_render_help(self):
        ctk.CTkLabel(self.settings_detail, text="ArcGIS Pro Help System", font=("Segoe UI", 14, "bold"), text_color="#1e293b").pack(anchor="w", padx=20, pady=(16, 8))
        for t, desc in [
            ("ArcGIS Pro 3.5 Online Documentation", "Comprehensive user guides, tool references, and workflow help."),
            ("Python & ArcPy Reference", "Documentation for arcpy.analysis, arcpy.management and arcpy.env."),
            ("Keyboard Shortcuts (Ctrl+F1, Alt+Q)", "Quick navigation and command execution reference."),
            ("Diagnostic Monitor & Performance", "Monitor graphics memory and rendering throughput.")
        ]:
            card = ctk.CTkFrame(self.settings_detail, fg_color="#f8fafc", border_color="#e2e8f0", border_width=1, corner_radius=4)
            card.pack(fill=tk.X, padx=20, pady=4)
            ctk.CTkLabel(card, text=t, font=("Segoe UI", 10, "bold"), text_color="#007AC2").pack(anchor="w", padx=10, pady=(6, 2))
            ctk.CTkLabel(card, text=desc, font=("Segoe UI", 8), text_color="#64748b").pack(anchor="w", padx=10, pady=(0, 6))

    def _settings_render_about(self):
        ctk.CTkLabel(self.settings_detail, text="About ArcGIS Pro", font=("Segoe UI", 14, "bold"), text_color="#1e293b").pack(anchor="w", padx=20, pady=(16, 8))
        card = ctk.CTkFrame(self.settings_detail, fg_color="#f8fafc", border_color="#e2e8f0", border_width=1, corner_radius=6)
        card.pack(fill=tk.X, padx=20, pady=8)
        ctk.CTkLabel(card, text="ArcGIS® Pro 3.5.0 Release", font=("Segoe UI", 12, "bold"), text_color="#1e293b").pack(anchor="w", padx=14, pady=(12, 2))
        ctk.CTkLabel(card, text="Build: 50342 • 64-bit Edition", font=("Segoe UI", 9), text_color="#64748b").pack(anchor="w", padx=14, pady=(0, 6))
        ctk.CTkLabel(card, text="Copyright © 2026 Esri Inc. All rights reserved.", font=("Segoe UI", 8), text_color="#94a3b8").pack(anchor="w", padx=14, pady=(0, 8))
        ctk.CTkLabel(card, text="✓ Your software is up to date.", font=("Segoe UI", 9, "bold"), text_color="#15803d").pack(anchor="w", padx=14, pady=(0, 12))

    def _settings_render_exit(self):
        ctk.CTkLabel(self.settings_detail, text="Exit ArcGIS Pro", font=("Segoe UI", 14, "bold"), text_color="#1e293b").pack(anchor="w", padx=20, pady=(16, 8))
        card = ctk.CTkFrame(self.settings_detail, fg_color="#f8fafc", border_color="#e2e8f0", border_width=1, corner_radius=6)
        card.pack(fill=tk.X, padx=20, pady=8)
        ctk.CTkLabel(card, text="Are you sure you want to close the current project and exit ArcGIS Pro?", font=("Segoe UI", 10), text_color="#334155").pack(anchor="w", padx=14, pady=(12, 8))
        ctk.CTkButton(card, text="🚪 Close and Exit", width=140, fg_color="#dc2626", hover_color="#b91c1c", text_color="#ffffff", font=("Segoe UI", 10, "bold"), command=lambda: self.on_exit() if self.on_exit else None).pack(anchor="w", padx=14, pady=(0, 12))
