"""Roda o fluxo completo do Sentinela Rural PARA UM CAR, a partir de dados públicos.

Uso:
    python examples/run_one_car.py caminho/para/car.geojson  [bioma]

Onde car.geojson é a geometria de UM imóvel (baixe no SICAR consulta pública).
Não precisa de nenhuma chave — Sentinel-2 e MapBiomas são públicos.
O envio no WhatsApp é só impresso (descomente para enviar de verdade, com a SUA chave Meta).
"""
import json
import sys

from sentinela import sentinel, mapbiomas, diagnose, overlay, export_kml, whatsapp


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    geojson_path = sys.argv[1]
    bioma = sys.argv[2] if len(sys.argv) > 2 else "Caatinga"

    fc = json.load(open(geojson_path))
    perimetro = fc["features"][0]["geometry"] if fc.get("type") == "FeatureCollection" else fc["geometry"] \
        if fc.get("type") == "Feature" else fc
    from shapely.geometry import shape
    bbox = shape(perimetro).bounds

    print("1) Satélite Sentinel-2 (AWS Open Data, sem GEE)…")
    rgb, when = sentinel.rgb_for_bbox(bbox)
    print(f"   cena de {when}, {rgb.shape}")

    print("2) MapBiomas (COG público, sem GEE)…")
    sh = mapbiomas.shares(bbox)
    consol08 = mapbiomas.consolidada_pre_2008(bbox)
    print(f"   hoje {sh} | consolidada em 2008: {consol08}%")

    print("3) Diagnóstico (regras do Código Florestal)…")
    # rios_geojson viria da hidrografia oficial (IBGE/ANA) recortada ao imóvel — ver docs/metodologia.md
    diag = diagnose.diagnosticar(perimetro, rios_geojson=[], bioma=bioma,
                                 shares_hoje=sh, consol_2008_pct=consol08)
    print("  ", {k: v for k, v in diag.items() if k not in ("app_geojson",)})

    print("4) Imagem antes/depois…")
    overlay.antes_depois(rgb, bbox, perimetro, diag.get("app_geojson"), out_path="antes_depois.png")
    print("   -> antes_depois.png")

    print("5) Pacote KML importável no módulo oficial…")
    export_kml.export_kml("CAR_demo", diag, perimetro, "CAR_retificacao.kml")
    print("   -> CAR_retificacao.kml")

    print("6) Fluxo de conversa (linguagem rural):")
    for m in whatsapp.fluxo_referencia("Seu Raimundo", diag):
        print("   ┃", m.replace("\n", "\n   ┃ "))
    # whatsapp.send_text("55XXXXXXXXXXX", whatsapp.fluxo_referencia("Seu Raimundo", diag)[0])


if __name__ == "__main__":
    main()
