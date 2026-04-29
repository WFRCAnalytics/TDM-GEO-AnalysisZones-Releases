import os
from pathlib import Path

import geopandas as gpd
from arcgis.gis import GIS
from arcgis.features import GeoAccessor, FeatureLayerCollection

RELEASES_URL = "https://github.com/WFRCAnalytics/TDM-GEO-AnalysisZones-Releases/releases"

# Layer registry — the only place that needs to change when a layer's format or
# path changes. Add MAZ (and any future layers) here when ready.
LAYERS: dict[str, dict] = {
    "taz": {
        "data_path": Path("data/taz/TAZ.shp"),
        "title": "Wasatch Front TAZ",
        "description_template": (
            "Traffic Analysis Zones (TAZ) for the Wasatch Front Travel Demand Model.\n\n"
            "Current version: {version}\n\n"
            "For all official releases and version history, visit:\n"
            f"{RELEASES_URL}"
        ),
        "tags": "TAZ, TDM, Wasatch Front, Transportation, WFRC",
        "item_id_env": "AGOL_TAZ_ITEM_ID",
    },
    "maz": {
        "data_path": Path("data/maz/MAZ.shp"),
        "title": "Wasatch Front MAZ",
        "description_template": (
            "Micro-Analysis Zones (MAZ) for the Wasatch Front Activity-Based Model.\n\n"
            "Current version: {version}\n\n"
            "For all official releases and version history, visit:\n"
            f"{RELEASES_URL}"
        ),
        "tags": "MAZ, ABM, Wasatch Front, Transportation, WFRC",
        "item_id_env": "AGOL_MAZ_ITEM_ID",
    },
}


def connect() -> GIS:
    gis = GIS(
        os.environ["AGOL_PORTAL_URL"],
        os.environ["AGOL_USERNAME"],
        os.environ["AGOL_PASSWORD"],
    )
    print(f"Connected as: {gis.properties.user.username}")
    return gis


def _to_sedf(gdf: gpd.GeoDataFrame):
    return GeoAccessor.from_geodataframe(gdf)


def publish(gis: GIS, layer: str, gdf: gpd.GeoDataFrame, *, version: str, public: bool = False) -> str:
    """Publish a GeoDataFrame as a new hosted feature layer. Returns item ID."""
    cfg = LAYERS[layer]
    description = cfg["description_template"].format(version=version)
    sdf = _to_sedf(gdf)
    feature_layer = sdf.spatial.to_featurelayer(
        title=cfg["title"],
        gis=gis,
        tags=cfg["tags"],
        description=description,
    )
    if public:
        feature_layer.update(item_properties={"access": "public"})
    return feature_layer.id


def overwrite_feature_service(gis: GIS, item_id: str, gdf: gpd.GeoDataFrame, *, version: str) -> dict:
    """Replace all features in an existing hosted feature layer with gdf contents."""
    item = gis.content.get(item_id)
    if item is None:
        raise ValueError(f"Item {item_id!r} not found on {gis.url}")

    cfg = next(c for c in LAYERS.values() if c["item_id_env"] and os.environ.get(c["item_id_env"]) == item_id)
    description = cfg["description_template"].format(version=version)
    item.update(item_properties={"description": description})

    layer = FeatureLayerCollection.fromitem(item).layers[0]
    layer.delete_features(where="1=1")

    sdf = _to_sedf(gdf)
    fs = sdf.spatial.to_featureset()
    return layer.edit_features(adds=fs.features)
