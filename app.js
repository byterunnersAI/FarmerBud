"use strict";

const CLIMATE_START = "20050901";
const CLIMATE_END = "20251231";
const YEARS = Array.from({ length: 20 }, (_, i) => 2006 + i);
const RAIN_RATIO = 0.8;
const WATER_POINTS_PER_100_MM = 5;
const MAX_DISTANCE_KM = 60;
const MAX_ELEVATION_M = 400;
const PO_VALLEY = [[44.4, 7.6], [45.8, 12.4]];
const MAP_LIMITS = [[43.6, 6.4], [46.6, 13.5]];
const UREA_PER_KG_N = 1 / 0.46;
const OUTLINE = "#3a2a14";

const CROPS = {
  COMMEAT: { name: "Soft wheat", season: [10, 6], gddBase: 0, sowing: [10, 25], days: 240, ph: [6.0, 7.0, 5.5, 8.5], residue: "straw" },
  WHEATD: { name: "Durum wheat", season: [10, 6], gddBase: 0, sowing: [10, 25], days: 240, ph: [6.0, 7.0, 5.5, 8.5], residue: "straw" },
  BARLEY: { name: "Barley", season: [10, 6], gddBase: 0, sowing: [10, 15], days: 235, ph: [6.5, 7.5, 6.0, 8.0], residue: "straw" },
  RAPE: { name: "Rapeseed", season: [9, 6], gddBase: 0, sowing: [9, 15], days: 270, ph: [6.5, 7.6, 5.5, 8.0], residue: "straw" },
  MAIZE: { name: "Maize", season: [4, 9], gddBase: 10, sowing: [4, 10], days: 160, ph: [5.0, 7.0, 4.5, 8.5], residue: "stalks" },
  SOYA: { name: "Soybean", season: [5, 9], gddBase: 10, sowing: [5, 10], days: 140, ph: [5.5, 6.5, 4.5, 8.4], residue: null },
  SUNFLO: { name: "Sunflower", season: [4, 8], gddBase: 10, sowing: [4, 15], days: 130, ph: [6.0, 7.5, 5.5, 8.0], residue: "stalks" },
  SORGH: { name: "Sorghum", season: [5, 9], gddBase: 10, sowing: [5, 15], days: 130, ph: [5.5, 7.5, 5.0, 8.0], residue: "stalks" },
  RICE: { name: "Rice", season: [4, 9], gddBase: 10, sowing: [4, 20], days: 150, ph: [5.5, 7.0, 4.5, 9.0], residue: "straw" },
  BEETS: { name: "Sugar beet", season: [3, 9], gddBase: 5, sowing: [3, 15], days: 170, ph: [6.0, 6.8, 5.5, 8.5], residue: null },
};

const FORBIDDEN = {
  "BEETS|RAPE": "beet cyst nematode (Heterodera schachtii), shared with rapeseed",
  "RAPE|BEETS": "beet cyst nematode (Heterodera schachtii)",
  "RAPE|SOYA": "Sclerotinia, a disease shared by rapeseed, soybean and sunflower",
  "RAPE|SUNFLO": "Sclerotinia, a disease shared by rapeseed, soybean and sunflower",
  "SOYA|RAPE": "Sclerotinia, a disease shared by rapeseed, soybean and sunflower",
  "SOYA|SUNFLO": "Sclerotinia, a disease shared by rapeseed, soybean and sunflower",
  "SUNFLO|RAPE": "Sclerotinia, a disease shared by rapeseed, soybean and sunflower",
  "SUNFLO|SOYA": "Sclerotinia, a disease shared by rapeseed, soybean and sunflower",
  "WHEATD|WHEATD": "durum wheat cannot follow an autumn cereal (Fusarium)",
  "WHEATD|COMMEAT": "durum wheat cannot follow an autumn cereal (Fusarium)",
  "WHEATD|BARLEY": "durum wheat cannot follow an autumn cereal (Fusarium)",
  "RAPE|RAPE": "the same crop two years in a row is not allowed",
  "SOYA|SOYA": "the same crop two years in a row is not allowed",
  "SUNFLO|SUNFLO": "the same crop two years in a row is not allowed",
  "BEETS|BEETS": "nematodes: sugar beet can come back to the same field only after 3 years",
};

const WARNINGS = {
  "MAIZE|MAIZE": "maize after maize is allowed only once in 5 years: rotating crops keeps the corn rootworm away",
  "COMMEAT|COMMEAT": "wheat after wheat is allowed only once in 5 years (Fusarium and take-all)",
  "COMMEAT|BARLEY": "after barley it counts as the same cereal again (Fusarium)",
  "COMMEAT|WHEATD": "after durum wheat it counts as the same cereal again (Fusarium)",
  "BARLEY|BARLEY": "barley after barley is allowed only once in 5 years",
  "BARLEY|COMMEAT": "after wheat it counts as the same cereal again",
  "BARLEY|WHEATD": "after wheat it counts as the same cereal again",
  "SORGH|SORGH": "sorghum after sorghum is allowed only once in 5 years",
  "WHEATD|MAIZE": "Fusarium risk: plough the maize residues into the soil before sowing",
  "WHEATD|SORGH": "Fusarium risk: plough the sorghum residues into the soil before sowing",
};

const TILE_COLORS = ["#a9d07c", "#ecdf7f", "#c3b0ea"];
const PLACES = ["1st", "2nd", "3rd"];

