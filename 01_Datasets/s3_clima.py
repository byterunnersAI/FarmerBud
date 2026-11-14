"""3) Clima: dati giornalieri NASA POWER per ogni punto, poi riassunti per STAGIONE DELLA COLTURA.

Perché NASA POWER e non Open-Meteo: 20 anni di dati giornalieri per 33 punti superano il limite
gratuito di Open-Meteo (richieste orarie e giornaliere). NASA POWER è gratuito e senza chiave.

Due correzioni, entrambe da citare nel write-up:
1. QUOTA E CALIBRAZIONE. NASA POWER (MERRA-2) lavora su celle di circa 50 km: vicino alle Alpi la quota media
   della cella è molto più alta del campo (es. Carmagnola 240 m, cella 706 m). La correzione è stata CALIBRATA
   confrontando NASA POWER con Open-Meteo sulle 16 province già scaricate (script s3b_controllo_clima.py):
   T_corretta = T_nasa - 0,56 °C + 4,2 °C ogni 1000 m di differenza di quota (cella - punto).
   Errore residuo medio dopo la calibrazione: circa 0,2 °C. Il gradiente teorico di 6,5 °C/km correggeva troppo.
2. ET0. NASA POWER non fornisce l'evapotraspirazione di riferimento: la calcoliamo con il metodo
   FAO-56 Penman-Monteith (FAO Irrigation and Drainage Paper 56, cap. 3-4) da temperatura, umidità,
   vento a 2 m e radiazione.

Output:
  raw/clima_nasa_power/<cod_provincia>.csv   dati giornalieri originali 2005-09-01 -> 2025-12-31
  interim/clima_giornaliero.csv              tutti i punti, temperature corrette + ET0
  interim/clima_stagioni.csv                 provincia × anno di raccolto × coltura -> feature climatiche
"""

import io
import re
import time

import numpy as np
import pandas as pd
import requests

from config import ANNO_FINE, ANNO_INIZIO, COLTURE, INTERIM, RAW

PARAMS = "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,ALLSKY_SFC_SW_DWN,RH2M,WS2M"
GRADIENTE = 0.64 * 6.5 / 1000  # °C per metro, calibrato su Open-Meteo (vedi sopra)
OFFSET_C = -0.56             # NASA POWER risultava mediamente più caldo di Open-Meteo
OUT_DIR = RAW / "clima_nasa_power"
OUT_DIR.mkdir(exist_ok=True)
punti = pd.read_csv(INTERIM / "punti_province.csv")


def scarica(p):
    f = OUT_DIR / f"{p.cod_provincia}.csv"
    if not f.exists():
        for tentativo in range(5):
            r = requests.get("https://power.larc.nasa.gov/api/temporal/daily/point", timeout=180, params={
                "parameters": PARAMS, "community": "AG", "latitude": p.lat, "longitude": p.lon,
                "start": f"{ANNO_INIZIO - 1}0901", "end": f"{ANNO_FINE}1231", "format": "CSV"})
            if r.status_code == 200:
                f.write_text(r.text)
                break
            time.sleep(20 * (tentativo + 1))
        else:
            raise SystemExit(f"NASA POWER non risponde per {p.cod_provincia}")
        time.sleep(1)
    testo = f.read_text()
    quota_cella = float(re.search(r"=\s*([\d.]+)\s*meters", testo).group(1))
    d = pd.read_csv(io.StringIO(testo.split("-END HEADER-")[1].strip())).replace(-999, np.nan)
    d["date"] = pd.to_datetime(d["YEAR"].astype(str) + d["DOY"].astype(str).str.zfill(3), format="%Y%j")
    return d, quota_cella


