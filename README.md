# ArcRib - ArcGIS® Pro Desktop GIS Reimplementation

**ArcRib** é um software de Sistema de Informações Geográficas (SIG / GIS) desktop desenvolvido em Python, reproduzindo com fidelidade visual e arquitetural a interface do **Esri ArcGIS® Pro 3.x** e o motor geométrico espacial baseado no padrão **OGC Simple Features**.

---

## 🌟 Principais Recursos e Telas

### 1. Start Page & Backstage Settings
- **Aba Home**: Modelos de projetos rápidos (*Map*, *Catalog*, *Global Scene*, *Local Scene*, *Start without a template*), lista e grade de projetos recentes com miniaturas e data de modificação.
- **Aba Learning Resources**: Tutoriais rápidos (*Quick-start tutorials*), séries temáticas (*Tutorial Series*), links oficiais da comunidade Esri e guia de migração do ArcMap.
- **Backstage Settings (14 Abas Oficiais)**:
  1. *New* (Modelos de novos projetos)
  2. *Open* (Navegação de arquivos `.aprx` e projetos recentes)
  3. *Info* (Metadados do projeto ativo e geodatabase padrão)
  4. *Save Project* (Salvamento de `.aprx` e `.gdb`)
  5. *Save Project As* (Cópia de segurança com mapas e camadas)
  6. *Portals* (Gerenciamento de conexões com ArcGIS Online / Portal)
  7. *Licensing* (Informações de licença *Named User / Advanced*)
  8. *Options* (Tema Claro/Escuro, unidades de coordenadas, tolerância de snapping)
  9. *Package Manager* (Ambiente Conda/Python e pacotes instalados: `arcpy`, `arcgeo`, etc.)
  10. *Add-In Manager* (Gerenciamento de extensões `.esriAddInX`)
  11. *Help* (Documentação online e atalhos de teclado)
  12. *About* (Versão do software e verificação de atualizações)
  13. *Learning Resources* (Acesso direto aos recursos de aprendizado)
  14. *Exit* (Confirmação para fechar o projeto e sair do app)

### 2. Fluent Ribbon & Barra de Título
- **Barra de Acesso Rápido**: Ações diretas de Novo, Abrir, Salvar, Desfazer e Refazer.
- **Dropdown do Projeto**: Exibe o projeto ativo com caminho e data/hora.
- **Busca de Comandos**: Campo de busca global (*Command Search*) com atalho `Alt+Q`.
- **Abas Principais (Core Tabs)**: *Map*, *Insert*, *Analysis*, *View*, *Edit*, *Imagery*, *Share*, *Help*.
- **Abas Contextuais**: Pílula destacada contendo *Feature Layer*, *Labeling* e *Data*.
- **Recolhimento da Ribbon**: Botão expansor/recolhedor e atalho `Ctrl+F1`.

### 3. Centro de Visualizações (Views)
- **Abas de Visualização**:
  - `🗺 Christchurch Urban Area ✕` (Mapa 2D interativo principal)
  - `🗺 Canterbury Region`
  - `📊 Liquefaction Risk`
  - `📋 Attributes Table` (Tabela de atributos acoplada com busca em tempo real)
  - `🐍 Python Window (arcpy)` (Console Python interativo executando ferramentas reais com `arcpy`)
- **Barra de Status**: Seletor de escala (`1:100,000 ▾`), Snapping, Grade, Rosa dos Ventos, Coordenadas dinâmicas (Graus Decimais e Web Mercator), Contador de feições selecionadas e controle de redesenho.

