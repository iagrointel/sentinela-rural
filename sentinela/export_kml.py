"""Pacote KML importável no módulo oficial do SICAR.

O módulo de cadastro oficial importa geometria nos formatos .shp/.zip/.kml/.gpx nativamente.
Geramos um KML/OGC padrão (perímetro + APP devida) em Python puro — SEM nenhuma dependência de
sistema (não precisa de GDAL/ogr2ogr). É o "hand-off": o produtor importa e envia no SICAR —
não submetemos por ele.
"""
from xml.sax.saxutils import escape


def _rings(geom):
    """Lista de anéis [(outer, [inner...]), ...] a partir de Polygon/MultiPolygon GeoJSON."""
    t = geom.get("type")
    if t == "Polygon":
        return [geom["coordinates"]]
    if t == "MultiPolygon":
        return list(geom["coordinates"])
    return []


def _coords(ring):
    # KML quer "lon,lat[,alt]" separados por espaço; fecha o anel se preciso
    pts = [f"{x:.8f},{y:.8f},0" for x, y, *_ in ring]
    if pts and pts[0] != pts[-1]:
        pts.append(pts[0])
    return " ".join(pts)


def _placemark(name, style, geom):
    polys = []
    for poly in _rings(geom):
        if not poly:
            continue
        outer = f"<outerBoundaryIs><LinearRing><coordinates>{_coords(poly[0])}</coordinates></LinearRing></outerBoundaryIs>"
        inners = "".join(
            f"<innerBoundaryIs><LinearRing><coordinates>{_coords(r)}</coordinates></LinearRing></innerBoundaryIs>"
            for r in poly[1:])
        polys.append(f"<Polygon><tessellate>1</tessellate>{outer}{inners}</Polygon>")
    body = polys[0] if len(polys) == 1 else f"<MultiGeometry>{''.join(polys)}</MultiGeometry>"
    return f"<Placemark><name>{escape(name)}</name><styleUrl>#{style}</styleUrl>{body}</Placemark>"


def export_kml(cod_imovel: str, diag: dict, perimetro_geojson, out_path: str) -> str:
    marks = [_placemark("Perímetro do imóvel", "imovel", perimetro_geojson)]
    if diag.get("app_geojson"):
        marks.append(_placemark(f"APP devida (~{diag.get('app_omitida_ha')} ha)", "app", diag["app_geojson"]))
    kml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>'
        f'<name>{escape(cod_imovel)}</name>'
        '<Style id="imovel"><LineStyle><color>ff00ffff</color><width>2</width></LineStyle>'
        '<PolyStyle><fill>0</fill></PolyStyle></Style>'
        '<Style id="app"><LineStyle><color>ff2d2dff</color><width>2</width></LineStyle>'
        '<PolyStyle><color>552d2dff</color></PolyStyle></Style>'
        + "".join(marks) +
        '</Document></kml>')
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(kml)
    return out_path


if __name__ == "__main__":
    perimetro = {"type": "Polygon", "coordinates": [[
        [-39.50, -5.00], [-39.49, -5.00], [-39.49, -4.99], [-39.50, -4.99], [-39.50, -5.00]]]}
    diag = {"app_omitida_ha": 4.2, "app_geojson": {"type": "Polygon", "coordinates": [[
        [-39.498, -4.998], [-39.494, -4.998], [-39.494, -4.995], [-39.498, -4.995], [-39.498, -4.998]]]}}
    print("KML:", export_kml("CE_demo", diag, perimetro, "CAR_retificacao.kml"))
