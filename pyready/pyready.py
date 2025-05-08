# /// script
# dependencies = ["requests", "rich"]
# ///

import requests
import json
from pathlib import Path
import argparse
from typing import Any
from collections.abc import Generator
import rich.progress


def get_json(filelist: Path) -> Generator[Any]:
    with filelist.open(encoding="utf-8") as f:
        lines = f.readlines()

    for line in rich.progress.track(
        lines, description=f"Processing {filelist} with PyPI"
    ):
        proj = line.strip()
        yield requests.get(f"https://pypi.org/pypi/{proj}/json").json()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filelist", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    with args.output.open("w", encoding="utf-8") as f:
        json.dump(list(get_json(args.filelist)), f)
