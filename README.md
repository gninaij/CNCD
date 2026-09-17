<div align="center">

# CNCD — Chinese News Contradiction Dataset

**Detecting Factual Contradictions in News Based on Large Language Models**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22808609.svg)](https://doi.org/10.5281/zenodo.22808609)
[![Dataset DOI](https://img.shields.io/badge/Data%20DOI-10.57760%2Fsciencedb.36026-blue)](https://doi.org/10.57760/sciencedb.36026)
[![License: MIT](https://img.shields.io/badge/Code%20License-MIT-yellow.svg)](DATA_LICENSE.md)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/Data%20License-CC%20BY--NC--SA%204.0-lightgrey.svg)](DATA_LICENSE.md)

**Paper** ([English PDF](paper/paper_en.pdf) · [中文 PDF](paper/paper_cn.pdf)) ·
**Dataset** ([ScienceDB](https://doi.org/10.57760/sciencedb.36026)) ·
**Zenodo** ([DOI](https://doi.org/10.5281/zenodo.22808609))

</div>

---

## Abstract

Online news provides readers with abundant information sources, yet the authenticity of such information is often not guaranteed. Prior work has achieved considerable success in identifying deliberately fabricated information, but existing methods struggle to handle reports that were not originally intended as fabrications yet were subsequently proved false. This paper proposes a method that detects factual contradictions in news by cross-validating reports describing the same event, since contradictory facts are a prerequisite for determining veracity. The method consists of two main tasks: identifying **denial reports**, and identifying the corresponding **denied reports**; the two together constitute a **contradictory news pair**. We also release CNCD (Chinese News Contradiction Dataset), which contains 1,957 denial reports, 800 denied reports and 5,022 manually verified contradictory news pairs drawn from 105,361 public Chinese news articles published between March and May 2023. Experiments show that the first task achieves a recall rate exceeding 97%, and that the second task effectively identifies mutually contradictory news pairs within the collection.

<!-- REMINDER: the BibTeX below says the dataset is version V2, while the counts above (1,957 / 800 / 5,022)
     are the V1 numbers. If ScienceDB has been updated to V2, replace these three numbers in the abstract
     and in the Dataset section below. Do not leave two different releases described at once. -->

### 摘要

互联网新闻数量庞大，但其真实性往往难以保证。以往的研究对蓄意伪造的信息有较好的识别能力，但对于并非出于伪造目的、后来被证伪的报道则难以有效判定。本文提出一种利用报道同一事件的新闻相互校验来发现事实矛盾的方法：该方法包含两个主要任务，分别为识别具有否定意见的新闻和识别与之相应的被否定的报道，二者构成矛盾新闻对；本文同时发布 CNCD 中文新闻矛盾数据集，包含 2023 年 3 月至 5 月采集的 105,361 篇公开中文新闻中的 1,957 篇否认报道、800 篇被否认报道与 5,022 个人工核验的矛盾新闻对。实验表明任务1的召回率超过 97%，任务2能够有效识别新闻集合中的矛盾新闻对。

## Method in one paragraph

Contradictions take time to emerge. An event is reported, later a party issues a denial, and a follow-up report covers that denial. **Task 1** finds the denial report: a lexical matching filter (positive and negative feature sets) first discards news without negation semantics, then an LLM decides whether the article explicitly denies something already disclosed and extracts the denied event with its subjects and locations. **Task 2** finds the denied report: the extracted denied content is used to retrieve candidates over Elasticsearch and Faiss (BGE embeddings), and the candidates pass through three cascaded filters — ENT Filter (all subjects and locations must appear), SIM Filter (similarity to the denial report within [0.6, 0.8]), and LLM Filter (two prompts checking event consistency and content exclusivity). The LLM Filter is  mandatory; the other two are optional.

## Key results

Task 1 — denial report identification: **P 88.22 / R 97.91 / F1 92.81**

Task 2 — contradictory news pair matching, filter ablation:

| Filter combination | Precision | Recall    | F1        | Time     |
| ------------------ | ---------:| ---------:| ---------:| --------:|
| ENT + SIM + LLM    | **67.53** | 24.74     | 36.21     | 17.63 h  |
| ENT + LLM          | 63.71     | 47.18     | 54.21     | 60.45 h  |
| SIM + LLM          | 61.02     | 35.07     | 44.54     | 101.73 h |
| LLM only           | 59.37     | **67.63** | **63.23** | 170.99 h |

Task 2 — retrieval ablation (LLM Filter only):

| Retrieval             | Precision | Recall    | F1        | Candidates |
| --------------------- | ---------:| ---------:| ---------:| ----------:|
| Elasticsearch         | 58.69     | 60.51     | 59.59     | 5,178      |
| Faiss                 | **67.15** | 41.55     | 51.34     | 3,108      |
| Elasticsearch + Faiss | 59.37     | **67.63** | **63.23** | 5,721      |

Two things are worth noting. 

First, this gives an explicit **accuracy–compute frontier**: F1 63.23 at 171 h down to F1 36.21 at 17.6 h, which is useful when deciding where to spend a compute budget. 

Second, the ablation shows the **SIM Filter is strictly dominated** — SIM + LLM is both slower (101.73 h vs 60.45 h) and worse on every metric than ENT + LLM. The [0.6, 0.8] similarity band discards a large number of true pairs, so the assumption behind this filter needs rethinking.

## Repository structure

```
CNCD/
├── src/
│   ├── check_fake_task1.py    # Task 1: denial report identification
│   ├── check_fake_task2.py    # Task 2: denied report search
│   ├── evaluate.py            # P / R / F1 for both tasks
│   ├── es_util.py             # Elasticsearch index creation and ingestion
│   ├── faiss_util.py          # Faiss index creation and ingestion
│   ├── llm_worker.py          # LLM API configuration and prompting
│   ├── text_util.py           # text processing helpers
│   └── log_util.py            # logging helpers
├── paper/
│   ├── paper_en.pdf           # full English translation
│   └── paper_cn.pdf           # Chinese original
├── model/BAAI/bge-base-zh-v1.5/   # place the embedding model here
├── output/                    # prediction files are written here
├── CITATION.cff
├── DATA_LICENSE.md
└── README_en.md / README.md
```

## Dataset

CNCD is **not distributed in this repository**. It is archived at Science Data Bank:

- DOI: [10.57760/sciencedb.36026](https://doi.org/10.57760/sciencedb.36026)
- CSTR: `31253.11.sciencedb.36026`
- License: **CC BY-NC-SA 4.0**

Download the three files from ScienceDB and place them under `dataset/`:

| File                        | Content                                                     |
| --------------------------- | ----------------------------------------------------------- |
| `CNCD.jsonl`                | the news collection: id, title, body text, publication date |
| `CNCD.task1.positive.jsonl` | denial reports with their labels                            |
| `CNCD.task2.CRP`            | contradictory news pairs, one news-ID pair per line         |

| Statistic                  | Count     |
| -------------------------- | ---------:|
| News articles              | 105,361   |
| Denial reports             | 1,957     |
| Denied reports             | 800       |
| Contradictory news pairs   | 5,022     |
| Collected before filtering | 2,172,523 |

The corpus was collected from dozens of public Chinese news websites and covers March–May 2023,
concentrated in economics reporting. Each contradictory pair was verified by a human annotator.

## Quick start

### 1. Environment

Tested with Python 3.12.

```shell
git clone https://github.com/gninaij/CNCD.git
cd CNCD
pip install -r requirements.txt
```

If you plan to run on GPU, install the GPU builds of the relevant packages instead.

### 2. Text embedding model

Download BGE from [Hugging Face](https://huggingface.co/BAAI/bge-base-zh-v1.5/tree/main) and place
it under `model/BAAI/bge-base-zh-v1.5/`.

### 3. Elasticsearch

Elasticsearch 7.6.1 has been verified to work. Start Elasticsearch, then build the index once
before the first run, using `src/es_util.py`:

```python
from src.es_util import create_index, add_data2es_txt

create_index()        # create the index
add_data2es_txt()     # insert the news collection
```

### 4. Faiss

Build the index once before the first run, using `src/faiss_util.py`:

```python
from src.faiss_util import add_data2faiss_txt

add_data2faiss_txt()  # embed and insert the news collection
```

This step is time-consuming because every article has to be embedded.

### 5. LLM access

Set your API key, endpoint URL and model name in `src/llm_worker.py`.

## Running the experiments

Elasticsearch must be running.

### Task 1

Run the identification task with `src/check_fake_task1.py`:

```python
if __name__ == '__main__':
    run()
```

Predictions are written to `f'{news_file}.task1.pred'` in `output/`.

Evaluate them with `src/evaluate.py`:

```python
result_file = '../output/task1.pred'
eva_task1(result_file)
```

### Task 2

Configure which optional filters to enable in `src/check_fake_task2.py`:

```python
if __name__ == '__main__':
    USE_ENT_FILTER = False   # whether to use the ENT Filter
    USE_SIM_FILTER = False   # whether to use the SIM Filter
    run()
```

The output file name reflects the combination you selected:

| `USE_ENT_FILTER` | `USE_SIM_FILTER` | Output file                     |
| ---------------- | ---------------- | ------------------------------- |
| True             | True             | `output/task2.pred_ent_sim_llm` |
| True             | False            | `output/task2.pred_ent_llm`     |
| False            | True             | `output/task2.pred_sim_llm`     |
| False            | False            | `output/task2.pred_llm`         |

Evaluate with `src/evaluate.py`:

```python
result_file = '../output/task2.pred_llm'
# result_file = '../output/task2.pred_ent_sim_llm'
# result_file = '../output/task2.pred_ent_llm'
# result_file = '../output/task2.pred_sim_llm'
eva_task2(result_file, 'test')
```

## Citation

If you use the code or the paper, please cite:

```bibtex
@software{jia2026cncd,
  title        = {CNCD: Detecting Factual Contradictions in News Based on Large Language Models},
  author       = {Jia, Ning and Wei, Zifu and He, Shumeng},
  year         = {2026},
  publisher    = {Zenodo},
  version      = {1.0.0},
  doi          = {10.5281/zenodo.22808609},
  url          = {https://github.com/gninaij/CNCD}
}

@dataset{jia2026cncd_dataset,
  title     = {Chinese News Contradiction Dataset},
  author    = {Jia, Ning},
  year      = {2026},
  publisher = {Science Data Bank},
  version   = {V2},
  doi       = {10.57760/sciencedb.36026},
  url       = {https://doi.org/10.57760/sciencedb.36026}
}
```

You can also click **Cite this repository** in the sidebar — GitHub reads `CITATION.cff` and
generates the entry for you.

## License

Code is **MIT**. The dataset is **CC BY-NC-SA 4.0** and distributed by Science Data Bank.
See [DATA_LICENSE.md](DATA_LICENSE.md) for the full terms, including notes on news copyright and
the licenses of third-party components.

## Acknowledgments

Supported by the High-Level Talent Program of Hunan University of Information Technology,
Project No. GCCXM2025005.

## Contact

Questions and bug reports are welcome in
[GitHub Issues](https://github.com/gninaij/CNCD/issues). For dataset access or commercial licensing,
please open an issue or contact the corresponding author.
