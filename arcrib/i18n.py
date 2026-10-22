"""
arcrib/i18n.py - Internationalization & Localized Strings for ArcRib
Extracted directly from Esri ArcGIS Pro 3.0 Portuguese (pt-BR) Language Pack DAML resources.
"""

from typing import Dict

# Active language: 'en' or 'pt-BR'
ACTIVE_LANGUAGE = "en"

LOCALIZED_CATALOG: Dict[str, Dict[str, str]] = {
    "en": {
        # Core Tabs
        "tab_project": "Project",
        "tab_map": "Map",
        "tab_insert": "Insert",
        "tab_analysis": "Analysis",
        "tab_view": "View",
        "tab_edit": "Edit",
        "tab_imagery": "Imagery",
        "tab_share": "Share",
        "tab_help": "Help",
        
        # Contextual Tabs
        "ctx_feature_layer": "Feature Layer",
        "ctx_labeling": "Labeling",
        "ctx_data": "Data",
        
        # Ribbon Groups
        "grp_clipboard": "Clipboard",
        "grp_navigate": "Navigate",
        "grp_layer": "Layer",
        "grp_selection": "Selection",
        "grp_inquiry": "Inquiry",
        "grp_project": "Project",
        "grp_connections": "Connections",
        "grp_geoprocessing": "Geoprocessing",
        "grp_tools": "Tools",
        "grp_scripting": "Scripting",
        "grp_windows": "Windows / Panes",
        "grp_features": "Features",
        "grp_manage_edits": "Manage Edits",
        "grp_snapping": "Snapping",
        "grp_customize": "Customize",
        "grp_package": "Package",
        "grp_share_as": "Share As",
        
        # Action Buttons
        "btn_explore": "Explore",
        "btn_full_extent": "Full Extent",
        "btn_fixed_zoom_in": "Fixed Zoom In",
        "btn_fixed_zoom_out": "Fixed Zoom Out",
        "btn_prev_extent": "Previous Extent",
        "btn_next_extent": "Next Extent",
        "btn_add_data": "Add Data",
        "btn_basemap": "Basemap",
        "btn_select": "Select",
        "btn_select_by_attributes": "Select By Attributes",
        "btn_select_by_location": "Select By Location",
        "btn_clear_selection": "Clear",
        "btn_popup": "Pop-up",
        "btn_measure": "Measure",
        "btn_locate": "Locate",
        
        "btn_new_map": "New Map",
        "btn_new_layout": "New Layout",
        "btn_new_report": "New Report",
        "btn_add_folder": "Add Folder",
        "btn_add_database": "Add Database",
        
        "btn_tools": "Tools",
        "btn_modelbuilder": "ModelBuilder",
        "btn_python": "Python Window",
        "btn_history": "History",
        "btn_buffer": "Buffer",
        "btn_spatial_join": "Spatial Join",
        "btn_clip": "Clip",
        "btn_summary_stats": "Summary Statistics",
        
        "btn_contents": "Contents",
        "btn_catalog": "Catalog",
        "btn_geoprocessing": "Geoprocessing",
        "btn_symbology": "Symbology",
        "btn_attributes": "Attributes",
        "btn_create_features": "Create Features",
        
        "btn_save_edits": "Save",
        "btn_discard_edits": "Discard",
        "btn_snapping_toggle": "Snapping",
        
        # Status Bar
        "status_scale": "Scale",
        "status_snapping_on": "Snapping: ON",
        "status_snapping_off": "Snapping: OFF",
        
        # TOC Views
        "toc_drawing_order": "List By Drawing Order",
        "toc_source": "List By Source",
        "toc_selection": "List By Selection",
        "toc_editing": "List By Editing",
        "toc_snapping": "List By Snapping",
        "toc_labeling": "List By Labeling",
        
        # Backstage Items
        "bs_new": "New",
        "bs_open": "Open",
        "bs_info": "Info",
        "bs_save": "Save",
        "bs_save_as": "Save As",
        "bs_portals": "Portals",
        "bs_licensing": "Licensing",
        "bs_options": "Options",
        "bs_package_manager": "Package Manager",
        "bs_addin_manager": "Add-in Manager",
        "bs_help": "Help",
        "bs_about": "About",
        "bs_learning": "Learning Resources",
        "bs_exit": "Exit"
    },
    
    "pt-BR": {
        # Core Tabs
        "tab_project": "Projeto",
        "tab_map": "Mapa",
        "tab_insert": "Inserir",
        "tab_analysis": "Análise",
        "tab_view": "Exibir",
        "tab_edit": "Editar",
        "tab_imagery": "Imagem",
        "tab_share": "Compartilhar",
        "tab_help": "Ajuda",
        
        # Contextual Tabs
        "ctx_feature_layer": "Camada de Feição",
        "ctx_labeling": "Rotulagem",
        "ctx_data": "Dados",
        
        # Ribbon Groups
        "grp_clipboard": "Área de Transferência",
        "grp_navigate": "Navegar",
        "grp_layer": "Camada",
        "grp_selection": "Seleção",
        "grp_inquiry": "Consulta / Medição",
        "grp_project": "Projeto",
        "grp_connections": "Conexões",
        "grp_geoprocessing": "Geoprocessamento",
        "grp_tools": "Ferramentas",
        "grp_scripting": "Scripts",
        "grp_windows": "Janelas / Painéis",
        "grp_features": "Feições",
        "grp_manage_edits": "Gerenciar Edições",
        "grp_snapping": "Ajuste Magnético (Snapping)",
        "grp_customize": "Personalizar",
        "grp_package": "Pacote",
        "grp_share_as": "Compartilhar Como",
        
        # Action Buttons
        "btn_explore": "Explorar",
        "btn_full_extent": "Extensão Total",
        "btn_fixed_zoom_in": "Aproximar Fixo",
        "btn_fixed_zoom_out": "Afastar Fixo",
        "btn_prev_extent": "Extensão Anterior",
        "btn_next_extent": "Próxima Extensão",
        "btn_add_data": "Adicionar Dados",
        "btn_basemap": "Mapa Base",
        "btn_select": "Selecionar",
        "btn_select_by_attributes": "Selecionar por Atributos",
        "btn_select_by_location": "Selecionar por Localização",
        "btn_clear_selection": "Limpar Seleção",
        "btn_popup": "Pop-up",
        "btn_measure": "Medir",
        "btn_locate": "Localizar",
        
        "btn_new_map": "Novo Mapa",
        "btn_new_layout": "Novo Layout",
        "btn_new_report": "Novo Relatório",
        "btn_add_folder": "Adicionar Pasta",
        "btn_add_database": "Adicionar Banco de Dados",
        
        "btn_tools": "Ferramentas",
        "btn_modelbuilder": "ModelBuilder",
        "btn_python": "Janela Python",
        "btn_history": "Histórico",
        "btn_buffer": "Buffer (Área de Influência)",
        "btn_spatial_join": "Ligação Espacial (Spatial Join)",
        "btn_clip": "Recortar (Clip)",
        "btn_summary_stats": "Estatísticas de Resumo",
        
        "btn_contents": "Conteúdo",
        "btn_catalog": "Catálogo",
        "btn_geoprocessing": "Geoprocessamento",
        "btn_symbology": "Simbologia",
        "btn_attributes": "Tabela de Atributos",
        "btn_create_features": "Criar Feições",
        
        "btn_save_edits": "Salvar",
        "btn_discard_edits": "Descartar",
        "btn_snapping_toggle": "Snapping",
        
        # Status Bar
        "status_scale": "Escala",
        "status_snapping_on": "Ajuste: ATIVADO",
        "status_snapping_off": "Ajuste: DESATIVADO",
        
        # TOC Views
        "toc_drawing_order": "Listar por Ordem de Desenho",
        "toc_source": "Listar por Fonte",
        "toc_selection": "Listar por Seleção",
        "toc_editing": "Listar por Edição",
        "toc_snapping": "Listar por Ajuste",
        "toc_labeling": "Listar por Rotulagem",
        
        # Backstage Items
        "bs_new": "Novo",
        "bs_open": "Abrir",
        "bs_info": "Informações",
        "bs_save": "Salvar",
        "bs_save_as": "Salvar Como",
        "bs_portals": "Portais",
        "bs_licensing": "Licenciamento",
        "bs_options": "Opções",
        "bs_package_manager": "Gerenciador de Pacotes",
        "bs_addin_manager": "Gerenciador de Suplementos",
        "bs_help": "Ajuda",
        "bs_about": "Sobre",
        "bs_learning": "Recursos de Aprendizado",
        "bs_exit": "Sair"
    }
}


def tr(key: str, default: str = "") -> str:
    """Translates a key according to the active language setting."""
    lang_dict = LOCALIZED_CATALOG.get(ACTIVE_LANGUAGE, LOCALIZED_CATALOG["en"])
    return lang_dict.get(key, default or key)


def set_language(lang: str) -> None:
    """Sets the active language ('en' or 'pt-BR')."""
    global ACTIVE_LANGUAGE
    if lang in LOCALIZED_CATALOG:
        ACTIVE_LANGUAGE = lang
