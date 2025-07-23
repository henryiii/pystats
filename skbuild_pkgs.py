#!/usr/bin/env -S uv run -q

# /// script
# dependencies = ["pandas", "matplotlib"]
# ///

import pandas as pd
import matplotlib.pyplot as plt
import datetime

plt.style.use("ggplot")

rel = pd.read_json("skbuild_releases.json")
rel.publishedAt = pd.to_datetime(rel.publishedAt)
rel.tagName = rel.tagName.str[1:]

def mk_rel(version, dtime):
    major = version.endswith(".0")
    ax = plt.gca()
    if major:
        ax.annotate(
            version.removesuffix(".0"),
            xy=(dtime, 100),
            xytext=(dtime, -200),
            arrowprops=dict(facecolor="black", shrink=0.01),
        )
    else:
        ax.plot(dtime, 50, 'g.')

df = pd.read_csv("skbuild_pkgs.csv", index_col=0, parse_dates=True)
df.plot(legend=False, ylabel="GitHub non-fork matches", style="-o")

for row in rel.itertuples():
    mk_rel(row.tagName, row.publishedAt)


# Move y-axis to the right
ax = plt.gca()
ax.yaxis.set_label_position("right")
ax.yaxis.tick_right()
ax.set_ylim(ymin=-200)

#plt.show()
plt.savefig("skbuild_pkgs.svg")  #  transparent=True)
