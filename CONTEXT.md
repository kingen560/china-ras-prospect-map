# Project context: H3 honeycomb map for finding Nofitech customers in China

_Started 2026-11-04. A living document: the next steps are to fill the open questions, then bring in data._

## 1. The idea in one sentence
An H3 hexagon map of China that shows **where new land-based fish-farming customers for Nofitech are most likely to be**. It combines geological data (from a researcher) with Chinese state subsidies (from someone with subsidy data).

## 2. Advice from Ivan (guest lecturer), and what it means here
| Ivan said | What it means for this project |
|---|---|
| Use res 8 for demos and fast iteration, and res 10 for the final product. Build at the finest resolution you can, because you can aggregate up but not down. | Res 10 (~0.015 km²) suits store-level questions. Fish farms are much bigger, and China is huge, so the finest useful level here is probably **res 6–7** (~36 km² / ~5 km²). We should still store the data at the finest resolution the geological data supports, then aggregate up. |
| Don't mix region-level data into the hex colour. Show it in a tooltip or sidebar instead. | Subsidies are mostly set by **province or city**, so they should **not** go into the hex score. Colour the hexes by geology and physical suitability, and show subsidies in the sidebar and tooltip. |
| Users ask questions within a region ("I'm in Oslo, where should I dig?"). | The UI should probably let the user **pick a province first, then rank hexes within it**. |
| Use deck.gl for visualisation. Use OSRM only if travel or neighbourhood context matters. | deck.gl's `H3HexagonLayer` fits this well. OSRM is probably not needed at first. Logistics (distance to seafood markets or ports) could be added later as a simple distance layer. |
| Focus on the end user, not the tech. Do a grill-me session first. | Section 6 is that. Answer those questions before writing code. |

