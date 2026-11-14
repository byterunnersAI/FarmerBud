# Fonti delle tabelle agronomiche

Tabelle scritte a mano dal team. Ogni valore viene da una di queste fonti; dove abbiamo dovuto scegliere, è indicato.

## `azoto.csv`: dose di azoto (kg N/ha)
Regione Emilia-Romagna, *Disciplinari di produzione integrata 2021, Norme tecniche colture erbacee*, schede "Dose standard N-P-K" di ogni coltura.
https://agricoltura.regione.emilia-romagna.it/produzioni-agroalimentari/temi/bio-agro-climambiente/agricoltura-integrata/Collezione-dpi/dpi_2021/norme/erbacee/raccolta-colture-erbacee.pdf

Come si usa una scheda: si parte dalla dose standard (valida per le rese tra `resa_min` e `resa_max`), si toglie o si aggiunge per resa attesa, coltura precedente, sostanza organica, residui interrati e piogge invernali (oltre 300 mm tra 1 ottobre e 28 febbraio). La somma degli aumenti non supera `aumento_massimo`.
Scelte nostre: frumento tenero = varietà panificabili FP/FPS (le più comuni); mais = scheda "media produzione" (6-9 t/ha) o "alta produzione" (10-14 t/ha) a seconda della resa prevista.

## `rotazioni.csv` e colonne di rotazione di `colture_agronomia.csv`
Stesso documento, voce "Avvicendamento colturale" e tabelle di difesa integrata (elateridi, diabrotica, fusariosi, Sclerotinia, nematode a cisti).

## Colonne su acqua in `colture_agronomia.csv`
FAO Irrigation and Drainage Paper 56, https://www.fao.org/4/x0490e/x0490e0b.htm
- `kc_ini`, `kc_mid`, `kc_end`: Tabella 12. Frumento e orzo autunnali: Kc ini 0,70 (frumento invernale su suolo non gelato). Mais, sorgo 0,30; soia 0,40; girasole e colza 0,35: valori di gruppo della Tabella 12. Quando la tabella dà un intervallo usiamo il valore centrale (frumento Kc end 0,30; riso 0,75), tranne il mais: Kc end 0,35, perché in pianura si raccoglie a granella secca.
- `giorni_*_fao`: lunghezza delle 4 fasi dalla Tabella 11 (voce mediterranea quando c'è; colza e orzo: come frumento invernale mediterraneo, la tabella non li riporta). Le fasi vengono riscalate sulla `durata_giorni`.
- `semina_mm_gg` e `durata_giorni`: date tipiche della Pianura Padana scelte dal team (es. frumento seminato dalla seconda metà di ottobre, come consigliato dal disciplinare).
- Pioggia efficace: metodo USDA Soil Conservation Service usato da FAO CROPWAT, su base mensile.
- Riserva del suolo: 80 mm di acqua facilmente utilizzabile (FAO-56 cap. 8, RAW = p × TAW, circa 0,5 × 150 mm per un metro di radici). Scelta del team, uguale per tutte le colture.
- Pioggia NASA POWER divisa per 0,80: è il rapporto medio con Open-Meteo trovato da `s3b_controllo_clima.py`.

## Colonne su suolo in `colture_agronomia.csv`
FAO ECOCROP (`PHOPMN`, `PHOPMX`, `PHMIN`, `PHMAX`, `TEXT`, `DRA`), copia del database distribuita da OpenCLIM: https://github.com/OpenCLIM/ecocrop
Classi di tessitura (scelta nostra): pesante = argilla ≥ 40%; leggera = sabbia ≥ 55% e argilla < 20%; altrimenti media.
