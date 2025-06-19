
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib import rcParams
from matplotlib.font_manager import FontProperties
from scipy.interpolate import UnivariateSpline


def format_title(name):
    clean = name.replace("diff_data_website_sample10k_", "").replace('__enriched.json', '').replace('_sample10k_', '')
    clean = clean.replace("SD21", "SD 2.1").replace("SD15", "SD 1.5")
    if clean.lower() == 'pixart':
        return 'PixArt'
    else:
        return clean.replace('_', ' ').title().replace("Sd 2.1", "SD 2.1").replace("Sd 1.5", "SD 1.5")


font_path = "/System/Library/Fonts/Avenir.ttc"
font_prop = FontProperties(fname=font_path)
rcParams["font.family"] = font_prop.get_name()

hex_colors = ["#65c7de", "#5776b4", "#582949", "#b16243", "#e8b548"]
custom_cmap = mcolors.LinearSegmentedColormap.from_list("custom_gradient", hex_colors)
norm = mcolors.Normalize(vmin=0, vmax=1.0)

output_dir = "figs"
os.makedirs(output_dir, exist_ok=True)

base_path = '/Users/matyasbohacek/Projects/sae-diff-thomas-viz/src/assets'
files = [f for f in os.listdir(base_path) if "__enriched" in f]


# Helper function for spline smoothing
def splin(x, y):
    spline = UnivariateSpline(x, y, s=10.0)
    return spline(x)


for i, f in enumerate(files):
    data = json.load(open(f'{base_path}/{f}'))

    x = np.array(data['nb_fire'])
    temperature = 0.4
    y_raw = np.array(data['relative_energy_diff'])
    y = 1 / (1 + np.exp(-y_raw / temperature))
    colors = y  # use the same sigmoid-transformed values for color mapping
    sizes = data['nb_fire'] / np.max(data['nb_fire']) * 2400.0  # Adjusted size scaling

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.set_facecolor("white")

    scatter = ax.scatter(x, y, s=sizes, alpha=0.9, edgecolors='none',
                         linewidth=0, c=colors, cmap=custom_cmap, norm=norm)

    nbins = 100
    bins = np.linspace(np.percentile(x, 0.5), np.percentile(x, 99.5), nbins)
    indices = np.digitize(x, bins)
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    y_low = []
    y_high = []

    for j in range(1, nbins):
        bin_y = y[indices == j]
        if len(bin_y) > 0:
            y_low.append(np.percentile(bin_y, 5))
            y_high.append(np.percentile(bin_y, 95))
        else:
            y_low.append(np.nan)
            y_high.append(np.nan)

    y_low = np.array(y_low)
    y_high = np.array(y_high)

    y_low = splin(bin_centers, y_low)
    y_high = splin(bin_centers, y_high)

    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.0)
        spine.set_edgecolor("black")

    ax.set_xlabel('Nb of Fire  $||Z_i||_0$', fontsize=20)
    ax.set_ylabel('Relative Energy Difference', fontsize=20)
    ax.tick_params(axis='y', which='both', labelsize=20)

    ax.set_title(format_title(f), fontsize=40)
    ax.tick_params(axis='x', which='both', labelsize=20)

    v = 0.5
    pmin, pmax = np.percentile(x, [v, 100 - v])
    ax.set_xlim(0, pmax)
    ax.set_ylim(0, 1)

    output_filename = f"{output_dir}/{format_title(f).replace('SD 1.5', 'SD15').replace('SD 2.1', 'SD21')}.png"
    plt.savefig(output_filename, format='png', dpi=400,
                bbox_inches='tight', pad_inches=0.1, transparent=True)

    plt.close()
