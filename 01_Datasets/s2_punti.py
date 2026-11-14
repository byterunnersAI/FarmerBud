"""2) Coordinate del punto rappresentativo di ogni provincia (Open-Meteo Geocoding, senza chiave).

Output: interim/punti_province.csv
Controlla che il comune trovato stia davvero nella regione giusta e segnala i punti sopra i 350 m.
"""

import time

import pandas as pd
import requests

from config import INTERIM, PROVINCE

rows = []
for cod, (prov, regione, comune) in PROVINCE.items():
    r = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                     params={"name": comune, "count": 10, "language": "it", "countryCode": "IT"}, timeout=30)
    r.raise_for_status()
    hits = [h for h in r.json().get("results", []) if h.get("admin1") == regione]
    if not hits:
        raise SystemExit(f"Comune non trovato in {regione}: {comune}")
    h = hits[0]
    rows.append(dict(cod_provincia=cod, provincia=prov, regione=regione, comune_punto=comune,
                     lat=h["latitude"], lon=h["longitude"], quota_m=h.get("elevation"),
                     provincia_trovata=h.get("admin2")))
    time.sleep(0.2)

p = pd.DataFrame(rows)
p.to_csv(INTERIM / "punti_province.csv", index=False)
print(p.to_string(index=False))
alti = p[p["quota_m"] > 350]
print("\nPunti sopra i 350 m:", ", ".join(alti["comune_punto"]) or "nessuno")