function cropIcon(code) {
  return `<img src="icons/${code.toLowerCase()}.jpg" alt="" width="256" height="256">`;
}

const SMALL_ICONS = {
  water: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 2C9 7 5 10.5 5 15a7 7 0 0 0 14 0c0-4.5-4-8-7-13Z" fill="#6fb3dc" stroke="${OUTLINE}" stroke-width="1.5"/></svg>`,
  nitrogen: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 7h12l1.5 14h-15Z" fill="#f4ead2" stroke="${OUTLINE}" stroke-width="1.5" stroke-linejoin="round"/><path d="M8 3h8l2 4H6Z" fill="#d9c79a" stroke="${OUTLINE}" stroke-width="1.5" stroke-linejoin="round"/><path d="M9.5 18v-6l5 6v-6" fill="none" stroke="${OUTLINE}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  stability: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M3 20.5h18" stroke="${OUTLINE}" stroke-width="1.6" stroke-linecap="round"/><path d="M4 15l4-4 4 3 4-6 4 2" fill="none" stroke="#96140c" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
};

const PIN_SVG = `<svg viewBox="0 0 40 50" aria-hidden="true" focusable="false"><ellipse cx="20" cy="44" rx="14" ry="4.5" fill="none" stroke="#fff6e0" stroke-width="2.5"/><path d="M20 1C11.7 1 5 7.6 5 15.8 5 27 20 43 20 43S35 27 35 15.8C35 7.6 28.3 1 20 1Z" fill="#e0201b" stroke="#3a0a07" stroke-width="2"/><circle cx="20" cy="15.5" r="5.5" fill="#fff6e0"/></svg>`;

let MODELS = null;
let map = null;
let marker = null;
let point = null;
let pointElevation = null;
let elevationRequest = 0;
let busy = false;
let lastResult = null;

class UserError extends Error {}

const $ = (id) => document.getElementById(id);

document.addEventListener("DOMContentLoaded", start);

async function start() {
  setupMap();
  setupForm();
  try {
    const answer = await fetch("models.json");
    if (!answer.ok) throw new Error(`models.json: HTTP ${answer.status}`);
    MODELS = await answer.json();
  } catch (error) {
    showStatus("Could not load the neural networks (models.json). Please reload the page.", "error");
    console.error(error);
  }
}

function setupMap() {
  map = L.map("map", { minZoom: 6, maxZoom: 18, maxBounds: MAP_LIMITS, maxBoundsViscosity: 1 });
  map.fitBounds(PO_VALLEY);
  map.attributionControl.setPrefix(false);
  const streets = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  });
  const satellite = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
    maxZoom: 19,
    attribution: "Imagery © Esri",
  });
  streets.addTo(map);
  L.control.layers({ Map: streets, Satellite: satellite }, null, { position: "topright" }).addTo(map);
  map.on("click", (event) => setPoint(event.latlng.lat, event.latlng.lng));
}

async function setPoint(lat, lon) {
  point = { lat: Number(lat.toFixed(4)), lon: Number(lon.toFixed(4)) };
  $("lat").value = point.lat.toFixed(4);
  $("lon").value = point.lon.toFixed(4);
  $("map-coords").textContent = `Lat ${point.lat.toFixed(4)} · Lon ${point.lon.toFixed(4)}`;
  if (marker) {
    marker.setLatLng([point.lat, point.lon]);
  } else {
    const icon = L.divIcon({ className: "pin", html: PIN_SVG, iconSize: [40, 50], iconAnchor: [20, 44] });
    marker = L.marker([point.lat, point.lon], { icon, keyboard: false }).addTo(map);
  }
  if (lastResult && !busy) showStatus("New location: press “Find my best crops” to update the results.", "info");
  pointElevation = null;
  $("elevation").value = "…";
  const request = ++elevationRequest;
  try {
    const elevation = await getElevation(point.lat, point.lon);
    if (request !== elevationRequest) return;
    pointElevation = elevation;
    $("elevation").value = `${Math.round(elevation)} m`;
  } catch (error) {
    if (request === elevationRequest) $("elevation").value = "n/a";
  }
}

function pointFromInputs() {
  const lat = parseNumber($("lat").value);
  const lon = parseNumber($("lon").value);
  if (Number.isNaN(lat) || Number.isNaN(lon)) return;
  if (lat < MAP_LIMITS[0][0] || lat > MAP_LIMITS[1][0] || lon < MAP_LIMITS[0][1] || lon > MAP_LIMITS[1][1]) {
    showStatus("These coordinates are outside the Po Valley: latitude must be about 44-46 and longitude about 7-13.", "error");
    return;
  }
  setPoint(lat, lon);
  map.setView([lat, lon], Math.max(map.getZoom(), 11));
}

function parseNumber(text) {
  const clean = text.trim().replace(",", ".");
  if (clean === "") return NaN;
  return Number(clean);
}

function setupForm() {
  $("lat").addEventListener("change", pointFromInputs);
  $("lon").addEventListener("change", pointFromInputs);
  $("ph-toggle").addEventListener("change", () => {
    $("ph").disabled = !$("ph-toggle").checked;
    if ($("ph-toggle").checked) $("ph").focus();
  });
  $("find").addEventListener("click", runAnalysis);
  $("podium").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-index]");
    if (button) openWhy(Number(button.dataset.index));
  });
  const dialog = $("why");
  $("why-close").addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
  dialog.addEventListener("close", () => document.body.classList.remove("modal-open"));
}

