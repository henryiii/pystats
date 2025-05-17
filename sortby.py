import json
import sys


with open("top-pypi-packages-2025-05.min.json") as f:
    j = json.load(f)

projs = {
    l["project"]: (i, l["download_count"] * 30 // 24) for i, l in enumerate(j["rows"])
}

input_projects = {line.strip() for line in sys.stdin if line.strip()}

for name, stats in projs.items():
    if name in input_projects:
        print(f"| {name} | {stats[0]} | {stats[1]:,} |")
print()
valid = input_projects & projs.keys()
left_over = sorted(input_projects - projs.keys())
for name in left_over:
    print(name)

print(f"Found {len(valid)} ranked projects")
print(f"out of {len(input_projects)} projects")
