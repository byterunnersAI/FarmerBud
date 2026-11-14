"""Regole agronomiche: acqua di irrigazione (FAO-56), dose di azoto, rotazioni, avvisi sul suolo, stabilità.

Legge le tabelle scritte a mano in tabelle/ (fonti in tabelle/FONTI.md).
Lo usano s7_fabbisogni.py e s8_dataset_azoto.py per creare i dataset delle reti 2 (acqua) e 3 (azoto),
che poi imparano a riprodurre queste regole.
"""

import numpy as np
import pandas as pd

from config import HERE

TAB = HERE / "tabelle"
AGRO = pd.read_csv(TAB / "colture_agronomia.csv").set_index("cod_coltura")
AZOTO = pd.read_csv(TAB / "azoto.csv")
ROTAZIONI = pd.read_csv(TAB / "rotazioni.csv")

# La pioggia NASA POWER è in media l'80% di quella Open-Meteo (s3b_controllo_clima.py): per l'acqua la riportiamo su.
RAPPORTO_PIOGGIA_NASA = 0.80

# Acqua del suolo che la coltura usa senza stress (FAO-56 cap. 8: RAW = p × TAW; circa 0,5 × 150 mm per un metro di
# radici in un suolo di medio impasto). Scelta del team, uguale per tutte le colture: alla semina il suolo è pieno.
RISERVA_SUOLO_MM = 80


# ------------------------------------------------------------------ suolo
def classe_tessitura(argilla_pct, sabbia_pct):
    if argilla_pct >= 40:
        return "pesante"
    if sabbia_pct >= 55 and argilla_pct < 20:
        return "leggera"
    return "media"


def carbonio_da_sostanza_organica(sostanza_organica_pct):
    """I referti di laboratorio danno la sostanza organica in %: il modello vuole il carbonio organico in g/kg."""
    return sostanza_organica_pct / 1.724 * 10


def avvisi_suolo(cod, ph, argilla_pct, sabbia_pct):
    r, avvisi = AGRO.loc[cod], []
    if not r.ph_min <= ph <= r.ph_max:
        avvisi.append(("sconsigliata", f"pH {ph:.1f} fuori dai limiti della coltura ({r.ph_min}-{r.ph_max})"))
    elif not r.ph_ottimo_min <= ph <= r.ph_ottimo_max:
        avvisi.append(("attenzione", f"pH {ph:.1f} fuori dall'intervallo ottimale ({r.ph_ottimo_min}-{r.ph_ottimo_max})"))
    classe = classe_tessitura(argilla_pct, sabbia_pct)
    if classe not in r.tessiture_adatte.split("|"):
        avvisi.append(("attenzione", f"suolo {classe}: la coltura preferisce suoli {r.tessiture_adatte.replace('|', ' o ')}"))
    return avvisi


# ------------------------------------------------------------------ acqua
def curva_kc(cod):
    """Kc giorno per giorno (FAO-56, figura 25): fase iniziale piatta, sviluppo in salita, metà piatta, fine in discesa."""
    r = AGRO.loc[cod]
    fasi = np.array([r.giorni_ini_fao, r.giorni_svil_fao, r.giorni_media_fao, r.giorni_finale_fao], dtype=float)
    ini, svil, media, fine = np.round(fasi / fasi.sum() * r.durata_giorni).astype(int)
    fine = int(r.durata_giorni) - ini - svil - media
    return np.concatenate([np.full(ini, r.kc_ini), np.linspace(r.kc_ini, r.kc_mid, svil),
                           np.full(media, r.kc_mid), np.linspace(r.kc_mid, r.kc_end, fine)])


def pioggia_efficace_mensile(p_mm, giorni):
    """Metodo USDA-SCS (FAO CROPWAT) su un mese intero; per i mesi parziali si riporta a 30 giorni e poi indietro."""
    p30 = p_mm * 30 / giorni
    eff = np.where(p30 < 250, p30 * (125 - 0.2 * p30) / 125, 125 + 0.1 * p30)
    return eff * giorni / 30


def date_semina(cod, anno_raccolto):
    mese, giorno = map(int, AGRO.loc[cod, "semina_mm_gg"].split("-"))
    anno = anno_raccolto - 1 if mese >= 8 else anno_raccolto  # semine autunnali: l'anno prima del raccolto
    inizio = pd.Timestamp(anno, mese, giorno)
    return pd.date_range(inizio, periods=int(AGRO.loc[cod, "durata_giorni"]), freq="D")


def fabbisogno_irriguo(clima, cod, anno_raccolto):
    """clima: dati giornalieri di UN punto con colonne date, ET0, PRECTOTCORR.
    Restituisce (mm, dalla semina al raccolto): ET0, pioggia (già corretta), ETc della coltura, pioggia efficace
    e acqua da irrigare."""
    giorni = date_semina(cod, anno_raccolto)
    s = clima.set_index("date").reindex(giorni)
    s["ETc"] = curva_kc(cod) * s["ET0"]
    s["P"] = s["PRECTOTCORR"] / RAPPORTO_PIOGGIA_NASA
    m = s.groupby(s.index.to_period("M")).agg(ETc=("ETc", "sum"), P=("P", "sum"), giorni=("ETc", "size"))
    m["P_eff"] = pioggia_efficace_mensile(m["P"], m["giorni"])
    # Bilancio mese per mese con la riserva del suolo: i mesi piovosi la riempiono, quelli secchi la svuotano;
    # si irriga solo quando la riserva non basta.
    riserva, irrigazione = RISERVA_SUOLO_MM, 0.0
    for etc, p_eff in zip(m["ETc"], m["P_eff"]):
        riserva = min(RISERVA_SUOLO_MM, riserva + p_eff - etc)
        if riserva < 0:
            irrigazione, riserva = irrigazione - riserva, 0.0
    return dict(et0_ciclo_mm=s["ET0"].sum(), pioggia_ciclo_mm=s["P"].sum(),
                etc_mm=m["ETc"].sum(), pioggia_efficace_mm=m["P_eff"].sum(), irrigazione_mm=irrigazione)


