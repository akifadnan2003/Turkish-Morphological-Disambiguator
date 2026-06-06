"""
Turkish Morphological Disambiguation using CRF.

Task: given a sentence, predict the correct POS tag (UPOS) and morphological
features (feats) for each token — i.e., disambiguate among all possible
morphological analyses.

Dataset: UD_Turkish-IMST (CoNLL-U format)
Model:   CRF via sklearn-crfsuite
"""

import os
import re
import argparse
import warnings
import pickle
from collections import Counter

import conllu
import sklearn_crfsuite
from sklearn_crfsuite import metrics as crf_metrics
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
)
from seqeval.metrics import classification_report as seq_report
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

warnings.filterwarnings("ignore")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ---------------------------------------------------------------------------
# CoNLL-U loading
# ---------------------------------------------------------------------------

def load_conllu(path):
    """Return list of sentences; each sentence is a list of token dicts."""
    sentences = []
    with open(path, encoding="utf-8") as f:
        for sent in conllu.parse_incr(f):
            tokens = []
            for tok in sent:
                # skip multi-word and empty nodes
                if not isinstance(tok["id"], int):
                    continue
                tokens.append({
                    "form":   tok["form"],
                    "lemma":  tok["lemma"] if tok["lemma"] else "_",
                    "upos":   tok["upos"]  if tok["upos"]  else "_",
                    "feats":  tok["feats"] if tok["feats"] else {},
                })
            if tokens:
                sentences.append(tokens)
    return sentences


# ---------------------------------------------------------------------------
# Label encoding
# We predict UPOS (part-of-speech) as the disambiguation label.
# This directly reflects choosing the correct morphological reading.
# ---------------------------------------------------------------------------

def get_label(token):
    return token["upos"]


# ---------------------------------------------------------------------------
# Feature extraction  (critical for Turkish agglutinative morphology)
# ---------------------------------------------------------------------------

TURKISH_SUFFIXES = [
    "dan", "den", "tan", "ten",   # ablative
    "da",  "de",  "ta",  "te",    # locative
    "a",   "e",   "ya",  "ye",    # dative
    "ı",   "i",   "u",   "ü",     # accusative
    "nın", "nin", "nun", "nün",   # genitive
    "lar", "ler",                  # plural
    "yor", "iyor",                 # present continuous
    "dı",  "di",  "du",  "dü",    # past
    "mış", "miş", "muş", "müş",   # evidential
    "lı",  "li",  "lu",  "lü",    # adjective-forming
    "sız", "siz", "suz", "süz",   # negation adjective
    "ca",  "ce",  "ça",  "çe",    # adverbial
    "ki",                          # relative
    "ken",                         # while
    "mak", "mek",                  # infinitive
]

def word_features(sent, i):
    form  = sent[i]["form"]
    lower = form.lower()
    n     = len(sent)

    f = {
        "bias":       1.0,
        "form":       lower,
        "form[:2]":   lower[:2],
        "form[:3]":   lower[:3],
        "form[-2:]":  lower[-2:],
        "form[-3:]":  lower[-3:],
        "form[-4:]":  lower[-4:],
        "upper":      form[0].isupper(),
        "is_digit":   form.isdigit(),
        "has_digit":  any(c.isdigit() for c in form),
        "length_bin": min(len(form), 10),
        "has_apos":   "'" in form,
    }

    # Turkish-specific suffix features
    for suf in TURKISH_SUFFIXES:
        if lower.endswith(suf):
            f[f"suf_{suf}"] = True

    # Vowel harmony indicator (front/back)
    back_vowels  = set("aıouAIOU")
    front_vowels = set("eiüöEİÜÖ")
    vowels_in_word = [c for c in form if c in back_vowels | front_vowels]
    if vowels_in_word:
        last_v = vowels_in_word[-1]
        f["vowel_harmony"] = "back" if last_v in back_vowels else "front"

    # Context: previous token
    if i > 0:
        prev = sent[i - 1]["form"].lower()
        f["prev_form"]     = prev
        f["prev_form[-2:]"] = prev[-2:]
        f["prev_form[-3:]"] = prev[-3:]
    else:
        f["BOS"] = True

    # Context: next token
    if i < n - 1:
        nxt = sent[i + 1]["form"].lower()
        f["next_form"]     = nxt
        f["next_form[:2]"] = nxt[:2]
        f["next_form[:3]"] = nxt[:3]
    else:
        f["EOS"] = True

    # Two tokens back
    if i > 1:
        f["prev2_form"] = sent[i - 2]["form"].lower()
    # Two tokens ahead
    if i < n - 2:
        f["next2_form"] = sent[i + 2]["form"].lower()

    return f


