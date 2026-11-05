"""Build H3 hex scores for the China salmon/trout RAS prospect mockup.

Every geology layer here is a global proxy, to be replaced by the researcher's data.

Usage:
    python -I scripts/build_hexes.py <raw_dir> <farms_csv> <out_dir>
"""
import csv
import json
import sys
from datetime import date
from pathlib import Path

import geopandas as gpd
import h3
import numpy as np
import rasterio
from PIL import Image
from rasterio.windows import from_bounds
from scipy.spatial import cKDTree
from shapely import get_coordinates, segmentize
from shapely.ops import polylabel

RAW, FARMS_CSV, OUT = map(Path, sys.argv[1:4])
BBOX = (73.0, 17.5, 135.5, 54.0)  # lon_min, lat_min, lon_max, lat_max
R_EARTH = 6371.0
RES_FINE, RES_OVERVIEW = 6, (5, 4)

# Model assumptions. The page shows these too, so keep them in sync via meta.
GW_OFFSET = 1.5           # shallow groundwater ~ mean annual air temp + 1-2 C (Benz et al. 2017)
T_ZERO_LOW, T_IDEAL_LOW, T_IDEAL_HIGH, T_ZERO_HIGH = 0.0, 6.0, 14.0, 22.0
W_TEMP, W_WATER = 0.6, 0.4
MAX_ELEV = 4000           # m; above this we assume no industrial RAS
GOOD = 70                 # hex score that counts as "suitable" in the province ranking

PROVINCES = {  # geoBoundaries shapeName -> (ISO 3166-2:CN code, English, Chinese)
    "Anhui Province": ("AH", "Anhui", "安徽"),
    "Beijing Municipality": ("BJ", "Beijing", "北京"),
    "Chongqing Municipality": ("CQ", "Chongqing", "重庆"),
    "Fujian Province": ("FJ", "Fujian", "福建"),
    "Gansu Province": ("GS", "Gansu", "甘肃"),
    "Guangzhou Province": ("GD", "Guangdong", "广东"),  # source mislabels Guangdong
    "Guangxi Zhuang Autonomous Region": ("GX", "Guangxi", "广西"),
    "Guizhou Province": ("GZ", "Guizhou", "贵州"),
    "Hainan Province": ("HI", "Hainan", "海南"),
    "Hebei Province": ("HE", "Hebei", "河北"),
    "Heilongjiang Province": ("HL", "Heilongjiang", "黑龙江"),
    "Henan Province": ("HA", "Henan", "河南"),
    "Hubei Province": ("HB", "Hubei", "湖北"),
    "Hunan Province": ("HN", "Hunan", "湖南"),
    "Inner Mongolia Autonomous Region": ("NM", "Inner Mongolia", "内蒙古"),
    "Jiangsu Province": ("JS", "Jiangsu", "江苏"),
    "Jiangxi Province": ("JX", "Jiangxi", "江西"),
    "Jilin Province": ("JL", "Jilin", "吉林"),
    "Liaoning Province": ("LN", "Liaoning", "辽宁"),
    "Ningxia Ningxia Hui Autonomous Region": ("NX", "Ningxia", "宁夏"),
    "Qinghai Province": ("QH", "Qinghai", "青海"),
    "Shaanxi Province": ("SN", "Shaanxi", "陕西"),
    "Shandong Province": ("SD", "Shandong", "山东"),
    "Shanghai Municipality": ("SH", "Shanghai", "上海"),
    "Shanxi Province": ("SX", "Shanxi", "山西"),
    "Sichuan Province": ("SC", "Sichuan", "四川"),
    "Tianjin Municipality": ("TJ", "Tianjin", "天津"),
    "Tibet Autonomous Region": ("XZ", "Tibet", "西藏"),
    "Xinjiang Uyghur Autonomous Region": ("XJ", "Xinjiang", "新疆"),
    "Yunnan Province": ("YN", "Yunnan", "云南"),
    "Zhejiang Province": ("ZJ", "Zhejiang", "浙江"),
    "Taiwan Province": ("TW", "Taiwan", "台湾"),
    "Hong Kong Special Administrative Region": ("HK", "Hong Kong", "香港"),
    "Macau Special Administrative Region": ("MO", "Macau", "澳门"),
}
NOT_RANKED = {"TW", "HK", "MO"}  # drawn for context; the subsidy programmes are mainland ones

