<template>
  <div class="data-card">
    <v-card-title>
      <div class="d-flex align-center">
        <!-- Rank badge for top differences tab -->
        <span v-if="showRank" class="rank-badge mr-2">{{ rank }}</span>

        <!-- ID Chip - always shown -->
        <v-chip :color="isCurrentConcept ? 'purple' : 'black'" class="ma-2">
          <v-icon>mdi-passport</v-icon>
          {{ concept.id }}
        </v-chip>

        <!-- Activations Chip - always shown -->
        <v-chip color="orange" class="ma-2">
          <v-icon>mdi-image-area</v-icon>
          {{ concept.nb_fire }}
        </v-chip>

        <!-- Energy Diff Chip -->
        <v-chip v-if="!hideEnergyDiff" class="ma-2" :style="diffChipStyle">
          <v-icon>mdi-thermometer</v-icon>
          {{ concept.energy_diff.toFixed(3) }}
        </v-chip>

        <!-- Relative Energy Diff Chip -->
        <v-chip v-if="!hideRelativeDiff" class="ma-2" :style="relativeDiffChipStyle">
          <v-icon>mdi-thermometer-auto</v-icon>
          {{ concept.relative_energy_diff.toFixed(3) }}
        </v-chip>

        <!-- Co-occurrence Chip -->
        <v-chip v-if="showCoOccurrence" color="indigo" class="ma-2">
          <v-icon>mdi-bridge</v-icon>
          {{ concept.links_value }}
        </v-chip>

        <!-- Magnify button (only in top diff tab) -->
        <v-btn v-if="showMagnify" icon size="small" @click="onMagnifyClick">
          <v-icon>mdi-magnify</v-icon>
        </v-btn>

        <v-btn icon size="small" class="ml-2" @click="copyVisibleImage('base')">
          <v-icon size="18">mdi-content-copy</v-icon>
        </v-btn>
        <v-btn icon size="small" class="ml-1" @click="copyVisibleImage('heatmap')">
          <v-icon size="18">mdi-fire</v-icon>
        </v-btn>
      </div>
    </v-card-title>

    <v-card-text>
      <v-row>
        <!-- Main concept visualization -->
        <v-col cols="12">
          <div class="image-stack-container">
            <div v-if="!baseLoaded || !heatmapLoaded" class="loading-overlay">
              <v-progress-circular indeterminate color="primary" />
            </div>

            <img ref="baseImageRef" class="base-image" :src="imageUrl" crossorigin="anonymous"
              @load="baseLoaded = true" />

            <img ref="heatmapImageRef" class="heatmap-image" :src="heatmapUrl" :style="{ opacity }"
              crossorigin="anonymous" @load="heatmapLoaded = true" />
          </div>
        </v-col>

        <template v-if="showExamples">
          <v-container>
            <!-- Header row -->
            <v-row>
              <v-col cols="6" class="text-center mb-2">
                <div class="text-subtitle-2 font-weight-medium">Most representative <b>Real Image</b></div>
              </v-col>
              <v-col cols="6" class="text-center mb-2">
                <div class="text-subtitle-2 font-weight-medium">Most representative <b>AI Image</b></div>
              </v-col>
            </v-row>

            <!-- Top row: representative images -->
            <v-row>
              <v-col cols="6">
                <v-img
                  :src="'https://huggingface.co/datasets/matybohacek/sae-diff/resolve/main/sample10k_' + modelKey + '/sample_' + concept.top_original_image + '/original.jpg'"
                  lazy-src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1' height='500' width='500'%3E%3C/svg%3E"
                  :alt="`Most representative real image for AI concept ${concept.id}`">
                  <template v-slot:placeholder>
                    <v-row class="fill-height ma-0" align="center" justify="center">
                      <v-progress-circular indeterminate color="grey-lighten-5"></v-progress-circular>
                    </v-row>
                  </template>
                </v-img>
              </v-col>
              <v-col cols="6">
                <v-img
                  :src="'https://huggingface.co/datasets/matybohacek/sae-diff/resolve/main/sample10k_' + modelKey + '/sample_' + concept.top_ai_image + '/ai.jpg'"
                  lazy-src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1' height='500' width='500'%3E%3C/svg%3E"
                  :alt="`Most representative AI image ${concept.id}`">
                  <template v-slot:placeholder>
                    <v-row class="fill-height ma-0" align="center" justify="center">
                      <v-progress-circular indeterminate color="grey-lighten-5"></v-progress-circular>
                    </v-row>
                  </template>
                </v-img>
              </v-col>
            </v-row>

            <!-- Subheader row -->
            <v-row class="mt-6">
              <v-col cols="6" class="text-center mb-2">
                <div class="text-subtitle-2 font-weight-medium">Corresponding <b>AI Image</b></div>
              </v-col>
              <v-col cols="6" class="text-center mb-2">
                <div class="text-subtitle-2 font-weight-medium">Corresponding <b>Real Image</b></div>
              </v-col>
            </v-row>

            <!-- Bottom row: corresponding matches -->
            <v-row>
              <v-col cols="6">
                <v-img
                  :src="'https://huggingface.co/datasets/matybohacek/sae-diff/resolve/main/sample10k_' + modelKey + '/sample_' + concept.top_original_image + '/ai.jpg'"
                  lazy-src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1' height='500' width='500'%3E%3C/svg%3E"
                  :alt="`AI interpretation of original image ${concept.id}`">
                  <template v-slot:placeholder>
                    <v-row class="fill-height ma-0" align="center" justify="center">
                      <v-progress-circular indeterminate color="grey-lighten-5"></v-progress-circular>
                    </v-row>
                  </template>
                </v-img>
              </v-col>
              <v-col cols="6">
                <v-img
                  :src="'https://huggingface.co/datasets/matybohacek/sae-diff/resolve/main/sample10k_' + modelKey + '/sample_' + concept.top_ai_image + '/original.jpg'"
                  lazy-src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1' height='500' width='500'%3E%3C/svg%3E"
                  :alt="`Closest real image to AI concept ${concept.id}`">
                  <template v-slot:placeholder>
                    <v-row class="fill-height ma-0" align="center" justify="center">
                      <v-progress-circular indeterminate color="grey-lighten-5"></v-progress-circular>
                    </v-row>
                  </template>
                </v-img>
              </v-col>
            </v-row>
          </v-container>
        </template>


      </v-row>
    </v-card-text>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue';

