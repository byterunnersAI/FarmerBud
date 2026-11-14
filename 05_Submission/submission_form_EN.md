# FarmerBud: answers for the submission form

*[Versione italiana](modulo_invio_IT.md)* · Copy each answer into the form. Deadline: **Sunday 15 November, 11:59 PM ET = Monday 16 November, 05:59 Italian time**. Submit a first version early, then resubmit: judges see the latest one.

| Form question | Answer |
|---|---|
| Project title | FarmerBud: which crops should I sow in my field? |
| Building as | Team |
| Team name | ByteRunners |
| Team members | Mattia Gambetti, Amelia Nobile, Alessandra Muça (add each member's email and school in the form, not in the repository) |
| Track | AI + Climate |
| Starting point | Our own idea |
| One-sentence pitch | FarmerBud helps a small farmer in Italy's Po Valley by taking the location of their field, with a click on a map, and giving back the 5 most suitable crops with expected yield, irrigation water, nitrogen and year-to-year stability, plus advice in plain words. |
| Code link | `https://github.com/byterunnersAI/FarmerBud` |
| Write-up link | `https://github.com/byterunnersAI/FarmerBud#readme` (the README is the write-up) |
| Demo video link | YouTube link, unlisted (see `04_Presentation/video_script_EN.md`) |
| What we added | Our own idea and our own dataset: we joined ISTAT crop yields, NASA POWER daily climate and SoilGrids soil for 33 lowland provinces, 10 crops and 20 years (2006-2025). We tested on years never seen (2022-2025, including the 2022 drought) and on provinces left out one at a time, and asked our own question: does the tool still rank crops well in a place it has never seen? It does (49% of the true top 3 against 41% for a simple rule and 35% by chance), even though the exact yield there is no better than the simple rule. We built an app where the farmer clicks on their field and gets advice in plain words. |
| Datasets, models and AI tools used | ISTAT crops by province; NASA POWER daily API; ISRIC SoilGrids v2.0; Open-Meteo (geocoding, elevation, climate check); FAO-56 (ET0, crop coefficients); Emilia-Romagna integrated production guidelines 2021 (nitrogen, rotations); FAO ECOCROP via OpenCLIM (pH, texture). 4 neural networks trained by us with scikit-learn (MLPRegressor); pandas, NumPy, matplotlib, ipyleaflet, ipywidgets. AI tools: Claude (Anthropic) through Claude Code, used as a coding assistant for the data scripts, notebooks and documents. |
| New to AI? | ✏️ To fill in: your answer |

## Final checklist (from the hackathon guide)
- [x] Public GitHub repository created: https://github.com/byterunnersAI/FarmerBud (everything except `00_Administration/` and the 3 Veritas PDFs, excluded by `.gitignore`).
- [x] Links and notebooks point to `byterunnersAI/FarmerBud`.
- [ ] Open every link in a **private / incognito window**: repository, README, the two "Open in Colab" badges, video.
- [ ] In Colab, run `2_FarmerBud_app_EN.ipynb` from the badge with *Run all* and click on a field: it must work without uploading anything.
- [ ] Record the video (max 2 minutes) and upload it to YouTube as **unlisted**.
- [ ] Check that every teammate's name, email and school are spelled correctly in the form.
- [ ] Every member must be able to explain every part of the project (the judges may ask during the finals).
