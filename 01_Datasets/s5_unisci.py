"""5) Unisce rese + clima + suolo nel CSV unico per l'addestramento.

Output:
  dataset_unico.csv   una riga = provincia × anno × coltura
  colture.csv         tabella delle colture (stagione, base gradi-giorno, Kc FAO-56)

Colonne aggiunte:
  resa_relativa = resa / mediana della stessa coltura in tutta la Pianura Padana negli anni 2006-2021
                  (solo anni di TRAIN, per non usare informazioni del periodo di test 2022-2025)
  sospetto      = True se la resa è anomala (meno del 30% o più del 200% della mediana): da controllare, non tolta
"""

import pandas as pd

from config import COLTURE, HERE, INTERIM

ANNO_FINE_TRAIN = 2021

rese = pd.read_csv(INTERIM / "rese.csv")
clima = pd.read_csv(INTERIM / "clima_stagioni.csv")
suolo = pd.read_csv(INTERIM / "suolo.csv")
assert "ph" in suolo and suolo.notna().all().all(), "suolo.csv incompleto: rilancia s4_suolo.py"
punti = pd.read_csv(INTERIM / "punti_province.csv")[["cod_provincia", "comune_punto", "lat", "lon", "quota_m"]]

d = (rese.merge(clima, on=["cod_provincia", "anno", "cod_coltura"], how="left")
         .merge(suolo, on="cod_provincia", how="left")
         .merge(punti, on="cod_provincia", how="left"))

mediana = d[d["anno"] <= ANNO_FINE_TRAIN].groupby("cod_coltura")["resa_t_ha"].median()
d["resa_relativa"] = (d["resa_t_ha"] / d["cod_coltura"].map(mediana)).round(3)
d["sospetto"] = ~d["resa_relativa"].between(0.3, 2.0)
d["periodo"] = d["anno"].map(lambda a: "train" if a <= ANNO_FINE_TRAIN else "test")

d = d.sort_values(["cod_provincia", "cod_coltura", "anno"])
d.to_csv(HERE / "dataset_unico.csv", index=False)

pd.DataFrame([{"cod_coltura": k, "coltura": v["nome"], "mese_inizio": v["stagione"][0], "mese_fine": v["stagione"][1],
               "gdd_base_C": v["gdd_base"], "kc_mid_fao56": v["kc_mid"], "kc_fonte_tabella12": v["kc_fonte"],
               "resa_mediana_padana_2006_2021_t_ha": round(mediana.get(k, float("nan")), 2)}
              for k, v in COLTURE.items()]).to_csv(HERE / "colture.csv", index=False)

# ---- controllo qualità ----
print(f"dataset_unico.csv: {len(d)} righe × {d.shape[1]} colonne")
print(f"Province: {d['cod_provincia'].nunique()} · Colture: {d['cod_coltura'].nunique()} · Anni: {d['anno'].min()}-{d['anno'].max()}")
print(f"Train (≤{ANNO_FINE_TRAIN}): {(d['periodo'] == 'train').sum()} righe · Test: {(d['periodo'] == 'test').sum()} righe")
mancanti = d.isna().sum()
print("Valori mancanti:", mancanti[mancanti > 0].to_dict() or "nessuno")
print(f"Righe sospette (resa anomala): {int(d['sospetto'].sum())}")
print(d[d["sospetto"]][["provincia", "anno", "coltura", "superficie_ha", "resa_t_ha", "resa_relativa"]].to_string(index=False))
print("\nRighe per coltura:")
print(d.groupby("coltura").size().sort_values(ascending=False).to_string())
