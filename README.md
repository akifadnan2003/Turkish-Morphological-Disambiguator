# Turkish Morphological Disambiguator

**BTU — Bursa Teknik Üniversitesi**  
Bilgisayar Mühendisliği Bölümü | Doğal Dil İşleme | 2025–2026 Bahar Dönemi  
**Öğrenci:** Akif Adnan — 20360859106 | Bireysel Çalışma

---

## How to Run

> Run all commands from inside the project folder. Python 3.8+ required.

### 1. Install dependencies
```bash
pip install sklearn-crfsuite scikit-learn matplotlib seqeval conllu flask python-docx reportlab
```

### 2. Download treebank data
```bash
python download_data.py
```
Downloads the UD Turkish-IMST treebank (train/dev/test splits) into `data/`. Takes ~10 seconds.

### 3. Train the CRF model
```bash
python -X utf8 morpho_disambig.py
```
- Trains CRF on 3,435 sentences — takes **1–2 minutes**
- Prints accuracy, precision, recall, F1 for dev and test sets
- Saves confusion matrix + per-class F1 charts to `results/`
- Saves trained model to `model/crf_model.pkl`

> **Skip this step** if `model/crf_model.pkl` already exists — the pre-trained model is included.

### 4. Run the web dashboard
```bash
python -X utf8 app.py
```
Then open **http://127.0.0.1:5000** in a browser.

The dashboard includes:
- Live sentence analysis — type any Turkish sentence and get color-coded POS tags with confidence scores
- CoNLL-U format output table
- Per-class precision / recall / F1 tables for the treebank test set
- My 25 manually annotated sentences with gold vs. predicted comparison, filterable by domain
- My feature engineering cards showing the 12 Turkish suffix feature groups

### 5. (Optional) Evaluate on manual annotations only
```bash
python -X utf8 evaluate_custom.py
```
Runs the model on `my_annotations.conllu` and prints a token-by-token comparison with per-class F1 report.

### 6. (Optional) Zemberek candidate disambiguation demo
```bash
python -X utf8 candidate_disambig.py
```
Demonstrates the candidate generation + CRF disambiguation pipeline on example sentences.

---

## Reports

Pre-built reports are in the `report/` folder — no need to run anything:

| File | Description |
|------|-------------|
| `report/NLP_Project_Report_AkifAdnan.pdf` | PDF project report |
| `report/NLP_Project_Report_AkifAdnan.docx` | Word project report |

---

## Project Structure

```
├── download_data.py         Downloads UD Turkish-IMST treebank
├── morpho_disambig.py       CRF feature extraction, training, evaluation
├── candidate_disambig.py    Zemberek-style candidate generation + CRF disambiguation demo
├── evaluate_custom.py       Evaluates model on manual annotations
├── app.py                   Flask web dashboard
├── templates/
│   └── index.html           Web UI
├── my_annotations.conllu    25 manually annotated Turkish sentences (CoNLL-U format)
├── report/
│   ├── NLP_Project_Report_AkifAdnan.pdf
│   └── NLP_Project_Report_AkifAdnan.docx
├── data/                    Treebank files (created by download_data.py)
├── model/                   Trained CRF model (created by morpho_disambig.py)
└── results/                 Charts and predictions (created by morpho_disambig.py)
```

---

## Overview

CRF-based morphological disambiguation for Turkish. The model predicts the correct **Universal Part-of-Speech (UPOS)** tag for each token using a Conditional Random Fields (CRF) model trained on the **UD Turkish-IMST Treebank**.

Morphological disambiguation is the task of selecting the correct grammatical reading of each word in context. Turkish is agglutinative — the same surface form can carry multiple possible analyses. This model resolves that ambiguity using learned sequence features.

| Metric | Treebank Test Set | Manual Annotations |
|--------|:-----------------:|:------------------:|
| Accuracy | **90.93%** | **87.57%** |
| Weighted F1 | **90.80%** | **87.22%** |
| Sentences | 1,100 | 25 (hand-annotated) |
| Tokens | 10,032 | 169 |

---

## My Contributions

### Manual Annotations (`my_annotations.conllu`)

25 Turkish sentences I personally annotated in CoNLL-U format, covering 6 domains:

