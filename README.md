<img alt="github-banner" src="https://github.com/user-attachments/assets/18caff40-e7be-41cd-a101-95fe7d307cdf" />

---

#### [Maty Bohacek](https://www.matyasbohacek.com), [Thomas Fel](https://thomasfel.fr), [Maneesh Agrawala](https://www.graphics.stanford.edu/~maneesh/), and [Ekdeep Singh Lubana](https://ekdeepslubana.github.io)

Despite their impressive performance, generative image models trained on large-scale datasets frequently fail to produce images with seemingly simple concepts—e.g., *human hands* or *objects appearing in groups of four*—that are reasonably expected to appear in the training data.  These failure modes have largely been documented anecdotally, leaving open the question of whether they reflect idiosyncratic anomalies or more structural limitations of these models.  To address this, we introduce a systematic approach for identifying and characterizing "conceptual blindspots"—concepts present in the training data but absent or misrepresented in a model's generations.  Our method leverages sparse autoencoders (SAEs) to extract interpretable concept embeddings, enabling a quantitative comparison of concept prevalence between real and generated images.  We train an archetypal SAE (RA-SAE) on DINOv2 features with 32,000 concepts—the largest such SAE to date—enabling fine-grained analysis of conceptual disparities.  Applied to four popular generative models (Stable Diffusion 1.5/2.1, PixArt, and Kandinsky), our approach reveals specific suppressed blindspots (e.g., *bird feeders*, *DVD discs*, and *whitespaces on documents*) and exaggerated blindspots (e.g., *wood background texture* and *palm trees*).  At the individual datapoint level, we further isolate memorization artifacts — instances where models reproduce highly specific visual templates seen during training.  Overall, we propose a theoretically grounded framework for systematically identifying conceptual blindspots in generative models by assessing their conceptual fidelity with respect to the underlying data-generating process.

> [Website](https://conceptual-blindspots.github.io) — [Paper](https://arxiv.org/abs/2506.19708) — [Exploratory Tool](https://sae-diff.github.io) — [Contact us](mailto:maty-at-stanford-dot-edu)
> 
> _Under Review_

## Modules

This repository is broken up into three modules: (1) Energy Difference Calculation, (2) Blindspot Analysis, and (3) Exploratory Tool. To apply our method to your T2I model, employ these modules in order, as each depends on the outputs of previous stages.

### Energy Difference Calculation

This module samples from the training dataset, generates matching images, extracts the SAE concepts, and calculates the energy differences δ(.). To use it, prepare your dataset of image-caption pairs and T2I model. 

### Blindspot Analysis

As a collection of exploratory scripts, this module performs distribution-level, datapoint-level, and co-occurrence analyses, revealing suppresses and exaggerated blindspots, as well as memorized datapoints. The findings from this module can be used to extend or improve your training dataset—particularly, which concepts would benefit from more samples or improved captions.

### Exploratory Tool

Built around a UMAP projection of all concepts, this module presents the results of the previous two modules in an interactive web application. You can see this tool in action on the models evaluated as a part of our paper (SD 1.5, SD 2.1, Kandinsky, and PixArt) [here](https://sae-diff.github.io/).

## Getting Started

Clone the repo and prepare an environment with essential dependencies (Python 3.10 is recommended):

```shell
git clone tbd
conda create -n conceptual-blindspots python=3.10
conda activate conceptual-blindspots
pip install -r requirements.txt
```

Prepare your T2I model and its training dataset in a compatible Hugging Face format (see examples for popular models and LAION here):

```python
# modify the load_pipeline() method in energy_difference/dataset_generation.py to support a HF-style T2I pipeline like so:
pipe = load_pipeline("your_model")
image = pipe(caption, width=512, height=512).images[0]

# prepare your dataset on HF hub (or locally) such that the following snippet from energy_difference/dataset_sampling.py loads a tabular dataset with 'url' and 'caption' columns
dataset = load_dataset("your_dataset", split="train")
```

Next, employ the above-mentioned modules in order, following their respective docs. You can start with the [Energy Difference Calculation](energy_difference/) module!

## Reproducing Paper Results

Use the following resources to reproduce the results reported in our paper:

<details>
<summary><b>Training Dataset Sample</b></summary>

> 10K Subset of LAION-5B
> 
> [↓ Download]()

</details>

<details>
<summary><b>Concept Extraction Model</b></summary>

> Custom-trained **RA-SAE-DINOv2-32k**, the largest model of its kind
> 
> [→ See on Hugging Face](https://huggingface.co/matybohacek/RA-SAE-DINOv2-32k)

</details>

<details>
<summary><b>Pre-computed Data</b></summary>

>
>| Model                     | Images         | Energy Difference | Web Data        |
>|--------------------------|----------------|-------------------|-----------------|
>| Stable Diffusion 1.5     | [↓ Download]() | [↓ Download]()    | [↓ Download]()  |
>| Stable Diffusion 1.5 DPO | [↓ Download]() | [↓ Download]()    | [↓ Download]()  |
>| Stable Diffusion 2.1     | [↓ Download]() | [↓ Download]()    | [↓ Download]()  |
>| Kandinsky                | [↓ Download]() | [↓ Download]()    | [↓ Download]()  |
>| Pixart                   | [↓ Download]() | [↓ Download]()    | [↓ Download]()  |
>

</details>

## Citation

```bibtex
@article{bohacek2025uncovering,
  title={Uncovering Conceptual Blindspots in Generative Image Models Using Sparse Autoencoders},
  author={Bohacek, Matyas and Fel, Thomas and Agrawala, Maneesh and Lubana, Ekdeep Singh},
  journal={arXiv preprint arXiv:2506.19708},
  year={2025}
}
```
