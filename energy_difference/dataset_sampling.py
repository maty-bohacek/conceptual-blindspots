
import os
import argparse
import random
import requests
import logging

import pandas as pd

from datasets import load_dataset
from urllib.parse import urlparse
from tqdm import tqdm


logging.basicConfig(level=logging.WARNING)


def parse_args():
    parser = argparse.ArgumentParser(description="Sample valid entries from LAION relaion2B-en-research-safe dataset")
    parser.add_argument(
        "--n",
        type=int,
        nargs="+",
        required=True,
        help="Number(s) of valid samples to collect (e.g., --n 1000 5000)"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="Directory to save CSV files"
    )
    return parser.parse_args()


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except ValueError:
        return False
    except:
        return False


def url_exists(url, timeout=5):
    if not is_valid_url(url):
        logging.warning(f"Invalid URL skipped (basic check): {url}")
        return False
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code == 200
    except (requests.RequestException, ValueError) as e:
        logging.warning(f"Request failed/skipped: {url} | {e}")
        return False
    except:
        return False


def collect_valid_samples(dataset, target_count):
    dataset_len = len(dataset)
    seen_indices = set()
    valid_samples = []

    with tqdm(total=target_count, desc=f"valid samples collected") as pbar:
        while len(valid_samples) < target_count:
            idx = random.randint(0, dataset_len - 1)
            if idx in seen_indices:
                continue
            seen_indices.add(idx)

            sample = dataset[idx]
            url = sample.get("url")
            if not url:
                continue
            if url_exists(url):
                valid_samples.append(sample)
                pbar.update(1)

    print(f"\tseen: {len(seen_indices)}, valid: {len(valid_samples)}")

    return valid_samples


def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    print("loading full LAION dataset")
    dataset = load_dataset("laion/relaion2B-en-research-safe", split="train")
    dataset_len = len(dataset)
    print(f"loaded {dataset_len:,} samples")

    for n in args.n:
        print(f"\nsampling {n} valid entries...")
        samples = collect_valid_samples(dataset, n)
        df = pd.DataFrame(samples)
        out_path = os.path.join(args.output_dir, f"sample_{n}.csv")
        df.to_csv(out_path, index=False)
        print(f"saved {n} valid samples to {out_path}")


if __name__ == "__main__":
    main()