def pioggia_invernale(clima, anno_raccolto):
    """Pioggia dal 1 ottobre al 28 febbraio prima del raccolto (regola sulla lisciviazione dell'azoto)."""
    d = clima["date"]
    s = clima[(d >= pd.Timestamp(anno_raccolto - 1, 10, 1)) & (d <= pd.Timestamp(anno_raccolto, 2, 28))]
    return s["PRECTOTCORR"].sum() / RAPPORTO_PIOGGIA_NASA


# ------------------------------------------------------------------ azoto
def dose_azoto(cod, resa_t_ha, precedente=None, medica_oltre_5_anni=False, sostanza_organica=None,
               residui_interrati=False, pioggia_ott_feb_mm=None):
    """Dose di azoto (kg N/ha) con le schede a dose standard dei disciplinari dell'Emilia-Romagna.
    sostanza_organica: None, "bassa" o "alta" (rispetto alle linee guida regionali)."""
    schede = AZOTO[AZOTO.cod_coltura == cod]
    if len(schede) > 1:  # mais: scheda media o alta produzione
        schede = schede.iloc[[int(np.argmin(abs((schede.resa_min_t_ha + schede.resa_max_t_ha) / 2 - resa_t_ha)))]]
    r = schede.iloc[0]
    if r.dose_standard_kg_ha == 0:
        return 0.0
    meno = piu = 0
    if resa_t_ha < r.resa_min_t_ha:
        meno += r.meno_se_resa_bassa
    elif resa_t_ha > r.resa_max_t_ha:
        piu += r.piu_se_resa_alta
    if precedente == "LUCERNE":
        meno += r.meno_dopo_medica_oltre_5_anni if medica_oltre_5_anni else r.meno_dopo_prato_leguminose
    if sostanza_organica == "alta":
        meno += r.meno_sostanza_organica_alta
    elif sostanza_organica == "bassa":
        piu += r.piu_sostanza_organica_bassa
    if residui_interrati:
        piu += r.piu_residui_interrati
    if pioggia_ott_feb_mm is not None and pioggia_ott_feb_mm > 300:
        piu += r.piu_piogge_invernali
    return float(max(0, r.dose_standard_kg_ha - meno + min(piu, r.aumento_massimo)))


# ------------------------------------------------------------------ rotazioni (insetti e malattie)
def controlla_rotazione(cod, precedenti):
    """precedenti: colture degli anni passati, dalla più recente (es. ["MAIZE", "COMMEAT"]).
    Restituisce una lista di (livello, messaggio)."""
    r, avvisi = AGRO.loc[cod], []
    stesso = lambda c: c == cod or (isinstance(r.gruppo_ristoppio, str) and AGRO.loc[c, "gruppo_ristoppio"] == r.gruppo_ristoppio) \
        if c in AGRO.index else False
    if r.ristoppio == "no" and any(stesso(c) for c in precedenti[:int(r.anni_pausa)]):
        avvisi.append(("vietata", f"ristoppio non ammesso: {r.motivo_rotazione}"))
    elif r.ristoppio == "una volta in 5 anni" and precedenti and stesso(precedenti[0]):
        if sum(stesso(c) for c in precedenti[:4]) >= 2:
            avvisi.append(("vietata", f"ristoppio già fatto negli ultimi 5 anni. {r.motivo_rotazione}".strip()))
        else:
            avvisi.append(("attenzione", f"ristoppio ammesso una sola volta in 5 anni. {r.motivo_rotazione}".strip()))
    elif r.ristoppio == "fino a 5 anni di fila":
        di_fila = next((i for i, c in enumerate(precedenti) if c != cod), len(precedenti))
        if di_fila >= 5:
            avvisi.append(("vietata", r.motivo_rotazione))
    for regola in ROTAZIONI[ROTAZIONI.coltura == cod].itertuples():
        if regola.precedente in precedenti[:regola.anni_indietro]:
            avvisi.append((regola.regola, regola.motivo))
    return avvisi


# ------------------------------------------------------------------ stabilità
def stabilita(resa_relativa):
    """Quanto la resa cambia da un anno all'altro: coefficiente di variazione e quota di anni scarsi (< 80% del normale)."""
    s = pd.Series(resa_relativa).dropna()
    if len(s) < 5:  # con meno di 5 anni la stabilità non si può stimare
        return dict(cv_pct=float("nan"), anni_scarsi_pct=float("nan"))
    return dict(cv_pct=100 * s.std() / s.mean(), anni_scarsi_pct=100 * (s < 0.8 * s.median()).mean())
