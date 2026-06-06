# Turkish Morphological Disambiguator

**BTU — Bursa Teknik Üniversitesi**  
Doğal Dil İşleme | 2025–2026 Bahar Dönemi

---

## Overview

CRF-based morphological disambiguation for Turkish. Given a sentence, the model predicts the correct **Universal Part-of-Speech (UPOS)** tag for each token using a Conditional Random Fields (CRF) model trained on the **UD Turkish-IMST Treebank**.

| Metric | Value |
|--------|-------|
| Test Accuracy | **90.93%** |
| Weighted F1 | **90.80%** |
| Algorithm | CRF (L-BFGS) |
| Dataset | UD Turkish-IMST (3,435 train / 1,100 test) |

---

## Project Structure

```
├── download_data.py      # Download UD Turkish-IMST treebank
├── morpho_disambig.py    # Train, evaluate, save model
├── app.py                # Flask web demo
├── templates/
│   └── index.html        # Web UI
└── README.md
```

---

## Setup

```bash
pip install sklearn-crfsuite scikit-learn matplotlib seqeval conllu flask
```

---

## Usage

### Step 1 — Download data
```bash
python download_data.py
```

### Step 2 — Train and evaluate
```bash
python -X utf8 morpho_disambig.py
```
Outputs per-class precision, recall, F1, accuracy, confusion matrix, and saves the model.

### Step 3 — Launch web demo
```bash
python -X utf8 app.py
```
Open **http://127.0.0.1:5000**

---

## Features

- Turkish-specific suffix features (case endings, tense markers, plural suffixes)
- Vowel harmony detection (front/back vowel class)
- Context window: 2 tokens left and right
- Word shape features (capitalization, digits, apostrophe)
- CRF sequence model (labels entire sentence jointly, not word-by-word)

## Output Format

Predictions are written in **CoNLL-U format** as required by the project specification:

```
# text = Dün akşam toplantıdan erken çıktım .
1   Dün          dün      ADV    ADV   _  _  _  _  _
2   akşam        akşam    ADV    ADV   _  _  _  _  _
3   toplantıdan  _        NOUN   NOUN  _  _  _  _  _
4   erken        _        ADV    ADV   _  _  _  _  _
5   çıktım       _        VERB   VERB  _  _  _  _  _
6   .            .        PUNCT  PUNCT _  _  _  _  _
```

## Evaluation

Results include per-class precision, recall, F1-score, and a confusion matrix — reported for both dev and test splits.

```
              precision    recall  f1-score
VERB            0.9375    0.9409    0.9392
NOUN            0.8432    0.9251    0.8823
ADJ             0.8485    0.7583    0.8009
PROPN           0.8333    0.7086    0.7659
PUNCT           0.9990    1.0000    0.9995
```
