#!/usr/bin/env bash
# Download the open datasets that build_hexes.py needs into data/raw/
# (about 390 MB to download, 1.1 GB unpacked). Each dataset gets its own folder.
# Sources and licences: DATA_SOURCES.md.
set -euo pipefail
cd "$(dirname "$0")/.."
RAW=data/raw
mkdir -p "$RAW"/{boundaries,chelsa,aqueduct,ne_coastline,ne_places,terrain_z6}

get() { curl -sfL --retry 2 -o "$1" "$2"; }

get "$RAW/boundaries/geoBoundaries-CHN-ADM1_simplified.geojson" \
  "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/CHN/ADM1/geoBoundaries-CHN-ADM1_simplified.geojson"
get "$RAW/ne_coastline/ne_10m_coastline.zip" "https://naciscdn.org/naturalearth/10m/physical/ne_10m_coastline.zip"
get "$RAW/ne_places/ne_10m_populated_places_simple.zip" "https://naciscdn.org/naturalearth/10m/cultural/ne_10m_populated_places_simple.zip"

# AWS Terrain Tiles (terrarium encoding), zoom 6, tiles covering China
for x in $(seq 44 56); do
  for y in $(seq 20 28); do
    get "$RAW/terrain_z6/6_${x}_${y}.png" "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/6/$x/$y.png" &
  done
  wait
done

get "$RAW/chelsa/CHELSA_bio1_1981-2010_V.2.1.tif" \
  "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_bio1_1981-2010_V.2.1.tif"
get "$RAW/aqueduct/aqueduct-4-0-water-risk-data.zip" "https://files.wri.org/aqueduct/aqueduct-4-0-water-risk-data.zip"

unzip -oq "$RAW/ne_coastline/ne_10m_coastline.zip" -d "$RAW/ne_coastline/extracted"
unzip -oq "$RAW/ne_places/ne_10m_populated_places_simple.zip" -d "$RAW/ne_places/extracted"
unzip -oq "$RAW/aqueduct/aqueduct-4-0-water-risk-data.zip" -d "$RAW/aqueduct/extracted"
echo "Done: $(du -sh "$RAW" | cut -f1) in $RAW"
