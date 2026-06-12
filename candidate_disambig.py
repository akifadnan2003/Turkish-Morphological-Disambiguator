"""
Candidate-based Morphological Disambiguation — simulates the Zemberek pipeline.

How the pipeline works (as described in the project spec):
  1. For each word, generate all possible morphological analyses (candidates).
     In the real pipeline this is done by Zemberek. Here we build a candidate
     dictionary from the training corpus — every UPOS+FEATS combination seen
     for a word in training becomes a candidate.
  2. The CRF model scores all candidates in context and selects the best one.

This script:
  - Builds the candidate dictionary from the training data
  - Demonstrates the disambiguation pipeline on example sentences
  - Prints the candidates for each word and the selected analysis

Run:
    python -X utf8 candidate_disambig.py
"""

import os
import pickle
from collections import defaultdict

from morpho_disambig import (
    load_conllu, sent_to_features,
    get_upos, get_feats, get_label,
)

DATA_DIR  = os.path.join(os.path.dirname(__file__), "data")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "crf_model.pkl")
TRAIN_PATH = os.path.join(DATA_DIR, "tr_imst-ud-train.conllu")


# ---------------------------------------------------------------------------
# Step 1 — Build candidate dictionary from training corpus
# ---------------------------------------------------------------------------

def build_candidate_dict(train_sents):
    """
    For every surface form seen in training, collect all distinct
    UPOS+FEATS labels it ever carried.  This is the corpus-based
    substitute for Zemberek's morphological analyser.
    """
    candidates = defaultdict(set)
    for sent in train_sents:
        for tok in sent:
            label = get_label(tok)
            candidates[tok["form"].lower()].add(label)
            # Also index by lowercased form without case sensitivity
    # Convert sets to sorted lists for deterministic output
    return {form: sorted(lbls) for form, lbls in candidates.items()}


# ---------------------------------------------------------------------------
# Step 2 — CRF disambiguates among candidates
# ---------------------------------------------------------------------------

def disambiguate(crf, candidate_dict, text):
    """
    Given a raw sentence, produce the disambiguation result:
      - For each word, list all morphological candidates
      - Use the CRF to select the most likely analysis in context
    Returns a list of token result dicts.
    """
    tokens = text.strip().split()
    if not tokens:
        return []

    # Build sent structure (upos/feats unknown at this point)
    sent = [{"form": t, "lemma": "_", "upos": "_", "feats": {}} for t in tokens]
    features  = sent_to_features(sent)
    labels    = crf.predict([features])[0]
    marginals = crf.predict_marginals([features])[0]

    results = []
    for i, (tok, selected_label) in enumerate(zip(tokens, labels)):
        # Candidates from dictionary (what Zemberek would provide)
        cands = candidate_dict.get(tok.lower(), [selected_label])
        if selected_label not in cands:
            cands = sorted(set(cands) | {selected_label})

        # Score each candidate with the CRF marginals
        scored = sorted(
            [(lbl, marginals[i].get(lbl, 0.0)) for lbl in cands],
            key=lambda x: x[1], reverse=True
        )

        results.append({
            "form":       tok,
            "candidates": scored,          # [(label, prob), ...]
            "selected":   selected_label,
            "pos":        get_upos(selected_label),
            "feats":      get_feats(selected_label),
            "confidence": round(marginals[i].get(selected_label, 0.0) * 100, 1),
        })
    return results


# ---------------------------------------------------------------------------
# Display helper
# ---------------------------------------------------------------------------

def print_result(result):
    SEP = "─" * 72
    print(SEP)
    print(f"  {'TOKEN':<20} {'SELECTED ANALYSIS':<35} {'CONF':>6}")
    print(SEP)
    for tok in result:
        sel = tok["selected"]
        print(f"  {tok['form']:<20} {sel:<35} {tok['confidence']:>5.1f}%")
        if len(tok["candidates"]) > 1:
            for lbl, prob in tok["candidates"]:
                marker = "  ◀ selected" if lbl == sel else ""
                print(f"    {'':20}  {lbl:<33} {prob*100:>5.1f}%{marker}")
    print(SEP)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not os.path.exists(MODEL_PATH):
        print("ERROR: No trained model found. Run python -X utf8 morpho_disambig.py first.")
        raise SystemExit(1)

    if not os.path.exists(TRAIN_PATH):
        print("ERROR: Training data not found. Run python download_data.py first.")
        raise SystemExit(1)

    print("Loading training corpus to build candidate dictionary...")
    train_sents = load_conllu(TRAIN_PATH)
    cand_dict   = build_candidate_dict(train_sents)
    print(f"  Candidate dictionary: {len(cand_dict):,} unique surface forms")
    print(f"  Avg candidates/word:  {sum(len(v) for v in cand_dict.values())/len(cand_dict):.1f}\n")

    with open(MODEL_PATH, "rb") as f:
        crf = pickle.load(f)

    DEMO_SENTENCES = [
        "Dün akşam toplantıdan erken çıktım .",
        "Hocasının önerdiği makaleyi kütüphanede dikkatlice okudum .",
        "Öğrenciler sınava bugün hazırlanıyor .",
        "Türkiye'nin başkenti Ankara'dır .",
    ]

    for sentence in DEMO_SENTENCES:
        print(f"\nInput: {sentence}")
        result = disambiguate(crf, cand_dict, sentence)
        print_result(result)
