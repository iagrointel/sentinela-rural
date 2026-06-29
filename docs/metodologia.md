# Metodologia (Código Florestal — Lei 12.651/2012)

O diagnóstico é **apoio à decisão** sobre dados públicos — não substitui a análise do órgão nem o aceite
do produtor no SICAR.

## APP de curso d'água (art. 4º, I)
Faixa marginal mínima de mata ciliar, pela largura do rio:

| Largura do curso d'água | Faixa de APP |
|---|---|
| até 10 m | 30 m |
| 10–50 m | 50 m |
| 50–200 m | 100 m |
| 200–600 m | 200 m |
| > 600 m | 500 m |

**APP devida = (buffer da hidrografia oficial pela faixa legal) ∩ imóvel.** A hidrografia vem do IBGE/ANA
(bases públicas), recortada ao perímetro. Em produção, reprojetar para UTM (cálculo métrico).

## Reserva Legal (art. 12)
Percentual mínimo de vegetação nativa por bioma. Compara-se o nativo observado (MapBiomas) ao mínimo:

| Bioma | Mínimo |
|---|---|
| Floresta na Amazônia Legal | 80% |
| Cerrado na Amazônia Legal | 35% |
| Demais regiões / biomas | 20% |

Estados da Amazônia Legal com ZEE podem reduzir/ajustar — ver norma estadual.

## Área consolidada (art. 61-A)
Uso antrópico **anterior a 22/07/2008** tem regras próprias de regularização. Detectado comparando a
classe MapBiomas de **2008 × hoje**: o que já era antrópico em 2008 é consolidado; conversão posterior é
passivo/desmatamento.

## Honestidade metodológica
- A hidrografia oficial pode estar defasada (drenagem natural × artificial) — por isso a APP é **apoio à
  decisão**, e pode-se cruzar com a água vista no Sentinel (NDWI) para sinalizar divergências.
- Bases de referência de uso do solo variam de 2 a 2,5 anos; usar a imagem de satélite mais recente
  reduz o erro.
