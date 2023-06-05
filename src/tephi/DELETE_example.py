import matplotlib.pyplot as plt
import os.path
import matplotlib.patheffects as pe
from src import tephi

dew_point = os.path.join(tephi.DATA_DIR, "dews.txt")
dew_data = tephi.loadtxt(dew_point, column_titles=("pressure", "dewpoint"))
dews = zip(dew_data.pressure, dew_data.dewpoint)
tpg = tephi.Tephigram()
profile = tpg.plot(
    dews,
    label="Dew-point temperature",
    linewidth=2,
    linestyle="--",
    marker="s",
)
barbs = [
    (0, 0, 900),
    (1, 30, 850),
    (5, 60, 800),
    (10, 90, 750),
    (15, 120, 700),
    (20, 150, 650),
    (25, 180, 600),
    (30, 210, 550),
    (35, 240, 500),
    (40, 270, 450),
    (45, 300, 400),
    (50, 330, 350),
    (55, 360, 300),
]

# profile.barbs(barbs, edgecolor="black", facecolor='black', sizes={"spacing": 0.2},lw=3)
profile.barbs(
    barbs,
    edgecolor="red",
    facecolor="black",
    sizes={"spacing": 0.2},
    lw=2,
    path_effects=[pe.Stroke()],
)

plt.show()