def sent_to_features(sent):
    return [word_features(sent, i) for i in range(len(sent))]

def sent_to_labels(sent):
    return [get_label(tok) for tok in sent]


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train(train_sents, dev_sents=None):
    X_train = [sent_to_features(s) for s in train_sents]
    y_train = [sent_to_labels(s)   for s in train_sents]

    crf = sklearn_crfsuite.CRF(
        algorithm="lbfgs",
        c1=0.05,
        c2=0.05,
        max_iterations=200,
        all_possible_transitions=True,
    )
    crf.fit(X_train, y_train)
    return crf


# ---------------------------------------------------------------------------
# Evaluation helpers
# ---------------------------------------------------------------------------

def flat_labels(crf, X_list, y_list):
    y_pred = crf.predict(X_list)
    y_true_flat = [lbl for seq in y_list  for lbl in seq]
    y_pred_flat = [lbl for seq in y_pred  for lbl in seq]
    return y_true_flat, y_pred_flat, y_pred


def plot_confusion_matrix(y_true, y_pred, labels, output_path):
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    fig, ax = plt.subplots(figsize=(12, 10))
    im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
    fig.colorbar(im, ax=ax)
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(labels, fontsize=8)
    thresh = cm.max() / 2.0
    for i in range(len(labels)):
        for j in range(len(labels)):
            if cm[i, j] > 0:
                ax.text(j, i, str(cm[i, j]),
                        ha="center", va="center",
                        color="white" if cm[i, j] > thresh else "black",
                        fontsize=7)
    ax.set_ylabel("True label")
    ax.set_xlabel("Predicted label")
    ax.set_title("Confusion Matrix — Morphological Disambiguation (UPOS)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"  confusion matrix saved: {output_path}")


def evaluate(crf, sents, split_name="test"):
    X = [sent_to_features(s) for s in sents]
    y = [sent_to_labels(s)   for s in sents]

    y_true_flat, y_pred_flat, _ = flat_labels(crf, X, y)

    labels = sorted(set(y_true_flat))
    acc    = accuracy_score(y_true_flat, y_pred_flat)

    print(f"\n{'='*60}")
    print(f"  Evaluation on {split_name} set  ({len(sents)} sentences)")
    print(f"{'='*60}")
    print(f"  Accuracy: {acc:.4f}  ({acc*100:.2f}%)\n")
    print(classification_report(y_true_flat, y_pred_flat,
                                 labels=labels, digits=4, zero_division=0))

    out_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(out_dir, exist_ok=True)
    plot_confusion_matrix(y_true_flat, y_pred_flat, labels,
                          os.path.join(out_dir, f"confusion_matrix_{split_name}.png"))

    # Per-class bar chart (F1)
    from sklearn.metrics import f1_score
    f1_per_class = f1_score(y_true_flat, y_pred_flat,
                             labels=labels, average=None, zero_division=0)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(labels, f1_per_class, color="steelblue")
    ax.set_xlabel("UPOS tag")
    ax.set_ylabel("F1 score")
    ax.set_title(f"Per-class F1 — {split_name}")
    ax.set_ylim(0, 1.05)
    for idx, v in enumerate(f1_per_class):
        ax.text(idx, v + 0.01, f"{v:.2f}", ha="center", fontsize=7)
    plt.tight_layout()
    f1_path = os.path.join(out_dir, f"f1_per_class_{split_name}.png")
    plt.savefig(f1_path, dpi=150)
    plt.close()
    print(f"  F1 bar chart saved:     {f1_path}")

    return acc


# ---------------------------------------------------------------------------
# CoNLL-U output
# ---------------------------------------------------------------------------

CONLLU_HEADER = """\
# text = {text}
# model = CRF Morphological Disambiguator
"""

def predict_and_write_conllu(crf, sents, output_path):
    """Write predictions in CoNLL-U format to output_path."""
    X = [sent_to_features(s) for s in sents]
    y_pred = crf.predict(X)

    with open(output_path, "w", encoding="utf-8") as out:
        for sent, pred_labels in zip(sents, y_pred):
            text = " ".join(t["form"] for t in sent)
            out.write(CONLLU_HEADER.format(text=text))
            for i, (tok, pred) in enumerate(zip(sent, pred_labels), start=1):
                true_label = tok["upos"]
                correct    = "yes" if pred == true_label else "no"
                out.write(
                    f"{i}\t{tok['form']}\t{tok['lemma']}\t"
                    f"{pred}\t{pred}\t_\t_\t_\t_\t"
                    f"GoldUPOS={true_label}|Match={correct}\n"
                )
            out.write("\n")
    print(f"  CoNLL-U predictions:  {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Turkish Morphological Disambiguation — CRF"
    )
    parser.add_argument("--train",  default=os.path.join(DATA_DIR, "tr_imst-ud-train.conllu"))
    parser.add_argument("--dev",    default=os.path.join(DATA_DIR, "tr_imst-ud-dev.conllu"))
    parser.add_argument("--test",   default=os.path.join(DATA_DIR, "tr_imst-ud-test.conllu"))
    parser.add_argument("--output", default=os.path.join(os.path.dirname(__file__),
                                                          "results", "predictions.conllu"))
    args = parser.parse_args()

    for path in (args.train, args.dev, args.test):
        if not os.path.exists(path):
            print(f"ERROR: file not found: {path}")
            print("Run  python download_data.py  first.")
            return

    print("Loading data...")
    train_sents = load_conllu(args.train)
    dev_sents   = load_conllu(args.dev)
    test_sents  = load_conllu(args.test)
    print(f"  train: {len(train_sents)} sentences")
    print(f"  dev:   {len(dev_sents)} sentences")
    print(f"  test:  {len(test_sents)} sentences")

    print("\nTraining CRF...")
    crf = train(train_sents, dev_sents)
    print("  done.")

    evaluate(crf, dev_sents,  split_name="dev")
    evaluate(crf, test_sents, split_name="test")

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    predict_and_write_conllu(crf, test_sents[:50], args.output)

    model_dir = os.path.join(os.path.dirname(__file__), "model")
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "crf_model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(crf, f)
    print(f"  model saved: {model_path}")

    print("\nAll done. Results saved to ./results/")


def load_model():
    model_path = os.path.join(os.path.dirname(__file__), "model", "crf_model.pkl")
    if not os.path.exists(model_path):
        return None
    with open(model_path, "rb") as f:
        return pickle.load(f)


def predict_sentence(crf, text):
    """Predict POS tags for a raw whitespace-tokenized Turkish sentence."""
    tokens = text.strip().split()
    if not tokens:
        return []
    sent = [{"form": t, "lemma": "_", "upos": "_", "feats": {}} for t in tokens]
    features = sent_to_features(sent)
    labels   = crf.predict([features])[0]
    marginals = crf.predict_marginals([features])[0]
    return [
        {
            "id":         i + 1,
            "form":       t,
            "pos":        lbl,
            "confidence": round(marginals[i].get(lbl, 0.0) * 100, 1),
        }
        for i, (t, lbl) in enumerate(zip(tokens, labels))
    ]


if __name__ == "__main__":
    main()
