## Exploratory Tool

To run, place all pre-processed energy difference and blindspot data files (ending with `__enriched.json`) into `src/assets`.

Then, run the following, and open the logged IP/port in your browser.

```shell
npm install
npm run
```

The enriched data files have the following structure:

```json
{
  "umap_x": [float, ...],               // UMAP x-coordinates for concepts
  "umap_y": [float, ...],               // UMAP y-coordinates for concepts
  "umap_colors": [[r, g, b], ...],      // RGB color array (modality spectrum)
  "umap_scale": [float, ...],           // Visual size scale of each point
  "energy": [float, ...],               // Energy from image activations
  "is_dead": [0 or 1, ...],             // Whether concept is inactive
  "connections_idx": [[float, ...], ...], // Co-occuring concepts
  "connections_val": [[float, ...], ...], // Strength of co-occurence connections
  "nb_fire": [int, ...]                 , // Number of time a concept fire
  "energy_diff": [float, ...]           , // Difference of energy the given concept
  "relative_energy_diff": [float, ...]  , // Relative difference of energy (diff / (energy a + energy b))
  "color_diff": [[r, g, b], ...]        , // Cmap color for energy diff
  "color_relative_diff": [[r, g, b], ...] , // Cmap color for relative energy diff
}
```
