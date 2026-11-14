"""4) Suolo: SoilGrids v2.0 (ISRIC) nel punto rappresentativo di ogni provincia, senza chiave.

Output:
  raw/soilgrids/<cod_provincia>.json   risposta originale
  interim/suolo.csv                    una riga per provincia, media pesata 0-30 cm

Valori convertiti nelle unità "normali" dividendo per il d_factor indicato da SoilGrids:
pH (-), argilla/sabbia/limo (%), carbonio organico (g/kg), azoto (g/kg).
I comuni sono spesso urbani (mascherati da SoilGrids): si usa il primo punto agricolo valido nei dintorni.
SoilGrids chiede un uso moderato (circa 5 richieste al minuto): lo script aspetta tra una richiesta e l'altra.
"""

import json
import time

import pandas as pd
import requests

from config import INTERIM, RAW

PROPS = ["phh2o", "clay", "sand", "silt", "soc", "nitrogen"]
NOMI = {"phh2o": "ph", "clay": "argilla_pct", "sand": "sabbia_pct", "silt": "limo_pct",
        "soc": "carbonio_organico_g_kg", "nitrogen": "azoto_g_kg"}
DEPTHS = {"0-5cm": 5, "5-15cm": 10, "15-30cm": 15}  # spessore = peso nella media
OUT_DIR = RAW / "soilgrids"
OUT_DIR.mkdir(exist_ok=True)

# I centri abitati sono mascherati da SoilGrids (valori nulli): se il punto del comune è urbano,
# proviamo punti vicini in campagna, a circa 3 e 6 km, e teniamo il primo con dati validi.
SPOSTAMENTI = [(0, 0)] + [(dy * k, dx * k) for k in (0.03, 0.06)
                          for dy, dx in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]]


def interroga(lat, lon):
    for tentativo in range(6):
        r = requests.get("https://rest.isric.org/soilgrids/v2.0/properties/query", timeout=120,
                         params=[("lon", round(lon, 4)), ("lat", round(lat, 4)), ("value", "mean")]
                         + [("property", x) for x in PROPS] + [("depth", x) for x in DEPTHS])
        time.sleep(13)
        if r.status_code == 200:
            return r.json()
        time.sleep(20 * (tentativo + 1))
    raise SystemExit(f"SoilGrids non risponde per {lat},{lon}")


def valido(data):
    return all(any(d["values"]["mean"] is not None for d in layer["depths"]) for layer in data["properties"]["layers"])


punti = pd.read_csv(INTERIM / "punti_province.csv")
rows = []
for p in punti.itertuples():
    f = OUT_DIR / f"{p.cod_provincia}.json"
    data = json.loads(f.read_text()) if f.exists() else None
    if data is None or not valido(data):
        for dy, dx in SPOSTAMENTI:
            data = interroga(p.lat + dy, p.lon + dx)
            if valido(data):
                f.write_text(json.dumps(data))
                break
        else:
            raise SystemExit(f"Nessun punto valido vicino a {p.comune_punto}")
    lon_s, lat_s = data["geometry"]["coordinates"]
    row = {"cod_provincia": p.cod_provincia, "lat_suolo": lat_s, "lon_suolo": lon_s}
    for layer in data["properties"]["layers"]:
        fattore = layer["unit_measure"]["d_factor"]
        vals = [(DEPTHS[d["label"]], d["values"]["mean"]) for d in layer["depths"] if d["values"]["mean"] is not None]
        row[NOMI[layer["name"]]] = sum(w * v for w, v in vals) / sum(w for w, _ in vals) / fattore
    rows.append(row)
    print(p.cod_provincia, p.provincia, {k: round(v, 2) for k, v in row.items() if k != "cod_provincia"}, flush=True)

s = pd.DataFrame(rows).round(4)
s.to_csv(INTERIM / "suolo.csv", index=False)
print(f"Salvato interim/suolo.csv: {len(s)} province, valori mancanti: {int(s.isna().sum().sum())}")
