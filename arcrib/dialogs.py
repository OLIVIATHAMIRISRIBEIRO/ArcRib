"""
arcrib.dialogs - Tool and Analysis Windows
Provides modern popup windows for:
- Attribute Table Inspector & Search
- Buffer Geoprocessing Tool
- Spatial Join Geoprocessing Tool
- Feature Identification & Inspection
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from typing import Dict, Any, Optional, Callable, List
from arcgeo.data import FeatureLayer, Feature
from arcgeo.geoprocessing import Geoprocessing


class AttributeTableWindow(ctk.CTkToplevel):
    """ArcGIS Pro style Attribute Table with real-time text filter and feature highlighting."""
    def __init__(self, parent, layer: FeatureLayer, on_select_feature: Optional[Callable[[int], None]] = None):
        super().__init__(parent)
        self.layer = layer
        self.on_select_feature = on_select_feature

        self.title(f"Tabela de Atributos - {layer.name} ({len(layer)} registros)")
        self.geometry("750x450")
        self.minsize(550, 350)

        self._build_ui()
        self._populate_table()

    def _build_ui(self):
        # Top Toolbar
        top_frame = ctk.CTkFrame(self, height=45, fg_color="#1e293b", corner_radius=0)
        top_frame.pack(fill=tk.X, side=tk.TOP, padx=0, pady=0)

        ctk.CTkLabel(top_frame, text=f"Camada: {self.layer.name}", font=("Segoe UI", 12, "bold"), text_color="#38bdf8").pack(side=tk.LEFT, padx=12, pady=8)

        # Search Bar
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._filter_table())
        search_entry = ctk.CTkEntry(top_frame, placeholder_text="Filtrar atributos...", textvariable=self.search_var, width=200, height=28)
        search_entry.pack(side=tk.RIGHT, padx=12, pady=8)

        # Treeview Table
        table_frame = ctk.CTkFrame(self, fg_color="#0f172a", corner_radius=0)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Determine columns
        sample_attrs = {}
        for feat in self.layer.features.values():
            sample_attrs.update(feat.attributes)
        self.columns = ["FID", "GEOMETRIA"] + sorted(list(sample_attrs.keys()))

        # Styling ttk Treeview for dark mode
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#1e293b",
                        foreground="#f8fafc",
                        fieldbackground="#1e293b",
                        rowheight=26,
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background="#0f172a",
                        foreground="#38bdf8",
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#0284c7")])

        self.tree = ttk.Treeview(table_frame, columns=self.columns, show="headings", selectmode="browse")

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110, anchor="center")

        self.tree.bind("<<TreeviewSelect>>", self._on_row_select)

    def _populate_table(self, filter_text: str = ""):
        self.tree.delete(*self.tree.get_children())
        filter_lower = filter_text.strip().lower()

        for feat in self.layer.features.values():
            geom_str = feat.geometry.__class__.__name__
            row_vals = [feat.fid, geom_str]

            matched = (filter_lower == "") or (str(feat.fid) in filter_lower) or (geom_str.lower() in filter_lower)

            for col in self.columns[2:]:
                val = feat.get(col, "")
                row_vals.append(val)
                if filter_lower in str(val).lower():
                    matched = True

            if matched:
                self.tree.insert("", "end", values=row_vals, iid=str(feat.fid))

    def _filter_table(self):
        self._populate_table(self.search_var.get())

    def _on_row_select(self, event):
        selected_items = self.tree.selection()
        if selected_items and self.on_select_feature:
            fid = int(selected_items[0])
            self.on_select_feature(fid)


class BufferToolDialog(ctk.CTkToplevel):
    """Geoprocessing Tool: Generate Buffer Polygons."""
    def __init__(self, parent, layers: List[FeatureLayer], on_buffer_created: Callable[[FeatureLayer], None]):
        super().__init__(parent)
        self.layers = layers
        self.on_buffer_created = on_buffer_created

        self.title("Geoprocessamento: Buffer (Área de Influência)")
        self.geometry("440x360")
        self.resizable(False, False)

        self._build_ui()

    def _build_ui(self):
        container = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=12)
        container.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        ctk.CTkLabel(container, text="Parâmetros da Ferramenta Buffer", font=("Segoe UI", 14, "bold"), text_color="#38bdf8").pack(anchor="w", padx=16, pady=(12, 16))

        # Layer Selection
        ctk.CTkLabel(container, text="Camada de Entrada (Input Layer):", font=("Segoe UI", 11)).pack(anchor="w", padx=16, pady=(4, 2))
        layer_names = [l.name for l in self.layers] or ["Nenhuma camada"]
        self.layer_combo = ctk.CTkComboBox(container, values=layer_names, width=380, height=32)
        self.layer_combo.pack(padx=16, pady=(0, 12))

        # Distance Entry
        ctk.CTkLabel(container, text="Distância do Buffer (em graus decimais ou raio):", font=("Segoe UI", 11)).pack(anchor="w", padx=16, pady=(4, 2))
        self.dist_entry = ctk.CTkEntry(container, placeholder_text="Ex: 1.0", width=380, height=32)
        self.dist_entry.insert(0, "1.0")
        self.dist_entry.pack(padx=16, pady=(0, 12))

        # Output Name
        ctk.CTkLabel(container, text="Nome da Camada Resultante:", font=("Segoe UI", 11)).pack(anchor="w", padx=16, pady=(4, 2))
        self.output_entry = ctk.CTkEntry(container, placeholder_text="Ex: Buffer_Capitais", width=380, height=32)
        self.output_entry.insert(0, "Buffer_Output")
        self.output_entry.pack(padx=16, pady=(0, 20))

        # Action Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill=tk.X, padx=16, pady=(0, 10))

        ctk.CTkButton(btn_frame, text="Cancelar", fg_color="#475569", hover_color="#334155", width=120, command=self.destroy).pack(side=tk.LEFT)
        ctk.CTkButton(btn_frame, text="Executar Buffer", fg_color="#0284c7", hover_color="#0369a1", width=180, command=self._execute).pack(side=tk.RIGHT)

    def _execute(self):
        selected_name = self.layer_combo.get()
        target_layer = next((l for l in self.layers if l.name == selected_name), None)
        if not target_layer:
            messagebox.showerror("Erro", "Selecione uma camada válida.")
            return

        try:
            distance = float(self.dist_entry.get().replace(",", "."))
            if distance <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "A distância deve ser um número positivo maior que zero.")
            return

        out_name = self.output_entry.get().strip() or f"{target_layer.name}_Buffer"
        buf_layer = Geoprocessing.buffer_layer(target_layer, distance=distance, output_name=out_name, num_segments=48)
        self.on_buffer_created(buf_layer)
        self.destroy()


class SpatialJoinDialog(ctk.CTkToplevel):
    """Geoprocessing Tool: Spatial Join (Points in Polygons)."""
    def __init__(self, parent, layers: List[FeatureLayer], on_join_created: Callable[[FeatureLayer], None]):
        super().__init__(parent)
        self.layers = layers
        self.on_join_created = on_join_created

        self.title("Geoprocessamento: Spatial Join")
        self.geometry("440x350")
        self.resizable(False, False)

        self._build_ui()

    def _build_ui(self):
        container = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=12)
        container.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        ctk.CTkLabel(container, text="Junção Espacial (Spatial Join)", font=("Segoe UI", 14, "bold"), text_color="#38bdf8").pack(anchor="w", padx=16, pady=(12, 16))

        point_layers = [l.name for l in self.layers if l.geometry_type == "Point"] or ["Nenhuma"]
        poly_layers = [l.name for l in self.layers if l.geometry_type == "Polygon"] or ["Nenhuma"]

        ctk.CTkLabel(container, text="Camada Alvo (Target - Pontos):", font=("Segoe UI", 11)).pack(anchor="w", padx=16, pady=(4, 2))
        self.target_combo = ctk.CTkComboBox(container, values=point_layers, width=380, height=32)
        self.target_combo.pack(padx=16, pady=(0, 10))

        ctk.CTkLabel(container, text="Camada de Junção (Join - Polígonos):", font=("Segoe UI", 11)).pack(anchor="w", padx=16, pady=(4, 2))
        self.join_combo = ctk.CTkComboBox(container, values=poly_layers, width=380, height=32)
        self.join_combo.pack(padx=16, pady=(0, 10))

        ctk.CTkLabel(container, text="Nome da Camada Resultante:", font=("Segoe UI", 11)).pack(anchor="w", padx=16, pady=(4, 2))
        self.out_name_entry = ctk.CTkEntry(container, placeholder_text="SpatialJoin_Result", width=380, height=32)
        self.out_name_entry.insert(0, "SpatialJoin_Result")
        self.out_name_entry.pack(padx=16, pady=(0, 20))

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill=tk.X, padx=16, pady=(0, 10))

        ctk.CTkButton(btn_frame, text="Cancelar", fg_color="#475569", hover_color="#334155", width=120, command=self.destroy).pack(side=tk.LEFT)
        ctk.CTkButton(btn_frame, text="Executar Join", fg_color="#0284c7", hover_color="#0369a1", width=180, command=self._execute).pack(side=tk.RIGHT)

    def _execute(self):
        t_name = self.target_combo.get()
        j_name = self.join_combo.get()
        target = next((l for l in self.layers if l.name == t_name), None)
        join = next((l for l in self.layers if l.name == j_name), None)

        if not target or not join:
            messagebox.showerror("Erro", "Selecione camadas válidas de pontos e polígonos.")
            return

        out_layer = Geoprocessing.spatial_join(target, join, self.out_name_entry.get().strip() or "SpatialJoin_Result")
        self.on_join_created(out_layer)
        self.destroy()
