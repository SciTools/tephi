"""Script to generate the Tephi logo."""

from pathlib import Path

import matplotlib.pyplot as plt
import tephi


# Prepare the data.
dew_point = Path(tephi.DATA_DIR) / "dews.txt"
dew_data = tephi.loadtxt(str(dew_point), column_titles=('pressure', 'dewpoint'))
# Limit the data to ensure there are no areas without lines.
dews = zip(dew_data.pressure[1:-2], dew_data.dewpoint[1:-2])


def coarsen_tephi_line(spec: list[tuple[int, int]], factor: int):
    return [(step * factor, zoom) for step, zoom in spec]


def restyle_tephi_line(line: dict):
    return line | dict(color="white", linestyle="solid", linewidth=3)


tephi.ISOBAR_SPEC = coarsen_tephi_line(tephi.ISOBAR_SPEC, 5)
tephi.WET_ADIABAT_SPEC = coarsen_tephi_line(tephi.WET_ADIABAT_SPEC, 5)
tephi.MIXING_RATIO_SPEC = coarsen_tephi_line(tephi.MIXING_RATIO_SPEC, 3)

tephi.ISOBAR_LINE = restyle_tephi_line(tephi.ISOBAR_LINE)
tephi.WET_ADIABAT_LINE = restyle_tephi_line(tephi.WET_ADIABAT_LINE)
tephi.MIXING_RATIO_LINE = restyle_tephi_line(tephi.MIXING_RATIO_LINE)

tpg = tephi.Tephigram()
tpg.plot(
    dews,
    color="white",
    linewidth=3,
    linestyle="dashed",
)

ax = plt.gca()

ax.set_facecolor("#7DA7FC")

for key, artist in ax.axis.items():
    artist.set_visible(False)
ax.grid(False)

for text in ax.texts:
    text.set_visible(False)

ax.set_aspect("auto")
plt.gcf().set_size_inches(6, 6)

ax.text(
    0.5,
    0.5,
    'Tφ',
    horizontalalignment='center',
    verticalalignment='center',
    transform=ax.transAxes,
    size=256,
    style="italic",
    weight="bold",
    zorder=10,
    color="white",
)

static_dir = Path(__file__).parent / "_static"
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
plt.savefig(static_dir / "tephi-logo.svg")
