<template>
    <div class="canvas-container">
        <!-- toolbar -->
        <v-toolbar>
            <v-toolbar-title>UMAP Options</v-toolbar-title>
            <v-spacer></v-spacer>
            <v-toolbar-items>
                <div style="margin-right: 10px; margin-top: 5px; min-width: 150px;">
                    <v-select v-model="data_source" :items="Object.keys(model_data)" label="Model"
                        variant="filled"></v-select>
                </div>
                <div style="margin-right: 30px;">
                    <v-checkbox v-model="relative_diff" label="Relative Difference" />
                </div>
                <div style="margin-right: 30px; width: 150px; margin-top: 5px;">
                    <v-text-field label="Specific ID" placeholder="Enter concept ID" variant="filled"
                        v-model="selected_id"></v-text-field>
                </div>
                <div style="margin-right: 30px; width: 150px; margin-top: 5px;">
                    <v-text-field label="Distance" placeholder="Distance to neighbours" variant="filled"
                        v-model="dist_neighbours"></v-text-field>
                </div>
                <div style="margin-right: 10px; margin-top: 5px; min-width: 150px;">
                    <v-select v-model="scale_type" :items="Object.keys(scale_types)" label="Scaling type"
                        variant="filled"></v-select>
                </div>
                <div style="margin-right: 10px; width: 150px; margin-top:10px">
                    <div class="text-caption">
                        Heatmap Opacity
                    </div>
                    <v-slider v-model="global_heatmap_opacity" step="0.01" min="0" max="1" thumb-label></v-slider>
                </div>
                <div style="margin-right: 30px;">
                    <v-checkbox v-model="auto_opacity_cycle" label="Auto Opacity" />
                </div>
            </v-toolbar-items>
        </v-toolbar>

        <!-- chart -->
        <div ref="chart_container" class="chart-container"></div>

        <v-card class="mt-2 pa-3 explanation-card">
            <v-card-title class="text-subtitle-1 font-weight-bold">Understanding the Visualization</v-card-title>
            <v-card-text class="text-body-2">
                <p>
                    This 2D UMAP projection visualizes the dictionary of SAE concepts extracted from vision-language
                    models.
                    Each point represents a concept vector (a linear direction in the shared embedding space).
                    <b>UMAP preserves local distances</b>, so points close together in the visualization correspond to
                    similar concepts in the original high-dimensional space,
                    though larger-scale clusters should be interpreted cautiously.
                </p>

                <p>
                    The <b>color gradient</b> spans from blue to orange, representing the energy difference between
                    concepts in AI-generated images and real images.
                    Specifically, we compute:
                    <br />
                    <code>diff = energy(concept on AI image) - energy(concept on real image)</code>
                    <br />
                    So a positive value (orange) indicates the concept is over-represented in AI content, while a
                    negative value (blue) suggests under-representation.
                </p>

                <div class="d-flex align-center my-2">
                    <span style="color: #65c7de; font-weight: bold;">AI under-represent</span>
                    <div class="gradient-bar mx-2"></div>
                    <span style="color: #e8b548; font-weight: bold;">AI over-represent</span>
                    <span class="ml-2">(under → over represent)</span>
                </div>

                <p class="mt-3 mb-2"><b>Interact with concepts:</b></p>
                <ul class="mb-2 pl-3">
                    <li><b>Click any point</b> to explore that concept's examples and properties</li>
                    <li>Use the <b>Specific ID</b> field to return to a concept by its identifier</li>
                    <li>Check the <b>Co-Occurrence tab</b> to see how concepts co-occur together</li>
                    <li>Check the <b>Top Differences tab</b> to see concepts with the highest or lowest differences</li>
                </ul>

                <p class="mt-3 mb-2"><b>Concept metrics:</b></p>
                <div class="d-flex flex-wrap align-center">
                    <div class="mr-4 mb-2 d-flex flex-column align-center">
                        <v-chip color="black" size="small"><v-icon size="x-small">mdi-passport</v-icon> 123</v-chip>
                        <span class="caption mt-1">Concept ID</span>
                    </div>
                    <div class="mr-4 mb-2 d-flex flex-column align-center">
                        <v-chip color="orange" size="small"><v-icon size="x-small">mdi-image-area</v-icon> 456</v-chip>
                        <span class="caption mt-1">Image activations</span>
                    </div>
                    <div class="mr-4 mb-2 d-flex flex-column align-center">
                        <v-chip color="indigo" size="small"><v-icon size="x-small">mdi-bridge</v-icon> 0.75</v-chip>
                        <span class="caption mt-1">Co-occurrence score</span>
                    </div>
                    <div class="mr-4 mb-2 d-flex flex-column align-center">
                        <v-chip color="blue" size="small"><v-icon size="x-small">mdi-thermometer</v-icon> 3.2</v-chip>
                        <span class="caption mt-1">Energy diff</span>
                    </div>
                    <div class="mr-4 mb-2 d-flex flex-column align-center">
                        <v-chip color="blue" size="small"><v-icon size="x-small">mdi-thermometer-auto</v-icon>
                            0.5</v-chip>
                        <span class="caption mt-1">Relative energy diff</span>
                    </div>
                </div>
            </v-card-text>
        </v-card>

        <!-- details drawer -->
        <v-navigation-drawer v-model="drawer" location="end" width="600" rail rail-width="600" elevation="10">
            <v-toolbar app dark fixed>
                <v-toolbar-title>Details</v-toolbar-title>
                <v-spacer></v-spacer>
                <v-btn icon @click="drawer = false">
                    <v-icon>mdi-close</v-icon>
                </v-btn>
            </v-toolbar>

            <v-tabs v-model="active_tab" bg-color="dark" dark>
                <v-tab value="selected">Selected</v-tab>
                <v-tab value="cooccurrence">Co-Occurrence</v-tab>
                <v-tab value="top_diff">Top Differences</v-tab>
            </v-tabs>

            <v-window v-model="active_tab">
                <!-- selected tab -->
                <v-window-item value="selected">
                    <v-card v-if="selected_point">
                        <ConceptItem v-for="(item, index) in selected_point" :key="item.id" :concept="item"
                            :model-key="model_to_key[data_source]" :is-current-concept="index === 0"
                            :compact="compact_image" :show-examples="true" :opacity="global_heatmap_opacity" />
                    </v-card>
                </v-window-item>

                <!-- co-occurrence tab -->
                <v-window-item value="cooccurrence">
                    <v-card v-if="co_occurring_concepts.length > 0">
                        <ConceptItem v-for="item in co_occurring_concepts" :key="item.id" :concept="item"
                            :model-key="model_to_key[data_source]"
                            :is-current-concept="item.id === selected_point?.[0]?.id" :compact="compact_image"
                            :show-co-occurrence="true" :hide-energy-diff="true" :hide-relative-diff="true"
                            :show-examples="true" :opacity="global_heatmap_opacity" />
                    </v-card>
                </v-window-item>

                <!-- top differences tab -->
                <v-window-item value="top_diff">
                    <v-card>
                        <v-card-title class="d-flex align-center">
                            <span>Top Differences</span>
                            <v-spacer></v-spacer>
                            <div style="width: 180px;">
                                <v-select v-model="diff_sort_order" :items="diffSortOptions" label="Sort by"
                                    variant="filled" density="compact"></v-select>
                            </div>
                            <div style="width: 100px; margin-left: 10px;">
                                <v-select v-model="top_diff_count" :items="[10, 20, 50, 100]" label="Count"
                                    variant="filled" density="compact"></v-select>
                            </div>
                        </v-card-title>

                        <v-card-text>
                            <div v-if="topDifferenceConcepts.length > 0" class="top-diff-container">
                                <ConceptItem v-for="(item, index) in visibleTopDifferenceConcepts" :key="item.id"
                                    :concept="item" :model-key="model_to_key[data_source]" :compact="compact_image"
                                    :show-rank="true" :rank="index + 1" :show-magnify="true"
                                    :hide-energy-diff="scale_type === 'Relative Diff'"
                                    :hide-relative-diff="scale_type !== 'Relative Diff'" @magnify-click="onPointClick"
                                    :show-examples="true" :opacity="global_heatmap_opacity" />

                                <div v-if="topDifferenceConcepts.length > visibleTopDifferenceConcepts.length"
                                    class="text-center pa-4">
                                    <v-btn @click="loadMoreTopDiff" color="black">
                                        Load more
                                    </v-btn>
                                </div>
                            </div>
                            <div v-else class="text-center pa-4">
                                No data available
                            </div>
                        </v-card-text>
                    </v-card>
                </v-window-item>
            </v-window>
        </v-navigation-drawer>
    </div>
