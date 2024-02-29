#!/usr/bin/env python

import contextlib
import sqlite3
import tomllib
from collections import Counter


def main():
    counter = Counter()
    with contextlib.closing(sqlite3.connect("pyproject_contents.db")) as con:
        cursor = con.cursor()
        for row in cursor.execute("SELECT contents FROM pyproject"):
            (contents,) = row
            with contextlib.suppress(tomllib.TOMLDecodeError):
                toml = tomllib.loads(contents)
                tools = toml.get("tool", {}).keys()
                counter += Counter(f"tool.{k}" for k in tools)

    for i, (k, v) in enumerate(counter.most_common()):
        print(f"{i:3} {k}: {v}")


if __name__ == "__main__":
    main()
