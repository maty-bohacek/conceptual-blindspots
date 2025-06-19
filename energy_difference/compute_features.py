
import os
import tqdm
import torch
import pickle
import argparse
import shutil
import tempfile

from torchvision import transforms
from einops import rearrange
from PIL import Image
from overcomplete import *
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader


NB_CONCEPTS = 32_000
DINO_BASE_MODEL_ID = "facebookresearch/dinov2"
DINO_VARIANT = "dinov2_vitb14_reg"
BTOPK_WEIGHTS_PATH = "weights/btopk2.pth"

IMAGENET_DEFAULT_MEAN = (0.485, 0.456, 0.406)
IMAGENET_DEFAULT_STD = (0.229, 0.224, 0.225)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

dino = torch.hub.load(DINO_BASE_MODEL_ID, DINO_VARIANT).eval().to(DEVICE)
sae = torch.load(os.path.join(BTOPK_WEIGHTS_PATH), weights_only=False, map_location=torch.device(DEVICE))
sae.running_threshold = 0.829

transform = transforms.Compose([
    transforms.Resize(256, interpolation=Image.BICUBIC),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=IMAGENET_DEFAULT_MEAN, std=IMAGENET_DEFAULT_STD),
])


def analyze_images(dataloader):
    average_energy = torch.zeros(NB_CONCEPTS).to(DEVICE)
    nb_images = 0
    ZZ_T = torch.zeros(NB_CONCEPTS, NB_CONCEPTS).to(DEVICE)

    with torch.no_grad():
        for images, _ in tqdm.tqdm(dataloader):
            images = images.to(DEVICE)

            activations = dino.forward_features(images)['x_prenorm']
            activations = dino.norm(activations)
            activations = rearrange(activations, "b t c -> (b t) c")

            _, codes = sae.module.encode(activations)

            ZZ_T += codes.T @ codes

            codes_reshaped = rearrange(codes, "(b t) c -> b t c", t=261)
            spatial_codes = rearrange(codes_reshaped[:, 5:], "b (w h) c -> b w h c", w=16, h=16)

            average_energy += torch.sum(codes, dim=0)
            nb_images += len(images)

    final_energy = average_energy / nb_images
    return final_energy, ZZ_T


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


def parse_args():
    parser = argparse.ArgumentParser(description="Analyze AI or original images for feature activations")
    parser.add_argument("--data_path", type=str, required=True, help="Path to the sampled dataset directory")
    parser.add_argument("--mode", type=str, choices=["ai", "original"], required=True, help="Image type to analyze")
    parser.add_argument("--output_prefix", type=str, default="results", help="Prefix for the output pickle files")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    print(f"preparing dataset from {args.data_path} [mode: {args.mode}]...")
    subset_path = build_imagefolder_subset(args.data_path, args.mode)
    dataset = ImageFolder(subset_path, transform=transform)
    dataloader = DataLoader(dataset, batch_size=10, shuffle=False)

    print("analyzing image features...")
    final_energy, ZZ_T = analyze_images(dataloader)

    with open(f"{args.output_prefix}_final_energy.pkl", "wb") as f:
        pickle.dump(final_energy, f)

    with open(f"{args.output_prefix}_ZZ_T.pkl", "wb") as f:
        pickle.dump(ZZ_T, f)

    shutil.rmtree(subset_path)

    print("done!")