</template>

<script setup>
import * as d3 from 'd3';
import { onMounted, ref, watch, computed } from 'vue';
import { clamp } from '@/assets/math_utils';
import ConceptItem from './conceptItem.vue';

import dataKandisky from '@/assets/diff_data_website_sample10k_kandinsky__enriched.json';
import dataPixart from '@/assets/diff_data_website_sample10k_pixart__enriched.json';
import dataSD15 from '@/assets/diff_data_website_sample10k_SD15__enriched.json';
import dataSD21 from '@/assets/diff_data_website_sample10k_SD21__enriched.json';

// props
const props = defineProps({
    width: { type: Number, default: 1560 },
    height: { type: Number, default: 800 },
});

const model_data = {
    'Kandisky': dataKandisky,
    'Pixart': dataPixart,
    'Stable Diffusion 1.5': dataSD15,
    'Stable Diffusion 2.1': dataSD21,
};

const model_to_key = {
    'Kandisky': 'kandinsky',
    'Pixart': 'pixart',
    'Stable Diffusion 1.5': 'SD15',
    'Stable Diffusion 2.1': 'SD21',
}

const scale_types = {
    'Relative Diff': 'relative_energy_diff',
    'Diff': 'energy_diff',
    'IN1K': 'scale',
};

// reactive state
const data_source = ref('Stable Diffusion 1.5');
const chart_container = ref(null);
const drawer = ref(false);
const selected_point = ref(null);
const use_energy = ref(true);
const dist_neighbours = ref(0.1);
const point_size = ref(1.0);
const compact_image = ref(false);
const selected_id = ref(null);
const active_tab = ref("selected");
const co_occurring_concepts = ref([]);
const relative_diff = ref(true);
const scale_type = ref('Diff');
const auto_opacity_cycle = ref(false);
let opacity_interval = null;
const global_heatmap_opacity = ref(0.5);

