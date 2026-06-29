"""SIGEF / SNCR — a camada distinta do Sentinela (regularização).

O CAR é ambiental; a regularização fundiária do pequeno produtor passa pelo **georreferenciamento
certificado** (SIGEF/INCRA) e pelo cadastro rural (SNCR/CCIR). Aqui respondemos uma pergunta de
regularização, **sem nenhum dado de pessoa**:

  • o perímetro do imóvel coincide com uma **parcela certificada no SIGEF**?  (sim/não + sobreposição)
  • quantos **módulos fiscais** ele tem  (classe do imóvel — pequena/média/grande)

As parcelas certificadas do SIGEF são **públicas** (Acervo Fundiário do INCRA — você baixa a
camada e traz). NÃO usamos titular, CPF, posse ou nome — só geometria. Isso é deliberado: o
cruzamento por identidade (sigilo) é o que NÃO abrimos.

Fonte pública: INCRA Acervo Fundiário / Certificação SIGEF — https://acervofundiario.incra.gov.br/
"""
import json

from shapely.geometry import shape
from shapely.ops import unary_union


def classe_modulo_fiscal(area_ha: float, modulo_fiscal_ha: float | None):
    """Classe do imóvel por módulos fiscais (Lei 8.629/1993). modulo_fiscal_ha é público por
    município (tabela INCRA). Sem ele, retorna só a área."""
    if not modulo_fiscal_ha:
        return {"area_ha": round(area_ha, 1), "modulos_fiscais": None, "classe": None}
    mf = area_ha / modulo_fiscal_ha
    classe = ("minifundio" if mf < 1 else "pequena (1–4 MF)" if mf <= 4
              else "media (4–15 MF)" if mf <= 15 else "grande (>15 MF)")
    return {"area_ha": round(area_ha, 1), "modulos_fiscais": round(mf, 2), "classe": classe}


def certificacao_sigef(perimetro_geojson, parcelas_sigef_path: str):
    """Cruza o perímetro com parcelas certificadas do SIGEF que VOCÊ traz (camada pública do
    INCRA). Saída MÍNIMA e sem identidade: certificado? quanto sobrepõe? quantas parcelas?
    Nunca titular/CPF — o cruzamento por identidade é sigilo e fica de fora (open-core)."""
    imovel = shape(perimetro_geojson)
    d = json.load(open(parcelas_sigef_path))
    feats = d["features"] if d.get("type") == "FeatureCollection" else [d]
    inter = []
    for f in feats:
        try:
            g = shape(f.get("geometry") or f)
        except Exception:
            continue
        if g.is_valid and g.intersects(imovel):
            inter.append(g.intersection(imovel))
    if not inter:
        return {"certificado_sigef": False, "sobreposicao_pct": 0.0, "n_parcelas": 0,
                "nota": "perímetro sem parcela certificada SIGEF na camada fornecida — "
                        "georreferenciamento pode estar pendente (apoio à regularização)."}
    cov = unary_union(inter).area
    pct = round(100 * cov / imovel.area, 1) if imovel.area else 0.0
    return {"certificado_sigef": True, "sobreposicao_pct": pct, "n_parcelas": len(inter),
            "nota": "perímetro coincide com parcela(s) certificada(s) no SIGEF (sem titular/CPF)."}
