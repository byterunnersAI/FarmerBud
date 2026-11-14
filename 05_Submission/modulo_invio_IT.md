# FarmerBud: risposte per il modulo di invio

*[English version](submission_form_EN.md)* · Il modulo va compilato **in inglese**: copia le risposte dalla versione inglese. Qui sotto la traduzione, per capire cosa scriviamo. Scadenza: **domenica 15 novembre, 23:59 ET = lunedì 16 novembre, 05:59 ora italiana**. Inviate presto una prima versione, poi reinviate: i giudici vedono l'ultima.

| Domanda del modulo | Risposta |
|---|---|
| Titolo del progetto | FarmerBud: quali colture seminare nel mio campo? |
| Partecipiamo come | Team |
| Nome del team | ByteRunners |
| Membri del team | Mattia Gambetti, Amelia Nobile, Alessandra Muça (email e scuola di ognuno vanno nel modulo, non nel repository) |
| Track | AI + Climate |
| Punto di partenza | Un'idea nostra |
| Frase di presentazione | FarmerBud aiuta un piccolo agricoltore della Pianura Padana prendendo la posizione del suo campo, con un clic su una mappa, e restituendo le 5 colture più adatte con resa attesa, acqua di irrigazione, azoto e stabilità negli anni, più consigli in parole semplici. |
| Link al codice | `https://github.com/byterunnersAI/FarmerBud` |
| Link al write-up | `https://github.com/byterunnersAI/FarmerBud#readme` (il README è il write-up) |
| Link al video | link YouTube non in elenco (vedi `04_Presentation/copione_video_IT.md`) |
| Cosa abbiamo aggiunto | Un'idea e un dataset nostri: abbiamo unito rese ISTAT, clima giornaliero NASA POWER e suolo SoilGrids per 33 province di pianura, 10 colture e 20 anni (2006-2025). Abbiamo testato su anni mai visti (2022-2025, compresa la siccità del 2022) e su province lasciate fuori una alla volta, con una domanda nostra: lo strumento mette ancora in classifica bene le colture in un posto mai visto? Sì (49% delle 3 migliori vere contro 41% di una regola semplice e 35% del caso), anche se lì la resa esatta non è migliore della regola semplice. Abbiamo costruito un'app in cui l'agricoltore clicca sul suo campo e riceve consigli in parole semplici. |
| Dataset, modelli e strumenti AI | ISTAT coltivazioni per provincia; API giornaliera NASA POWER; ISRIC SoilGrids v2.0; Open-Meteo (geocoding, quota, controllo del clima); FAO-56 (ET0, coefficienti colturali); Disciplinari di produzione integrata Emilia-Romagna 2021 (azoto, rotazioni); FAO ECOCROP tramite OpenCLIM (pH, tessitura). 4 reti neurali addestrate da noi con scikit-learn (MLPRegressor); pandas, NumPy, matplotlib, ipyleaflet, ipywidgets. Strumenti AI: Claude (Anthropic) tramite Claude Code, usato come assistente di programmazione per script dei dati, notebook e documenti. |
| Siete nuovi all'AI? | ✏️ Da compilare: la vostra risposta |

## Checklist finale (dalla guida dell'hackathon)
- [x] Repository GitHub pubblico creato: https://github.com/byterunnersAI/FarmerBud (tutto tranne `00_Administration/` e i 3 PDF di Veritas, esclusi dal `.gitignore`).
- [x] Link e notebook puntano a `byterunnersAI/FarmerBud`.
- [ ] Aprite ogni link in una **finestra in incognito**: repository, README, i due badge "Open in Colab", video.
- [ ] Su Colab eseguite `2_FarmerBud_app_EN.ipynb` dal badge con *Esegui tutte* e cliccate su un campo: deve funzionare senza caricare niente.
- [ ] Registrate il video (massimo 2 minuti) e caricatelo su YouTube come **non in elenco**.
- [ ] Controllate che nome, email e scuola di ognuno siano scritti giusti nel modulo.
- [ ] Ognuno deve saper spiegare ogni parte del progetto (in finale i giudici fanno domande).
