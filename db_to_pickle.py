#!/usr/bin/env python3

import contextlib
import pickle
import sqlite3
from collections.abc import Generator
from pathlib import Path
from typing import Any
from itertools import groupby

import tomllib
from packaging.version import Version, InvalidVersion


def version(version: str) -> Version:
    try:
        return Version(version)
    except InvalidVersion:
        return Version("0.0")


def get_tomls(db: str) -> Generator[tuple[str, str, dict[str, Any]], None, None]:
    with contextlib.closing(sqlite3.connect(db)) as con:
        cursor = con.cursor()
        CMD = "SELECT project_name, project_version, contents FROM pyproject ORDER BY project_name"
        vals = cursor.execute(CMD)
        for x in groupby(vals.fetchall(), key=lambda x: x[0]):
            project_name, group = x
            group = list(group)
            _, project_version, contents = max(group, key=lambda x: version(x[1]))
            if project_name == "cmake":
                print("Example: cmake", project_version, [x[1] for x in group])
            with contextlib.suppress(tomllib.TOMLDecodeError):
                yield project_name, project_version, tomllib.loads(contents)


def make_cache(db: str) -> None:
    pkl = Path(f"{db}.pkl")
    with pkl.open("wb", pickle.HIGHEST_PROTOCOL) as f:
        pickle.dump(list(get_tomls(db)), f)


if __name__ == "__main__":
    make_cache("pyproject_contents.db")
