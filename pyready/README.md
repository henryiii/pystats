To run:

```bash
# Take list of projects and get all json info
uv run pyready.py myproj.txt --output myproj.json
# Process json info into readyness info
uv run pymodel.py myproj.json
```

You can get a list of the top packages from the parent folder with:

```bash
jq -r '.rows[:360] | .[] | .project' top-pypi-packages.min.json > pyready/top360.txt
```
