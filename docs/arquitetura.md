# Arquitetura

```
FONTES ABERTAS                INGESTÃO / MÉTODO            SAÍDA                 CANAL
Sentinel-2 (AWS) ─┐
MapBiomas (GCS)  ─┤
Hidrografia IBGE ─┼─►  diagnóstico (este repo)  ─►  antes/depois  ─┬─►  WhatsApp (produtor)
SNCR / SIGEF     ─┤    APP · RL · consolidada       KML/.CAR        └─►  Painel (órgão)
SICAR público    ─┘                                  + dossiê
                                                          │
                                                          ▼
                                              módulo oficial (import) ─► ENVIAR no SICAR
```

## O que está neste repositório (núcleo aberto)
- Acesso a dados públicos (Sentinel-2 via AWS, MapBiomas via COG público) — **sem Google Earth Engine**.
- As regras de diagnóstico (APP, Reserva Legal, consolidada) — o método.
- Render antes/depois, export KML importável, e o fluxo de conversa de referência.
- **Roda para um CAR, com dados públicos, sem nenhuma chave nossa.**

## O que NÃO está aqui (o serviço da equipe)
- A **base nacional consolidada** (8,4M CAR, 9 camadas, 27 estados em PostGIS).
- A **orquestração concorrente** sobre milhões de cadastros, o webhook de produção e a fila.
- A integração com o painel do órgão e a operação em produção.

> Reproduzir num CAR = método (aberto). Rodar nos 8,4 milhões em produção = operação (serviço).

## Hand-off ao SICAR
Não recriamos o SICAR. O módulo de cadastro oficial **importa geometria** (.shp/.zip/.kml/.gpx); geramos
um KML/OGC padrão (`ogr2ogr`) que o produtor importa e envia. **O aceite é sempre dele, no SICAR.**