## 3. China's fish industry: the short version
- **Scale:** China is by far the world's largest aquaculture producer, with about 60.6 Mt farmed out of 73.6 Mt total aquatic output in 2024 ([China Daily, Nov 2025](https://www.chinadaily.com.cn/a/202511/24/WS692396a7a310d6866eb2af2d.html)).
- **Where it is:** Guangdong (~7.7 Mt) and Shandong (~6.6 Mt) led farmed seafood output in 2022 ([Statista](https://www.statista.com/statistics/1128636/china-cultured-seafood-production-volume-by-region/)). Fujian is also a big producer. For freshwater farming, Hubei, Guangdong and Jiangsu lead ([The Fish Site](https://thefishsite.com/articles/china-fishery-products-annual-2011), older data).
- **What it looks like:** Most of it is still ponds and sea cages. The direction of policy is toward "high-quality development": modernised ponds, tailwater (effluent) treatment, offshore cages, and factory-style (工厂化) indoor farming.

### Land-based RAS: Nofitech's segment
- **Zhejiang (Ningbo, Xiangshan)** is the reference case. Nordic Aqua Partners runs a Norwegian-run Atlantic salmon RAS farm there. It harvested about 2,026 t in 2025, has a Phase 2 that started receiving fish in Oct 2025, and is targeting 20,000 t ([weareaquaculture](https://weareaquaculture.com/amp/story/news/finance/nordic-aqua-partners-q4-2025-clear-path-to-20000-tons), [Xinhua/BRI](https://eng.yidaiyilu.gov.cn/p/0MM9CPN7.html)). AKVA supplied the technology ([AKVA case](https://blog.akvagroup.com/land-based/turn-key-delivery/case-stories/noap-china/noap-china-1)).
- **Other entrants:** Pure Salmon has partnered with China Road & Bridge, a state-owned company, on a RAS demo ([Undercurrent](https://www.undercurrentnews.com/2025/09/15/pure-salmon-technology-partners-with-chinese-state-owned-firm-on-ras-project/)). Haisheng Group plans two farms ([Salmon Business](https://www.salmonbusiness.com/leading-hong-kong-fruit-juice-company-says-its-investing-in-two-land-based-salmon-farms-in-china/?amp=1)). Some projects have been controversial ([SeafoodSource](https://www.seafoodsource.com/news/aquaculture/two-proposed-ras-salmon-farms-cause-stir-in-china)).
- **Caveat:** Much of the growth is still *planned* capacity. I found no provincial statistics on RAS specifically.

## 4. Subsidy landscape (first scan, to be replaced by the subsidy contact's data)
- **Fujian:** fishery modernisation subsidy funds for 2025–2027 ([GTA](https://globaltradealert.org/state-act/91333-china-fujian-province-state-aid-to-support-the-aquatic-processing-industry)).
- **Jiangsu:** CNY 200 M for the marine industry, 2025 ([GTA](https://globaltradealert.org/intervention/143335-china-jiangsu-province-cny-200-million-to-support-provincial-marine-industry)).
- **Ningbo (Zhejiang):** subsidies for building or upgrading tailwater treatment, 2020–22.
- **Anhui:** up to ¥3,000/mu (a Chinese area unit, about 667 m²) for pond renovation and effluent handling, 2024.
- **National:** support for moving fishing effort offshore and into deep-sea cages, plus fuel-subsidy reform ([SeafoodSource](https://www.seafoodsource.com/premium/global-bulletin/china-offers-subsidies-for-transition-to-offshore-aquaculture-distant-water-fishing)).
- **Pattern:** Subsidies are set at province or city level and target modernisation and environmental upgrades. Effluent rules matter here, because a RAS can be pitched as a way to *comply* with them, not only as a subsidy target.
- **Next search:** Chinese-language terms (工厂化养殖 补贴, 循环水养殖 补贴, 尾水治理) on provincial agriculture and finance department sites.

## 5. Why geology matters for land-based farms (hypotheses to check with the researcher)
| Factor | Why it matters for RAS / flow-through farms |
|---|---|
| Groundwater availability and yield | Most land-based farms need a stable source of make-up water. |
| Water temperature (geothermal gradient) | Affects how much energy heating or cooling costs, and which species are viable. |
| Salinity (brackish or saline aquifers) | Can allow marine species inland, such as salmon post-smolt, shrimp or grouper. |
| Water chemistry (Fe, Mn, H₂S, CO₂, nitrate) | Affects how much water treatment is needed, which is Nofitech's area. |
| Ground stability and bedrock depth | Affects the cost of foundations for tanks and buildings. |
| Seismic, flood and subsidence risk | Hard exclusion zones. |
| Distance to coast (seawater intake) | Matters for marine RAS. |

## 6a. Decisions (grill-me round 1, 2026-11-04)
| Question | Answer |
|---|---|
| Main user | **Nofitech sales** |
| What they do with it | **Pick which province or provinces to focus on first** |
| Customer | **New RAS investors** and **state-owned firms / local government projects** |
| Segment | **Salmon / trout** (cold water) |
| Map flow | **Two steps.** (1) Rank provinces by subsidies plus aggregated hex suitability. (2) Open a province and see hexes coloured by geology only, with subsidies in the sidebar. |
| Geological data | **Unknown so far.** Ask the researcher (see 6c). |
| Validation | **None in-house.** Build a list of known Chinese salmon and trout RAS farms from public sources. |
| Audience | **Internal Nofitech only.** Data may be sensitive. |

### What the answers mean
- **Cold water is the main geological factor.** Salmon and trout need roughly 8–16 °C water. Cold, plentiful groundwater cuts energy costs, so groundwater temperature, yield and quality matter more than anything else. Brackish or saline aquifers are a bonus for the seawater grow-out phase.
- **Step 1 is a comparison between provinces,** so subsidies *are* the main factor there. That doesn't conflict with Ivan: his "don't mix" rule applies to the hex colouring in step 2.
- **The customers are investors and SOEs,** not small farmers. Signals besides geology are therefore power-grid capacity (the State Grid's role in Ningbo), access to industrial land, and access to markets (Shanghai, Beijing, Guangzhou), since salmon is sold fresh to cities.
- **There is no ground truth yet.** The first data task is a public list of salmon and trout RAS projects in China: Nordic Aqua in Ningbo, Pure Salmon with China Road & Bridge, Haisheng, and trout farms in Qinghai and Gansu (cold-water cage and land-based farming). If the map ranks these places low, the score is wrong.

### 6e. Ground-truth list v2: after Chinese-language search (2026-11-04)
`data/known_salmonid_farms_china.csv` now has **24 sites in 11 provinces**. The new finds from Chinese-language sources:
- **Beijing Xinguize (北京新鲑泽) is the top lead.** It runs RAS farms for others and plans **20 farms of 10,000 t each by 2030**. It has already signed Shenyang Sujiatun (Aug 2025) and Yantai Huangbohai New Area (Nov 2025, CNY 2.3 bn).
- **Jiangsu Xinyu, Changzhou:** 5,000 t, CNY 500 M. Its grow-out hall has been running since June 2025.
- **Hubei Zhongxiang:** a state-owned trout RAS, 3,000 t, CNY 361 M. This is RAS in a warm climate, where geology helps less.
- **Hebei Weichang (Chengde):** a 1,200 t seedling and grow-out base for the Beijing–Tianjin market.
- **Sichuan Ya'an (Baoxing, Yingjing):** trout raised in cold mountain water (10–15 °C), with a target of 10,000 t by 2030.
- **Yantai:** the city has a "salmon 10,000 t plan". Today it has 730,000 m³ of farming water and produces 2,500 t/yr, aiming for 10,000 t by 2027. Changdao and Laizhou are part of it.
- **Context points (not RAS):** Qinghai is the largest trout region, with about 15,000 t mostly from cages in the Longyangxia reservoir, plus 11 land-based farms. Hejing in Xinjiang uses spring water that stays below 10 °C all year.
- **Norsal = 诺鲜三文鱼 (Nuo Fresh).** Neither English nor Chinese sources show any progress after 2020, so the project has probably stalled. I couldn't find where the Pure Salmon x CRBC site is.

**What this means for the model:** The sites fall into two groups.
1. **Coastal RAS, driven by investors and local government:** Shandong, Liaoning, Jiangsu, Zhejiang, Guangdong.
2. **Inland farms built on cold water:** Qinghai, Gansu, Xinjiang, Sichuan, Hebei.

Geology mainly explains the second group. The first is explained by subsidies, government projects and access to markets. That supports the two-step design. It also suggests showing the province ranking from step 1 as **two separate scores**, physical suitability and investment climate, rather than one blended number.

### 6d. Ground-truth list (v1, 2026-11-04)
The list is in `data/known_salmonid_farms_china.csv`: 12 sites in 7 provinces, plus one with no known location (Pure Salmon x CRBC).
- **Operating:** Ningbo (Zhejiang), Yantai ex-Oriental Ocean (Shandong), Yantai Jinghai trout (Shandong), Jinpu Dalian (Liaoning), Yuzhong hatchery (Gansu), Kumtag desert trout (Gansu), Nilka trout ponds (Xinjiang, not RAS).
- **Planned:** Norsal Yantai, Baring Farsund Shanwei (Guangdong), Haisheng Bole (Xinjiang) and Qinghai, Pure Salmon x CRBC (location unknown).
- **Clusters:** Shandong/Yantai and the Bohai coast (Liaoning) are the clearest hubs. The northwest (Gansu, Xinjiang, Qinghai) is a cold-water trout belt. Zhejiang and Guangdong are outliers driven by subsidies and investors.
- **Coordinates are approximate.** The `coord_precision` column says whether each point is town, district, city, county, region or province level. That's fine at res 5–6, but not for hex-level checks at res 7.
- **To do:** search Chinese-language sources (三文鱼 工厂化 循环水, 虹鳟 陆基), check that Norsal and Yantai are still active, and find where the Pure Salmon x CRBC site is.

### 6c. Questions for the geology researcher
1. Which variables? Groundwater depth, yield, temperature, salinity, chemistry (Fe, Mn, H₂S, nitrate), aquifer type.
2. What format? Points, raster or polygons, and which coordinate system?
3. How detailed, and over what area? All of China or specific provinces?
4. How old is the data, and are there any gaps?
5. May it be used in an internal Nofitech tool?

## 6b. Original grill-me questions (kept for reference)
**User and problem**
1. Who opens this map? A Nofitech salesperson, management, or a Chinese partner or distributor?
2. What decision do they make with it? Who to call, where to send a sales trip, or which province to enter first?
3. What does a "customer" mean here? Existing pond farmers who need to upgrade, new RAS investors, state-owned companies, or equipment integrators?
4. What does Nofitech actually sell into this, and which species or segment fits best: salmon, other marine fish, shrimp, or freshwater?

**Data**
5. What does the geological data cover? Which variables, what format (points, rasters, polygons), how detailed, and over which area: all of China or a few provinces?
6. What does the subsidy data look like? Programme lists, amounts per province, or project-level data?
7. Do we have ground truth, meaning known RAS farms or existing customers? Without it we can't check whether the score makes sense.

**Output**
8. Is the end product a map to explore, a ranked target list (CSV), or both?
9. Is this for a school project, an internal Nofitech tool, or both? Who sees it, and is any of the data confidential?

## 6f. Mockup plan (before asking for more geology data)
The goal is to show the researcher, the subsidy contact and Nofitech sales what the tool could do. It uses only open stand-in data (see `DATA_SOURCES.md`) and labels it all "global proxy".

**Screen 1: China overview (step 1, choose a province)**
- A choropleth of provinces with two bars per province:
  - **Physical suitability**: the average of the hex scores inside the province.
  - **Investment climate**: placeholder subsidy level plus the number of known projects.
- The 24 known farms as points, coloured operating or planned.
- A sidebar ranking provinces, sortable by either score.

**Screen 2: one province (step 2, where in the province)**
- H3 hexes at res 6, coloured by **cold-water score only**. The score combines the temperature proxy, Aqueduct groundwater decline and water stress, and elevation.
- Tooltip per hex: the values behind the score and the distance to the nearest big market.
- Sidebar: the province's subsidy programmes (placeholder), its known farms, and the top 10 hexes.
- A greyed-out "Coming with researcher data" panel listing measured temperature, yield, salinity and chemistry. **This panel is the ask.**

**Tech:** Python (`h3`, `geopandas`, `rasterio`) makes the hex scores as a static JSON file, and one HTML page with deck.gl draws the map. A demo should start with Shandong and Qinghai, the two contrasting cases.

## 6g. Mockup v1 built (2026-11-04)
- `mockup/index.html` is built from `scripts/build_hexes.py`. It has 282,959 hexes at res 6, averaged up to res 5 (41,053) and res 4. See README.md for how to run it.
- **Score:** 60% temperature (CHELSA air temperature + 1.5 °C; ideal 6–14 °C) + 40% water (Aqueduct water stress + groundwater decline). Land above 4,000 m scores 0.
- **Spot checks** against known city climates are within 1–2 °C, and elevations match.
- **Farm check:** inland cold-water sites score high (Yuzhong 98, Longyangxia 100, Baoxing 91). Coastal RAS sites score low (Ningbo 49, Wujin 49, Shanwei 33). This confirms that the province view needs two separate scores.
- **Data gotcha:** geoBoundaries labels Guangdong as "Guangzhou Province". The script corrects it.

## 6h. Mockup v2: easier for sales (2026-11-05)
- **Answer first.** The page opens with "Top 3 provinces right now", ranked by activity first and then by best-land score. Today that is Shandong, Sichuan and Liaoning. Each gets one sentence and a pitch.
- **Four kinds of market (2×2).** Water (best-land score of 90+ = Strong) is crossed with activity (2 or more projects or programmes):
  - **Go now:** Liaoning, Sichuan, Gansu.
  - **Sell the fix:** Shandong, Zhejiang, Guangdong, Xinjiang, Qinghai, Jiangsu. The pitch names the problem: warm water → cooling; scarce water → high recirculation and water treatment; very cold water → heating and heat recovery.
  - **Pioneer:** 9 provinces with strong water and few projects, such as Jilin, Heilongjiang and Yunnan.
  - **Watch:** the rest.
- **Simple by default.** The page uses words (Strong / Good / Weak) instead of numbers. A "Show details" switch brings back the numbers, layers, ranking and method.
- **"Why this score?"** Every hex shows bars for water temperature and water supply. Market access is shown for context only and is not in the score yet.
- **Open question:** should market access go into the hex score, or stay as context?

## 6i. Demo tour for the researcher meeting (2026-11-05)
- Start it with `#demo` or the **▶ Demo tour** button. It has seven steps: overview → temperature (proxy) → water supply → check against real farms → four kinds of market → inside Shandong → "what your data would change".
- The tour ends with the question: *what can you share, and at what level of detail?* That is the meeting's ask for the researcher. For the subsidy contact, the message is that "activity" becomes real money.
- **Text that changes with the data:** farm scores and segment names are read from the data, so the tour text stays correct after a rebuild.

## 7. Proposed technical skeleton (once section 6 is answered)
- Python: `h3`, `geopandas`, `rasterio` to build hexes and aggregate geology into them. Output as Parquet or GeoJSON.
- Front end: deck.gl `H3HexagonLayer`, a province picker, a sidebar with subsidy info, and a ranked list of the top hexes in the selected region.
- Resolution: start at res 5–6 for the whole country, and go to res 7 within the chosen provinces.
