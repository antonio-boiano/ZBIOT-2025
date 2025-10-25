import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import seaborn as sns
import matplotlib.pyplot as plt

# plt.rc('text', usetex=True)
# plt.rc('font', family='serif')
# plt.rcParams["font.size"] = "10"
# plt.rcParams["axes.titlesize"] = "10"
# plt.rcParams["axes.labelsize"] = "10"
# plt.rcParams["legend.fontsize"] = "8"
# plt.rcParams['hatch.linewidth'] = "1"
plt.rc('font', family='serif')
plt.rcParams.update({
    "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
    "legend.fontsize": 8, 'hatch.linewidth': 1
})

def get_figsize(columnwidth, wf=0.5, hf=(5.**0.5-1.0)/1.0, ):
    """Parameters:
    - wf [float]:  width fraction in columnwidth units
    - hf [float]:  height fraction in columnwidth units.
                    Set by default to golden ratio.
    - columnwidth [float]: width of the column in latex. Get this from LaTeX 
                            using \showthe\columnwidth
    Returns:  [fig_width,fig_height]: that should be given to matplotlib
    """
    fig_width_pt = columnwidth*wf 
    inches_per_pt = 1.0/72.27               # Convert pt to inch
    fig_width = fig_width_pt*inches_per_pt  # width in inches
    fig_height = fig_width*hf      # height in inches
    return [fig_width, fig_height]

import numpy as np
from matplotlib import colors as mcolors

def get_styles(n_val=8,color_p = None):
    base_colors = ['#66C2A5', '#8DA0CB', '#E5C494', '#B3B3B3', '#A6D854']
    # Interpolazione se servono più colori
    if n_val <= len(base_colors):
        palette = base_colors[:n_val]
    else:
        rgb = np.array([mcolors.to_rgb(c) for c in base_colors])
        palette = []
        for i in range(n_val):
            pos = i * (len(base_colors) - 1) / (n_val - 1)
            idx = int(pos)
            frac = pos - idx
            if idx == len(base_colors) - 1:
                color = rgb[idx]
            else:
                color = rgb[idx] * (1 - frac) + rgb[idx + 1] * frac
            palette.append(mcolors.to_hex(color))

    linestyles = [
        '-',                  # linea solida
        '--',                 # linea tratteggiata
        ':',                  # linea puntinata
        '-.',                 # linea tratto-punto
        (0, (1, 1)),          # puntinato molto fitto
        (0, (5, 1)),          # punto-lungo
        (0, (5, 5)),          # tratto-spazio regolare
        (0, (5, 10)),         # trattini lunghi e spazi larghi
        (0, (10, 5)),         # trattini molto lunghi
        (0, (3, 5, 1, 5)),    # ciclo tratto/punto
        (0, (3, 1, 1, 1)),    # tratto breve + punto breve
        (0, (2, 2, 10, 2)),   # pattern misto con spazio extra
        (0, (1, 5)),          # puntini distanziati
    ]
    return palette, linestyles[:n_val]
    