### 4. Painéis Acoplados & Empilhados (Stacked Panes)
- **Contents (TOC)**: Modos de visualização com 6 ícones de filtro (Ordem de Desenho `☰`, Fontes de Dados `🗄`, Seleção `☑`, Edição `✏`, Snapping `🧲`, Rótulos `🏷`), grupos de camadas com legendas categorizadas por tipo (linhas contínuas e tracejadas para ferry) e contadores de feições.
- **Barra de Painéis Empilhados**: Alternância instantânea e menu popup `▾` para os 6 painéis:
  1. **Catalog**: Pastas, Maps, Toolboxes, Databases (`.gdb`) e Layouts.
  2. **Create Features**: Modelos de edição (*Templates*) para Polígonos, Linhas e Pontos.
  3. **Locate**: Geocodificação rápida de pontos de interesse com foco automático no mapa.
  4. **Symbology (Format Polygon Symbol)**: Abas *Gallery* e *Properties*, abas gráficas (Aparência 🖌, Camadas 📑, Estrutura 🔧), paleta de cores para preenchimento e contorno, spinbox de espessura (`pt`), pré-visualização em Canvas ao vivo com resizer `···` e chave *Auto Apply*.
  5. **Geoprocessing**: Ferramentas de Análise espacial (*Buffer*, *Spatial Join*, *Clip*, *Summary Statistics*, *Export ESRI JSON*).
  6. **Chart Properties**: Gráficos dinâmicos de barras por nível de risco e área.

---

## 🏛 Arquitetura do ArcRib vs ArcGIS Pro

| Componente | ArcGIS Pro | ArcRib |
| :--- | :--- | :--- |
| **Interface de Usuário** | Fluent Ribbon (.NET WPF) | CustomTkinter Fluent Light UI (`#007AC2`, `#f8fafc`, `#e2e8f0`) |
| **Motor de Geometria** | `ArcGIS.Core.dll` (ArcObjects C++) | `arcgeo.geometry` (Primitivas OGC, Gauss/Shoelace, Haversine, Ray-casting) |
| **Indexação Espacial** | R-Tree / Grid Index | `arcgeo.spatial_index` (QuadTree 2D com busca em $\mathcal{O}(\log N)$) |
| **Modelo de Camadas** | `FeatureClass` / `FeatureLayer` | `arcgeo.data.FeatureLayer` (GeoJSON nativo, FIDs, Atributos) |
| **Geoprocessamento & ArcPy** | `ArcGIS.Desktop.GeoProcessing` / `arcpy` | `arcgeo.geoprocessing` + `arcgeo.arcpy` (Buffer, Spatial Join, Clip, Summary Stats, GetCount) |
| **Cartografia & Renderização** | DirectX / OpenGL 2D & 3D | Canvas Interativo 2D + Exportador Vetorial SVG |

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.10+
- Dependências:
  ```bash
  pip install customtkinter pillow
  ```

### Iniciar o Aplicativo
```bash
python run_arcrib.py
```

### Executar a Suíte de Testes Automatizados (30 Testes)
```bash
python -m unittest discover tests
```

---

## 🧪 Estrutura do Projeto

```
ArcGEO/
├── README.md               # Documentação completa
├── run_arcrib.py           # Ponto de entrada do aplicativo desktop
├── arcpy.py                # Wrapper de compatibilidade ArcPy de nível superior
├── capitais_esri.json      # Conjunto de dados de teste formato ESRI
├── arcgeo/                 # Motor GIS nativo
│   ├── geometry.py         # Primitivas OGC (Point, Polyline, Polygon, Envelope)
│   ├── spatial_index.py    # QuadTree 2D
│   ├── data.py             # FeatureLayer, Feature, GeoJSON parser
│   ├── geoprocessing.py    # Buffer, Spatial Join, Clip, Estatísticas
│   ├── mapping.py          # Renderizadores, Simbologia e Exportador SVG
│   ├── basemaps.py         # Servidores de Basemap (OSM, Esri World Imagery, etc.)
│   └── arcpy.py            # Módulo de compatibilidade com sintaxe oficial arcpy
├── arcrib/                 # Aplicação Desktop (Interface ArcGIS Pro)
│   ├── app.py              # Janela principal, Ribbon, TOC, Painéis empilhados, Viewport
│   ├── canvas.py           # Canvas GIS interativo com transformações geográficas
│   ├── start_page.py       # Start Page, Home, Recursos de Aprendizado e Backstage Settings
│   └── sample_data.py      # Datasets de demonstração (Christchurch e Brasil)
└── tests/                  # Testes unitários e de integração
    ├── test_arcgeo.py      # Testes do motor matemático e geométrico
    └── test_arcrib.py      # Testes da GUI, Ribbon, Backstage e painéis
```
