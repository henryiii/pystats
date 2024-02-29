import contextlib
import pickle
import sqlite3
import tomllib
from collections.abc import Generator
from collections import Counter
from typing import Any
from pathlib import Path

def get_tomls_cached(db: str) -> Generator[tuple[str, str, dict[str, Any]], None, None]:
    pkl = Path(f"{db}.pkl")
    with pkl.open("rb") as f:
        yield from pickle.load(f)


def main():
    counter = Counter()
    with contextlib.closing(sqlite3.connect("pyproject_contents.db")) as con:
        cursor = con.cursor()
        for _, _, toml in get_tomls_cached("pyproject_contents.db"):
            backend = toml.get("build-system", {}).get("build-backend", "unknown")
            if isinstance(backend, str):
                counter[backend] += 1
            else:
                counter["busted"] += 1

    for i, (k, v) in enumerate(counter.most_common()):
        print(f"{i:3} {k}: {v}")

    print(f"total: {counter.total()}")

if __name__ == "__main__":
    main()
