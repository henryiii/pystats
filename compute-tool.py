#!/usr/bin/env python3

import argparse
import pickle
from collections import Counter
from collections.abc import Generator
from pathlib import Path
from typing import Any
import enum


class Contents(enum.Enum):
    Values = enum.auto()
    Reprs = enum.auto()
    Lengths = enum.auto()
    Lines = enum.auto()


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


def main(tool: str, get_contents: Contents, level: int = 0) -> None:
    if tool:
        match get_contents:
            case Contents.Reprs:
                print(f"{tool} contents:")
            case Contents.Lengths:
                print(f"{tool} lengths:")
            case Contents.Lines:
                print(f"{tool} lines:")
            case Contents.Values:
                print(tool + ".*" * (level + 1) + ":")
    else:
        if get_contents != Contents.Values:
            raise AssertionError("Can't get contents with no section")

        print("*:")

    if get_contents != Contents.Values and level > 0:
        raise AssertionError("Can't use level with contents")

    counter = Counter()
    for _, _, toml in get_tomls_cached("pyproject_contents.db"):
        item = dig(toml, *tool.split(".")) if tool else toml
        match item, get_contents:
            case None | "", _:
                pass
            case _, Contents.Values:
                counter += Counter(all_keys(item, level=level))
            case list(), Contents.Reprs:
                for x in item:
                    counter[repr(x)] += 1
            case _, Contents.Reprs:
                counter[repr(item)] += 1
            case _, Contents.Lengths:
                counter[len(item)] += 1
            case str(), Contents.Lines:
                counter[item.count("\n")] += 1
            case {}, Contents.Lines:
                counter[-1] += 1

    if get_contents in {Contents.Lengths, Contents.Lines}:
        for k, v in sorted(counter.items()):
            print(f"{k}: {v}")
    else:
        for k, v in counter.most_common():
            print(f"{k}: {v}")


def blame(tool: str, string: str, contents: Contents) -> None:
    if string and contents == Contents.Reprs:
        print(tool, "=", string)
    elif string and contents == Contents.Lengths:
        print(tool, "=", string, "chars")
    elif string and contents == Contents.Lines:
        print(tool, "=", string, "lines")
    else:
        print(tool, "= ...")

    for name, version, toml in get_tomls_cached("pyproject_contents.db"):
        item = dig(toml, *tool.split(".")) if tool else toml
        if not string and item:
            print(name, version, "=", repr(item))
        elif contents == Contents.Lengths and len(item) == int(string):
            print(name, version)
        elif contents == Contents.Reprs and repr(item) == string:
            print(name, version)
        elif (
            contents == Contents.Lines
            and isinstance(item, str)
            and item.count("\n") == int(string)
        ):
            print(name, version)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tool", help="Tool to processes")
    parser.add_argument(
        "-c", "--contents", default="Values", choices={c.name for c in Contents}
    )
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
        blame(args.tool, args.blame, Contents[args.contents])
    else:
        main(args.tool, Contents[args.contents], args.level)
