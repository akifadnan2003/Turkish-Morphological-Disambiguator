# Turkish Morphological Disambiguator

**BTU — Bursa Teknik Üniversitesi**  
Bilgisayar Mühendisliği Bölümü | Doğal Dil İşleme | 2025–2026 Bahar Dönemi

---

## Overview

CRF-based morphological disambiguation for Turkish. Given a sentence, the model predicts the correct **Universal Part-of-Speech (UPOS)** tag for each token using a Conditional Random Fields (CRF) model trained on the **UD Turkish-IMST Treebank**.

Morphological disambiguation is the task of selecting the correct grammatical reading of each word in context. Turkish is an agglutinative language where the same surface form can carry multiple possible analyses — this model resolves that ambiguity using learned sequence features.

| Metric | Treebank Test Set | Manual Annotations |
|--------|:-----------------:|:------------------:|
| Accuracy | **90.93%** | **87.57%** |
| Weighted F1 | **90.80%** | **87.22%** |
| Sentences | 1,100 | 25 (hand-annotated) |
| Tokens | 10,032 | 169 |

---

## Project Structure

```
├── download_data.py        # Downloads UD Turkish-IMST treebank splits
├── morpho_disambig.py      # Feature extraction, CRF training, evaluation, model save
├── evaluate_custom.py      # Evaluates model against manually annotated sentences
├── app.py                  # Flask web demo server
├── templates/
│   └── index.html          # Web UI — spaCy-style annotation view + CoNLL-U table
├── my_annotations.conllu   # 25 manually annotated Turkish sentences (CoNLL-U format)
└── README.md
```

> **Generated on first run** (not tracked in git):
> `data/` — treebank files &nbsp;|&nbsp; `model/` — trained CRF weights &nbsp;|&nbsp; `results/` — charts and predictions

---

## Setup

```bash
pip install sklearn-crfsuite scikit-learn matplotlib seqeval conllu flask
```

---

## Usage

### Step 1 — Download treebank data
```bash
python download_data.py
```
Downloads `tr_imst-ud-train.conllu`, `tr_imst-ud-dev.conllu`, `tr_imst-ud-test.conllu` into `./data/`.

### Step 2 — Train and evaluate
```bash
python -X utf8 morpho_disambig.py
```
- Trains CRF on 3,435 sentences
- Evaluates on dev and test splits
- Saves per-class precision / recall / F1 / accuracy
- Generates confusion matrix and F1 bar chart as PNG files in `./results/`
- Saves trained model to `./model/crf_model.pkl`
- Writes CoNLL-U predictions to `./results/predictions.conllu`

### Step 3 — Evaluate on manual annotations
```bash
python -X utf8 evaluate_custom.py
```
Runs the trained model on the 25 hand-annotated sentences in `my_annotations.conllu` and prints a token-by-token comparison with per-class F1 report.

### Step 4 — Launch web demo
```bash
python -X utf8 app.py
```
Open **http://127.0.0.1:5000**

---

## Web Demo

The Flask web application provides a live demonstration interface:

- **Input** — type any space-tokenized Turkish sentence or click an example
- **Visual tab** — spaCy-style inline annotation with color-coded POS tags and confidence scores per token
- **CoNLL-U tab** — full CoNLL-U format table output
- **Sidebar** — model performance metrics (accuracy, weighted F1, dataset stats)
- **Charts** — confusion matrix and per-class F1 bar chart embedded on the page

---

## Manual Annotations (`my_annotations.conllu`)

25 Turkish sentences manually annotated in CoNLL-U format, covering:

| Domain | Sentences |
|--------|:---------:|
| University / academic | 8 |
| Daily life | 8 |
| NLP / technology | 5 |
| Geography | 2 |
| Nature | 1 |
| NLP evaluation | 1 |

Each token is annotated with:
- **UPOS** — Universal Part-of-Speech tag
- **Lemma** — dictionary root form
- **FEATS** — morphological features: `Case`, `Number`, `Person`, `Tense`, `Mood`, `Polarity`, `VerbForm`, `Voice`, `Poss`

Annotations include linguistically interesting cases such as converbs (`VerbForm=Conv`), verbal nouns (`VerbForm=Vnoun`), negative polarity (`Polarity=Neg`), and passive voice (`Voice=Pass`).

---

## Features

**Turkish-specific suffix features** (40+ features encoding morphological knowledge):

| Feature | Examples | Signal |
|---------|---------|--------|
| Ablative suffix | `-dan`, `-den`, `-tan`, `-ten` | NOUN |
| Locative suffix | `-da`, `-de`, `-ta`, `-te` | NOUN |
| Present cont. | `-yor`, `-iyor` | VERB |
| Past tense | `-dı`, `-di`, `-du`, `-dü` | VERB |
| Plural | `-lar`, `-ler` | NOUN |
| Infinitive | `-mak`, `-mek` | VERB |
| Adj-forming | `-lı`, `-li`, `-lu`, `-lü` | ADJ |
| Evidential past | `-mış`, `-miş`, `-muş`, `-müş` | VERB |

**Context window:** ±2 tokens (previous 2 and next 2 words)

**Word shape:** capitalization, digits, apostrophe (proper noun indicator)

**Vowel harmony:** front/back vowel class of the last vowel in the word

---

## Output Format

All predictions are written in **CoNLL-U format** as required by the project specification:

```
# text = Dün akşam toplantıdan erken çıktım .
1   Dün          dün      ADV    ADV   _  _  _  _  _
2   akşam        akşam    ADV    ADV   _  _  _  _  _
3   toplantıdan  toplantı NOUN   NOUN  Case=Abl|Number=Sing|Person=3  _  _  _  _
4   erken        erken    ADV    ADV   _  _  _  _  _
5   çıktım       çık      VERB   VERB  Mood=Ind|Number=Sing|Person=1|Tense=Past  _  _  _  _
6   .            .        PUNCT  PUNCT _  _  _  _  _
```

---

## Evaluation Results

### Treebank Test Set (1,100 sentences)

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
- ADV recall drops to 46% on the custom set — short adverbs like *dün*, *bugün*, *yarın* lack strong suffix signals and are frequently confused with NOUN
- ADJ/NOUN boundary is the hardest — Turkish adjectives and nouns often share identical surface forms
