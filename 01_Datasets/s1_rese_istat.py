"""1) Rese delle colture per provincia (ISTAT).

Output:
  raw/istat_coltivazioni_raw.csv   risposta ISTAT completa (tutte le province d'Italia)
  interim/rese.csv                 provincia × anno × coltura, con superficie, produzione e resa (t/ha)
"""

import io

import pandas as pd
import requests

from config import ANNO_FINE, ANNO_INIZIO, COLTURE, INTERIM, PROVINCE, RAW, SUPERFICIE_MINIMA_HA

URL = (
    "https://esploradati.istat.it/SDMXWS/rest/data/IT1,101_1015_DF_DCSP_COLTIVAZIONI_2,1.0/"
    "A..ART+HP_Q_EXT." + "+".join(COLTURE) + f".ALL?startPeriod={ANNO_INIZIO}"
)
HEADERS = {"Accept": "application/vnd.sdmx.data+csv;version=1.0.0"}

raw_path = RAW / "istat_coltivazioni_raw.csv"
if not raw_path.exists():
    print("Scarico da ISTAT...")
    r = requests.get(URL, headers=HEADERS, timeout=300)
    r.raise_for_status()
    raw_path.write_bytes(r.content)
d = pd.read_csv(raw_path)

d = d[d["REF_AREA"].isin(PROVINCE) & d["TIME_PERIOD"].between(ANNO_INIZIO, ANNO_FINE)]
t = d.pivot_table(index=["REF_AREA", "TIME_PERIOD", "TYPE_OF_CROP"], columns="DATA_TYPE",
                  values="OBS_VALUE", aggfunc="first").reset_index()
t = t.rename(columns={"REF_AREA": "cod_provincia", "TIME_PERIOD": "anno", "TYPE_OF_CROP": "cod_coltura",
                      "ART": "superficie_ha", "HP_Q_EXT": "produzione_q"})

t["provincia"] = t["cod_provincia"].map(lambda c: PROVINCE[c][0])
t["regione"] = t["cod_provincia"].map(lambda c: PROVINCE[c][1])
t["coltura"] = t["cod_coltura"].map(lambda c: COLTURE[c]["nome"])
t["resa_t_ha"] = t["produzione_q"] / t["superficie_ha"] / 10  # quintali -> tonnellate

n0 = len(t)
t = t.dropna(subset=["resa_t_ha"])
t = t[(t["superficie_ha"] >= SUPERFICIE_MINIMA_HA) & (t["resa_t_ha"] > 0)]
print(f"Righe: {n0} -> {len(t)} dopo aver tolto valori mancanti, rese nulle e superfici < {SUPERFICIE_MINIMA_HA} ha")

cols = ["cod_provincia", "provincia", "regione", "anno", "cod_coltura", "coltura",
        "superficie_ha", "produzione_q", "resa_t_ha"]
t[cols].sort_values(["cod_provincia", "cod_coltura", "anno"]).to_csv(INTERIM / "rese.csv", index=False)
print(t.groupby("coltura")["resa_t_ha"].describe()[["count", "min", "50%", "max"]].round(2).to_string())
