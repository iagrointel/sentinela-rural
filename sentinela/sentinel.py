"""Sentinel-2 RGB a partir do AWS Open Data — sem Google Earth Engine, sem login.

Usa o catálogo STAC público da Element84 (earth-search) e lê os COGs do bucket aberto
`sentinel-s2-l2a` no S3 (acesso anônimo). Retorna um array RGB (true color) para a área de um CAR.
"""
import os
import numpy as np
import rasterio
from rasterio.warp import transform_geom
from rasterio.features import geometry_mask
from rasterio.windows import from_bounds
from pystac_client import Client

# Leitura anônima dos COGs públicos no S3 da AWS Open Data.
os.environ.setdefault("AWS_NO_SIGN_REQUEST", "YES")
os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
os.environ.setdefault("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif")

STAC = "https://earth-search.aws.element84.com/v1"


def best_scene(bbox, datetime="2023-01-01/2024-12-31", max_cloud=40):
    """Cena Sentinel-2 L2A menos nublada na janela, para o bbox (lon/lat)."""
    cat = Client.open(STAC)
    items = list(
        cat.search(
            collections=["sentinel-2-l2a"],
            bbox=bbox,
            datetime=datetime,
            query={"eo:cloud_cover": {"lt": max_cloud}},
            sortby=[{"field": "properties.eo:cloud_cover", "direction": "asc"}],
            max_items=1,
        ).items()
    )
    if not items:
        raise RuntimeError("Nenhuma cena Sentinel-2 encontrada na janela/área.")
    return items[0]


def rgb_for_bbox(bbox, datetime="2023-01-01/2024-12-31"):
    """Array RGB (H, W, 3) uint8 da melhor cena para o bbox (minx, miny, maxx, maxy em lon/lat)."""
    item = best_scene(bbox, datetime)
    bands = []
    for key in ("red", "green", "blue"):
        href = item.assets[key].href
        with rasterio.open(href) as src:
            geo = {"type": "Polygon", "coordinates": [[
                (bbox[0], bbox[1]), (bbox[2], bbox[1]),
                (bbox[2], bbox[3]), (bbox[0], bbox[3]), (bbox[0], bbox[1])]]}
            geo = transform_geom("EPSG:4326", src.crs.to_string(), geo)
            minx, miny, maxx, maxy = rasterio.features.bounds(geo)
            win = from_bounds(minx, miny, maxx, maxy, src.transform)
            arr = src.read(1, window=win).astype("float32")
        bands.append(arr)
    rgb = np.dstack(bands)
    # esticão simples de contraste (percentis 2–98) para visualização true-color
    lo, hi = np.percentile(rgb, (2, 98))
    rgb = np.clip((rgb - lo) / max(hi - lo, 1e-6), 0, 1)
    return (rgb * 255).astype("uint8"), item.properties.get("datetime")


if __name__ == "__main__":
    # exemplo: um trecho do semiárido cearense
    rgb, when = rgb_for_bbox((-39.52, -5.02, -39.46, -4.97))
    print("RGB", rgb.shape, "cena de", when)
