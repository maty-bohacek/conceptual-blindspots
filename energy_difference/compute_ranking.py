
import os
import tqdm
import argparse
import os
import torch
import json
import csv
import tempfile

from torchvision import transforms
from einops import rearrange
from PIL import Image
from overcomplete import *
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader


def parse_args():
    parser = argparse.ArgumentParser(description="Analyze AI or original images for feature activations")
    parser.add_argument("--data_path", type=str, required=True, help="Path to the sampled dataset directory")
    parser.add_argument("--mode", type=str, choices=["ai", "original"], required=True, help="Image type to analyze")
    parser.add_argument("--output_prefix", type=str, default="results", help="Prefix for the output pickle files")
    return parser.parse_args()


args = parse_args()


def build_imagefolder_subset(root, mode):
    assert mode in ["ai", "original"], "mode must be 'ai' or 'original'"

    tmp_dir = tempfile.mkdtemp()
    class_dir = os.path.join(tmp_dir, "class0")
    os.makedirs(class_dir, exist_ok=True)

    for sample_name in os.listdir(root):
        sample_path = os.path.join(root, sample_name)
        if not os.path.isdir(sample_path):
            continue
        image_path = os.path.join(sample_path, f"{mode}.jpg")
        if os.path.exists(image_path):
            link_name = os.path.join(class_dir, f"{sample_name}.jpg")
            os.symlink(image_path, link_name)

    return tmp_dir


# ========== CONFIG ==========
NB_CONCEPTS = 32000
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BATCH_SIZE = 4
DINO_BASE_MODEL_ID = "facebookresearch/dinov2"
DINO_VARIANT = "dinov2_vitb14_reg"
BTOPK_WEIGHTS_PATH = "weights/btopk2.pth"
DATASET_PATH = build_imagefolder_subset(args.data_path, args.mode)
OUTPUT_PREFIX = args.output_prefix
# ============================

transform = transforms.Compose([
    transforms.Resize(256, interpolation=Image.BICUBIC),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
])

# LeaderBoard definition
class LeaderBoard:
    def __init__(self, num_neurons, top_n, w, h):
        self.num_neurons = num_neurons
        self.top_n = top_n
        self.best_activations = torch.full((num_neurons, top_n, w, h), float('-inf'), device=DEVICE)
        self.best_urls = [[''] * top_n for _ in range(num_neurons)]

    def update(self, activations, urls):
        n, w, h, c = activations.shape
        assert c == self.num_neurons, f"Concept count mismatch: {c} != {self.num_neurons}"

        activations = activations.to(DEVICE)
        mean_activations = activations.half().mean(dim=(1, 2))  # (n, c)

        for neuron in range(self.num_neurons):
            neuron_acts = activations[:, :, :, neuron]  # (n, w, h)
            prev_acts = self.best_activations[neuron]   # (top_n, w, h)
            prev_urls = self.best_urls[neuron]          # list of str

            combined = torch.cat([prev_acts, neuron_acts], dim=0)      # (top_n + n, w, h)
            combined_urls = prev_urls + urls                           # (top_n + n)

            scores = combined.mean(dim=(1, 2))  # (top_n + n,)
            topk = torch.topk(scores, self.top_n)

            self.best_activations[neuron] = combined[topk.indices]
            self.best_urls[neuron] = [combined_urls[i] for i in topk.indices.tolist()]

# Load models
print("Loading models...")
dino = torch.hub.load(DINO_BASE_MODEL_ID, DINO_VARIANT).eval().to(DEVICE)
sae = torch.load(BTOPK_WEIGHTS_PATH, weights_only=False, map_location=torch.device(DEVICE))
sae.running_threshold = 0.829

# Load dataset
print("Loading dataset...")
dataset = ImageFolder(DATASET_PATH, transform=transform)
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False)

# Init leaderboard
leaderboard = LeaderBoard(num_neurons=NB_CONCEPTS, top_n=10, w=16, h=16)

# Analyze images
print("Analyzing images...")
with torch.no_grad():
    for i, (images, _) in tqdm.tqdm(enumerate(dataloader)):
        paths = [dataset.samples[i * BATCH_SIZE + j][0].split("/")[-1] for j in range(len(images))]
        images = images.to(DEVICE)

        activations = dino.forward_features(images)['x_prenorm']
        activations = dino.norm(activations)
        activations = rearrange(activations, "b t c -> (b t) c")

        _, codes = sae.module.encode(activations)
        codes_reshaped = rearrange(codes, "(b t) c -> b t c", t=261)
        spatial_codes = rearrange(codes_reshaped[:, 5:], "b (w h) c -> b w h c", w=16, h=16)

        leaderboard.update(spatial_codes, paths)

# Prepare outputs
print("Saving JSON and CSV results...")
top_image_dict = {i: leaderboard.best_urls[i][0] for i in range(NB_CONCEPTS)}

# Save as JSON
with open(f"{OUTPUT_PREFIX}.json", "w") as f:
    json.dump(top_image_dict, f, indent=2)

# Save as CSV
with open(f"{OUTPUT_PREFIX}.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["concept_id", "top_image_path"])
    for k, v in top_image_dict.items():
        writer.writerow([k, v])

print("Done!")
