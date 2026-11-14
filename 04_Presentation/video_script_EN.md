# FarmerBud: 2-minute demo video script

*[Versione italiana](copione_video_IT.md)* · Structure from the hackathon guide: problem 15 s, demo 60 s, how it works 30 s, next steps 15 s. A screen recording with your voice is enough (OBS, Loom or the computer's recorder). Upload to YouTube as **unlisted** and check the link in a logged-out browser.

**Before recording:** open `02_AI_Model/2_FarmerBud_app_EN.ipynb` in Colab, run all cells once (so the networks are already loaded), scroll to the map. Keep `03_Evaluation/figures/results_vs_baseline.png` open in another tab.

| Time | On screen | What to say |
|---|---|---|
| **0:00-0:15** · The problem | Title "🌱 FarmerBud" at the top of the app | "Every season a small farmer in the Po Valley has to decide what to sow. In the 2022 drought maize lost almost 20% of its yield, while wheat was fine. FarmerBud helps that farmer choose crops that fit their field and today's climate." |
| **0:15-0:30** · Demo, input | Zoom on the map, click on a field near Cremona. The pin and the coordinates appear | "The farmer just clicks on their field. If they want, they say what they grew last year, maize here, and whether they can irrigate." |
| **0:30-0:45** · Demo, waiting | Press **Compute**. The messages appear: elevation, soil, 20 years of climate, the 4 networks | "FarmerBud downloads 20 years of daily climate and the soil for that exact point, and runs our 4 neural networks on every year." |
| **0:45-1:15** · Demo, output | The coloured table, then the advice list | "Here are the 5 best crops. Green is better. Soft wheat yields 4% above the Po Valley average and needs almost no water. Soybean yields well too, needs no nitrogen fertiliser, but in a dry summer like 2022 it would need about 290 mm of irrigation. And because the field had maize, it reminds the farmer to plough in the residues before durum wheat, against Fusarium." |
| **1:15-1:45** · How it works | Switch to `results_vs_baseline.png` | "We joined three public sources: ISTAT yields for 33 provinces and 10 crops over 20 years, NASA POWER climate and SoilGrids soil. We tested on 2022 to 2025, years the networks never saw, and on provinces left out one at a time. Predicting the exact yield of a new place is hard: there our network is level with a simple average. But for ranking crops, which is the farmer's real decision, it gets 49% of the top 3 right, against 41% for the simple rule and 35% by chance." |
| **1:45-2:00** · Next steps | Back to the app table | "Our biggest limit: we only have province averages, not single fields. Next, we want field-level data and future climate scenarios, to show farmers how their best crops will change. FarmerBud is a prototype, not agronomic advice." |

**Tips:** the numbers in the script are those of the example field (45.15 N, 9.95 E, last crop maize, irrigated): if you click elsewhere, read your own. Speak slowly, one main message (the ranking result). If the live run is slow, cut the waiting part in editing or use the example in section 7 of the notebook.
