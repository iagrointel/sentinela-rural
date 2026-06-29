"""Roda o fluxo completo do Sentinela Rural PARA UM CAR, a partir de dados públicos.

Uso:
    python examples/run_one_car.py examples/car.geojson  [bioma]  [--sigef parcelas_sigef.geojson]

Onde car.geojson é a geometria de UM imóvel (baixe no SICAR consulta pública; um exemplo real
já vem em examples/car.geojson). Não precisa de nenhuma chave — Sentinel-2, MapBiomas e a
hidrografia (OpenStreetMap) são públicos. O envio no WhatsApp é só impresso (descomente para
enviar de verdade, com a SUA chave Meta).
"""
import json
import sys

from sentinela import sentinel, mapbiomas, diagnose, overlay, export_kml, whatsapp, rivers, sigef


def main():
    args = sys.argv[1:]
    sigef_path = None
    if "--sigef" in args:
        i = args.index("--sigef"); sigef_path = args[i + 1]; del args[i:i + 2]
    if not args:
        print(__doc__)
        sys.exit(1)
    geojson_path = args[0]
    bioma = args[1] if len(args) > 1 else "Caatinga"

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

    print("3) Hidrografia pública (OpenStreetMap) para a APP…")
    rios = rivers.rios_publicos(bbox)
    print(f"   {len(rios)} curso(s) d'água no recorte"
          + ("" if rios else " — APP não avaliada (em produção: IBGE BC250)"))

    print("4) Diagnóstico (regras do Código Florestal)…")
    diag = diagnose.diagnosticar(perimetro, rios_geojson=rios, bioma=bioma,
                                 shares_hoje=sh, consol_2008_pct=consol08)
    print("  ", {k: v for k, v in diag.items() if k not in ("app_geojson",)})

    if sigef_path:
        print("4b) SIGEF/SNCR — regularização (parcela certificada pública, sem CPF)…")
        diag["sigef"] = sigef.certificacao_sigef(perimetro, sigef_path)
        print("  ", diag["sigef"])

    print("5) Imagem antes/depois…")
    overlay.antes_depois(rgb, bbox, perimetro, diag.get("app_geojson"), out_path="antes_depois.png")
    print("   -> antes_depois.png")

    print("6) Pacote KML importável no módulo oficial…")
    export_kml.export_kml("CAR_demo", diag, perimetro, "CAR_retificacao.kml")
    print("   -> CAR_retificacao.kml")

    print("7) Fluxo de conversa (linguagem rural):")
    for m in whatsapp.fluxo_referencia("Seu Raimundo", diag):
        print("   ┃", m.replace("\n", "\n   ┃ "))
    # whatsapp.send_text("55XXXXXXXXXXX", whatsapp.fluxo_referencia("Seu Raimundo", diag)[0])


if __name__ == "__main__":
    main()
