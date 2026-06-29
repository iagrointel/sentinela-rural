"""MapBiomas — uso e cobertura do solo a partir do COG público, SEM Google Earth Engine.

Lê os rasters anuais direto do bucket público na Google Cloud Storage via GDAL `/vsicurl`
(leitura por janela, não baixa o país inteiro). Usado para distinguir vegetação nativa,
área consolidada (antropizada) e água — e para comparar 2008 × hoje (consolidada pré-2008).
"""
import os
import numpy as np
import rasterio
from rasterio.warp import transform_geom
from rasterio.windows import from_bounds

os.environ.setdefault("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif")

# Coleção 9 (30 m). Para a Coleção 10 (2024): troque por
# .../collection_10/lulc/coverage/brazil_coverage_{year}.tif
COG = ("/vsicurl/https://storage.googleapis.com/mapbiomas-public/initiatives/"
       "brasil/collection_9/lclu/coverage/brasil_coverage_{year}.tif")

# Agrupamento simplificado das classes MapBiomas (ver legenda oficial p/ o detalhe).
NATIVA = {1, 3, 4, 5, 6, 49, 10, 11, 12, 32, 29, 50, 13}      # floresta + formações naturais
CONSOLIDADA = {14, 15, 18, 19, 39, 20, 40, 62, 41, 36, 46, 47, 48, 9, 21}  # agro/antrópico
AGUA = {26, 33, 31}


def classes_for_bbox(bbox, year=2023):
    """Lê o raster MapBiomas do ano para o bbox (lon/lat). Retorna (array de classes, transform, crs)."""
    href = COG.format(year=year)
    with rasterio.open(href) as src:
        geo = {"type": "Polygon", "coordinates": [[
            (bbox[0], bbox[1]), (bbox[2], bbox[1]),
            (bbox[2], bbox[3]), (bbox[0], bbox[3]), (bbox[0], bbox[1])]]}
        geo = transform_geom("EPSG:4326", src.crs.to_string(), geo)
        minx, miny, maxx, maxy = rasterio.features.bounds(geo)
        win = from_bounds(minx, miny, maxx, maxy, src.transform)
        arr = src.read(1, window=win)
        tr = src.window_transform(win)
    return arr, tr, src.crs


def shares(bbox, year=2023):
    """% de vegetação nativa, consolidada e água na área (proporção dos pixels classificados)."""
    arr, _, _ = classes_for_bbox(bbox, year)
    total = max(arr.size, 1)
    nat = np.isin(arr, list(NATIVA)).sum() / total
    con = np.isin(arr, list(CONSOLIDADA)).sum() / total
    agua = np.isin(arr, list(AGUA)).sum() / total
    return {"nativa": round(nat * 100, 1), "consolidada": round(con * 100, 1), "agua": round(agua * 100, 1)}


def consolidada_pre_2008(bbox):
    """Fração da área que já era consolidada (antrópica) em 2008 — base do art. 61-A do Código Florestal."""
    arr08, _, _ = classes_for_bbox(bbox, 2008)
    return round(float(np.isin(arr08, list(CONSOLIDADA)).mean()) * 100, 1)


if __name__ == "__main__":
    bbox = (-39.52, -5.02, -39.46, -4.97)
    print("hoje:", shares(bbox), "| consolidada em 2008:", consolidada_pre_2008(bbox), "%")