| Domain | Sentences |
|--------|:---------:|
| University / academic | 8 |
| Daily life | 8 |
| NLP / technology | 5 |
| Geography | 2 |
| Nature | 1 |
| NLP evaluation | 1 |

Each token is annotated with UPOS, Lemma, and morphological FEATS (`Case`, `Number`, `Person`, `Tense`, `Mood`, `Polarity`, `VerbForm`, `Voice`, `Poss`). Includes linguistically interesting cases: converbs (`VerbForm=Conv`), verbal nouns (`VerbForm=Vnoun`), negative polarity, passive voice.

### Feature Engineering

40+ hand-crafted Turkish-specific features encoding morphological knowledge:

| Feature Group | Examples | Target Tag |
|---------|---------|--------|
| Ablative suffix | `-dan`, `-den`, `-tan`, `-ten` | NOUN |
| Locative suffix | `-da`, `-de`, `-ta`, `-te` | NOUN |
| Present continuous | `-yor`, `-iyor` | VERB |
| Past tense | `-dı`, `-di`, `-du`, `-dü` | VERB |
| Plural | `-lar`, `-ler` | NOUN |
| Infinitive | `-mak`, `-mek` | VERB |
| Adjective-forming | `-lı`, `-li`, `-lu`, `-lü` | ADJ |
| Evidential past | `-mış`, `-miş`, `-muş`, `-müş` | VERB |

Context window: ±2 tokens. Word shape features: capitalization, digits, apostrophe (proper noun signal). Vowel harmony class of the last vowel.

### Two-Stage Pipeline (Zemberek Simulation)

The project spec requires Zemberek-based candidate generation. Since Java/gRPC dependencies are impractical in a Python environment, this is simulated with a **Corpus-Based Candidate Dictionary**:

- **Stage 1 — CRF:** predicts UPOS tag in context (90.93% accuracy)
- **Stage 2 — Corpus dictionary:** assigns the most frequent FEATS seen for that (word, UPOS) pair in training (11,762 entries)

`candidate_disambig.py` shows the full pipeline: candidate list per word → CRF marginal scoring → best analysis selected.

---

## Evaluation Results

### Treebank Test Set (1,100 sentences, 10,032 tokens)

```
              precision    recall  f1-score   support

       PUNCT     0.9990    1.0000    0.9995      1933
         AUX     0.9442    0.9621    0.9531       211
       CCONJ     0.9635    0.9635    0.9635       356
        VERB     0.9375    0.9409    0.9392      1928
        NOUN     0.8432    0.9251    0.8823      2430
         ADP     0.9556    0.9048    0.9295       357
        PRON     0.9452    0.9289    0.9370       464
         DET     0.8422    0.9622    0.8982       344
         ADJ     0.8485    0.7583    0.8009       960
         ADV     0.8875    0.7701    0.8246       461
         NUM     0.9073    0.7135    0.7988       192
       PROPN     0.8333    0.7086    0.7659       374

    accuracy                         0.9093     10032
   macro avg     0.8505    0.7941    0.8161     10032
weighted avg     0.9099    0.9093    0.9080     10032
```

### Manual Annotation Set (25 sentences, 169 tokens)

```
              precision    recall  f1-score   support

         ADJ     0.6364    0.7778    0.7000        18
         ADP     1.0000    1.0000    1.0000         2
         ADV     1.0000    0.4615    0.6316        13
       CCONJ     1.0000    1.0000    1.0000         1
         DET     1.0000    1.0000    1.0000        11
        NOUN     0.8571    0.8276    0.8421        58
         NUM     0.7500    1.0000    0.8571         3
        PRON     1.0000    1.0000    1.0000         2
       PROPN     0.7500    1.0000    0.8571         6
       PUNCT     1.0000    1.0000    1.0000        25
        VERB     0.9375    1.0000    0.9677        30

    accuracy                         0.8757       169
```

**Key observations:**
- VERB and PUNCT are disambiguated near-perfectly — Turkish verb morphology (tense/person suffixes) is highly distinctive
- PROPN recall is 100% but precision 75% — the model over-predicts proper nouns for unknown capitalized words
- ADV recall drops to 46% on the custom set — short adverbs like *dün*, *bugün*, *yarın* lack strong suffix signals
- ADJ/NOUN boundary is the hardest — Turkish adjectives and nouns often share identical surface forms