// Make dataset reactive
const dataset = ref([]);

// New refs for top differences feature
const diff_sort_order = ref('highest');
const diffSortOptions = ['highest', 'lowest'];
const top_diff_count = ref(20);
const visible_top_diff_count = ref(10);

// Initial data
let data = model_data[data_source.value];

// Canvas vars
let canvas, context, x_scale, y_scale, zoom;

// Constants
const CONCEPTS_IDS = Array.from({ length: 32000 }, (_, i) => i);
const ORIGINAL_OPACITY = 0.8;
const CLICK_COLOR = '#00c950';
const HOVER_COLOR = '#05df72';
const SELECTED_COLOR = HOVER_COLOR
const STROKE_COLOR = 'rgba(71, 85, 105, 0.5)';
const DEFAULT_SIZE = 10.0;
const MIN_RADIUS = 0.5;
const MAX_RADIUS = 10000.0;

// State tracking
let current_clicked_id = null;
let current_selected_ids = [];
let hovered_point_id = null;

// Initialize dataset
dataset.value = create_dataset(data);

// Computed for top differences
const topDifferenceConcepts = computed(() => {
    if (!dataset.value || dataset.value.length === 0) return [];

    const activeDataset = dataset.value.filter(d => d.is_dead === 0);
    let sorted = [...activeDataset];

    // Sort by the appropriate diff value
    if (scale_type.value === 'Relative Diff') {
        if (diff_sort_order.value === 'highest') {
            sorted = sorted.sort((a, b) => b.relative_energy_diff - a.relative_energy_diff);
        } else {
            sorted = sorted.sort((a, b) => a.relative_energy_diff - b.relative_energy_diff);
        }
    } else {
        if (diff_sort_order.value === 'highest') {
            sorted = sorted.sort((a, b) => b.energy_diff - a.energy_diff);
        } else {
            sorted = sorted.sort((a, b) => a.energy_diff - b.energy_diff);
        }
    }

    return sorted.slice(0, top_diff_count.value);
});

const visibleTopDifferenceConcepts = computed(() => {
    return topDifferenceConcepts.value.slice(0, visible_top_diff_count.value);
});

