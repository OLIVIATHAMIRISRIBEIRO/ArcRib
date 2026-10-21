"""
demo_arcgeo.py - Demonstration of ArcGEO GIS Engine
Shows complete GIS workflow matching ArcGIS Pro capabilities:
1. FeatureLayer creation & feature insertion
2. Spatial reference coordinate projection
3. QuadTree spatial index querying
4. Geoprocessing: Buffer & Spatial Join
5. Cartographic map composition & SVG rendering
"""

from arcgeo.geometry import Point, Polygon, Polyline, Envelope, SpatialReference
from arcgeo.data import FeatureLayer
from arcgeo.geoprocessing import Geoprocessing
from arcgeo.mapping import Map, SimpleRenderer, UniqueValueRenderer


def main():
    print("==================================================")
    print("   ARCGEO: DEMONSTRAÇÃO DO MOTOR GIS PROPRÍO      ")
    print("==================================================")

    # 1. Camada de Cidades (Pontos)
    cities = FeatureLayer("Capitais", geometry_type="Point")
    cities.add_feature(Point(-46.6333, -23.5505), {"NAME": "Sao Paulo", "POP": 12300000, "REGION": "Sudeste"})
    cities.add_feature(Point(-43.1729, -22.9068), {"NAME": "Rio de Janeiro", "POP": 6700000, "REGION": "Sudeste"})
    cities.add_feature(Point(-43.9378, -19.9208), {"NAME": "Belo Horizonte", "POP": 2500000, "REGION": "Sudeste"})
    cities.add_feature(Point(-47.8825, -15.7942), {"NAME": "Brasilia", "POP": 3050000, "REGION": "Centro-Oeste"})
    cities.add_feature(Point(-49.2731, -25.4284), {"NAME": "Curitiba", "POP": 1950000, "REGION": "Sul"})
    cities.add_feature(Point(-38.5108, -12.9714), {"NAME": "Salvador", "POP": 2900000, "REGION": "Nordeste"})
    print(f"[OK] Camada de Capitais criada: {len(cities)} feicoes.")

    # 2. Geoprocessamento: Buffer (Área de Influência de 1.5 graus)
    print("[*] Executando Geoprocessing.buffer_layer (1.5 graus)...")
    buffers = Geoprocessing.buffer_layer(cities, distance=1.5, output_name="AreasDeInfluencia", num_segments=48)
    print(f"[OK] Buffers gerados: {len(buffers)} poligonos de cobertura.")

    # 3. Camada de Zonas / Polígonos de Regiões
    zones = FeatureLayer("RegiaoSudeste_Box", geometry_type="Polygon")
    sudeste_poly = Polygon([(-48.5, -26.0), (-40.0, -26.0), (-40.0, -18.0), (-48.5, -18.0)])
    zones.add_feature(sudeste_poly, {"ZONE_NAME": "Macrorregiao Sudeste"})

    # 4. Geoprocessamento: Spatial Join (Associação Espacial)
    print("[*] Executando Geoprocessing.spatial_join (identificar cidades no Sudeste)...")
    joined = Geoprocessing.spatial_join(cities, zones, "Capitais_Com_Zona")
    for feat in joined.features.values():
        zona = feat.get("JOIN_ZONE_NAME", "Fora da Zona")
        print(f"   -> {feat.get('NAME')}: {zona}")

    # 5. Índice Espacial (Busca por BoundingBox em O(log N))
    search_env = Envelope(-48.0, -25.0, -42.0, -21.0)
    print(f"\n[*] Consulta no Indice Espacial QuadTree para BoundingBox: {search_env}")
    found = cities.select_by_envelope(search_env)
    print(f"   -> {len(found)} cidades encontradas no quadrante:")
    for f in found:
        print(f"      * {f.get('NAME')} (Lat: {f.geometry.y:.2f}, Lon: {f.geometry.x:.2f})")

    # 6. Estatísticas Descritivas
    stats = Geoprocessing.summary_statistics(cities, "POP")
    print(f"\n[*] Estatisticas de Populacao:")
    print(f"   Total: {stats['sum']:,.0f} hab | Media: {stats['mean']:,.0f} hab | Max: {stats['max']:,.0f} hab")

    # 7. Cartografia & Exportação de Mapa Vetorial SVG
    print("\n[*] Renderizando Mapa Cartografico (SVG)...")
    my_map = Map("Mapa de Cidades e Areas de Influencia - ArcGEO")
    my_map.add_layer(zones, SimpleRenderer(fill="#1e293b", stroke="#475569", stroke_width=2.0, opacity=0.4))
    my_map.add_layer(buffers, SimpleRenderer(fill="#38bdf8", stroke="#0284c7", stroke_width=1.2, opacity=0.25))
    my_map.add_layer(cities, UniqueValueRenderer(
        field="REGION",
        color_map={
            "Sudeste": "#ef4444",
            "Sul": "#10b981",
            "Centro-Oeste": "#f59e0b",
            "Nordeste": "#a855f7"
        }
    ))

    svg_content = my_map.export_svg(width=900, height=650)
    output_svg_path = "map_output.svg"
    with open(output_svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"[OK] Mapa exportado com sucesso: {output_svg_path}")

    # 8. Demonstração de Scripting no Padrão ArcPy
    print("\n[*] Demonstração com Sintaxe Padrão ArcGIS ArcPy:")
    import arcpy
    print(f"   -> arcpy.management.GetCount(cities): {arcpy.management.GetCount(cities)} registros")
    arcpy_buf = arcpy.analysis.Buffer(cities, "ArcPy_Buffer_100km", "100 Kilometers")
    print(f"   -> arcpy.analysis.Buffer: Gerada camada '{arcpy_buf.name}' com {len(arcpy_buf)} feições ({arcpy_buf.esri_geometry_type})")

    filtered = arcpy.management.SelectLayerByAttribute(cities, where_clause="POP > 5000000")
    print(f"   -> arcpy.management.SelectLayerByAttribute (POP > 5M): {[f.get('NAME') for f in filtered]}")

    # 9. Exportação no Formato Padrão ESRI JSON
    esri_json_path = "capitais_esri.json"
    import json
    with open(esri_json_path, "w", encoding="utf-8") as f:
        json.dump(cities.to_esri_json(), f, indent=2)
    print(f"[OK] Camada exportada no formato padrão ESRI FeatureSet JSON: {esri_json_path}")
    print("==================================================")


if __name__ == "__main__":
    main()
