import json

with open("top-pypi-packages-30-days.min.json") as f:
    j = json.load(f)

projs = {l["project"]: (i, l["download_count"]) for i, l in enumerate(j["rows"])}

my = {
    "awkward",
    "awkward0",
    "boost-histogram",
    "build",
    "cabinetry",
    "check-sdist",
    "cibuildwheel",
    "cmake",
    "decaylanguage",
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
    "probfit",
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
    "semester",
    "sp-repo-review",
    "sphinxcontrib-moderncmakedomain",
    "trampolim",
    "uhi",
    "uproot",
    "uproot-browser",
    "uproot4",
    "validate-pyproject",
    "validate-pyproject-schema-store",
    "vector",
}
myp = {k: v for k, v in projs.items() if k in my}

for p in myp:
    print(f"#{myp[p][0]:<4}", f"{p:30}", f"{myp[p][1]:,}")


print(f"Total monthly downloads: {sum(x[1] for x in myp.values())//1000000:}M")


for item in ["skbuild", "meson", "maturin"]:
    print("\n---\n")
    print(item)

    with open(f"{item}_proj.txt") as f:
        pkgs = [x.split()[0].lower().replace(".", "-").replace("_", "-") for x in f][1:]

    myp = {k: v for k, v in projs.items() if k in pkgs}
    for p in myp:
        print(f"#{myp[p][0]:<4}", f"{p:20}", f"{myp[p][1]:,}")