// Dataset creation function
function create_dataset(source_data) {
    const result = [];
    const energies = CONCEPTS_IDS.map(i => source_data.energy[i]);
    const max_energy = Math.max(...energies);

    const max_diff = Math.max(...CONCEPTS_IDS.map(i => Math.abs(source_data.energy_diff[i])));

    const mean_relative_diff = CONCEPTS_IDS.reduce((acc, i) => acc + Math.abs(source_data.relative_energy_diff[i]), 0) / CONCEPTS_IDS.length;
    const std_relative_diff = Math.sqrt(CONCEPTS_IDS.reduce((acc, i) => acc + Math.pow(source_data.relative_energy_diff[i] - mean_relative_diff, 2), 0) / CONCEPTS_IDS.length);

    CONCEPTS_IDS.forEach(i => {
        result.push({
            id: i,
            x: source_data.umap_x[i],
            y: source_data.umap_y[i],
            color: [source_data.umap_colors[i][0], source_data.umap_colors[i][1], source_data.umap_colors[i][2], 1.0],
            normalized_energy: energies[i] / max_energy,
            scale: source_data.umap_scale[i],
            links: source_data.connections_idx[i],
            links_value: source_data.connections_val[i],
            is_dead: Number(source_data.is_dead[i]),
            nb_fire: Number(source_data.nb_fire[i]),
            energy_diff: Number(source_data.energy_diff[i]) / max_diff,
            relative_energy_diff: ((Number(source_data.relative_energy_diff[i]) - mean_relative_diff) / std_relative_diff) * 0.1,
            color_diff: [source_data.color_diff[i][0], source_data.color_diff[i][1], source_data.color_diff[i][2], 1.0],
            color_relative_diff: [source_data.color_relative_diff[i][0], source_data.color_relative_diff[i][1], source_data.color_relative_diff[i][2], 1.0],
            top_ai_image: source_data.top_ai_image[i].split('/')[0].split('_')[1],
            top_original_image: source_data.top_original_image[i].split('/')[0].split('_')[1],
        });
    });

    return result;
}

// Function to load more items in the top differences tab
function loadMoreTopDiff() {
    visible_top_diff_count.value = Math.min(visible_top_diff_count.value + 10, topDifferenceConcepts.value.length);
}

// Get radius based on energy and zoom
function get_radius(d, transform) {
    let radius = 1;
    if (scale_type.value === 'Diff') {
        radius = d.energy_diff;
    } else if (scale_type.value === 'Relative Diff') {
        radius = d.relative_energy_diff;
    } else if (scale_type.value === 'IN1K') {
        radius = d.scale;
    }
    radius = Math.abs(Number(radius)) ** 0.5 * DEFAULT_SIZE;
    radius *= transform.k ** 0.8;
    radius = clamp(radius, MIN_RADIUS, MAX_RADIUS);
    radius *= point_size.value;
    return radius;
}

// Init on mount
onMounted(() => create_chart());

// Create chart and set up events
function create_chart() {
    chart_container.value.innerHTML = '';

    canvas = d3.select(chart_container.value)
        .append('canvas')
        .attr('width', props.width)
        .attr('height', props.height)
        .style('display', 'block')
        .node();

    const pixel_ratio = window.devicePixelRatio || 1;
    canvas.width = props.width * pixel_ratio;
    canvas.height = props.height * pixel_ratio;
    canvas.style.width = `${props.width}px`;
    canvas.style.height = `${props.height}px`;

    chart_container.value.style.width = `${props.width}px`;
    chart_container.value.style.height = `${props.height}px`;

    context = canvas.getContext('2d');
    context.scale(pixel_ratio, pixel_ratio);

    x_scale = d3.scaleLinear()
        .domain(d3.extent(dataset.value, d => d.x))
        .range([0.0, props.width]);

    y_scale = d3.scaleLinear()
        .domain(d3.extent(dataset.value, d => d.y))
        .range([props.height - 1, 1]);

    zoom = d3.zoom()
        .scaleExtent([0.1, 100])
        .on('zoom', handle_zoom);

    const canvas_selection = d3.select(canvas);
    canvas_selection.call(zoom);
    canvas_selection.on('mousemove', handle_mouse_move);
    canvas_selection.on('click', handle_click);

    draw(d3.zoomIdentity);
}

// Draw single point
function draw_point(x, y, radius, color, opacity) {
    context.beginPath();
    context.arc(x, y, radius, 0, 2 * Math.PI);
    context.fillStyle = color;
    context.globalAlpha = opacity;
    context.fill();
}

