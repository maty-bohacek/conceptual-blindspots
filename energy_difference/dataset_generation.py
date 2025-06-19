import os
import argparse
import torch
import requests
import pandas as pd

from tqdm import tqdm
from PIL import Image
from io import BytesIO
from diffusers import DiffusionPipeline, UNet2DConditionModel


def download_image(url, save_path):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert("RGB")
        image.save(save_path)
        return True
    except Exception as e:
        print(f"failed to download image from {url}: {e}")
        return False


def generate_image(caption, pipe, save_path):
    try:
        image = pipe(caption, width=512, height=512).images[0]
        image.save(save_path)
        return True
    except Exception as e:
        print(f"failed to generate image for caption '{caption}': {e}")
        return False


def load_pipeline(model_name, use_dpo=False):
    device = "cuda" if torch.cuda.is_available() else "cpu"

    if model_name == "stable-diffusion-2-1":
        pipe = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-2-1")
    elif model_name == "stable-diffusion-1-5":
        pipe = DiffusionPipeline.from_pretrained("benjamin-paine/stable-diffusion-v1-5", torch_dtype=torch.float16)
        if use_dpo:
            print("Loading DPO UNet into SD 1.5 pipeline...")
            unet_id = "mhdang/dpo-sd1.5-text2image-v1"
            unet = UNet2DConditionModel.from_pretrained(unet_id, subfolder="unet", torch_dtype=torch.float16)
            pipe.unet = unet
    elif model_name == "if":
        from diffusers import IFPipeline
        pipe = IFPipeline.from_pretrained("DeepFloyd/IF-I-L-v1.0", torch_dtype=torch.float16)
    elif model_name == "kandinsky":
        from diffusers import AutoPipelineForText2Image
        pipe = AutoPipelineForText2Image.from_pretrained("kandinsky-community/kandinsky-2-1")
    elif model_name == "pixart":
        pipe = DiffusionPipeline.from_pretrained("PixArt-alpha/PixArt-XL-2-1024-MS")
    else:
        raise ValueError(f"Unknown model name: {model_name}")

    return pipe.to(device)


def parse_args():
    parser = argparse.ArgumentParser(description="Generate images from captions")
    parser.add_argument("--csv", type=str, required=True, help="Path to CSV file with 'url' and 'caption' columns")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory to save images")
    parser.add_argument("--model", type=str, choices=["stable-diffusion-1-5", "stable-diffusion-2-1", "if", "kandinsky", "pixart"], default="stable-diffusion-2-1", help="Model to use for image generation")
    parser.add_argument("--dpo", action="store_true", help="Use DPO UNet for SD 1.5 model")
    return parser.parse_args()


def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    if args.dpo and args.model != "stable-diffusion-1-5":
        raise ValueError("--dpo is only supported with --model stable-diffusion-1-5")

    print("loading dataset...")
    df = pd.read_csv(args.csv)

    print(f"loading model '{args.model}' from Hugging Face...")
    pipe = load_pipeline(args.model, use_dpo=args.dpo)

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="processing samples"):
        url = row.get("url")
        caption = row.get("caption")

        if not url or not caption:
            print(f"skipping row {idx} due to missing URL or caption")
            continue

        subdir = os.path.join(args.output_dir, f"sample_{idx}")
        original_path = os.path.join(subdir, "original.jpg")
        ai_path = os.path.join(subdir, "ai.jpg")

        if os.path.exists(original_path) and os.path.exists(ai_path):
            continue

        os.makedirs(subdir, exist_ok=True)

        if not os.path.exists(original_path):
            download_image(url, original_path)

        if not os.path.exists(ai_path):
            generate_image(caption, pipe, ai_path)

    print("done!")


if __name__ == "__main__":
    main()
