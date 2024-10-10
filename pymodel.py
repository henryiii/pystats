# /// script
# dependencies = ["pydantic", "rich", "requests"]
# requires-python = ">=3.13"
# ///

import pydantic
from pathlib import Path
import json
from rich import print
import typing
import enum
from collections.abc import Generator
import collections


class Info(pydantic.BaseModel):
    name: str
    classifiers: list[str]
    version: str
    requires_python: str | None


class Release(pydantic.BaseModel):
    filename: str


class Project(pydantic.BaseModel):
    info: Info
    releases: dict[str, list[Release]]


class ProjectList(pydantic.RootModel):
    root: list[Project]


class Status(enum.Enum):
    Wheel = enum.auto()
    Classifier = enum.auto()
    NoWheel = enum.auto()
    NoClassifier = enum.auto()
    Unknown = enum.auto()


def get_classifiers(proj: Project) -> list[str]:
    versions = (c.split()[-1] for c in proj.info.classifiers if "Python :: 3." in c)
    return sorted(versions, key=lambda v: [int(d) for d in v.split(".")])


def get_status(proj: Project) -> Status:
    if [r.filename for r in proj.releases[proj.info.version] if "313" in r.filename]:
        return Status.Wheel

    classifiers = get_classifiers(proj)

    if "3.13" in classifiers:
        return Status.Classifier

    if [r.filename for r in proj.releases[proj.info.version] if "312" in r.filename]:
        return Status.NoWheel

    if classifiers:
        return Status.NoClassifier

    return Status.Unknown


def display(res: ProjectList) -> Generator[None]:
    stats = collections.Counter()
    max_classifiers = collections.Counter()
    for proj in res.root:
        print(f"[bold]{proj.info.name}", end=" ")
        status = get_status(proj)
        stats.update([status])
        match get_status(proj):
            case Status.Wheel:
                print("[green]Yes Wheels", end=" ")
            case Status.Classifier:
                print("[green]Yes", end=" ")
            case Status.NoWheel:
                print("[red bold]Needs wheels!", end=" ")
            case Status.NoClassifier:
                classifiers = get_classifiers(proj)
                print(f"[red]No ({classifiers[-1]})", end=" ")
                max_classifiers.update([classifiers[-1]])
            case Status.Unknown:
                pass
            case never:
                typing.assert_never(never)

        print(f"[yellow]{proj.info.requires_python}")

    print()
    print("[bold]Totals:")
    for status in Status:
        print(f"  {status.name}: {stats.get(status)}")

    print()
    print("[bold]Max classifiers:")
    for clsfr, total in sorted(
        max_classifiers.items(), key=lambda v: [int(d) for d in v[0].split(".")],
        reverse=True
    ):
        print(f"  {clsfr}: {total}")


txt = Path("myproj.json").read_text()
lst = json.loads(txt)
res = ProjectList.model_validate_json(txt, strict=True)
display(res)