// Main drawing function
function draw(transform) {
    context.fillStyle = 'white';
    context.clearRect(0, 0, props.width, props.height);
    context.fillRect(0, 0, props.width, props.height);
    context.imageSmoothingEnabled = true;
    context.imageSmoothingQuality = 'high';

    let clicked_point = null;
    const selected_points = [];
    const hovered_points = [];
    const other_points = [];

    // Collect points by type
    dataset.value.forEach(d => {
        if (d.is_dead !== 0) return;

        const x = transform.applyX(x_scale(d.x));
        const y = transform.applyY(y_scale(d.y));
        const radius = get_radius(d, transform);

        const color_mult = 255;
        let color = `rgba(${d.color[0] * color_mult}, ${d.color[1] * color_mult}, ${d.color[2] * color_mult}, 1.0)`;
        if (relative_diff.value) {
            color = `rgba(${d.color_relative_diff[0] * color_mult}, ${d.color_relative_diff[1] * color_mult}, ${d.color_relative_diff[2] * color_mult}, 1.0)`;
        } else {
            color = `rgba(${d.color_diff[0] * color_mult}, ${d.color_diff[1] * color_mult}, ${d.color_diff[2] * color_mult}, 1.0)`;
        }
        let opacity = ORIGINAL_OPACITY;

        if (d.id === current_clicked_id) {
            color = CLICK_COLOR;
            opacity = 1.0;
            clicked_point = { x, y, radius, color, opacity };
        } else if (current_selected_ids.includes(d.id)) {
            color = SELECTED_COLOR;
            opacity = 0.9;
            selected_points.push({ x, y, radius, color, opacity });
        } else if (d.id === hovered_point_id) {
            color = HOVER_COLOR;
            opacity = 1.0;
            hovered_points.push({ x, y, radius, color, opacity });
        } else {
            other_points.push({ x, y, radius, color, opacity });
        }
    });

    // Draw regular points first
    other_points.forEach(p => draw_point(p.x, p.y, p.radius, p.color, p.opacity));

    // Draw connections
    if (co_occurring_concepts.value.length > 0 && clicked_point) {
        const x2 = clicked_point.x;
        const y2 = clicked_point.y;
        context.strokeStyle = STROKE_COLOR;

        const max_link_value = Math.max(...co_occurring_concepts.value.map(d => d.links_value));

        co_occurring_concepts.value.forEach(d => {
            const x1 = transform.applyX(x_scale(d.x));
            const y1 = transform.applyY(y_scale(d.y));
            context.lineWidth = d.links_value / max_link_value * 5.0;

            const cx = (x1 + x2) / 2;
            const cy = (y1 + y2) / 2 - 50;

            context.beginPath();
            context.moveTo(x1, y1);
            context.quadraticCurveTo(cx, cy, x2, y2);
            context.stroke();
        });
    }

    // Draw highlighted points on top
    selected_points.forEach(p => draw_point(p.x, p.y, p.radius, p.color, p.opacity));
    hovered_points.forEach(p => draw_point(p.x, p.y, p.radius, p.color, p.opacity));
    if (clicked_point) {
        draw_point(clicked_point.x, clicked_point.y, clicked_point.radius, clicked_point.color, clicked_point.opacity);
    }
}

// Handle zoom
function handle_zoom(event) {
    draw(event.transform);
}

// Handle mouse movement
function handle_mouse_move(event) {
    const transform = d3.zoomTransform(canvas);
    const [mouse_x, mouse_y] = d3.pointer(event);
    const data_x = transform.invertX(mouse_x);
    const data_y = transform.invertY(mouse_y);

    let closest_point = null;
    let min_distance = Infinity;

    dataset.value.forEach(d => {
        if (d.is_dead !== 0) return;

        const x = x_scale(d.x);
        const y = y_scale(d.y);
        const distance = Math.sqrt((x - data_x) ** 2 + (y - data_y) ** 2);
        const hit_radius = get_radius(d, transform) * 2 * transform.k;

        if (distance < hit_radius && distance < min_distance) {
            min_distance = distance;
            closest_point = d;
        }
    });

    if (closest_point?.id !== hovered_point_id) {
        hovered_point_id = closest_point?.id || null;
        draw(d3.zoomTransform(canvas));
    }
}

// Handle click
function handle_click(event) {
    if (hovered_point_id !== null) {
        const clicked_point = dataset.value.find(d => d.id === hovered_point_id);
        if (clicked_point) {
            onPointClick(clicked_point);
        }
    }
}

// Process point click
function onPointClick(point) {
    current_clicked_id = point.id;
    const neighbors = find_nearest_points(point, dist_neighbours.value);
    current_selected_ids = neighbors.map(d => d.id);

    selected_point.value = neighbors;
    drawer.value = true;
    active_tab.value = "selected"; // Switch to selected tab when clicking a point

    co_occurring_concepts.value = point.links.map((id, index) => {
        const linked_concept = dataset.value.find(d => d.id === id);
        if (linked_concept) {
            return {
                ...linked_concept,
                links_value: point.links_value[index],
            };
        }
        return null;
    }).filter(Boolean);

    draw(d3.zoomTransform(canvas));
}

