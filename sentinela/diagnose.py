"""Regras de diagnóstico do CAR (Lei 12.651/2012 — Código Florestal).

Tudo calculado sobre dados públicos. As regras aqui são o NÚCLEO ABERTO do método:
- APP de curso d'água: faixa de mata ciliar por buffer da hidrografia (art. 4º).
- Reserva Legal: percentual mínimo por bioma (art. 12).
- Área consolidada: uso antrópico anterior a 22/07/2008 (art. 61-A), via MapBiomas 2008.
"""
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

# Reserva Legal mínima por bioma (art. 12). Amazônia Legal tem regra própria (20–80%, ver ZEE).
RL_MINIMA = {
    "Amazônia": 0.80,      # floresta na Amazônia Legal
    "Cerrado": 0.35,       # cerrado na Amazônia Legal; fora dela, 20%
    "Caatinga": 0.20,
    "Mata Atlântica": 0.20,
    "Pampa": 0.20,
    "Pantanal": 0.20,
    "default": 0.20,
}

# Faixa de APP por largura do curso d'água (art. 4º, I).
def app_largura(largura_rio_m: float) -> float:
    if largura_rio_m <= 10:   return 30
    if largura_rio_m <= 50:   return 50
    if largura_rio_m <= 200:  return 100
    if largura_rio_m <= 600:  return 200
    return 500


def app_de_rio(perimetro_geojson, rios_geojson, largura_rio_m=10):
    """APP devida = (buffer do rio pela faixa legal) ∩ imóvel. Retorna (geometria_app, area_ha)."""
    imovel = shape(perimetro_geojson)
    if not rios_geojson:
        return None, 0.0
    rios = unary_union([shape(r) for r in rios_geojson])
    faixa = app_largura(largura_rio_m)
    # buffer em graus aproximado (1 grau ~ 111 km). Para produção, reprojetar para métrico (UTM).
    app = rios.buffer(faixa / 111_000).intersection(imovel)
    if app.is_empty:
        return None, 0.0
    area_ha = app.area * (111_000 ** 2) / 10_000  # graus² → m² → ha (aprox.)
    return mapping(app), round(area_ha, 2)


def reserva_legal(bioma: str, share_nativa_pct: float):
    """Compara a vegetação nativa observada com o mínimo do bioma. Retorna déficit em pontos %."""
    minimo = RL_MINIMA.get(bioma, RL_MINIMA["default"]) * 100
    deficit = max(0.0, minimo - share_nativa_pct)
    return {"minimo_pct": minimo, "nativa_pct": share_nativa_pct, "deficit_pct": round(deficit, 1)}


def diagnosticar(perimetro_geojson, rios_geojson, bioma, shares_hoje, consol_2008_pct, largura_rio_m=10):
    """Diagnóstico consolidado de um CAR. Apoio à decisão — não substitui a análise do órgão."""
    app_geo, app_ha = app_de_rio(perimetro_geojson, rios_geojson, largura_rio_m)
    rl = reserva_legal(bioma, shares_hoje.get("nativa", 0))
    return {
        "app_omitida_ha": app_ha,
        "app_geojson": app_geo,
        "reserva_legal": rl,
        "consolidada_pre_2008_pct": consol_2008_pct,
        "bioma": bioma,
        "nota": "Apoio à decisão (satélite + bases abertas). O aceite da retificação é do produtor, no SICAR.",
    }