# Placeholder for the subsidy contact's data: what the desk research found (CONTEXT.md §4, §6e).
PROGRAMMES = {
    "FJ": ["Fishery modernisation subsidy funds, 2025–2027"],
    "JS": ["CNY 200 M provincial marine-industry support (2025)"],
    "ZJ": ["Ningbo tailwater-treatment subsidies (2020–22)",
           "Grid upgrade for the Ningbo salmon RAS"],
    "AH": ["Pond renovation, up to CNY 3,000 per mu (2024)"],
    "GD": ["Deep-sea cage subsidy (2019)",
           "China–Europe Ocean Fishery Innovation Park, Shanwei"],
    "SD": ["Yantai 'salmon 10,000 t plan', target 2027",
           "Provincial R&D programme on salmon breeding"],
    "LN": ["Dalian Jinpu salmon-industry plan (CNY 10 bn), CNY 350 M base built"],
    "SC": ["Baoxing County trout plan, 10,000 t by 2030"],
    "QH": ["Cold-water fish named a provincial priority product"],
}

# Fresh salmon sells in big cities: tier-1 cities plus major regional hubs (hand-picked for the mockup).
MARKETS = {  # Natural Earth name -> display name
    "Shanghai": "Shanghai", "Beijing": "Beijing", "Guangzhou": "Guangzhou", "Shenzhen": "Shenzhen",
    "Hong Kong": "Hong Kong", "Chengdu": "Chengdu", "Chongqing": "Chongqing", "Hangzhou": "Hangzhou",
    "Wuhan": "Wuhan", "Nanjing": "Nanjing", "Tianjin": "Tianjin", "Xian": "Xi'an",
    "Shenyeng": "Shenyang", "Qingdao": "Qingdao", "Zhengzhou": "Zhengzhou", "Changsha": "Changsha",
    "Kunming": "Kunming",
}


def to_xyz(lon, lat):
    lo, la = np.radians(lon), np.radians(lat)
    return np.column_stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def nearest_km(tree, lon, lat):
    d, idx = tree.query(to_xyz(lon, lat))
    return 2 * np.arcsin(np.clip(d / 2, 0, 1)) * R_EARTH, idx


def fill_nearest(values, lon, lat):
    """Fill NaNs (coastal hexes whose centre falls in the sea) from the nearest valid hex."""
    bad = np.isnan(values)
    if bad.any() and (~bad).any():
        tree = cKDTree(to_xyz(lon[~bad], lat[~bad]))
        _, idx = tree.query(to_xyz(lon[bad], lat[bad]))
        values[bad] = values[~bad][idx]
    return values


# --- Provinces and hexes -------------------------------------------------------------
prov = gpd.read_file(RAW / "boundaries/geoBoundaries-CHN-ADM1_simplified.geojson")
missing = set(prov.shapeName) - set(PROVINCES)
assert not missing, f"unmapped province names: {missing}"
prov["pid"] = [PROVINCES[n][0] for n in prov.shapeName]
ranked = prov[~prov.pid.isin(NOT_RANKED)].sort_values("pid").reset_index(drop=True)
PIDS = list(ranked.pid)

cell_prov = {}
for i, geom in enumerate(ranked.geometry):
    for c in h3.geo_to_cells(geom.__geo_interface__, RES_FINE):
        cell_prov.setdefault(c, i)  # first province wins on (rare) overlaps
cells = np.array(list(cell_prov))
pidx = np.array([cell_prov[c] for c in cells])
lat, lon = np.array([h3.cell_to_latlng(c) for c in cells]).T
area = np.array([h3.cell_area(c, "km^2") for c in cells])
print(f"res {RES_FINE}: {len(cells):,} hexes, {area.sum():,.0f} km²")

# --- Temperature proxy: CHELSA BIO1, block-mean to ~3.7 km, sampled at hex centres ----
with rasterio.open(RAW / "chelsa/CHELSA_bio1_1981-2010_V.2.1.tif") as src:
    win = from_bounds(*BBOX, transform=src.transform).round_offsets().round_lengths()
    raw = src.read(1, window=win).astype("float32")
    tr = src.window_transform(win)
    scale, offset = src.scales[0], src.offsets[0]
