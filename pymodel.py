# /// script
# dependencies = ["pydantic", "rich"]
# ///

import pydantic
from pathlib import Path
import json
from rich import print


class Info(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(strict=True)

    name: str
    classifiers: list[str]
    version: str
    requires_python: str | None


class Release(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(strict=True)

    filename: str


class Project(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(strict=True)

    info: Info
    releases: dict[str, list[Release]]


class ProjectList(pydantic.RootModel):
    root: list[Project]


txt = Path("myproj.json").read_text()
lst = json.loads(txt)
res = ProjectList.model_validate_json(txt)

for proj in res.root:
    has_new = bool([c for c in proj.info.classifiers if "3.13" in c])
    has_old = bool([c for c in proj.info.classifiers if "3.12" in c])
    has_wheel = bool(
        [r.filename for r in proj.releases[proj.info.version] if "313" in r.filename]
    )
    old_wheel = bool(
        [r.filename for r in proj.releases[proj.info.version] if "312" in r.filename]
    )

    print(f"[bold]{proj.info.name}", end=" ")
    if has_new:
        print("[green]Yes", end=" ")
    if has_wheel:
        print("[green]Wheels", end=" ")
    elif old_wheel:
        print("[red bold]Needs wheels!", end=" ")

    if has_old and not has_new and not has_wheel:
        print("[red]No", end=" ")

    print(f"[yellow]{proj.info.requires_python}")
