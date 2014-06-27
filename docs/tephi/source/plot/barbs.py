import matplotlib.pyplot as plt
import numpy as np

_BARB_BINS = np.arange(20) * 5 + 3
knots = {0: '1-2 knots',
         1: '3-7 knots',
         2: '8-12 knots',
         3: '13-17 knots',
         4: '18-22 knots',
         5: '23-27 knots',
         6: '28-32 knots',
         7: '33-37 knots',
         8: '38-42 knots',
         9: '43-47 knots',
         10: '48-52 knots',
         11: '53-57 knots',
         12: '58-62 knots',
         13: '63-67 knots',
         14: '68-72 knots',
         15: '73-77 knots',
         16: '78-82 knots',
         17: '83-87 knots',
         18: '88-92 knots',
         19: '93-97 knots',
         20: '98-102 knots'}

color = 'blue'
kwargs = dict(length=8, color=color)
lsx = 1
rsx = 3
ly = 23
delta = 0.3

plt.barbs(lsx, ly, 0, 0, **kwargs)
plt.text(lsx + delta, ly, 'Calm')

plt.plot([lsx - 0.36, lsx], [ly - 2, ly -2], linewidth=2, color=color)
plt.text(lsx + delta, ly - 2, knots[0])

for i, u in enumerate(range(5, 50, 5)):
    y = ly - (i + 2) * 2
    plt.barbs(lsx, y, u, 0, **kwargs)
    plt.text(lsx + delta, y, knots[np.searchsorted(_BARB_BINS, u, side='right')])

for i, u in enumerate(range(50, 105, 5)):
    y = ly - i * 2
    plt.barbs(rsx, y, u, 0, **kwargs)
    plt.text(rsx + delta, y, knots[np.searchsorted(_BARB_BINS, u, side='right')])

ax = plt.gca()
ax.set_xlim(0, 5)
ax.set_ylim(1, 25)
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)
plt.show()
