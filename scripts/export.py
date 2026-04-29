"""Export a layer to an alternate format.

Reads the canonical data file defined in the layer registry (any format
geopandas supports) and writes to the requested output format.
Output is written to exports/ (git-ignored).

Usage:
    uv run python scripts/export.py --layer taz --format gpkg
    uv run python scripts/export.py --layer taz --format geojson
    uv run python scripts/export.py --layer taz --format geoparquet
    uv run python scripts/export.py --layer taz --format sqlite
"""
import argparse
import sys
from pathlib import Path

import geopandas as gpd

from analysiszones import agol

OUT_DIR = Path("exports")
FORMATS = ("gpkg", "geojson", "geoparquet", "sqlite")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layer", choices=list(agol.LAYERS), required=True)
    parser.add_argument("--format", choices=FORMATS, required=True)
    args = parser.parse_args()

    data_path = agol.LAYERS[args.layer]["data_path"]
    if not data_path.exists():
        print(f"ERROR: Data file not found at {data_path}")
        sys.exit(1)

    OUT_DIR.mkdir(exist_ok=True)
    gdf = gpd.read_file(data_path, engine="pyogrio")
    stem = args.layer

    match args.format:
        case "gpkg":
            out = OUT_DIR / f"{stem}.gpkg"
            gdf.to_file(out, driver="GPKG")
        case "geojson":
            out = OUT_DIR / f"{stem}.geojson"
            gdf.to_file(out, driver="GeoJSON")
        case "geoparquet":
            out = OUT_DIR / f"{stem}.parquet"
            gdf.to_parquet(out)
        case "sqlite":
            out = OUT_DIR / f"{stem}.sqlite"
            gdf.to_file(out, driver="SQLite", layer=stem)

    print(f"Exported → {out}")


if __name__ == "__main__":
    main()
