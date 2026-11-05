# China RAS prospect map (mockup)

An H3 honeycomb map that ranks Chinese provinces, and areas within them, for salmon and trout RAS. It uses open global proxy data. The point is to show the geology researcher and the subsidy contact what their data would improve.

**Open the map:** https://kingen560.github.io/china-ras-prospect-map/mockup/
**Start the demo tour:** https://kingen560.github.io/china-ras-prospect-map/mockup/#demo

## View the mockup
The page loads its data with `fetch`, so it needs a local web server (opening the file directly won't work):

```bash
python3 -m http.server 8765 --directory mockup
```

Then open http://localhost:8765. Add `#SD` (or any province code) to the address to open a province directly.

## Demo tour (for meetings)
Open http://localhost:8765/#demo, or click **▶ Demo tour** on the map. The tour has seven steps:
1. The China overview.
2. Water temperature.
3. Water supply.
4. A check against real farms.
5. The four kinds of market.
6. Inside Shandong.
7. What the researcher's data would change.

Each step moves the map by itself. Use the arrow keys (or a presentation clicker, which sends PageUp/PageDown) to move between steps, and Esc to leave.

## Rebuild the hex data
The raw data is not in the repository: it is 1.1 GB unpacked, and two of the files are over GitHub's 100 MB limit. Download it first, then build:

```bash
bash scripts/download_data.sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -I scripts/build_hexes.py data/raw data/known_salmonid_farms_china.csv mockup/data
```
The build takes about 20 seconds. The finished map data in `mockup/data/` is in the repository, so the mockup runs without this step. The datasets and their licences are listed in `DATA_SOURCES.md`.

## Files
- `CONTEXT.md`: the project brief, decisions and findings.
- `DATA_SOURCES.md`: the open datasets and what each one stands in for.
- `data/known_salmonid_farms_china.csv`: 24 known farms and projects, used to check the scores.
- `scripts/build_hexes.py`: proxies → H3 res 6 hex scores, averaged up to res 5 and res 4.
- `mockup/index.html`: the two-step map, built with deck.gl.