function readChoices() {
  const previous = $("previous-crop").value;
  const organic = { dk: 0, low: -1, normal: 0, high: 1 }[$("organic-matter").value];
  let ph = null;
  if ($("ph-toggle").checked) {
    ph = parseNumber($("ph").value);
    if (Number.isNaN(ph) || ph < 3.5 || ph > 10) {
      throw new UserError("Please write a soil pH between 3.5 and 10, or switch the pH off.");
    }
  }
  return { previous, organic, ph };
}

function showStatus(message, kind) {
  const status = $("status");
  status.textContent = message;
  status.className = `status status-${kind}`;
}

function setBusy(value) {
  busy = value;
  $("find").disabled = value;
  $("find").textContent = value ? "Working…" : "Find my best crops";
}

async function runAnalysis() {
  if (!MODELS) return showStatus("The neural networks are still loading: try again in a moment.", "error");
  if (!point) return showStatus("First click on your field on the map, or write its coordinates.", "error");
  let choices;
  try {
    choices = readChoices();
  } catch (error) {
    return showStatus(error.message, "error");
  }
  setBusy(true);
  try {
    lastResult = await analyseField(point.lat, point.lon, choices, (message) => showStatus(message, "busy"));
    showResults(lastResult);
    if (lastResult.ranking.length === 0) {
      showStatus("No crop fits your field: read why in the results below.", "error");
    } else {
      showStatus("Done! Here are the best crops for your field.", "ok");
    }
    $("results").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    showStatus(error instanceof UserError ? error.message : "Something went wrong while downloading the data. Check your connection and try again.", "error");
    console.error(error);
  } finally {
    setBusy(false);
  }
}

