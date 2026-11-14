# 01_Datasets: come sono stati costruiti i dati di FarmerBud

*[English version](README.md)*

Tutti i dati sono pubblici e scaricati da questi script. Una riga del dataset principale = **una provincia × una coltura × un anno** (33 province di pianura, 10 colture, 2006-2025).

## Come rigenerare tutto
Da questa cartella, in ordine. Ogni script riusa i file già scaricati in `raw/`, quindi la seconda volta è veloce.

```bash
python3 s1_rese_istat.py        # rese ISTAT per provincia
python3 s2_punti.py             # un punto di pianura per ogni provincia
python3 s3_clima.py             # clima giornaliero NASA POWER + ET0 FAO-56, riassunto per stagione della coltura
python3 s3b_controllo_clima.py  # facoltativo: confronto NASA POWER con Open-Meteo su 16 province
python3 s4_suolo.py             # suolo SoilGrids (lento, circa 8 minuti: rispetta i limiti del servizio)
python3 s5_unisci.py            # CSV unico + controllo qualità
python3 s6_dataset_modello.py   # dataset della rete 1 (resa): solo righe affidabili e colonne utili
python3 s7_fabbisogni.py        # dataset della rete 2 (acqua) con la formula FAO-56
python3 s8_dataset_azoto.py     # dataset della rete 3 (azoto) con le schede dei disciplinari
```

Le scelte del team (province escluse, comune usato come punto, stagioni delle colture) sono tutte in `config.py`.

## File
| File | Contenuto |
|---|---|
| `dataset_modello.csv` | **Dataset della rete 1 (resa) e della rete 4 (stabilità).** 4.967 righe × 27 colonne: 23 input, il target `resa_relativa` e `cod_provincia`, `anno`, `periodo` (servono solo per dividere train e test) |
| `interim/acqua_anni.csv` | **Dataset della rete 2 (acqua).** 6.600 righe: ET0 e pioggia dalla semina al raccolto, acqua da irrigare con FAO-56 |
| `interim/azoto_anni.csv` | **Dataset della rete 3 (azoto).** 4.967 righe: resa, piogge invernali, scelte dell'agricoltore (simulate), dose di azoto dalle schede |
| `dataset_unico.csv` | Il CSV completo senza filtri (5.154 righe × 38 colonne), per controlli e write-up |
| `colture.csv` | Stagione, base dei gradi-giorno, Kc FAO-56 e resa mediana di ogni coltura |
| `fabbisogni_province.csv` | Controllo: resa mediana, stabilità, acqua e azoto per provincia × coltura calcolati con le sole regole |
| `agronomia.py` | Le regole agronomiche (acqua FAO-56, azoto, rotazioni, stabilità) usate per creare i dataset delle reti 2 e 3 |
| `tabelle/` | Tabelle scritte a mano: Kc e fasi FAO-56, dosi di azoto, rotazioni, pH. Fonti in `tabelle/FONTI.md` |
| `interim/` | Tabelle intermedie: rese, punti, clima giornaliero e per stagione, suolo |
| `raw/` | Dati come arrivano dalle fonti (ISTAT, NASA POWER, SoilGrids, Open-Meteo di controllo) |

## Pulizia dei dati
- **Rese:** resa = produzione raccolta ÷ superficie totale (ISTAT). Scartate le rese su meno di 100 ha.
- **Province:** escluse le 3 quasi interamente montane (Verbano-Cusio-Ossola, Sondrio, Belluno).
- **Righe tolte da `s6`:** erba medica (177 righe: dati ISTAT solo dal 2020 e rese incoerenti tra province, forse peso fresco contro fieno) e 10 rese quasi certamente errate (sotto il 30% o sopra il 200% della mediana).
- **Colonne tolte da `s6`:** quelle derivate dal target (`resa_t_ha`, `superficie_ha`, `produzione_q`), i nomi e i doppioni. Non usarle come input: sarebbe *data leakage*.
- **Target:** `resa_relativa` = resa ÷ mediana della stessa coltura nel 2006-2021. 1,00 = anno normale. Così colture molto diverse (mais 10 t/ha, soia 3 t/ha) si possono confrontare.

## Fonti
- ISTAT, *Coltivazioni: superfici e produzione per provincia*, dataflow `101_1015_DF_DCSP_COLTIVAZIONI_2`: https://esploradati.istat.it/databrowser/
- NASA POWER, Daily API (community AG): https://power.larc.nasa.gov/docs/services/api/temporal/daily/
- ISRIC SoilGrids v2.0: https://rest.isric.org/soilgrids/v2.0/docs
- Open-Meteo, Geocoding API e Historical Weather API (solo controllo): https://open-meteo.com/
- FAO Irrigation and Drainage Paper 56 (ET0, Kc): https://www.fao.org/4/x0490e/x0490e00.htm
- Regione Emilia-Romagna, Disciplinari di produzione integrata 2021 (azoto, rotazioni): vedi `tabelle/FONTI.md`
- FAO ECOCROP (pH, tessitura): vedi `tabelle/FONTI.md`

## Limiti noti
- Clima e suolo vengono da **un solo punto di pianura per provincia**, mentre le rese ISTAT sono la media di tutta la provincia.
- NASA POWER ha celle di circa 50 km: la temperatura è corretta per la quota con una correzione calibrata su Open-Meteo (errore residuo circa 0,2 °C). La pioggia NASA POWER è in media il 20% più bassa di quella Open-Meteo: per l'acqua la dividiamo per 0,80.
- Perché NASA POWER: 20 anni di dati giornalieri per 33 punti superano il limite gratuito di Open-Meteo.
- Stagioni, date di semina, basi dei gradi-giorno e riserva d'acqua del suolo (80 mm) sono approssimazioni del team.
- L'acqua del riso è solo l'evapotraspirazione: la risaia sommersa ne richiede molta di più.
- Le regole di azoto e rotazione vengono dai disciplinari dell'Emilia-Romagna: le altre regioni hanno regole simili ma non identiche.
