# Sentinela Rural

[🇧🇷 Português](README.md) · **🇬🇧 English**

**The WhatsApp bridge between the environmental agency and the small farmer.** The satellite fills
what is missing in the rural land registry (CAR), translates the pendency into plain rural language,
and generates the package ready for the official SICAR module.

> 🇧🇷 haCARthon · **Challenge 1** — the Rural Environmental Registry (CAR) as a Digital Public Good.
> Support for the **farmer's regularization** — **the farmer accepts**, in the official module. We do
> not rebuild SICAR.

This repository is the **open core** of the solution: the method, the code and the documentation,
**reproducible from public data**. It runs the full flow **for one property** — with no key of ours.

*(CAR = Cadastro Ambiental Rural, Brazil's Rural Environmental Registry. SICAR is its official
system. APP = legally protected riparian/hillside buffers. Legal Reserve = a % of native vegetation
each property must keep, by biome. SIGEF/SNCR = the federal georeferencing & rural-cadastre systems.)*

---

## The problem

The CAR is the country's main environmental-management tool, but it only protects when it is
**correct and validated** — and the bottleneck is the farmer:

- **~6.5 million** registrations await analysis, many with only the perimeter (≈60% have no SIGEF
  parcel) and no environmental layers;
- **920,571** were already analyzed and are frozen, waiting for the farmer to answer a notice they never read.

Same root cause: the small farmer (93.6% of the base), digitally excluded, receives everything in
technical language on a portal they cannot access.

## The solution (the loop)

1. **Agency triggers** — the analyst (or the analysis itself) selects the case and sends the message.
2. **Satellite + translation** — the engine reads the property by satellite, builds the *before/after*,
   and translates the pendency: what to fix, how, by when.
3. **WhatsApp** — the farmer confirms what the satellite found (draws nothing).
4. **Official hand-off** — the system generates an **importable KML/.CAR** → the farmer imports it into
   the official module → submits to SICAR. **We don't rebuild SICAR; the acceptance is theirs.**

## ⚡ Reproduce on a CAR — no login, no license (an example is included)

```bash
pip install -r requirements.txt
python examples/run_one_car.py examples/car.geojson Caatinga
```

`examples/car.geojson` is a **real public perimeter** (Paraíba state, Caatinga biome, ~126 ha) — swap
it for any CAR geometry (download it from the
[SICAR public consultation](https://consultapublica.car.gov.br/publico/imoveis/index)). The script:
pulls the **Sentinel-2 RGB** from AWS Open Data (no GEE, no login), reads **MapBiomas** from the public
bucket, fetches **hydrography from OpenStreetMap** for the APP, applies the rules (APP from river buffer,
Legal Reserve by biome, pre-2008 consolidated use), renders the *before/after*, and exports the
**importable KML**. WhatsApp sending (`sentinela/whatsapp.py`) uses the Meta Cloud API with **your own** key.

![before/after example](examples/saida_antes_depois.png)

### Distinctive layer: SIGEF / SNCR — regularization (public, no CPF)

The CAR is environmental; land-tenure regularization runs through **certified georeferencing (SIGEF)**
and the rural cadastre (SNCR/CCIR). We answer — **with no personal data** — whether the perimeter
coincides with a **SIGEF-certified parcel** and how many **fiscal modules** it has. SIGEF parcels are
**public** ([INCRA Land Acervo](https://acervofundiario.incra.gov.br/)); you download and bring the layer:

```bash
python examples/run_one_car.py examples/car.geojson Caatinga \
       --sigef parcelas_sigef_incra.geojson
# → "sigef": { "certificado_sigef": true, "sobreposicao_pct": 42.8, "n_parcelas": 1 }   (no holder/CPF)
```

Output is deliberately **minimal and identity-free**: the cross by holder/CPF is confidential and stays
**out** (open core). `examples/parcelas_sigef_exemplo.geojson` is illustrative only — download the real
parcels from INCRA.

## Open-core model

> **The core is open and reproducible on a CAR.** The **already-assembled national base** (8.4M CARs,
> 9 layers, 27 states in PostGIS) and the **concurrent operation** over millions of registrations are the
> **team's service** — years of work over public data, not a closed requirement nor a secret algorithm.

In one sentence: **we publish the method; the assembled base and the operation, we don't.** Anyone runs
it on a CAR; running it over the 8.4 million in production is the service.

## Stack — 100% open, no lock-in

| Layer | What we use |
|---|---|
| Satellite imagery | **Sentinel-2 L2A** via AWS Open Data (`earth-search.aws.element84.com`) — no GEE, no login |
| Land use / land cover | **MapBiomas** (public COG on Google Cloud Storage, direct download) |
| Hydrography / boundaries | IBGE, ANA (public shapefiles) · OpenStreetMap (public proxy, BYO) |
| Land cadastre | SNCR, SIGEF, **SICAR public consultation** |
| Geoprocessing | shapely · rasterio · pyproj (pure Python — no system GDAL) |
| Basemap | OpenStreetMap |

**No Google Earth Engine. No paid ArcGIS.** That is the call's Digital Public Good premise.

## Structure

```
sentinela/
  sentinel.py     # Sentinel-2 RGB from AWS Open Data (no GEE)
  mapbiomas.py    # reads the MapBiomas COG (no GEE)
  rivers.py       # public hydrography (OpenStreetMap) for the APP — no base of ours
  diagnose.py     # rules: APP (river buffer), Legal Reserve (by biome), pre-2008 consolidated
  sigef.py        # SIGEF/SNCR: certification + fiscal module (public, no CPF) — distinctive layer
  overlay.py      # before/after image
  export_kml.py   # importable KML/.CAR package for the official module
  whatsapp.py     # Meta Cloud API sending + reference conversation flow
examples/
  run_one_car.py            # runs the full flow on a public CAR (+ --sigef)
  car.geojson               # real public example perimeter (PB, Caatinga)
  parcelas_sigef_exemplo.geojson   # illustrative (download the real one from INCRA)
  saida_antes_depois.png    # example output (no need to run to see it)
  saida_CAR_retificacao.kml
docs/                      # architecture and methodology
```

## License

[MIT](LICENSE) — use, adapt and redistribute. Contributions and adaptations by other states/countries are welcome.
