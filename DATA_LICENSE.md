# Licensing

This repository uses **two different licenses**, depending on what you are looking at.

## 1. Code — MIT License

Everything in this repository is released under the **MIT License** (see the `LICENSE` file),
except for the dataset files described below.

```
MIT License

Copyright (c) 2026 Ning Jia

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 2. Dataset — CC BY-NC-SA 4.0

The dataset files (`CNCD.jsonl`, `CNCD.task1.positive.jsonl`, `CNCD.task2.CRP`) are
**not distributed from this repository**. Download them from Science Data Bank (see below) and place
them under `dataset/`.

CNCD is archived and distributed by **Science Data Bank**:

- DOI: [10.57760/sciencedb.36026](https://doi.org/10.57760/sciencedb.36026)
- CSTR: `31253.11.sciencedb.36026`
- License: **CC BY-NC-SA 4.0** (Attribution · NonCommercial · ShareAlike)

Under CC BY-NC-SA 4.0 you may share and adapt the dataset provided that you:

1. give appropriate credit and cite the DOI above;
2. do **not** use it for commercial purposes;
3. distribute any derivative work under the same license.

**Commercial use requires a separate agreement.** Please contact the corresponding author.

## Why two licenses

A single MIT declaration would have been wrong: MIT cannot license dataset content, and it
would have silently dropped the NonCommercial and ShareAlike terms the authors chose for the
data. Keeping the MIT license scoped to the source code, and pointing every dataset use back
to the ScienceDB record, makes both declarations accurate.

## Notes on the data itself

- Source articles were collected from public Chinese news websites (March–May 2023).
- **Copyright in the news articles themselves belongs to the original publishers.** Collecting
  publicly available text does not transfer redistribution rights. Users are responsible for
  ensuring their own use complies with applicable law.
- Some articles name natural persons. Users handling this data under the GDPR, PIPL or similar
  regimes should perform their own assessment before further distribution.
- The third-party components used with this dataset carry their own licenses:
  Faiss (MIT), Elasticsearch (Elastic License 2.0 / SSPL / AGPL), BGE (MIT), DeepSeek-V3
  (DeepSeek License). Check each before commercial deployment.
