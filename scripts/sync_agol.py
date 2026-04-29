"""Overwrite a hosted feature service with the current layer data.

Also updates the item description with the current version and a link to
the GitHub releases page. The title is kept stable across releases.

Usage:
    uv run python scripts/sync_agol.py --layer taz --version v8.4.0
    uv run python scripts/sync_agol.py --layer maz --version v1.0.0
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
    parser.add_argument("--version", required=True, help="Release version tag, e.g. v8.4.0")
    args = parser.parse_args()

    cfg = agol.LAYERS[args.layer]
    env_var = cfg["item_id_env"]

    for var in ("AGOL_PORTAL_URL", "AGOL_USERNAME", "AGOL_PASSWORD", env_var):
        if not os.environ.get(var):
            hint = f"Run publish_agol.py --layer {args.layer} first." if var == env_var else "Check your .env."
            print(f"ERROR: {var} is not set. {hint}")
            sys.exit(1)

    data_path = cfg["data_path"]
    if not data_path.exists():
        print(f"ERROR: Data file not found at {data_path}")
        sys.exit(1)

    print(f"Reading {args.layer.upper()} data from {data_path} ...")
    gdf = gpd.read_file(data_path, engine="pyogrio")

    print("Connecting to ArcGIS Online ...")
    gis = agol.connect()

    item_id = os.environ[env_var]
    print(f"Overwriting '{cfg['title']}' → {args.version} (item: {item_id}) ...")
    result = agol.overwrite_feature_service(gis, item_id, gdf, version=args.version)

    added = len(result.get("addResults", []))
    failed = sum(1 for r in result.get("addResults", []) if not r.get("success"))
    print(f"Done: {added} features synced, {failed} failed.")


if __name__ == "__main__":
    main()
