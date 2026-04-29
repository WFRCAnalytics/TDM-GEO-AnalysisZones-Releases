"""Run pre-release validation on a layer data file.

Usage:
    uv run python scripts/validate.py --layer taz
    uv run python scripts/validate.py --layer maz
"""
import argparse
import sys

from analysiszones import agol, validate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layer", choices=list(agol.LAYERS), required=True)
    args = parser.parse_args()

    data_path = agol.LAYERS[args.layer]["data_path"]

    print(f"Validating {data_path} ...")
    if not data_path.exists():
        print(f"  ERROR  File not found: {data_path}")
        sys.exit(1)

    ok = validate.run(data_path)
    if not ok:
        sys.exit(1)
    print("Validation passed — ready to release.")


if __name__ == "__main__":
    main()
