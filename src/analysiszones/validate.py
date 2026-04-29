from pathlib import Path
import geopandas as gpd

# ── Configuration ─────────────────────────────────────────────────────────────
# Adjust these to match the actual shapefile schema and coordinate system.
TAZ_ID_FIELD = "TAZID"
REQUIRED_FIELDS = [TAZ_ID_FIELD]
EXPECTED_CRS = "EPSG:26912"   # NAD83 UTM Zone 12N — standard for Wasatch Front
# ─────────────────────────────────────────────────────────────────────────────


def load(shp_path: Path) -> gpd.GeoDataFrame:
    return gpd.read_file(shp_path, engine="pyogrio")


def _check_crs(gdf: gpd.GeoDataFrame) -> list[str]:
    if gdf.crs is None:
        return ["CRS is not defined"]
    if gdf.crs.to_epsg() != int(EXPECTED_CRS.split(":")[1]):
        return [f"CRS is {gdf.crs}, expected {EXPECTED_CRS}"]
    return []


def _check_geometry(gdf: gpd.GeoDataFrame) -> list[str]:
    errors = []
    null_count = gdf.geometry.isna().sum()
    if null_count:
        errors.append(f"{null_count} null geometries")
    invalid_count = (~gdf.geometry.dropna().is_valid).sum()
    if invalid_count:
        errors.append(f"{invalid_count} invalid geometries")
    return errors


def _check_schema(gdf: gpd.GeoDataFrame) -> list[str]:
    missing = [f for f in REQUIRED_FIELDS if f not in gdf.columns]
    return [f"Missing required fields: {missing}"] if missing else []


def _check_duplicates(gdf: gpd.GeoDataFrame) -> list[str]:
    if TAZ_ID_FIELD not in gdf.columns:
        return []
    dupes = gdf[TAZ_ID_FIELD].duplicated().sum()
    return [f"{dupes} duplicate {TAZ_ID_FIELD} values"] if dupes else []


def run(shp_path: Path) -> bool:
    """Return True if all checks pass, False otherwise."""
    gdf = load(shp_path)
    errors = (
        _check_crs(gdf)
        + _check_geometry(gdf)
        + _check_schema(gdf)
        + _check_duplicates(gdf)
    )
    if errors:
        for e in errors:
            print(f"  FAIL  {e}")
        return False
    print(f"  OK    {len(gdf)} features  CRS={gdf.crs}")
    return True
