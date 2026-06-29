"""Imagem antes/depois — o satélite com as camadas sugeridas por cima.

"Antes" = o RGB Sentinel-2 limpo (o que o produtor tinha: só um contorno).
"Depois" = o mesmo satélite com perímetro + APP devida desenhados — a prova visual que facilita o aceite.
"""
from PIL import Image, ImageDraw
import numpy as np


def _to_px(coords, bounds, size):
    minx, miny, maxx, maxy = bounds
    w, h = size
    out = []
    for x, y in coords:
        px = (x - minx) / max(maxx - minx, 1e-9) * w
        py = (maxy - y) / max(maxy - miny, 1e-9) * h  # y invertido
        out.append((px, py))
    return out


def antes_depois(rgb: np.ndarray, bounds, perimetro_geojson, app_geojson=None, out_path="antes_depois.png"):
    """Gera uma imagem lado a lado (antes | depois) a partir do RGB e das geometrias (lon/lat)."""
    h, w, _ = rgb.shape
    base = Image.fromarray(rgb)
    depois = base.copy()
    d = ImageDraw.Draw(depois, "RGBA")

    def poly(geo, outline, fill=None, width=3):
        if not geo:
            return
        rings = geo["coordinates"] if geo["type"] == "Polygon" else [r[0] for r in geo["coordinates"]]
        for ring in (rings if geo["type"] == "Polygon" else rings):
            pts = _to_px(ring, bounds, (w, h))
            d.polygon(pts, outline=outline, fill=fill, width=width)

    if app_geojson:
        poly(app_geojson, outline=(154, 107, 30, 255), fill=(154, 107, 30, 90))  # APP em dourado
    poly(perimetro_geojson, outline=(46, 107, 69, 255), width=4)                  # perímetro em verde

    canvas = Image.new("RGB", (w * 2 + 12, h), (12, 20, 15))
    canvas.paste(base, (0, 0))
    canvas.paste(depois, (w + 12, 0))
    canvas.save(out_path)
    return out_path