raw[(raw == 0) | (raw == 65535)] = np.nan
air = raw * scale + offset
F = 4
h, w = (air.shape[0] // F) * F, (air.shape[1] // F) * F
with np.errstate(all="ignore"):
    coarse = np.nanmean(air[:h, :w].reshape(h // F, F, w // F, F), axis=(1, 3))
col = ((lon - tr.c) / (tr.a * F)).astype(int).clip(0, coarse.shape[1] - 1)
row = ((lat - tr.f) / (tr.e * F)).astype(int).clip(0, coarse.shape[0] - 1)
air_t = fill_nearest(coarse[row, col].astype("float64"), lon, lat)
gw_t = air_t + GW_OFFSET

# --- Elevation: AWS terrain tiles (terrarium), zoom 6 ---------------------------------
X0, X1, Y0, Y1 = 44, 56, 20, 28
mosaic = np.full(((Y1 - Y0 + 1) * 256, (X1 - X0 + 1) * 256), np.nan, dtype="float32")
for x in range(X0, X1 + 1):
    for y in range(Y0, Y1 + 1):
        rgb = np.asarray(Image.open(RAW / f"terrain_z6/6_{x}_{y}.png").convert("RGB"), dtype="float64")
        mosaic[(y - Y0) * 256:(y - Y0 + 1) * 256, (x - X0) * 256:(x - X0 + 1) * 256] = (
            rgb[..., 0] * 256 + rgb[..., 1] + rgb[..., 2] / 256 - 32768)
world_px = 2 ** 6 * 256
lat_r = np.radians(lat)
px = ((lon + 180) / 360 * world_px - X0 * 256).astype(int).clip(0, mosaic.shape[1] - 1)
py = ((1 - np.log(np.tan(lat_r) + 1 / np.cos(lat_r)) / np.pi) / 2 * world_px - Y0 * 256).astype(int)
elev = np.maximum(mosaic[py.clip(0, mosaic.shape[0] - 1), px], 0)

# --- Distance to coast and to big markets ----------------------------------------------
coast = gpd.read_file(RAW / "ne_coastline/extracted/ne_10m_coastline.shp", bbox=(60, 0, 150, 60))
cpts = get_coordinates(segmentize(coast.geometry.values, 0.02))
coast_km, _ = nearest_km(cKDTree(to_xyz(cpts[:, 0], cpts[:, 1])), lon, lat)

places = gpd.read_file(RAW / "ne_places/extracted/ne_10m_populated_places_simple.shp")
mk = places[places.name.isin(MARKETS) & places.adm0_a3.isin(["CHN", "HKG"])]
mk = mk.sort_values("pop_max", ascending=False).drop_duplicates("name").reset_index(drop=True)
assert len(mk) == len(MARKETS), set(MARKETS) - set(mk.name)
market_km, market_idx = nearest_km(cKDTree(to_xyz(mk.longitude.values, mk.latitude.values)), lon, lat)

# --- Water: WRI Aqueduct 4.0 baseline water stress + groundwater table decline ----------
aq = gpd.read_file(
    RAW / "aqueduct/extracted/Aqueduct40_waterrisk_download_Y2023M07D05/GDB/Aq40_Y2023D07M05.gdb",
    layer="baseline_annual", bbox=BBOX,
    columns=["bws_score", "bws_cat", "bws_label", "gtd_score", "gtd_cat", "gtd_label", "gtd_raw"])
pts = gpd.GeoDataFrame(geometry=gpd.points_from_xy(lon, lat), crs="EPSG:4326")
j = gpd.sjoin(pts, aq, how="left", predicate="within")
j = j[~j.index.duplicated(keep="first")].sort_index()
bws = j.bws_score.to_numpy(dtype="float64")
bws = np.where(j.bws_cat.to_numpy() == -1, 5.0, bws)       # "Arid and low water use"
bws[bws < 0] = np.nan
gtd = j.gtd_score.to_numpy(dtype="float64")
gtd = np.where(j.gtd_label.to_numpy() == "Insignificant Trend", 0.0, gtd)
gtd[gtd < 0] = np.nan
print("Aqueduct labels (share of hexes):")
print((j.bws_label.value_counts(normalize=True, dropna=False).round(3)).to_string())
print((j.gtd_label.value_counts(normalize=True, dropna=False).round(3)).to_string())
bws = fill_nearest(bws, lon, lat)
gtd = fill_nearest(gtd, lon, lat)

# --- Score ----------------------------------------------------------------------------
s_temp = np.interp(gw_t, [T_ZERO_LOW, T_IDEAL_LOW, T_IDEAL_HIGH, T_ZERO_HIGH], [0, 1, 1, 0])
s_water = 1 - (bws + gtd) / 10
score = 100 * (W_TEMP * s_temp + W_WATER * s_water)
score[elev > MAX_ELEV] = 0
score = np.round(score).astype(int)


def columns(sel, extra=None):
    out = {
        "h": cells[sel].tolist(),
        "s": score[sel].tolist(),
        "t": np.round(gw_t[sel] * 10).astype(int).tolist(),
        "w": np.round(bws[sel] * 10).astype(int).tolist(),
        "g": np.round(gtd[sel] * 10).astype(int).tolist(),
        "e": np.round(elev[sel]).astype(int).tolist(),
        "c": np.round(coast_km[sel]).astype(int).tolist(),
        "m": np.round(market_km[sel]).astype(int).tolist(),
        "k": market_idx[sel].tolist(),
    }
    out.update(extra or {})
    return out


OUT.mkdir(parents=True, exist_ok=True)
(OUT / f"hex_r{RES_FINE}").mkdir(exist_ok=True)

# --- Overview resolutions: aggregate fine hexes up to their parents (never the reverse) -
for res in RES_OVERVIEW:
    parents = np.array([h3.cell_to_parent(c, res) for c in cells])
    uniq, inv = np.unique(parents, return_inverse=True)
    cnt = np.bincount(inv)

    def mean_up(v):
        return np.bincount(inv, weights=v) / cnt

    def majority(codes, n):
        return np.bincount(inv * n + codes, minlength=len(uniq) * n).reshape(len(uniq), n).argmax(axis=1)

    overview = {
        "res": res,
        "h": uniq.tolist(),
        "p": majority(pidx, len(PIDS)).tolist(),
        "s": np.round(mean_up(score)).astype(int).tolist(),
        "t": np.round(mean_up(gw_t) * 10).astype(int).tolist(),
        "w": np.round(mean_up(bws) * 10).astype(int).tolist(),
        "g": np.round(mean_up(gtd) * 10).astype(int).tolist(),
        "e": np.round(mean_up(elev)).astype(int).tolist(),
        "c": np.round(mean_up(coast_km)).astype(int).tolist(),
        "m": np.round(mean_up(market_km)).astype(int).tolist(),
        "k": majority(market_idx, len(mk)).tolist(),
        "n": cnt.tolist(),
    }
    (OUT / f"hex_r{res}.json").write_text(json.dumps(overview, separators=(",", ":")))
    print(f"res {res}: {len(uniq):,} hexes")

# --- Known farms: score of the hex each farm sits in ------------------------------------
with open(FARMS_CSV, newline="", encoding="utf-8") as f:
    farm_rows = list(csv.DictReader(f))
fine_index = {c: i for i, c in enumerate(cells)}
valid_tree = cKDTree(to_xyz(lon, lat))
farms = []
for r in farm_rows:
    status = r["status"].lower()
    kind = ("context" if "not ras" in r["system"].lower() else
            "operating" if status.startswith("operating") else "planned")
    farm = {k: r[k] for k in ("id", "name", "company", "province", "location", "species", "system",
                              "status", "capacity_t", "owner_type", "source_url", "notes",
                              "coord_precision")}
    farm["kind"] = kind
    if r["lat"] and r["lon"]:
        flat, flon = float(r["lat"]), float(r["lon"])
        c = h3.latlng_to_cell(flat, flon, RES_FINE)
        i = fine_index.get(c)
        if i is None:  # farm centre falls just outside our hexes (coast, border)
            _, i = valid_tree.query(to_xyz(np.array([flon]), np.array([flat])))
            i = int(i[0])
        same = pidx == pidx[i]
        farm.update(lat=flat, lon=flon, hex=cells[i], score=int(score[i]), pid=PIDS[pidx[i]],
                    pct=int(round(100 * (score[same] < score[i]).mean())))
    farms.append(farm)
(OUT / "farms.json").write_text(json.dumps(farms, ensure_ascii=False, indent=1))

# --- Province stats, top areas and per-province fine hex files --------------------------
farm_kinds = {}
for fm in farms:
    if fm.get("pid") and fm["kind"] != "context":
        farm_kinds.setdefault(fm["pid"], []).append(fm["kind"])
n_signal = {p: len(farm_kinds.get(p, [])) + len(PROGRAMMES.get(p, [])) for p in PIDS}
max_signal = max(n_signal.values())

provinces = []
for i, row in ranked.iterrows():
    sel = pidx == i
    order = np.argsort(-score[sel], kind="stable")
    pc = cells[sel][order]
    picked, blocked = [], set()
    for c in pc:  # top areas at least ~3 hex rings apart, so they are distinct places
        if c in blocked:
            continue
        picked.append(c)
        blocked.update(h3.grid_disk(c, 3))
        if len(picked) == 10:
            break
    top = []
    for c in picked:
        k = fine_index[c]
        top.append({"h": c, "s": int(score[k]), "t": round(float(gw_t[k]), 1),
                    "w": round(float(bws[k]), 1), "g": round(float(gtd[k]), 1),
                    "m": int(round(market_km[k])), "k": int(market_idx[k])})
    sname = row.shapeName
    pid, en, zh = PROVINCES[sname]
    minx, miny, maxx, maxy = row.geometry.bounds
    parts = getattr(row.geometry, "geoms", [row.geometry])
    label = polylabel(max(parts, key=lambda g: g.area), tolerance=0.05)
    provinces.append({
        "id": pid, "en": en, "zh": zh,
        "bbox": [round(minx, 3), round(miny, 3), round(maxx, 3), round(maxy, 3)],
        "label": [round(label.x, 3), round(label.y, 3)],
        "hexes": int(sel.sum()),
        "area_km2": int(area[sel].sum()),
        "good_km2": int(area[sel & (score >= GOOD)].sum()),
        "p90": int(np.percentile(score[sel], 90)),
        "mean_t": round(float(np.average(gw_t[sel], weights=area[sel])), 1),
        "high_stress_share": round(float(area[sel & (bws >= 3)].sum() / area[sel].sum()), 2),
        "projects": farm_kinds.get(pid, []),
        "programmes": PROGRAMMES.get(pid, []),
        "signal": round(100 * n_signal[pid] / max_signal),
        "top": top,
    })
    (OUT / f"hex_r{RES_FINE}/{pid}.json").write_text(
        json.dumps(columns(sel, {"res": RES_FINE}), separators=(",", ":")))

meta = {
    "built": date.today().isoformat(),
    "res_fine": RES_FINE, "res_overview": list(RES_OVERVIEW),
    "gw_offset": GW_OFFSET,
    "t_curve": [T_ZERO_LOW, T_IDEAL_LOW, T_IDEAL_HIGH, T_ZERO_HIGH],
    "weights": {"temperature": W_TEMP, "water": W_WATER},
    "max_elev": MAX_ELEV, "good": GOOD,
    "markets": [{"name": MARKETS[n], "lat": round(a, 3), "lon": round(o, 3)}
                for n, a, o in zip(mk.name, mk.latitude, mk.longitude)],
}
(OUT / "provinces.json").write_text(json.dumps({"meta": meta, "provinces": provinces},
                                               ensure_ascii=False, indent=1))

# Shapes for drawing: all 34 units, plus a coastline clipped to the map area.
draw = prov[["pid", "geometry"]].copy()
draw["en"] = [PROVINCES[n][1] for n in prov.shapeName]
draw["zh"] = [PROVINCES[n][2] for n in prov.shapeName]
draw["ranked"] = ~draw.pid.isin(NOT_RANKED)
draw.geometry = draw.geometry.simplify(0.01, preserve_topology=True)
draw.to_file(OUT / "provinces.geojson", driver="GeoJSON", COORDINATE_PRECISION=3)
cl = coast.clip(BBOX).explode(index_parts=False)
cl.geometry = cl.geometry.simplify(0.02)
cl[["geometry"]].to_file(OUT / "coast.geojson", driver="GeoJSON", COORDINATE_PRECISION=3)

ranking = sorted(provinces, key=lambda p: -p["p90"])
print("\nProvince  p90  good_km2  mean_t  high_stress  signal")
for p in ranking:
    print(f"{p['id']:3} {p['en']:15} {p['p90']:3} {p['good_km2']:9,} {p['mean_t']:6} "
          f"{p['high_stress_share']:5} {p['signal']:4}")
print("\nFarms (score, percentile in province):")
for fm in farms:
    if "score" in fm:
        print(f"  {fm['id']:>2} {fm['name'][:42]:42} {fm['pid']}  {fm['score']:3}  p{fm['pct']:<3} {fm['kind']}")
