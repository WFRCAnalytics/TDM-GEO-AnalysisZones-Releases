# TDM GEO Analysis Zones — Releases

Official source of truth for **Traffic Analysis Zones (TAZ)** — and **Micro-Analysis Zones (MAZ)** in the future — used by the Wasatch Front Travel Demand Model (TDM) and any downstream applications.

Each release is a tagged Git commit. The shapefile in `data/<layer>/` always reflects the version at that tag.

---

## Repository Structure

```
TDM-GEO-AnalysisZones-Releases/
├── data/
│   ├── taz/
│   │   ├── TAZ.shp           # Authoritative TAZ shapefile (+ sidecar files)
│   │   └── ...               # .shx  .dbf  .prj  .cpg
│   └── maz/                  # Populated when MAZ is introduced
│
├── scripts/
│   ├── validate.py           # Validate a layer before cutting a release
│   ├── publish_agol.py       # Create a new hosted feature service (run once per layer)
│   ├── sync_agol.py          # Overwrite an existing hosted feature service
│   └── export.py             # Convert a layer to alternate formats
│
├── src/analysiszones/
│   ├── agol.py               # Layer registry + ArcGIS Online helpers
│   └── validate.py           # Validation logic (CRS, geometry, schema, duplicates)
│
├── .env.example              # Template for ArcGIS Online credentials
├── CHANGELOG.md              # Human-readable release history
├── pyproject.toml            # Python project and dependency manifest
└── uv.lock                   # Locked dependency graph for reproducible installs
```

---

## Versioning

Releases follow the scheme **`vMAJOR.MINOR.PATCH`** (e.g., `v8.3.0`, `v8.4.0`).

- Each tag points to a commit where the layer shapefile is the exact dataset for that release.
- `CHANGELOG.md` describes what changed between versions.
- To retrieve an older version of TAZ: `git checkout v8.3.0 -- data/taz/`

---

## Getting Started

### 1. Install uv

uv is the only tool you need to install manually. It manages Python and all dependencies.

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify the install:
```bash
uv --version
```

### 2. Clone and Sync

```bash
git clone <repo-url>
cd TDM-GEO-AnalysisZones-Releases
uv sync
```

`uv sync` will:
- Download Python 3.11 automatically if it is not already installed
- Create `.venv/` inside the repository
- Install all locked dependencies from `uv.lock`

No separate `pip install`, `conda`, or virtual environment setup is needed.

### 3. Environment Variables (ArcGIS Online)

Copy the template and fill in your credentials:

```bash
cp .env.example .env
```

| Variable            | Description                                                        |
|---------------------|--------------------------------------------------------------------|
| `AGOL_PORTAL_URL`   | ArcGIS Online or Enterprise portal URL                             |
| `AGOL_USERNAME`     | ArcGIS Online username                                             |
| `AGOL_PASSWORD`     | ArcGIS Online password                                             |
| `AGOL_TAZ_ITEM_ID`  | Item ID of the TAZ hosted feature service (set after first publish)|
| `AGOL_MAZ_ITEM_ID`  | Item ID of the MAZ hosted feature service (set after first publish)|

`.env` is git-ignored and should never be committed.

---

## Scripts

All scripts are run from the repository root via `uv run` and accept a `--layer` argument.

### Validate

Checks CRS, geometry validity, required fields, and duplicate zone IDs before a release.

```bash
uv run python scripts/validate.py --layer taz
uv run python scripts/validate.py --layer maz
```

### Publish to ArcGIS Online (first time only)

Creates a new hosted feature service for a layer. Run this **once per layer**. It prints the
Item ID — copy it into `.env` as `AGOL_TAZ_ITEM_ID` or `AGOL_MAZ_ITEM_ID`.

```bash
uv run python scripts/publish_agol.py --layer taz --version v8.3.0 --public
uv run python scripts/publish_agol.py --layer maz --version v1.0.0 --public
```

### Sync to ArcGIS Online (every release)

Overwrites the existing hosted feature service with the current shapefile.
Requires the corresponding `AGOL_<LAYER>_ITEM_ID` to be set in `.env`.

```bash
uv run python scripts/sync_agol.py --layer taz --version v8.4.0
uv run python scripts/sync_agol.py --layer maz --version v1.0.0
```

### Export to Alternate Formats

Converts a layer shapefile to a different format for downstream use.
Output is written to `exports/` (git-ignored).