const props = defineProps({
  concept: {
    type: Object,
    required: true
  },
  modelKey: {
    type: String,
    required: true
  },
  isCurrentConcept: {
    type: Boolean,
    default: false
  },
  compact: {
    type: Boolean,
    default: false
  },
  showExamples: {
    type: Boolean,
    default: false
  },
  showCoOccurrence: {
    type: Boolean,
    default: false
  },
  hideEnergyDiff: {
    type: Boolean,
    default: false
  },
  hideRelativeDiff: {
    type: Boolean,
    default: false
  },
  showRank: {
    type: Boolean,
    default: false
  },
  rank: {
    type: Number,
    default: 0
  },
  showMagnify: {
    type: Boolean,
    default: false
  },
  opacity: {
    type: Number,
    default: 0.5
  },
});

const emit = defineEmits(['magnify-click']);

const imageUrl = `https://kempner-prod-thomasfel-storage.s3.amazonaws.com/dinov2/${props.concept.id}_image.webp`;
const heatmapUrl = `https://kempner-prod-thomasfel-storage.s3.amazonaws.com/dinov2/${props.concept.id}_heatmap.webp`;

const baseImageRef = ref(null);
const heatmapImageRef = ref(null);
const baseLoaded = ref(false);
const heatmapLoaded = ref(false);

async function copyVisibleImage(type = 'base') {
  await nextTick();

  const imgEl = type === 'base' ? baseImageRef.value : heatmapImageRef.value;
  if (!imgEl?.complete) {
    console.warn('⛔ image not loaded yet');
    return;
  }

  const canvas = document.createElement('canvas');
  canvas.width = imgEl.naturalWidth;
  canvas.height = imgEl.naturalHeight;

  const ctx = canvas.getContext('2d');
  ctx.drawImage(imgEl, 0, 0);

  canvas.toBlob(async (blob) => {
    if (!blob) return;
    try {
      await navigator.clipboard.write([
        new ClipboardItem({ [blob.type]: blob }),
      ]);
      console.log(`✅ ${type} image copied to clipboard`);
    } catch (err) {
      console.error('❌ clipboard write failed', err);
    }
  }, 'image/png');
}

// Helper functions to compute styles for chips
const getTextColor = (rgbArray) => {
  const r = rgbArray[0] * 255;
  const g = rgbArray[1] * 255;
  const b = rgbArray[2] * 255;
  // Perceived luminance (ITU-R BT.709)
  const luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b;
  return luminance > 128 ? 'black' : 'white';
};

const diffChipStyle = computed(() => {
  const colorArray = props.concept.color_diff;
  return {
    background: `rgba(${colorArray[0] * 255}, ${colorArray[1] * 255}, ${colorArray[2] * 255}, 1)`,
    color: getTextColor(colorArray)
  };
});

const relativeDiffChipStyle = computed(() => {
  const colorArray = props.concept.color_relative_diff;
  return {
    background: `rgba(${colorArray[0] * 255}, ${colorArray[1] * 255}, ${colorArray[2] * 255}, 1)`,
    color: getTextColor(colorArray)
  };
});

const onMagnifyClick = () => {
  emit('magnify-click', props.concept);
};
</script>

<style scoped>
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

img.compact {
  object-fit: cover;
}

img {
  object-fit: contain;
  width: 100%;
  height: 100%;
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background-color: #64748b;
  color: white;
  border-radius: 50%;
  font-size: 0.8rem;
  font-weight: bold;
}

.data-card {
  transition: all 0.2s ease;
  opacity: 0.9;
  border: dashed 2px transparent;
  margin: 3px;
  border-radius: 3px;
}

.data-card:hover {
  opacity: 1.0;
  border-color: #cbd5e1;
}

.image-stack-container {
  position: relative;
  width: 100%;
  overflow: hidden;
  border-radius: 4px;
  display: inline-block;
}

.image-stack-container img,
.image-stack-container .v-img {
  display: block;
  width: 100%;
  height: auto;
  object-fit: contain;
}

.base-image,
.heatmap-image {
  position: relative;
  z-index: 1;
}

.base-image {
  mix-blend-mode: normal;
  filter: saturate(1.0) contrast(1.0);
  transition: filter 0.2s ease;
}

.data-card:hover .base-image {
  filter: saturate(1.1) contrast(1.1);
}

.heatmap-image {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 2;
  width: 100%;
  height: 100%;
  pointer-events: none;
  mix-blend-mode: normal;
}
</style>