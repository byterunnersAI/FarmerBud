# 01_Datasets: how FarmerBud's data were built

*[Versione italiana](README_IT.md)*

All data are public and downloaded by these scripts. One row of the main dataset = **one province × one crop × one year** (33 lowland provinces, 10 crops, 2006-2025). File and column names are in Italian (e.g. `resa` = yield, `pioggia` = rain, `suolo` = soil, `azoto` = nitrogen).

## How to rebuild everything
From this folder, in order. Every script reuses the files already downloaded in `raw/`, so the second run is fast.

```bash
python3 s1_rese_istat.py        # ISTAT yields per province
python3 s2_punti.py             # one lowland point per province
python3 s3_clima.py             # NASA POWER daily climate + FAO-56 ET0, summarised per crop season
python3 s3b_controllo_clima.py  # optional: NASA POWER vs Open-Meteo check on 16 provinces
python3 s4_suolo.py             # SoilGrids soil (slow, about 8 minutes: respects the service limits)
python3 s5_unisci.py            # merged CSV + quality report
python3 s6_dataset_modello.py   # dataset of network 1 (yield): reliable rows and useful columns only
python3 s7_fabbisogni.py        # dataset of network 2 (water) with the FAO-56 formula
python3 s8_dataset_azoto.py     # dataset of network 3 (nitrogen) with the official fertilisation sheets
```

The team's choices (excluded provinces, town used as the point, crop seasons) are all in `config.py`.

## Files
| File | Content |
|---|---|
| `dataset_modello.csv` | **Dataset of network 1 (yield) and network 4 (stability).** 4,967 rows × 27 columns: 23 inputs, the target `resa_relativa` and `cod_provincia`, `anno`, `periodo` (only used to split train and test) |
| `interim/acqua_anni.csv` | **Dataset of network 2 (water).** 6,600 rows: ET0 and rain from sowing to harvest, irrigation water from FAO-56 |
| `interim/azoto_anni.csv` | **Dataset of network 3 (nitrogen).** 4,967 rows: yield, winter rain, farmer's choices (simulated), nitrogen dose from the official sheets |
| `dataset_unico.csv` | The full CSV without filters (5,154 rows × 38 columns), for checks and the write-up |
| `colture.csv` | Season, growing degree-day base, FAO-56 Kc and median yield of every crop |
| `fabbisogni_province.csv` | Check: median yield, stability, water and nitrogen per province × crop computed with the rules only |
| `agronomia.py` | The agronomic rules (FAO-56 water, nitrogen, rotations, stability) used to build the datasets of networks 2 and 3 |
| `tabelle/` | Hand-written tables: FAO-56 Kc and stages, nitrogen doses, rotations, pH. Sources in `tabelle/FONTI.md` |
| `interim/` | Intermediate tables: yields, points, daily and seasonal climate, soil |
| `raw/` | Data as they come from the sources (ISTAT, NASA POWER, SoilGrids, Open-Meteo check) |

## Data cleaning
- **Yields:** yield = harvested production ÷ total area (ISTAT). Yields on less than 100 ha are discarded.
- **Provinces:** the 3 almost entirely mountainous ones are excluded (Verbano-Cusio-Ossola, Sondrio, Belluno).
- **Rows removed by `s6`:** alfalfa (177 rows: ISTAT data only from 2020 and inconsistent yields between provinces, probably fresh weight vs hay) and 10 yields that are almost certainly wrong (below 30% or above 200% of the median).
- **Columns removed by `s6`:** those derived from the target (`resa_t_ha`, `superficie_ha`, `produzione_q`), names and duplicates. Do not use them as inputs: it would be *data leakage*.
- **Target:** `resa_relativa` (relative yield) = yield ÷ median of the same crop in 2006-2021. 1.00 = normal year. This way very different crops (maize 10 t/ha, soybean 3 t/ha) can be compared.

## Sources
- ISTAT, *Crops: area and production by province*, dataflow `101_1015_DF_DCSP_COLTIVAZIONI_2`: https://esploradati.istat.it/databrowser/
- NASA POWER, Daily API (AG community): https://power.larc.nasa.gov/docs/services/api/temporal/daily/
- ISRIC SoilGrids v2.0: https://rest.isric.org/soilgrids/v2.0/docs
- Open-Meteo, Geocoding API and Historical Weather API (check only): https://open-meteo.com/
- FAO Irrigation and Drainage Paper 56 (ET0, Kc): https://www.fao.org/4/x0490e/x0490e00.htm
- Emilia-Romagna Region, Integrated production guidelines 2021 (nitrogen, rotations): see `tabelle/FONTI.md`
- FAO ECOCROP (pH, soil texture): see `tabelle/FONTI.md`

## Known limits
- Climate and soil come from **one lowland point per province**, while ISTAT yields are the average of the whole province.
- NASA POWER cells are about 50 km wide: temperature is corrected for elevation with a correction calibrated on Open-Meteo (residual error about 0.2 °C). NASA POWER rain is on average 20% lower than Open-Meteo's: for water we divide it by 0.80.
- Why NASA POWER: 20 years of daily data for 33 points exceed Open-Meteo's free limit.
- Seasons, sowing dates, degree-day bases and the soil water reserve (80 mm) are team approximations.
- Rice water is evapotranspiration only: a flooded paddy needs much more.
- Nitrogen and rotation rules come from the Emilia-Romagna guidelines: the other regions have similar but not identical rules.