```bash
uv run python scripts/export.py --layer taz --format gpkg        # GeoPackage
uv run python scripts/export.py --layer taz --format geojson     # GeoJSON
uv run python scripts/export.py --layer taz --format geoparquet  # GeoParquet
uv run python scripts/export.py --layer taz --format sqlite      # SQLite (for CubePy / ABM)
```

---

## Release Workflow

### First release of a new layer

```bash
# 1. Place shapefile in data/<layer>/
uv run python scripts/validate.py --layer taz

# 2. Publish to ArcGIS Online and save the printed Item ID to .env
uv run python scripts/publish_agol.py --layer taz --version v8.3.0 --public

# 3. Commit and tag
git add data/taz/ CHANGELOG.md
git commit -m "Release v8.3.0 — Wasatch Front TAZ (YYYY-MM-DD)"
git tag v8.3.0
git push && git push --tags
```

### Subsequent releases

```bash
# 1. Place updated shapefile in data/<layer>/
uv run python scripts/validate.py --layer taz

# 2. Overwrite the existing feature service
uv run python scripts/sync_agol.py --layer taz --version v8.4.0

# 3. Commit and tag
git add data/taz/ CHANGELOG.md
git commit -m "Release v8.4.0"
git tag v8.4.0
git push && git push --tags
```

### When the shapefile filename changes (two-commit workflow)

If the shapefile is renamed (e.g. `WFv900_TAZ.shp` → `WFv1000_TAZ.shp`), Git must track the rename and the code must be updated **before** the new data lands. Do this as two separate commits.

**Commit 1 — rename only (no data change):**

```bash
# 1a. Rename every sidecar file (.shp .shx .dbf .prj .cpg) in the data folder.
#     Use git mv for each so Git tracks the rename rather than a delete+add.
git mv data/taz/WFv900_TAZ.shp  data/taz/WFv1000_TAZ.shp
git mv data/taz/WFv900_TAZ.shx  data/taz/WFv1000_TAZ.shx
git mv data/taz/WFv900_TAZ.dbf  data/taz/WFv1000_TAZ.dbf
git mv data/taz/WFv900_TAZ.prj  data/taz/WFv1000_TAZ.prj
git mv data/taz/WFv900_TAZ.cpg  data/taz/WFv1000_TAZ.cpg

# 1b. Update the data_path for that layer in src/analysiszones/agol.py.
#     The "data_path" key is the only place the filename is registered:
#
#       "taz": {
#           "data_path": Path("data/taz/WFv1000_TAZ.shp"),   ← change this
#           ...
#       }

# 1c. Commit the rename + code change together.
git add data/taz/ src/analysiszones/agol.py
git commit -m "rename taz file for vX.Y.Z (pre) release"
git push
```

**Commit 2 — replace data and publish:**

```bash
# 2a. Copy the new shapefile (all sidecar files) from the model folder
#     into data/taz/, overwriting the placeholders from commit 1.

# 2b. Validate the new data.
uv run python scripts/validate.py --layer taz

# 2c. Sync to ArcGIS Online.
uv run python scripts/sync_agol.py --layer taz --version vX.Y.Z

# 2d. Commit, tag, and push.
git add data/taz/ CHANGELOG.md
git commit -m "Release vX.Y.Z — Wasatch Front TAZ"
git tag vX.Y.Z
git push && git push --tags
```

> **Why two commits?** Git detects renames by comparing file content. If the rename and the data replacement happen in the same commit, Git sees a delete + add of unrelated content and loses history. Separating the rename (commit 1) from the data update (commit 2) keeps `git log -- data/taz/WFv1000_TAZ.shp` traceable back through the old filename.

---

## Data

| Zone Type | Status  | Format    | CRS                             | ArcGIS Online |
|-----------|---------|-----------|---------------------------------|---------------|
| TAZ       | Active  | Shapefile | NAD83 UTM Zone 12N (EPSG:26912) | [Wasatch Front TAZ](https://wfrc.maps.arcgis.com/home/item.html?id=6cdfccde494d41a291de6da3c8c1bf08) |
| MAZ       | Planned | TBD       | TBD                             | — |

MAZ support will be added when the Wasatch Front TDM transitions to an Activity-Based Model (ABM).

---

## Dependencies

Managed via `uv` and locked in `uv.lock`.

| Package         | Purpose                                    |
|-----------------|--------------------------------------------|
| `arcgis`        | ArcGIS Online / Enterprise API             |
| `geopandas`     | Geospatial data reading and processing     |
| `fiona`         | Shapefile I/O backend                      |
| `pyogrio`       | Fast vector I/O backend                    |
| `pandas`        | Tabular data operations                    |
| `python-dotenv` | Load credentials from `.env`               |
