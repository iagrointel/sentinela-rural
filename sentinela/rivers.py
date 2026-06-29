"""Hidrografia pública para a APP — sem login, sem licença.

Em produção o órgão usa a hidrografia oficial (IBGE BC250 / ANA). Para reproduzir o fluxo em
QUALQUER perímetro sem nenhuma base nossa, este módulo busca os cursos d'água do
OpenStreetMap (Overpass, aberto) na bbox do imóvel. É um proxy público — não substitui a
base oficial certificada.
"""
import json
import urllib.parse
import urllib.request


def rios_publicos(bbox, timeout=25):
    """Retorna uma lista de geometrias GeoJSON (LineString) de cursos d'água na bbox.
    bbox = (minx, miny, maxx, maxy) em graus. Lista vazia se indisponível (degrada com honestidade)."""
    minx, miny, maxx, maxy = bbox
    q = (f'[out:json][timeout:{timeout}];'
         f'(way["waterway"~"river|stream|canal"]({miny},{minx},{maxy},{maxx}););out geom;')
    try:
        req = urllib.request.Request(
            "https://overpass-api.de/api/interpreter",
            data=urllib.parse.urlencode({"data": q}).encode(),
            headers={"User-Agent": "sentinela-rural/openpublic"})
        d = json.loads(urllib.request.urlopen(req, timeout=timeout + 5).read())
    except Exception:
        return []
    rios = []
    for el in d.get("elements", []):
        pts = el.get("geometry", [])
        if len(pts) >= 2:
            rios.append({"type": "LineString", "coordinates": [[p["lon"], p["lat"]] for p in pts]})
    return rios
