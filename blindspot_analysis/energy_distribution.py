import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from matplotlib import rcParams
from matplotlib.font_manager import FontProperties
from matplotlib.colorbar import ColorbarBase

font_path = "/System/Library/Fonts/Avenir.ttc"
font_prop = FontProperties(fname=font_path)
rcParams["font.family"] = font_prop.get_name()

hex_colors = ["#65c7de", "#5776b4", "#582949", "#b16243", "#e8b548"]
custom_cmap = mcolors.LinearSegmentedColormap.from_list("custom_gradient", hex_colors)
norm = mcolors.Normalize(vmin=-1.0, vmax=1.0)

umap_dir = "all_umap_scale_diff"
hist_dir = "simple_hist_energy_with_median"
os.makedirs(umap_dir, exist_ok=True)
os.makedirs(hist_dir, exist_ok=True)


def save_colormap_legend(cmap, norm, orientation, filename,
                         tick_fontsize=32, label=None, label_fontsize=16):
    fig, ax = plt.subplots(
        figsize=(6, 1) if orientation == 'horizontal' else (1, 6)
    )
    cb = ColorbarBase(ax, cmap=cmap, norm=norm, orientation=orientation)

    # if you want an axis label on the colorbar:
    if label is not None:
        cb.set_label(label, fontsize=label_fontsize)

    # increase the tick label font size
    cb.ax.tick_params(labelsize=tick_fontsize)

    plt.savefig(filename, dpi=300, bbox_inches="tight", transparent=True)
    plt.close()


save_colormap_legend(custom_cmap, norm, "horizontal", f"{umap_dir}/colormap_legend_horizontal.png")
save_colormap_legend(custom_cmap, mcolors.Normalize(vmin=-1.5, vmax=1.5), "horizontal", f"{hist_dir}/colormap_legend_horizontal.png")
save_colormap_legend(custom_cmap, norm, "vertical", f"{umap_dir}/colormap_legend_vertical.png")
save_colormap_legend(custom_cmap, mcolors.Normalize(vmin=-1.5, vmax=1.5), "vertical", f"{hist_dir}/colormap_legend_vertical.png")

save_colormap_legend(custom_cmap, mcolors.Normalize(vmin=0, vmax=1), "vertical", f"colormap_legend_vertical.png")


base_path = '/Users/matyasbohacek/Projects/sae-diff-thomas-viz/src/assets'
files = [f for f in os.listdir(base_path) if "__enriched" in f]


def format_title(name):
    clean = name.replace("diff_data_website_sample10k_", "").replace('__enriched.json', '').replace('_sample10k_', '')
    clean = clean.replace("SD21", "SD 2.1").replace("SD15", "SD 1.5")
    if clean.lower() == 'pixart':
        return 'PixArt'
    else:
        return clean.replace('_', ' ').title().title().replace("Sd 2.1", "SD 2.1").replace("Sd 1.5", "SD 1.5").replace("Dpo", "DPO")

norm = mcolors.Normalize(vmin=0, vmax=1)
vmin, vmax = 0, 1
bins = np.linspace(vmin, vmax, 100)
bin_centers = 0.5 * (bins[:-1] + bins[1:])
T = 0.8

global_max = 0.0
for f in files:
    data = json.load(open(os.path.join(base_path, f)))
    vals = np.array(data['energy_diff'])
    vals = 1 / (1 + np.exp(-np.array(data['energy_diff']) / T))  # sigmoid(-x)
    counts, _ = np.histogram(vals, bins=bins, density=True)
    global_max = max(global_max, counts.max())

for f in files:
    data = json.load(open(os.path.join(base_path, f)))
    vals = np.array(data['energy_diff'])
    vals = 1 / (1 + np.exp(-np.array(data['energy_diff']) / T))

    print("min", np.min(vals))
    print("max", np.max(vals))

    counts, _ = np.histogram(vals, bins=bins, density=True)
    colors = [custom_cmap((bc - vmin) / (vmax - vmin)) for bc in bin_centers]
    median = np.median(vals)

    fig, ax = plt.subplots(figsize=(4, 3))
    ax.bar(bin_centers, counts, width=bins[1] - bins[0], color=colors)
    ax.axvline(median, color='#020618', linestyle='--', linewidth=1)

    ax.set_xlim(vmin, vmax)

    # switch to log‐scale and set a tiny positive floor
    ax.set_yscale('log')
    ax.set_ylim(global_max * 1e-3, global_max * 1.05)

    ax.set_title(format_title(f), fontsize=30)

    ax.set_xlabel('Energy Difference', fontsize=16)

    ax.tick_params(axis='both', which='both', labelsize=16)
    ax.set_ylabel('Density', fontsize=16)

    out_name = f.split('_sample10k_')[-1].replace('__enriched.json', '') + ".png"
    plt.savefig(
        os.path.join(hist_dir, out_name),
        dpi=400,
        bbox_inches="tight",
        transparent=False,
        pad_inches=0.0
    )
    plt.close(fig)
