import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib import rcParams
from matplotlib.font_manager import FontProperties
import seaborn as sns

font_path = "/System/Library/Fonts/Avenir.ttc"
font_prop = FontProperties(fname=font_path)
rcParams["font.family"] = font_prop.get_name()

hex_colors = ["#65c7de", "#5776b4", "#582949", "#b16243", "#e8b548"]
custom_cmap = mcolors.LinearSegmentedColormap.from_list("custom_gradient", hex_colors)
norm = mcolors.Normalize(vmin=-1.0, vmax=1.0)

output_dir = "correlation_plots"
os.makedirs(output_dir, exist_ok=True)


def format_title(name):
    if name.lower() == 'pixart':
        return 'PixArt'
    elif name == 'SD15':
        return 'SD 1.5'
    elif name == 'SD21':
        return 'SD 2.1'
    else:
        return name.replace('_', ' ').title()


base_path = '/Users/matyasbohacek/Projects/sae-diff-thomas-viz/src/assets'
files = [f for f in os.listdir(base_path) if "__enriched" in f]

data_all = {}
for f in files:
    with open(os.path.join(base_path, f)) as infile:
        data = json.load(infile)
        model = f.split('_')[4]
        print(model)
        data_all[model] = {
            'rel_diff': np.array(data['relative_energy_diff']),
            'nb_fire': np.array(data['nb_fire']),
            'color': np.array(data['color_relative_diff'])
        }

pairs = [('SD15', 'SD21'), ('SD15', 'pixart'), ('SD15', 'kandinsky')]
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

default_corr_color = "#e8b548"
high_corr_color = "#65d6a4"

for i, (m1, m2) in enumerate(pairs):
    ax = axes[i]
    x = data_all[m1]['rel_diff']
    y = data_all[m2]['rel_diff']
    fire = data_all[m1]['nb_fire']
    color = data_all[m1]['color']

    mask = np.isfinite(x) & np.isfinite(y)
    x, y, fire, color = x[mask], y[mask], fire[mask], color[mask]
    size = np.clip(fire / np.max(fire) * 600, 0.1, 10)

    ax.set_facecolor("white")
    scatter = ax.scatter(x, y, s=size, c=color, cmap=custom_cmap,
                         norm=norm, alpha=0.9, edgecolors='none', linewidth=0.0)

    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-1.05, 1.05)
    ax.set_xlabel(format_title(m1), fontsize=32)
    ax.set_ylabel(format_title(m2), fontsize=32)

    # Style the axes to match run.py
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.0)
        spine.set_edgecolor("black")

    ax.tick_params(axis='both', which='both', labelsize=32)

    corr = np.corrcoef(x, y)[0, 1]

    text_color = high_corr_color if corr > 0.8 else default_corr_color

    ax.text(0.08, 0.88, f'r={corr:.2f}', transform=ax.transAxes,
            fontsize=32, color=text_color, weight=800)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "corr_samples.png"),
            dpi=400, bbox_inches="tight", transparent=True, pad_inches=0.0)
plt.close(fig)

models = ['SD15', 'SD21', 'pixart', 'kandinsky']
formatted_models = [format_title(m) for m in models]

corr_corr = np.zeros((len(models), len(models)))

for i, m1 in enumerate(models):
    for j, m2 in enumerate(models):
        x = data_all[m1]['rel_diff']
        y = data_all[m2]['rel_diff']
        corr_corr[i, j] = np.corrcoef(x, y)[0, 1]

fig, ax = plt.subplots(figsize=(7, 7))
ax.set_facecolor("white")

heat_cmap = mcolors.LinearSegmentedColormap.from_list("heat_gradient",
                                                      [hex_colors[0], hex_colors[2], hex_colors[4]])

sns.heatmap(corr_corr, xticklabels=formatted_models, yticklabels=formatted_models,
            annot=True, cmap=heat_cmap, vmin=0.0, vmax=1.0, ax=ax,
            annot_kws={"size": 24}, cbar=False)

for spine in ax.spines.values():
    spine.set_visible(True)
    spine.set_linewidth(1.0)
    spine.set_edgecolor("black")

ax.tick_params(axis='both', which='both', labelsize=24)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "corr_corr.png"),
            dpi=400, bbox_inches="tight", transparent=True, pad_inches=0.0)
plt.close(fig)
