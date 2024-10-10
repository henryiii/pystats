# /// script
# dependencies = ["requests"]
# ///

import requests
import json
from pathlib import Path

my = {
    "awkward",
    "awkward-cpp",
    "boost-histogram",
    "build",
    "cabinetry",
    "check-sdist",
    "cibuildwheel",
    "cmake",
    "cython-cmake",
    "decaylanguage",
    "f2py-cmake",
    "flake8-errmsg",
    "goofit",
    "hepunits",
    "hist",
    "histoprint",
    "iminuit",
    "meson-python",
    "mplhep",
    "ninja",
    "nox",
    "particle",
    "pipx",
    "plumbum",
    "pybind11",
    "pybind11-global",
    "pyhepmc",
    "pyhf",
    "pylhe",
    "pyproject-metadata",
    "repo-review",
    "resample",
    "scikit-build",
    "scikit-build-core",
    "scikit-hep",
    "sp-repo-review",
    "sphinxcontrib-moderncmakedomain",
    "uhi",
    "uproot",
    "uproot-browser",
    "validate-pyproject",
    "validate-pyproject-schema-store",
    "vector",
}

projs = [
    requests.get(f"https://pypi.org/pypi/{proj}/json").json() for proj in sorted(my)
]

Path("myproj.json").write_text(json.dumps(projs))
