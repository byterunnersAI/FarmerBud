"""7) Acqua, azoto e stabilità per ogni provincia e coltura: le colonne della heatmap che non vengono dal modello.

Usa le regole di agronomia.py (fonti in tabelle/FONTI.md) sul clima giornaliero NASA POWER e sulle rese ISTAT.

Output:
  interim/acqua_anni.csv     provincia × coltura × anno, tutto in mm dalla semina al raccolto: ET0, pioggia (corretta),
                             ETc, pioggia efficace, irrigazione; più la pioggia ottobre-febbraio (regola dell'azoto).
                             È anche il dataset della rete neurale dell'acqua (02_AI_Model, rete 2).
  fabbisogni_province.csv    provincia × coltura: resa mediana, stabilità, irrigazione (anno normale e anno secco), azoto
"""

import pandas as pd

from agronomia import AGRO, dose_azoto, fabbisogno_irriguo, pioggia_invernale, stabilita
from config import ANNO_FINE, ANNO_INIZIO, HERE, INTERIM

clima = pd.read_csv(INTERIM / "clima_giornaliero.csv", parse_dates=["date"],
                    usecols=["date", "cod_provincia", "ET0", "PRECTOTCORR"])
colture_acqua = [c for c in AGRO.index if pd.notna(AGRO.loc[c, "durata_giorni"])]

righe = []
for prov, c in clima.groupby("cod_provincia"):
    for anno in range(ANNO_INIZIO, ANNO_FINE + 1):
        p_inv = pioggia_invernale(c, anno)
        for cod in colture_acqua:
            righe.append(dict(cod_provincia=prov, cod_coltura=cod, anno=anno, pioggia_ott_feb_mm=p_inv,
                              **fabbisogno_irriguo(c, cod, anno)))
acqua = pd.DataFrame(righe).round(1)
acqua.to_csv(INTERIM / "acqua_anni.csv", index=False)

d = pd.read_csv(HERE / "dataset_unico.csv")
d = d[~d["sospetto"] & (d["cod_coltura"] != "LUCERNE")]
out = []
for (prov, cod), g in d.groupby(["cod_provincia", "cod_coltura"]):
    a = acqua[(acqua.cod_provincia == prov) & (acqua.cod_coltura == cod)]
    resa = g["resa_t_ha"].median()
    out.append(dict(
        cod_provincia=prov, provincia=g["provincia"].iloc[0], cod_coltura=cod, coltura=g["coltura"].iloc[0],
        anni_dati=len(g), resa_mediana_t_ha=resa, resa_relativa_mediana=g["resa_relativa"].median(),
        **stabilita(g["resa_relativa"]),
        irrigazione_mediana_mm=a["irrigazione_mm"].median(),
        irrigazione_anno_secco_mm=a["irrigazione_mm"].quantile(0.8),  # 1 anno su 5 serve almeno questa acqua
        azoto_kg_ha=dose_azoto(cod, resa, pioggia_ott_feb_mm=a["pioggia_ott_feb_mm"].median()),
    ))
f = pd.DataFrame(out).round(2)
f.to_csv(HERE / "fabbisogni_province.csv", index=False)

print(f"fabbisogni_province.csv: {len(f)} righe (provincia × coltura), valori mancanti: {int(f.isna().sum().sum())}")
print("\nMediana tra le province:")
print(f.groupby("coltura")[["resa_mediana_t_ha", "cv_pct", "anni_scarsi_pct", "irrigazione_mediana_mm",
                            "irrigazione_anno_secco_mm", "azoto_kg_ha"]].median().round(0).to_string())
