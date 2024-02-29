#!/usr/bin/env python3

import argparse
import pickle
from collections import Counter
from collections.abc import Generator
from pathlib import Path
from typing import Any


def dig(value: Any, key: str, *keys: str) -> Any:
    res = value.get(key, {})
    return dig(res, *keys) if keys else res


def all_keys(
    d: dict[str, Any], level: int, *prefixes: str
) -> Generator[str, None, None]:
    for key, value in d.items():
        if isinstance(value, dict) and level > 0:
            yield from all_keys(value, level - 1, *prefixes, key)
        else:
            yield ".".join([*prefixes, key])


def get_tomls_cached(db: str) -> Generator[tuple[str, str, dict[str, Any]], None, None]:
    pkl = Path(f"{db}.pkl")
    with pkl.open("rb") as f:
        yield from pickle.load(f)


def main(tool: str, get_contents: bool, level: int = 0) -> None:
    if tool:
        if get_contents:
            print(f"{tool} contents:")
        else:
            print(tool + ".*" * (level + 1) + ":")
    else:
        if get_contents:
            raise AssertionError("Can't get contents with no section")

        print("*:")

    if get_contents and level > 0:
        raise AssertionError("Can't use level with contents")

    counter = Counter()
    for _, _, toml in get_tomls_cached("pyproject_contents.db"):
        item = dig(toml, *tool.split(".")) if tool else toml
        if item:
            if get_contents:
                if isinstance(item, list):
                    for x in item:
                        counter[repr(x)] += 1
                else:
                    counter[repr(item)] += 1
            else:
                counter += Counter(all_keys(item, level=level))

    for k, v in counter.most_common():
        print(f"{k}: {v}")


def blame(tool: str, string: str) -> None:
    if string:
        print(tool, "=", string)
    else:
        print(tool, "= ...")
    for name, version, toml in get_tomls_cached("pyproject_contents.db"):
        item = dig(toml, *tool.split(".")) if tool else toml
        if not string and item:
            print(name, version, "=", repr(item))
        elif repr(item) == string:
            print(name, version)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tool", help="Tool to processes")
    parser.add_argument("-c", "--contents", action="store_true")
    parser.add_argument(
        "-l", "--level", type=int, default=0, help="Unpack nested levels"
    )
    parser.add_argument(
        "-b",
        "--blame",
        help="print matching project names, empty string to print any value (careful)",
    )
    args = parser.parse_args()
    if args.blame is not None:
        assert args.level == 0
        assert not args.contents
        blame(args.tool, args.blame)
    else:
        main(args.tool, args.contents, args.level)
