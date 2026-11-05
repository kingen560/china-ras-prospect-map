# Open data for the mockup (located 2026-11-04, nothing downloaded yet)

The mockup's job is to show the researcher and the subsidy contact **what the tool could become**, so they see why their data matters. Every layer below is a free, global stand-in. The researcher's data replaces the geology stand-ins later.

## Tier 1: enough for a convincing mockup
| Layer | Dataset | What it stands in for | Resolution | License | Notes |
|---|---|---|---|---|---|
| Province and county borders | **geoBoundaries** CHN ADM1/ADM2 (or Natural Earth admin-1) | Province picker, step 1 ranking | vector | CC BY 4.0 / public domain | See the boundary warning below |
| **Cold-water proxy** | **CHELSA** or **WorldClim 2.1** annual mean air temperature (BIO1) | Shallow groundwater temperature. As a rule of thumb, groundwater ≈ mean annual air temperature + 1–2 °C (Benz et al. 2017) | 1 km | CHELSA CC BY 4.0. **WorldClim is non-commercial only**, so use CHELSA for Nofitech | The single most important layer for salmon and trout |
| **Water stress** | **WRI Aqueduct 4.0**: baseline water stress + **groundwater table decline** | Whether there's enough make-up water, and the regulatory risk around it | sub-basin / aquifer polygons | CC BY 4.0 ([GitHub](https://github.com/wri/Aqueduct40)) | Also on Google Earth Engine. Groundwater units follow WHYMAP |
| Elevation | Copernicus DEM GLO-90 (or SRTM) | Cost of pumping, flood exposure, the high-altitude cold belt | 90 m | free (Copernicus) | Aggregate to hexes |
| Distance to coast | Natural Earth coastline | Seawater intake for marine RAS | vector | public domain | Compute distance per hex |
| Markets | Natural Earth populated places, or **GHSL** urban centres | Distance to Shanghai, Beijing and Guangzhou for fresh salmon | vector / 1 km | public domain / CC BY 4.0 | |
| **Known farms** | our `data/known_salmonid_farms_china.csv` (24 sites) | The farms we check the scores against | points | own work | Already done |
| Subsidies (placeholder) | Hand-entered from CONTEXT.md §4 (Fujian, Jiangsu, Zhejiang/Ningbo, Anhui, Guangdong, Shandong/Yantai plan, Liaoning/Dalian plan) | The subsidy contact's data | province | own | Clearly labelled as a mockup |

## Tier 2: makes it look like real geology (nice to have)
| Layer | Dataset | Stands in for | License / access |
|---|---|---|---|
| Water table depth | Fan, Li & Miguez-Macho 2013/2017 global model ([JRC AquaKnow](https://aquaknow.jrc.ec.europa.eu/node/18916)) | Groundwater depth | Free for research with citation. Check terms for commercial use |
| Shallow groundwater temperature (modelled) | Benz et al. 2017 ERL, about 1 km; 2024 Nat. Geosci. update ([KIT record](https://openpolar.no/Record/ftdatacite:10.5445%2Fir%2F1000171587)) | A direct temperature layer instead of the air-temperature proxy | Repository terms to be confirmed |
| Aquifer productivity | **WHYMAP** groundwater resources map (BGR) | Groundwater yield | Free with attribution |
| Karst aquifers | **WOKAM** World Karst Aquifer Map (BGR) | Southern China karst springs | Free with attribution |
| Rock types | **GLiM** (Hartmann & Moosdorf 2012) | Foundation conditions and water chemistry | PANGAEA, CC BY |
| Permeability | **GLHYMPS 2.0** (Borealis) | Aquifer quality | CC BY |
| Seismic hazard | GEM Global Seismic Hazard Map | Exclusion zones | **CC BY-NC-SA**: OK for an internal mockup, not for a product |
| Power plants and grid | WRI Global Power Plant Database / OSM power lines (Geofabrik China) | Grid capacity (State Grid mattered in Ningbo) | CC BY 4.0 / ODbL |
| Flood risk | Aqueduct floods | Exclusion zones | CC BY 4.0 |

## What only the researcher can give (= the "ask" after the mockup)
- Measured groundwater **temperature, yield, depth and salinity** from Chinese wells and boreholes.
- **Water chemistry** (Fe, Mn, H₂S, CO₂, nitrate). This is the treatment need, which is Nofitech's own area.
- China-specific hydrogeological maps (China Geological Survey). These are much finer than the global models.

## Things to watch
- **China's borders.** Maps published in or for China need officially approved boundaries (审图号). geoBoundaries and Natural Earth draw disputed areas differently from the official Chinese map. That's fine for an internal Nofitech mockup, but **don't show it to Chinese partners without fixing the boundaries**.
- **Licenses.** Use CHELSA instead of WorldClim, and treat the GEM seismic map as internal only.
- **Proxy honesty.** The mockup must label every geology layer as a "global proxy". That's the point of the pitch: "imagine this with real data".
