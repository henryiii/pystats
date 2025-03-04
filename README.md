This works like this:

## Step 1: download all index parquet files

You can download them with:

```bash
curl -L --remote-name-all $(curl -L "https://github.com/pypi-data/data/raw/main/links/dataset.txt")
```

Now you'll have `index-*.parquet` files.

## Step 2: produce latest pyproject csv's

You can use `pyproject-latest-to-csv.py` to produce `extract-pyproject-latest.csv`. This gets the latest versions of pyproject.toml file metadata.

```bash
python pyproject-latest-to-csv.py
```

## Step 3: Download pyproject.tomls

This is the "hard" step; you have to process a lot of GitHub requests. Use `pyproject-download.py` to produce `pyproject_contents.db`. It will reuse an existing one if possible.

```bash
python pyproject-download.py
```

## Step 4: Produce the latest version pickle

This file is slow to load (due to needing to parse all the TOML's), so we make a `.pkl` file of the parsed contents. We also make sure we only have the latest versions, since multiple runs of step 3 could produce newer versions.

```bash
python db_to_pickle.py
```

## Step 5: Run your queries!

Now you can use `compute_tool.py`/`compute_tools.py` to run queries over the data.


---

# 8,000 top packages (added for PyCon 2024)

## Download

Download the top packages list (monthly):

```bash
wget https://hugovk.github.io/top-pypi-packages/top-pypi-packages.min.json
```

## Print counts

Produce package lists based on what you are interested, for example:

```console
./compute-tool.py build-system.build-backend -b "'hatchling.build'" -c Reprs > hatchling_proj.txt
```

To print this out, see `count.py`.

## Count files for most recent release

Run the SQL query:

```console
duckdb < extract.sql
```

This will produce `'extract-filecount-latest.csv'`.