// Find nearby points
function find_nearest_points(target, dist) {
    dist = Number(dist);

    let distances = dataset.value.map(d => {
        const dx = d.x - target.x;
        const dy = d.y - target.y;
        return { point: d, distance: Math.sqrt(dx * dx + dy * dy) };
    });

    distances = distances.filter(obj => obj.distance <= dist * 0.05);
    // sort by relative diff absolute value
    distances = distances.sort((a, b) => Math.abs(b.point.relative_energy_diff) - Math.abs(a.point.relative_energy_diff));
    //distances = distances.sort((a, b) => b.point.normalized_energy - a.point.normalized_energy);
    distances = distances.filter(obj => obj.point.id != target.id);
    distances = distances.filter(obj => obj.point.is_dead == 0);
    distances.unshift({ point: target, distance: 0 });

    return distances.map(obj => obj.point);
}

// Reset visible top diff count when changing sort order or model
function resetVisibleTopDiff() {
    visible_top_diff_count.value = 10;
}

// Watch for display option changes
watch(use_energy, () => {
    if (canvas) draw(d3.zoomTransform(canvas));
});

watch(relative_diff, () => {
    if (canvas) draw(d3.zoomTransform(canvas));
});

watch(scale_type, () => {
    if (canvas) draw(d3.zoomTransform(canvas));
    resetVisibleTopDiff();
});

watch(data_source, () => {
    data = model_data[data_source.value];

    resetVisibleTopDiff();
    dataset.value = create_dataset(data);

    // Reset selected values
    selected_point.value = null;
    current_clicked_id = null;
    current_selected_ids = [];
    co_occurring_concepts.value = [];

    // When dataset changes, we need to update the scales
    if (canvas) {
        x_scale.domain(d3.extent(dataset.value, d => d.x));
        y_scale.domain(d3.extent(dataset.value, d => d.y));
        draw(d3.zoomTransform(canvas));
    }
});

watch(diff_sort_order, resetVisibleTopDiff);
watch(top_diff_count, resetVisibleTopDiff);

// Watch for selected id
watch(selected_id, () => {
    if (selected_id.value !== null && selected_id.value !== '') {
        const found_point = dataset.value.find(d => d.id === Number(selected_id.value));
        if (found_point) {
            onPointClick(found_point);
        } else {
            selected_point.value = null;
            current_clicked_id = null;
            current_selected_ids = [];
            co_occurring_concepts.value = [];
        }
    }
});

// Watch for distance changes
watch(dist_neighbours, () => {
    if (current_clicked_id !== null) {
        const point = dataset.value.find(d => d.id === current_clicked_id);
        if (point) onPointClick(point);
    }
});

watch(auto_opacity_cycle, (enabled) => {
    if (enabled) {
        let t = 0;
        opacity_interval = setInterval(() => {
            // smoothly go 0 → 1 → 0 with a 3 sec period
            t += 50;
            const seconds = (t % 3000) / 3000;
            global_heatmap_opacity.value = 0.5 * (1 + Math.sin(2 * Math.PI * seconds - Math.PI / 2)); // sine wave from 0 to 1
        }, 50);
    } else {
        clearInterval(opacity_interval);
        opacity_interval = null;
    }
});
</script>

<style scoped>
.chart-container {
    border: 1px solid rgba(13, 13, 21, 0.3);
    text-align: center;
    overflow: hidden;
    border-radius: 3px;
    margin: auto;
}

.canvas-container {
    padding: 20px;
}

.explanation-card {
    font-size: 0.9em;
    margin-top: 10px;
}

img.compact {
    object-fit: cover;
}

img {
    object-fit: contain;
    width: 100%;
    height: 100%;
}

.v-responsive__sizer {
    padding-bottom: 0 !important;
}

pre {
    display: inline-block;
    text-wrap: auto;
    background-color: #e2e8f0;
    border-radius: 2px;
    padding: 10px;
    overflow: hidden;
    color: #020617;
}

.data-card {
    transition: all 0.2s ease;
    opacity: 0.8;
    border: dashed 2px transparent;
    margin: 3px;
    border-radius: 3px;
}

.data-card:hover {
    opacity: 1.0;
    border-color: #cbd5e1;
}

.gradient-bar {
    height: 12px;
    width: 120px;
    background: linear-gradient(to right, #65c7de, #5776b4, #582949, #b16243, #e8b548);
    border-radius: 6px;
}

.caption {
    font-size: 0.75rem;
    color: rgba(0, 0, 0, 0.6);
}
</style>