def et0_penman_monteith(tmean, tmax, tmin, rh, u2, rs, lat_deg, quota, doy):
    """ET0 giornaliera (mm) secondo FAO-56, equazione 6. rs in MJ/m2/giorno, u2 in m/s."""
    e0 = lambda t: 0.6108 * np.exp(17.27 * t / (t + 237.3))
    es = (e0(tmax) + e0(tmin)) / 2
    ea = rh / 100 * es
    delta = 4098 * e0(tmean) / (tmean + 237.3) ** 2
    pressione = 101.3 * ((293 - 0.0065 * quota) / 293) ** 5.26
    gamma = 0.000665 * pressione
    phi = np.radians(lat_deg)
    dr = 1 + 0.033 * np.cos(2 * np.pi * doy / 365)
    decl = 0.409 * np.sin(2 * np.pi * doy / 365 - 1.39)
    ws = np.arccos(np.clip(-np.tan(phi) * np.tan(decl), -1, 1))
    ra = 24 * 60 / np.pi * 0.0820 * dr * (ws * np.sin(phi) * np.sin(decl) + np.cos(phi) * np.cos(decl) * np.sin(ws))
    rso = (0.75 + 2e-5 * quota) * ra
    rns = 0.77 * rs
    rnl = 4.903e-9 * ((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2 * (0.34 - 0.14 * np.sqrt(ea)) \
        * (1.35 * np.clip(rs / rso, 0, 1) - 0.35)
    rn = rns - rnl
    et0 = (0.408 * delta * rn + gamma * 900 / (tmean + 273) * u2 * (es - ea)) / (delta + gamma * (1 + 0.34 * u2))
    return np.clip(et0, 0, None)


def periodo_secco_max(pioggia, soglia=1.0):
    best = cur = 0
    for secco in (pioggia < soglia):
        cur = cur + 1 if secco else 0
        best = max(best, cur)
    return best


giornalieri, rows = [], []
for p in punti.itertuples():
    d, quota_cella = scarica(p)
    corr = OFFSET_C + (quota_cella - p.quota_m) * GRADIENTE
    for col in ["T2M", "T2M_MAX", "T2M_MIN"]:
        d[col] = d[col] + corr
    d["ET0"] = et0_penman_monteith(d["T2M"], d["T2M_MAX"], d["T2M_MIN"], d["RH2M"], d["WS2M"],
                                   d["ALLSKY_SFC_SW_DWN"], p.lat, p.quota_m, d["DOY"])
    d["cod_provincia"] = p.cod_provincia
    giornalieri.append(d)
    print(f"{p.cod_provincia} {p.provincia:<22} cella {quota_cella:5.0f} m, punto {p.quota_m:4.0f} m "
          f"-> correzione {corr:+.1f} °C, giorni mancanti {int(d['T2M'].isna().sum())}")

    for cod, c in COLTURE.items():
        m0, m1 = c["stagione"]
        for anno in range(ANNO_INIZIO, ANNO_FINE + 1):
            inizio = pd.Timestamp(anno - 1 if m0 > m1 else anno, m0, 1)
            fine = pd.Timestamp(anno, m1, 1) + pd.offsets.MonthEnd(0)
            s = d[(d["date"] >= inizio) & (d["date"] <= fine)]
            pioggia, et0 = s["PRECTOTCORR"].sum(), s["ET0"].sum()
            rows.append(dict(
                cod_provincia=p.cod_provincia, anno=anno, cod_coltura=cod,
                giorni_stagione=len(s),
                temp_media=s["T2M"].mean(), temp_max_media=s["T2M_MAX"].mean(), temp_min_media=s["T2M_MIN"].mean(),
                pioggia_mm=pioggia, et0_mm=et0, bilancio_idrico_mm=pioggia - et0,
                radiazione_MJ_m2=s["ALLSKY_SFC_SW_DWN"].sum(), umidita_media=s["RH2M"].mean(),
                vento_medio_m_s=s["WS2M"].mean(),
                gradi_giorno=np.clip(s["T2M"] - c["gdd_base"], 0, None).sum(),
                giorni_sopra_35=int((s["T2M_MAX"] > 35).sum()),
                giorni_gelo=int((s["T2M_MIN"] < 0).sum()),
                periodo_secco_max_giorni=periodo_secco_max(s["PRECTOTCORR"].values),
            ))

pd.concat(giornalieri).round(3).to_csv(INTERIM / "clima_giornaliero.csv", index=False)
out = pd.DataFrame(rows).round(2)
out.to_csv(INTERIM / "clima_stagioni.csv", index=False)
print(f"Salvato interim/clima_stagioni.csv: {len(out)} righe, valori mancanti: {int(out.isna().sum().sum())}")
