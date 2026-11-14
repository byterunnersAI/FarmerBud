"""6) Dal CSV unico al CSV per addestrare il modello: solo le righe affidabili e solo le colonne utili.

dataset_unico.csv resta completo (serve per i controlli e per il write-up); il modello legge dataset_modello.csv.

Righe tolte:
  - erba medica: dati ISTAT solo 2020-2025 e rese incoerenti tra province (fresca o fieno?)
  - righe "sospetto": rese sotto il 30% o sopra il 200% della mediana, quasi certamente errori
Colonne tolte:
  - derivate dal target (data leakage): resa_t_ha, superficie_ha, produzione_q, sospetto
  - identificativi e nomi: provincia, regione, comune_punto, coltura
  - doppioni: lat_suolo, lon_suolo (≈ lat, lon), giorni_stagione (dipende solo dalla coltura)
Colonne tenute ma NON da usare come feature: cod_provincia, anno, periodo (servono solo per dividere train e test).
"""

import pandas as pd

from config import HERE

SOLO_PER_DIVIDERE = ["cod_provincia", "anno", "periodo"]
FEATURE = ["cod_coltura",
           "temp_media", "temp_max_media", "temp_min_media", "pioggia_mm", "et0_mm", "bilancio_idrico_mm",
           "radiazione_MJ_m2", "umidita_media", "vento_medio_m_s", "gradi_giorno", "giorni_sopra_35",
           "giorni_gelo", "periodo_secco_max_giorni",
           "ph", "argilla_pct", "sabbia_pct", "limo_pct", "carbonio_organico_g_kg", "azoto_g_kg",
           "lat", "lon", "quota_m"]
TARGET = "resa_relativa"

d = pd.read_csv(HERE / "dataset_unico.csv")
n0 = len(d)
medica = d["cod_coltura"] == "LUCERNE"
sospette = d["sospetto"] & ~medica
m = d[~medica & ~d["sospetto"]][SOLO_PER_DIVIDERE + FEATURE + [TARGET]]
m.to_csv(HERE / "dataset_modello.csv", index=False)

print(f"Righe: {n0} -> {len(m)}  (tolte {medica.sum()} di erba medica e {sospette.sum()} sospette)")
print(f"Colonne: {d.shape[1]} -> {m.shape[1]}  ({len(FEATURE)} feature, 1 target, {len(SOLO_PER_DIVIDERE)} solo per dividere)")
print(f"Train: {(m['periodo'] == 'train').sum()} righe · Test: {(m['periodo'] == 'test').sum()} righe · "
      f"Colture: {m['cod_coltura'].nunique()} · Valori mancanti: {int(m.isna().sum().sum())}")
