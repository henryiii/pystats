To run:

```bash
# Take list of projects and get all json info
uv run pyready.py myproj.txt --output myproj.json
# Process json info into readyness info
uv run pymodel.py myproj.json
```