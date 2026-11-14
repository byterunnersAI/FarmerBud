"""Impostazioni comuni agli script di 01_Datasets.

Tutto ciò che è una SCELTA del team (province escluse, punto rappresentativo,
stagioni delle colture) sta qui, così si cambia in un posto solo.
"""

from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"          # dati scaricati così come arrivano
INTERIM = HERE / "interim"  # tabelle intermedie già pulite
RAW.mkdir(exist_ok=True)
INTERIM.mkdir(exist_ok=True)

ANNO_INIZIO, ANNO_FINE = 2006, 2025   # 2026 escluso: dati ISTAT ancora provvisori e stagione non conclusa

# Superficie minima (ettari) perché una resa provinciale sia considerata affidabile
SUPERFICIE_MINIMA_HA = 100

# ---------------------------------------------------------------------------
# Province della Pianura Padana (codici ISTAT/NUTS, nomi verificati sul codelist ISTAT CL_ITTER107).
# Per ogni provincia: un comune di PIANURA usato come punto rappresentativo per clima e suolo
# (scelta del team: spesso il capoluogo è in collina o in città).
# Escluse perché quasi interamente montane: Verbano-Cusio-Ossola (ITC14), Sondrio (ITC44), Belluno (ITD33).
# ---------------------------------------------------------------------------
PROVINCE = {
    # Piemonte
    "ITC11": ("Torino", "Piemonte", "Carmagnola"),
    "ITC12": ("Vercelli", "Piemonte", "Vercelli"),
    "ITC13": ("Biella", "Piemonte", "Salussola"),
    "ITC15": ("Novara", "Piemonte", "Novara"),
    "ITC16": ("Cuneo", "Piemonte", "Savigliano"),
    "ITC17": ("Asti", "Piemonte", "Asti"),
    "ITC18": ("Alessandria", "Piemonte", "Alessandria"),
    # Lombardia
    "ITC41": ("Varese", "Lombardia", "Gallarate"),
    "ITC42": ("Como", "Lombardia", "Mariano Comense"),
    "ITC43": ("Lecco", "Lombardia", "Merate"),
    "ITC45": ("Milano", "Lombardia", "Abbiategrasso"),
    "ITC46": ("Bergamo", "Lombardia", "Treviglio"),
    "ITC47": ("Brescia", "Lombardia", "Ghedi"),
    "ITC48": ("Pavia", "Lombardia", "Mortara"),
    "ITC49": ("Lodi", "Lombardia", "Lodi"),
    "ITC4A": ("Cremona", "Lombardia", "Cremona"),
    "ITC4B": ("Mantova", "Lombardia", "Mantova"),
    "IT108": ("Monza e della Brianza", "Lombardia", "Vimercate"),
    # Veneto
    "ITD31": ("Verona", "Veneto", "Isola della Scala"),
    "ITD32": ("Vicenza", "Veneto", "Camisano Vicentino"),
    "ITD34": ("Treviso", "Veneto", "Castelfranco Veneto"),
    "ITD35": ("Venezia", "Veneto", "San Donà di Piave"),
    "ITD36": ("Padova", "Veneto", "Piove di Sacco"),
    "ITD37": ("Rovigo", "Veneto", "Rovigo"),
    # Emilia-Romagna
    "ITD51": ("Piacenza", "Emilia-Romagna", "Piacenza"),
    "ITD52": ("Parma", "Emilia-Romagna", "Fontanellato"),
    "ITD53": ("Reggio nell'Emilia", "Emilia-Romagna", "Correggio"),
    "ITD54": ("Modena", "Emilia-Romagna", "Carpi"),
    "ITD55": ("Bologna", "Emilia-Romagna", "Budrio"),
    "ITD56": ("Ferrara", "Emilia-Romagna", "Ferrara"),
    "ITD57": ("Ravenna", "Emilia-Romagna", "Lugo"),
    "ITD58": ("Forlì-Cesena", "Emilia-Romagna", "Forlì"),
    "ITD59": ("Rimini", "Emilia-Romagna", "Santarcangelo di Romagna"),
}

# ---------------------------------------------------------------------------
# Colture (codici ISTAT verificati sul codelist del dataflow 101_1015_DF_DCSP_COLTIVAZIONI_2).
# stagione = (mese di inizio, mese di fine). Se inizio > fine, la stagione parte
# nell'anno PRIMA del raccolto (colture autunno-vernine).
# Stagioni e base dei gradi-giorno: approssimazione del team, da rivedere se serve.
# kc_mid: coefficiente colturale a metà stagione, FAO-56 Tabella 12 (intervalli -> valore centrale).
# ---------------------------------------------------------------------------
COLTURE = {
    "COMMEAT": dict(nome="frumento tenero", stagione=(10, 6), gdd_base=0, kc_mid=1.15, kc_fonte="Wheat 1.15"),
    "WHEATD": dict(nome="frumento duro", stagione=(10, 6), gdd_base=0, kc_mid=1.15, kc_fonte="Wheat 1.15"),
    "BARLEY": dict(nome="orzo", stagione=(10, 6), gdd_base=0, kc_mid=1.15, kc_fonte="Barley 1.15"),
    "RAPE": dict(nome="colza", stagione=(9, 6), gdd_base=0, kc_mid=1.075, kc_fonte="Rapeseed, Canola 1.0-1.15"),
    "MAIZE": dict(nome="mais", stagione=(4, 9), gdd_base=10, kc_mid=1.20, kc_fonte="Maize, Field (grain) 1.20"),
    "SOYA": dict(nome="soia", stagione=(5, 9), gdd_base=10, kc_mid=1.15, kc_fonte="Soybeans 1.15"),
    "SUNFLO": dict(nome="girasole", stagione=(4, 8), gdd_base=10, kc_mid=1.075, kc_fonte="Sunflower 1.0-1.15"),
    "SORGH": dict(nome="sorgo", stagione=(5, 9), gdd_base=10, kc_mid=1.05, kc_fonte="Sorghum grain 1.00-1.10"),
    "RICE": dict(nome="riso", stagione=(4, 9), gdd_base=10, kc_mid=1.20, kc_fonte="Rice 1.20"),
    "BEETS": dict(nome="barbabietola da zucchero", stagione=(3, 9), gdd_base=5, kc_mid=1.20, kc_fonte="Sugar Beet 1.20"),
    "LUCERNE": dict(nome="erba medica", stagione=(3, 10), gdd_base=5, kc_mid=0.95, kc_fonte="Alfalfa Hay averaged 0.95"),
}