async function fetchWithTimeout(url, ms) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), ms);
  try {
    return await fetch(url, { signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

async function getElevation(lat, lon) {
  const answer = await fetchWithTimeout(`https://api.open-meteo.com/v1/elevation?latitude=${lat}&longitude=${lon}`, 20000);
  if (!answer.ok) throw new Error(`Open-Meteo: HTTP ${answer.status}`);
  const data = await answer.json();
  return data.elevation[0];
}

async function querySoilGrids(lat, lon) {
  const names = { phh2o: "ph", clay: "argilla_pct", sand: "sabbia_pct", silt: "limo_pct", soc: "carbonio_organico_g_kg", nitrogen: "azoto_g_kg" };
  const thickness = { "0-5cm": 5, "5-15cm": 10, "15-30cm": 15 };
  const url = new URL("https://rest.isric.org/soilgrids/v2.0/properties/query");
  url.searchParams.append("lon", lon.toFixed(4));
  url.searchParams.append("lat", lat.toFixed(4));
  url.searchParams.append("value", "mean");
  for (const name of Object.keys(names)) url.searchParams.append("property", name);
  for (const depth of Object.keys(thickness)) url.searchParams.append("depth", depth);
  let data;
  try {
    const answer = await fetchWithTimeout(url, 25000);
    if (!answer.ok) return { status: "error" };
    data = await answer.json();
  } catch (error) {
    return { status: "error" };
  }
  const soil = {};
  for (const layer of data.properties.layers) {
    const values = layer.depths.filter((d) => d.values.mean !== null).map((d) => [thickness[d.label], d.values.mean]);
    if (values.length === 0) return { status: "nodata" };
    const totalThickness = values.reduce((sum, [w]) => sum + w, 0);
    soil[names[layer.name]] = values.reduce((sum, [w, v]) => sum + w * v, 0) / totalThickness / layer.unit_measure.d_factor;
  }
  return { status: "ok", soil };
}

async function getSoil(lat, lon, nearest, elevation) {
  const moves = elevation <= 0 ? [[0, 0]] : [[0, 0], [0.02, 0], [-0.02, 0], [0, 0.02], [0, -0.02]];
  for (const [dlat, dlon] of moves) {
    const found = await querySoilGrids(lat + dlat, lon + dlon);
    if (found.status === "ok") return { values: found.soil, source: "SoilGrids (ISRIC)" };
    if (found.status === "error") break;
  }
  const columns = ["ph", "argilla_pct", "sabbia_pct", "limo_pct", "carbonio_organico_g_kg", "azoto_g_kg"];
  const values = Object.fromEntries(columns.map((column) => [column, nearest[column]]));
  return { values, source: `nearest FarmerBud point (${nearest.comune_punto})` };
}

async function downloadClimate(lat, lon, elevation) {
  const names = ["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "ALLSKY_SFC_SW_DWN", "RH2M", "WS2M"];
  const url = new URL("https://power.larc.nasa.gov/api/temporal/daily/point");
  url.search = new URLSearchParams({
    parameters: names.join(","), community: "AG", latitude: lat.toFixed(4), longitude: lon.toFixed(4),
    start: CLIMATE_START, end: CLIMATE_END, format: "JSON",
  });
  const answer = await fetchWithTimeout(url, 120000);
  if (!answer.ok) throw new Error(`NASA POWER: HTTP ${answer.status}`);
  const data = await answer.json();
  const cellElevation = data.geometry.coordinates[2];
  const missing = data.header.fill_value;
  const series = data.properties.parameter;
  const dates = Object.keys(series.T2M).sort();
  const correction = -0.56 + ((cellElevation - elevation) * 0.64 * 6.5) / 1000;
  const days = { time: [], doy: [] };
  for (const name of names) days[name] = [];
  for (const date of dates) {
    const year = Number(date.slice(0, 4));
    const month = Number(date.slice(4, 6));
    const day = Number(date.slice(6, 8));
    const time = Date.UTC(year, month - 1, day);
    days.time.push(time);
    days.doy.push(Math.round((time - Date.UTC(year, 0, 0)) / 86400000));
    for (const name of names) {
      const value = series[name][date];
      days[name].push(value === missing ? NaN : value);
    }
  }
  for (const name of ["T2M", "T2M_MAX", "T2M_MIN"]) days[name] = days[name].map((t) => t + correction);
  days.ET0 = days.time.map((_, i) => et0PenmanMonteith(
    days.T2M[i], days.T2M_MAX[i], days.T2M_MIN[i], days.RH2M[i], days.WS2M[i], days.ALLSKY_SFC_SW_DWN[i], lat, elevation, days.doy[i]));
  return days;
}

function et0PenmanMonteith(tmean, tmax, tmin, rh, u2, rs, lat, elevation, doy) {
  const e0 = (t) => 0.6108 * Math.exp((17.27 * t) / (t + 237.3));
  const es = (e0(tmax) + e0(tmin)) / 2;
  const ea = (rh / 100) * es;
  const delta = (4098 * e0(tmean)) / (tmean + 237.3) ** 2;
  const gamma = 0.000665 * 101.3 * ((293 - 0.0065 * elevation) / 293) ** 5.26;
  const phi = (lat * Math.PI) / 180;
  const dr = 1 + 0.033 * Math.cos((2 * Math.PI * doy) / 365);
  const decl = 0.409 * Math.sin((2 * Math.PI * doy) / 365 - 1.39);
  const ws = Math.acos(Math.min(1, Math.max(-1, -Math.tan(phi) * Math.tan(decl))));
  const ra = ((24 * 60) / Math.PI) * 0.082 * dr * (ws * Math.sin(phi) * Math.sin(decl) + Math.cos(phi) * Math.cos(decl) * Math.sin(ws));
  const rso = (0.75 + 2e-5 * elevation) * ra;
  const rnl = ((4.903e-9 * ((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4)) / 2) * (0.34 - 0.14 * Math.sqrt(ea)) * (1.35 * Math.min(1, Math.max(0, rs / rso)) - 0.35);
  const rn = 0.77 * rs - rnl;
  const et0 = (0.408 * delta * rn + ((gamma * 900) / (tmean + 273)) * u2 * (es - ea)) / (delta + gamma * (1 + 0.34 * u2));
  return et0 < 0 ? 0 : et0;
}

function dayRange(days, from, to, inclusive) {
  const indexes = [];
  for (let i = 0; i < days.time.length; i++) {
    const t = days.time[i];
    if (t >= from && (inclusive ? t <= to : t < to)) indexes.push(i);
  }
  return indexes;
}

function sum(values) {
  return values.reduce((total, v) => (Number.isNaN(v) ? total : total + v), 0);
}

function mean(values) {
  const valid = values.filter((v) => !Number.isNaN(v));
  return valid.reduce((total, v) => total + v, 0) / valid.length;
}

function std(values) {
  const valid = values.filter((v) => !Number.isNaN(v));
  const m = mean(valid);
  return Math.sqrt(valid.reduce((total, v) => total + (v - m) ** 2, 0) / (valid.length - 1));
}

function percentile(values, p) {
  const sorted = [...values].sort((a, b) => a - b);
  const position = ((sorted.length - 1) * p) / 100;
  const below = Math.floor(position);
  const above = Math.ceil(position);
  return sorted[below] + (sorted[above] - sorted[below]) * (position - below);
}

function median(values) {
  return percentile(values, 50);
}

function longestDrySpell(rain) {
  let best = 0;
  let current = 0;
  for (const r of rain) {
    current = r < 1 ? current + 1 : 0;
    best = Math.max(best, current);
  }
  return best;
}

function seasonClimate(days, code, year) {
  const [startMonth, endMonth] = CROPS[code].season;
  const from = Date.UTC(startMonth > endMonth ? year - 1 : year, startMonth - 1, 1);
  const to = Date.UTC(year, endMonth, 0);
  const idx = dayRange(days, from, to, true);
  const pick = (name) => idx.map((i) => days[name][i]);
  const rain = sum(pick("PRECTOTCORR"));
  const et0 = sum(pick("ET0"));
  return {
    temp_media: mean(pick("T2M")),
    temp_max_media: mean(pick("T2M_MAX")),
    temp_min_media: mean(pick("T2M_MIN")),
    pioggia_mm: rain,
    et0_mm: et0,
    bilancio_idrico_mm: rain - et0,
    radiazione_MJ_m2: sum(pick("ALLSKY_SFC_SW_DWN")),
    umidita_media: mean(pick("RH2M")),
    vento_medio_m_s: mean(pick("WS2M")),
    gradi_giorno: sum(pick("T2M").map((t) => (Number.isNaN(t) ? NaN : Math.max(0, t - CROPS[code].gddBase)))),
    giorni_sopra_35: pick("T2M_MAX").filter((t) => t > 35).length,
    giorni_gelo: pick("T2M_MIN").filter((t) => t < 0).length,
    periodo_secco_max_giorni: longestDrySpell(pick("PRECTOTCORR")),
  };
}

function cycleWater(days, code, year) {
  const [month, day] = CROPS[code].sowing;
  const sowing = Date.UTC(month >= 8 ? year - 1 : year, month - 1, day);
  const idx = dayRange(days, sowing, sowing + CROPS[code].days * 86400000, false);
  return {
    et0_ciclo_mm: sum(idx.map((i) => days.ET0[i])),
    pioggia_ciclo_mm: sum(idx.map((i) => days.PRECTOTCORR[i])) / RAIN_RATIO,
  };
}

function winterRain(days, year) {
  const idx = dayRange(days, Date.UTC(year - 1, 9, 1), Date.UTC(year, 1, 28), true);
  return sum(idx.map((i) => days.PRECTOTCORR[i])) / RAIN_RATIO;
}

function predict(name, numbers, categories) {
  const m = MODELS[name];
  const inputs = { ...numbers };
  for (const [key, value] of Object.entries(categories)) inputs[`${key}_${value}`] = 1;
  let h = m.columns.map((column, i) => ((inputs[column] ?? 0) - m.mean[i]) / m.scale[i]);
  m.weights.forEach((w, layer) => {
    const out = m.biases[layer].map((b, j) => h.reduce((total, x, i) => total + x * w[i][j], b));
    h = layer < m.weights.length - 1 ? out.map((v) => Math.max(0, v)) : out;
  });
  const result = h[0] * m.out_scale;
  if (!Number.isFinite(result)) throw new UserError("Some climate data for this point are missing: please try a point nearby.");
  return result;
}

function cropForecast(code, days, place, rainWinter, choices) {
  const rows = YEARS.map((year) => ({ ...seasonClimate(days, code, year), ...place }));
  const relative = median(rows.map((row) => predict("yield", row, { cod_coltura: code })));
  const tHa = relative * MODELS.crop_median_t_ha[code];
  const water = YEARS.map((year) => Math.max(0, predict("water", cycleWater(days, code, year), { cod_coltura: code })));
  const nitrogenInputs = { resa_t_ha: tHa, pioggia_ott_feb_mm: rainWinter, sostanza_organica: choices.organic };
  const nitrogenRaw = predict("nitrogen", nitrogenInputs, { coltura_precedente: choices.previous, cod_coltura: code });
  const nitrogenUnknown = predict("nitrogen", nitrogenInputs, { coltura_precedente: "NONE", cod_coltura: code });
  const nitrogen = Math.max(0, Math.round(nitrogenRaw / 5) * 5);
  const stability = MODELS.stability;
  const stabilityInputs = { ...place };
  for (const column of stability.climate) stabilityInputs[column] = mean(rows.map((row) => row[column]));
  for (const column of stability.climate_spread) stabilityInputs[`${column}_std`] = std(rows.map((row) => row[column]));
  const cv = predict("stability", stabilityInputs, { cod_coltura: code });
  return {
    code,
    name: CROPS[code].name,
    relative,
    tHa,
    waterNormal: median(water),
    waterDry: percentile(water, 80),
    nitrogen,
    nitrogenFromPrevious: Math.round((nitrogenRaw - nitrogenUnknown) / 5) * 5,
    cv,
  };
}

function distanceKm(lat1, lon1, lat2, lon2) {
  return 111 * Math.hypot(lat1 - lat2, (lon1 - lon2) * Math.cos((lat1 * Math.PI) / 180));
}

function nearestPoint(lat, lon) {
  let best = null;
  for (const p of MODELS.points) {
    const distance = distanceKm(lat, lon, p.lat, p.lon);
    if (!best || distance < best.distance) best = { point: p, distance };
  }
  return best;
}

function clipSoil(soil) {
  const columns = ["ph", "argilla_pct", "sabbia_pct", "limo_pct", "carbonio_organico_g_kg", "azoto_g_kg"];
  const networkSoil = {};
  const clipped = [];
  for (const column of columns) {
    const values = MODELS.points.map((p) => p[column]);
    const low = Math.min(...values);
    const high = Math.max(...values);
    networkSoil[column] = Math.min(high, Math.max(low, soil[column]));
    if (networkSoil[column] !== soil[column]) clipped.push(column);
  }
  return { networkSoil, clipped };
}

function exclusionReason(code, previous, ph) {
  const rotation = FORBIDDEN[`${code}|${previous}`];
  if (rotation) return rotation;
  const [, , low, high] = CROPS[code].ph;
  if (ph < low || ph > high) return `soil pH ${ph.toFixed(1)} is outside its limits (${low}-${high})`;
  return null;
}

function areaClimate(days) {
  const idx = dayRange(days, Date.UTC(2006, 0, 1), Date.UTC(2025, 11, 31), true);
  const pick = (name) => idx.map((i) => days[name][i]);
  return {
    temperature: mean(pick("T2M")),
    rain: sum(pick("PRECTOTCORR")) / RAIN_RATIO / YEARS.length,
    humidity: mean(pick("RH2M")),
    wind: mean(pick("WS2M")),
  };
}

async function analyseField(lat, lon, choices, log) {
  const nearest = nearestPoint(lat, lon);
  if (nearest.distance > MAX_DISTANCE_KM) {
    throw new UserError("This point is outside the Po Valley lowland that FarmerBud knows: please choose a field in the plain.");
  }
  log("Reading the elevation of your field…");
  const elevation = pointElevation ?? (await getElevation(lat, lon));
  if (elevation > MAX_ELEVATION_M) {
    throw new UserError(`This point is at ${Math.round(elevation)} m: it is not lowland. FarmerBud only knows fields below ${MAX_ELEVATION_M} m.`);
  }
  log("Looking for your soil on SoilGrids…");
  const soilFound = await getSoil(lat, lon, nearest.point, elevation);
  if (elevation <= 0 && !soilFound.source.startsWith("SoilGrids")) {
    throw new UserError("This point looks like sea or lagoon: please choose a field on land.");
  }
  log("Downloading 20 years of climate from NASA POWER (about 10 seconds)…");
  const days = await downloadClimate(lat, lon, elevation);
  log("The 4 neural networks are working…");
  const soil = { ...soilFound.values };
  if (choices.ph !== null) soil.ph = choices.ph;
  const { networkSoil, clipped } = clipSoil(soil);
  const place = { ...networkSoil, lat, lon, quota_m: elevation };
  const rainWinter = median(YEARS.map((year) => winterRain(days, year)));
  const crops = Object.keys(CROPS).map((code) => cropForecast(code, days, place, rainWinter, choices));
  const averageWater = mean(crops.map((crop) => crop.waterNormal));
  for (const crop of crops) {
    crop.yieldPoints = crop.relative * 100;
    crop.waterPoints = ((averageWater - crop.waterNormal) / 100) * WATER_POINTS_PER_100_MM;
    crop.score = crop.yieldPoints + crop.waterPoints;
    crop.excluded = exclusionReason(crop.code, choices.previous, soil.ph);
  }
  const ranking = crops.filter((crop) => !crop.excluded).sort((a, b) => b.score - a.score);
  return { lat, lon, elevation, soil, soilSource: soilFound.source, clipped, area: areaClimate(days), crops, ranking, averageWater, choices };
}

function whole(x) {
  return Math.round(x).toLocaleString("en-US");
}

function about(x) {
  return whole(Math.round(x / 10) * 10);
}

function signedPercent(relative) {
  const percent = Math.round((relative - 1) * 100);
  return percent > 0 ? `+${percent}%` : percent < 0 ? `−${Math.abs(percent)}%` : "±0%";
}

function lower(name) {
  return name.charAt(0).toLowerCase() + name.slice(1);
}

function showResults(result) {
  const top = result.ranking.slice(0, 3);
  $("podium").innerHTML = top.map((crop, i) => `
    <article class="crop-card">
      <div class="crop-tile" style="--tile:${TILE_COLORS[i]}">
        <span class="rank">${PLACES[i]}</span>
        ${cropIcon(crop.code)}
      </div>
      <h3 class="crop-name">${crop.name}</h3>
      <button class="btn-why" type="button" data-index="${i}" aria-label="Why ${crop.name}?">Why?</button>
    </article>`).join("");
  const soil = result.soil;
  $("soil-list").innerHTML = [
    ["Clay", `${Math.round(soil.argilla_pct)}%`],
    ["Sand", `${Math.round(soil.sabbia_pct)}%`],
    ["Silt", `${Math.round(soil.limo_pct)}%`],
    ["Organic carbon", `${soil.carbonio_organico_g_kg.toFixed(1)} g/kg`],
  ].map(([label, value]) => `<li><span>${label}</span><strong>${value}</strong></li>`).join("");
  $("soil-source").textContent = `Top 30 cm of soil · source: ${result.soilSource}`;
  const area = result.area;
  $("area-list").innerHTML = [
    ["Mean temperature", `${area.temperature.toFixed(1)} °C`],
    ["Rain", `${whole(area.rain)} mm/year`],
    ["Mean humidity", `${Math.round(area.humidity)}%`],
    ["Mean wind", `${area.wind.toFixed(1)} m/s`],
  ].map(([label, value]) => `<li><span>${label}</span><strong>${value}</strong></li>`).join("");
  const message = fewCropsMessage(result);
  $("results-message").innerHTML = message;
  $("results-message").hidden = message === "";
  $("facts").hidden = false;
}

function fewCropsMessage(result) {
  const count = result.ranking.length;
  if (count >= 3) return "";
  const ph = result.soil.ph;
  const byPh = result.crops.filter((c) => ph < CROPS[c.code].ph[2] || ph > CROPS[c.code].ph[3]).length;
  const byRotation = result.crops.filter((c) => c.excluded).length - byPh;
  if (count === 0 && byRotation === 0) {
    const lowest = Math.min(...Object.values(CROPS).map((c) => c.ph[2]));
    const highest = Math.max(...Object.values(CROPS).map((c) => c.ph[3]));
    const problem = ph < lowest
      ? `A soil pH of ${ph.toFixed(1)} is too acidic for all 10 crops FarmerBud knows: the lowest pH they can take is ${lowest.toFixed(1)}.`
      : `A soil pH of ${ph.toFixed(1)} is too alkaline for all 10 crops FarmerBud knows: the highest pH they can take is ${highest.toFixed(1)}.`;
    const advice = result.choices.ph !== null
      ? "Check the pH you wrote, or switch it off to use the soil pH from SoilGrids."
      : "Ask an agronomist how to correct your soil before sowing.";
    return `<strong class="alert">No crop fits your field.</strong> ${problem} ${advice}`;
  }
  const excluded = result.crops.length - count;
  const reason = byRotation === 0 ? ` by your soil pH (${ph.toFixed(1)})`
    : byPh === 0 ? " by last year's crop"
    : `, ${byPh} by your soil pH (${ph.toFixed(1)}) and ${byRotation} by last year's crop`;
  if (count === 0) return `<strong class="alert">No crop fits your field.</strong> All ${excluded} crops are ruled out${reason}.`;
  return `<strong>Only ${count === 1 ? "1 crop fits" : "2 crops fit"} your field.</strong> The other ${excluded} are ruled out${reason}. Press <strong>Why?</strong> for the details.`;
}

function openWhy(index) {
  const crop = lastResult.ranking[index];
  $("why-title").textContent = `${crop.name} Info`;
  $("why-body").innerHTML = whyHtml(crop, index, lastResult);
  $("why").scrollTop = 0;
  document.body.classList.add("modal-open");
  $("why").showModal();
}

function statCard(icon, label, value, detail, meaning) {
  return `
    <div class="stat">
      <div class="stat-head">${icon}<span>${label}</span></div>
      <p class="stat-value">${value}</p>
      <p class="stat-detail">${detail}</p>
      <p class="stat-meaning">${meaning}</p>
    </div>`;
}

function whyHtml(crop, index, result) {
  const top = result.ranking.slice(0, 3);
  const avgWater = result.averageWater;
  const previousName = result.choices.previous === "NONE" ? null : CROPS[result.choices.previous].name;
  const steadiness = crop.cv <= 10 ? "Very steady" : crop.cv <= 15 ? "Steady" : crop.cv <= 20 ? "Changes quite a lot" : "Changes a lot";

  let html = `<div class="stat-grid">`;
  html += statCard(cropIcon(crop.code), "Yield", `${crop.tHa.toFixed(1)} t/ha`,
    `${signedPercent(crop.relative)} compared with the Po Valley average`,
    "How much you harvest per hectare in a normal year.");
  html += statCard(SMALL_ICONS.water, "Irrigation water", `${whole(crop.waterNormal)} mm`,
    `${whole(crop.waterDry)} mm in a dry year like 2022`,
    "Water to add on top of rain. 1 mm = 10 m³ per hectare.");
  html += statCard(SMALL_ICONS.nitrogen, "Nitrogen needed", `${whole(crop.nitrogen)} kg N/ha`,
    crop.nitrogen === 0 ? "No nitrogen fertiliser needed" : `about ${about(crop.nitrogen * UREA_PER_KG_N)} kg of urea per hectare`,
    "Fertiliser the crop needs to reach that yield.");
  html += statCard(SMALL_ICONS.stability, "Stability", `${Math.round(crop.cv)}%`,
    `${steadiness}: the harvest changes by about ${Math.round(crop.cv)}% from one year to the next`,
    "Why it matters: a low number means a steadier income, year after year. A high number means some years can go much worse: riskier if you have loans or little savings.");
  html += `</div>`;

  /*
  const above = index > 0 ? result.ranking[index - 1] : null;
  html += `<section class="why-section"><h3>Why is it ${PLACES[index]}?</h3>`;
  const waterSign = crop.waterPoints >= 0 ? "+" : "−";
  html += `<p class="score-line"><span>${Math.round(crop.yieldPoints)} yield points</span> <span>${waterSign} ${Math.abs(crop.waterPoints).toFixed(1)} water points</span> <span>= <strong>${crop.score.toFixed(1)} points</strong></span></p>`;
  html += `<p>Yield counts the most: 100 points is the Po Valley average for this crop. Water adds or removes points: +5 for every 100 mm less than the average crop on your field (${whole(avgWater)} mm), −5 for every 100 mm more.</p>`;
  if (index === 0) {
    const bestYield = result.ranking.reduce((best, c) => (c.relative > best.relative ? c : best));
    if (bestYield === crop) {
      html += `<p>It is the crop that yields best on your field (${signedPercent(crop.relative)}), so it is the safest bet among the 10 crops we checked.</p>`;
    } else {
      html += `<p>${bestYield.name} yields a little more (${signedPercent(bestYield.relative)} against ${signedPercent(crop.relative)}), but it needs ${whole(bestYield.waterNormal - crop.waterNormal)} mm more water: with the water points, ${lower(crop.name)} wins.</p>`;
    }
    if (result.ranking[1]) html += `<p>It is ${(crop.score - result.ranking[1].score).toFixed(1)} points ahead of ${lower(result.ranking[1].name)}.</p>`;
  } else if (crop.relative < above.relative && crop.waterNormal > above.waterNormal) {
    html += `<p>It comes after ${lower(above.name)} because it yields less (${signedPercent(crop.relative)} against ${signedPercent(above.relative)}) and needs more water (${whole(crop.waterNormal)} mm against ${whole(above.waterNormal)} mm).</p>`;
  } else if (crop.relative < above.relative) {
    html += `<p>It comes after ${lower(above.name)} because it yields less (${signedPercent(crop.relative)} against ${signedPercent(above.relative)}). It needs ${whole(above.waterNormal - crop.waterNormal)} mm less water, but that is not enough to catch up.</p>`;
  } else {
    html += `<p>It yields more than ${lower(above.name)} (${signedPercent(crop.relative)} against ${signedPercent(above.relative)}), but it needs ${whole(crop.waterNormal - above.waterNormal)} mm more water, and that costs it points.</p>`;
  }
  html += `</section>`;
  */

  html += `<section class="why-section"><h3>How it helps you save</h3><ul>`;
  if (crop.waterNormal <= avgWater) {
    html += `<li><strong>Water:</strong> it needs ${whole(avgWater - crop.waterNormal)} mm less than the average crop on your field, about ${about((avgWater - crop.waterNormal) * 10)} m³ of water saved per hectare in a normal year, and less pumping.</li>`;
  } else {
    html += `<li><strong>Water:</strong> it needs ${whole(crop.waterNormal - avgWater)} mm more than the average crop on your field (about ${about((crop.waterNormal - avgWater) * 10)} m³ per hectare): plan your irrigation, above all in dry years.</li>`;
  }
  const hungriest = top.reduce((max, c) => (c.nitrogen > max.nitrogen ? c : max));
  if (crop.nitrogen === 0) {
    html += `<li><strong>Nitrogen:</strong> it is a legume: bacteria on its roots take nitrogen from the air, so you buy no nitrogen fertiliser, and the next crop finds some nitrogen in the soil.</li>`;
  } else if (hungriest !== crop) {
    html += `<li><strong>Nitrogen:</strong> compared with ${lower(hungriest.name)}, it needs ${whole(hungriest.nitrogen - crop.nitrogen)} kg N/ha less: about ${about((hungriest.nitrogen - crop.nitrogen) * UREA_PER_KG_N)} kg of urea saved per hectare.</li>`;
  } else {
    html += `<li><strong>Nitrogen:</strong> it needs the most nitrogen of your 3 crops (about ${about(crop.nitrogen * UREA_PER_KG_N)} kg of urea per hectare): its higher harvest has to pay for it.</li>`;
  }
  if (previousName && CROPS[result.choices.previous].residue && crop.nitrogenFromPrevious >= 10) {
    html += `<li><strong>Last year's crop:</strong> ${lower(previousName)} leaves ${CROPS[result.choices.previous].residue} in the soil. Breaking them down uses nitrogen, so the network adds about ${whole(crop.nitrogenFromPrevious)} kg N/ha.</li>`;
  }
  const steadiest = top.reduce((min, c) => (c.cv < min.cv ? c : min));
  const shakiest = top.reduce((max, c) => (c.cv > max.cv ? c : max));
  if (top.length > 1 && steadiest === crop) {
    html += `<li><strong>Risk:</strong> it is the steadiest of your 3 crops, so fewer bad surprises from one year to the next.</li>`;
  } else if (top.length > 1 && shakiest === crop) {
    html += `<li><strong>Risk:</strong> it is the least steady of your 3 crops: keep some savings for the bad years.</li>`;
  }
  html += `</ul></section>`;

  html += `<section class="why-section"><h3>How the 4 numbers fit together</h3><ol>`;
  html += `<li>The <strong>yield</strong> network looks at 20 years of climate on your field and at your soil, and predicts the harvest.</li>`;
  html += `<li>The <strong>nitrogen</strong> network starts from that harvest: a bigger harvest needs more nitrogen. It also uses last year's crop and your soil organic matter.</li>`;
  html += `<li>The <strong>water</strong> network says how much irrigation the crop needs on top of rain to reach that harvest, in a normal and in a dry year.</li>`;
  html += `<li>The <strong>stability</strong> network says how much the harvest changes from year to year.</li>`;
  html += `</ol><p>The ranking adds yield points and water points. Nitrogen and stability help you plan your costs and your risk.</p></section>`;

  const notes = [];
  const warning = WARNINGS[`${crop.code}|${result.choices.previous}`];
  if (warning) notes.push(warning.charAt(0).toUpperCase() + warning.slice(1) + ".");
  const [phLow, phHigh] = CROPS[crop.code].ph;
  if (result.soil.ph < phLow || result.soil.ph > phHigh) notes.push(`Your soil pH (${result.soil.ph.toFixed(1)}) is outside the best range for this crop (${phLow}-${phHigh}).`);
  if (crop.code === "RICE") notes.push("Rice needs a paddy field that can be flooded.");
  if (result.clipped.length > 0) notes.push("Some soil values are outside what the networks have seen, so they used the closest value they know: take the numbers as a rough guide.");
  if (!result.soilSource.startsWith("SoilGrids")) notes.push(`We could not read the soil of your exact field, so we used the ${result.soilSource}.`);
  const groups = {};
  for (const c of result.crops.filter((c) => c.excluded)) (groups[c.excluded] = groups[c.excluded] || []).push(lower(c.name));
  const reasons = Object.entries(groups).map(([reason, names]) => `${names.join(" and ")} (${reason})`);
  if (reasons.length > 0) notes.push(`Not considered for your field: ${reasons.join("; ")}.`);
  if (notes.length > 0) html += `<section class="why-section"><h3>Good to know</h3><ul>${notes.map((n) => `<li>${n}</li>`).join("")}</ul></section>`;
  return html;
}
