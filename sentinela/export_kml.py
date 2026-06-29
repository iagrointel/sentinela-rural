"""Pacote KML importável no módulo oficial do SICAR.

O módulo de cadastro oficial importa geometria nos formatos .shp/.zip/.kml/.gpx nativamente
(controllers/geometria → toGeoJSON). Geramos um KML/OGC padrão via `ogr2ogr` a partir de um
GeoJSON com as feições (perímetro, APP devida, rio oficial). É o "hand-off": o produtor importa
e envia no SICAR — não submetemos por ele.
"""
import json
import os
import subprocess
import tempfile


def export_kml(cod_imovel: str, diag: dict, perimetro_geojson, out_path: str) -> str:
    feats = [{"type": "Feature", "properties": {"name": "Perímetro do imóvel", "camada": "imovel"},
              "geometry": perimetro_geojson}]
    if diag.get("app_geojson"):
        feats.append({"type": "Feature",
                      "properties": {"name": f"APP devida (~{diag.get('app_omitida_ha')} ha)", "camada": "app"},
                      "geometry": diag["app_geojson"]})
    fc = {"type": "FeatureCollection", "features": feats}

    with tempfile.NamedTemporaryFile("w", suffix=".geojson", delete=False) as tf:
        json.dump(fc, tf)
        gj = tf.name
    try:
        subprocess.run(["ogr2ogr", "-f", "KML", out_path, gj, "-nln", cod_imovel],
                       capture_output=True, check=True)
    finally:
        os.unlink(gj)
    return out_path


if __name__ == "__main__":
    perimetro = {"type": "Polygon", "coordinates": [[
        [-39.50, -5.00], [-39.49, -5.00], [-39.49, -4.99], [-39.50, -4.99], [-39.50, -5.00]]]}
    diag = {"app_omitida_ha": 4.2, "app_geojson": {"type": "Polygon", "coordinates": [[
        [-39.498, -4.998], [-39.494, -4.998], [-39.494, -4.995], [-39.498, -4.995], [-39.498, -4.998]]]}}
    print("KML:", export_kml("CE_demo", diag, perimetro, "CAR_retificacao.kml"))
