"""Publish a layer as a new hosted feature service on ArcGIS Online.

Run this ONCE per layer to create the feature service for the first time.
It will print the Item ID — save it in .env. After that, use sync_agol.py
for all subsequent releases.

Usage:
    uv run python scripts/publish_agol.py --layer taz --version v8.3.0 --public
    uv run python scripts/publish_agol.py --layer maz --version v1.0.0 --public
"""
import argparse
import os
import sys

import geopandas as gpd
from dotenv import load_dotenv

from analysiszones import agol

load_dotenv()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layer", choices=list(agol.LAYERS), required=True)
    parser.add_argument("--version", required=True, help="Release version tag, e.g. v8.3.0")
    parser.add_argument("--public", action="store_true", help="Share the layer publicly after publishing")
    args = parser.parse_args()

    cfg = agol.LAYERS[args.layer]

    for var in ("AGOL_PORTAL_URL", "AGOL_USERNAME", "AGOL_PASSWORD"):
        if not os.environ.get(var):
            print(f"ERROR: {var} is not set. Check your .env.")
            sys.exit(1)

    data_path = cfg["data_path"]
    if not data_path.exists():
        print(f"ERROR: Data file not found at {data_path}")
        sys.exit(1)

    print(f"Reading {args.layer.upper()} data from {data_path} ...")
    gdf = gpd.read_file(data_path, engine="pyogrio")

    print("Connecting to ArcGIS Online ...")
    gis = agol.connect()

    visibility = "public" if args.public else "private"
    print(f"Publishing '{cfg['title']}' ({args.version}) as a {visibility} hosted feature layer ...")
    item_id = agol.publish(gis, args.layer, gdf, version=args.version, public=args.public)

    env_var = cfg["item_id_env"]
    print(f"\nSuccess! Add the following line to your .env:")
    print(f"  {env_var}={item_id}")


if __name__ == "__main__":
    main()
