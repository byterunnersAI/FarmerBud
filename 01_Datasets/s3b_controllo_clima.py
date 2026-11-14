"""3b) Controllo: il clima NASA POWER (corretto per quota, ET0 calcolata da noi) è coerente con Open-Meteo?

Usa i 16 file Open-Meteo scaricati prima di superare il limite gratuito (raw/clima_openmeteo_controllo/).
Confronta valori annuali per provincia: temperatura media, pioggia totale, ET0 totale.
Utile per il write-up: mostra che la fonte scelta e il calcolo FAO-56 sono affidabili, o dove non lo sono.
"""

import pandas as pd

from config import INTERIM, RAW

nasa = pd.read_csv(INTERIM / "clima_giornaliero.csv", parse_dates=["date"])
righe = []
for f in sorted((RAW / "clima_openmeteo_controllo").glob("*.csv")):
    om = pd.read_csv(f, parse_dates=["date"])
    om["cod_provincia"] = f.stem
    m = om.merge(nasa, on=["cod_provincia", "date"])
    m = m[m["date"].dt.year.between(2006, 2025)]
    a = m.groupby(m["date"].dt.year).agg(
        t_om=("temperature_2m_mean", "mean"), t_nasa=("T2M", "mean"),
        p_om=("precipitation_sum", "sum"), p_nasa=("PRECTOTCORR", "sum"),
        e_om=("et0_fao_evapotranspiration", "sum"), e_nasa=("ET0", "sum"))
    righe.append(dict(
        cod_provincia=f.stem,
        diff_temp_C=(a.t_nasa - a.t_om).mean(),
        corr_temp_giornaliera=m["T2M"].corr(m["temperature_2m_mean"]),
        rapporto_pioggia=(a.p_nasa / a.p_om).mean(),
        rapporto_et0=(a.e_nasa / a.e_om).mean(),
        corr_et0_giornaliera=m["ET0"].corr(m["et0_fao_evapotranspiration"]),
    ))

r = pd.DataFrame(righe).round(2)
print(r.to_string(index=False))
print("\nMedia su tutte le province:")
print(r.drop(columns="cod_provincia").mean().round(2).to_string())
r.to_csv(INTERIM / "controllo_clima_nasa_vs_openmeteo.csv", index=False)
