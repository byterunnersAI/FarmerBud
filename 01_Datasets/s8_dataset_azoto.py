"""8) Dataset per la rete neurale dell'azoto (02_AI_Model, rete 3).

Una riga = provincia × coltura × anno, con la resa vera ISTAT e la pioggia ottobre-febbraio di quell'anno.
La dose di azoto (kg N/ha) è calcolata con le schede dei disciplinari (agronomia.dose_azoto).

Le scelte dell'agricoltore che la scheda considera non esistono nei dati ISTAT, quindi le SIMULIAMO a caso
(con un seme fisso, così il file è sempre uguale): coltura precedente erba medica, sostanza organica del suolo,
residui della coltura precedente interrati. Servono perché la rete impari anche queste regole.

Output: interim/azoto_anni.csv
"""

import numpy as np
import pandas as pd

from agronomia import dose_azoto
from config import HERE, INTERIM

d = pd.read_csv(HERE / "dataset_unico.csv")
d = d[~d["sospetto"] & (d["cod_coltura"] != "LUCERNE")][["cod_provincia", "cod_coltura", "anno", "resa_t_ha"]]
pioggia = pd.read_csv(INTERIM / "acqua_anni.csv")[["cod_provincia", "anno", "pioggia_ott_feb_mm"]].drop_duplicates()
d = d.merge(pioggia, on=["cod_provincia", "anno"], how="left")

caso = np.random.default_rng(42)
d["dopo_medica"] = (caso.random(len(d)) < 0.15).astype(int)          # 15% dei campi viene da un medicaio
d["sostanza_organica"] = caso.choice([-1, 0, 1], size=len(d), p=[0.25, 0.5, 0.25])  # -1 bassa, 0 normale, 1 alta
d["residui_interrati"] = (caso.random(len(d)) < 0.5).astype(int)    # metà interra paglie o stocchi

nomi_so = {-1: "bassa", 0: None, 1: "alta"}
d["azoto_kg_ha"] = [dose_azoto(r.cod_coltura, r.resa_t_ha,
                               precedente="LUCERNE" if r.dopo_medica else None,
                               sostanza_organica=nomi_so[r.sostanza_organica],
                               residui_interrati=bool(r.residui_interrati),
                               pioggia_ott_feb_mm=r.pioggia_ott_feb_mm)
                    for r in d.itertuples()]

d.round(2).to_csv(INTERIM / "azoto_anni.csv", index=False)
print(f"interim/azoto_anni.csv: {len(d)} righe, valori mancanti: {int(d.isna().sum().sum())}")
print(d.groupby("cod_coltura")["azoto_kg_ha"].describe()[["mean", "min", "max"]].round(0).to_string())
