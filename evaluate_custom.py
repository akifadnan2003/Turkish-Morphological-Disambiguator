"""
Evaluate the trained CRF model on manually annotated sentences.

This script:
1. Loads my_annotations.conllu (25 hand-annotated Turkish sentences)
2. Runs CRF model predictions on each sentence
3. Compares predictions vs manual gold labels
4. Prints a detailed token-by-token comparison
5. Reports accuracy and per-class F1 on the custom set

Run: python -X utf8 evaluate_custom.py
"""

import os
import conllu
from morpho_disambig import load_model, sent_to_features, sent_to_labels
from sklearn.metrics import classification_report, accuracy_score

CUSTOM_FILE = os.path.join(os.path.dirname(__file__), "my_annotations.conllu")

# ANSI colours for terminal output
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


def load_custom(path):
    sentences = []
    with open(path, encoding="utf-8") as f:
        for sent in conllu.parse_incr(f):
            tokens = []
            for tok in sent:
                if not isinstance(tok["id"], int):
                    continue
                tokens.append({
                    "form":  tok["form"],
                    "lemma": tok["lemma"] if tok["lemma"] else "_",
                    "upos":  tok["upos"]  if tok["upos"]  else "_",
                    "feats": tok["feats"] if tok["feats"] else {},
                })
            if tokens:
                meta = dict(sent.metadata)
                sentences.append({
                    "tokens":      tokens,
                    "text":        meta.get("text", ""),
                    "translation": meta.get("translation", ""),
                    "sent_id":     meta.get("sent_id", ""),
                    "domain":      meta.get("domain", ""),
                })
    return sentences


def print_sentence_result(sent_data, pred_labels):
    tokens     = sent_data["tokens"]
    gold_labels = [t["upos"] for t in tokens]

    correct = sum(p == g for p, g in zip(pred_labels, gold_labels))
    total   = len(tokens)

    print(f"\n  {BOLD}{sent_data['sent_id']}{RESET}  [{sent_data['domain']}]")
    print(f"  {CYAN}{sent_data['text']}{RESET}")
    print(f"  ({sent_data['translation']})")
    print()
    print(f"  {'TOKEN':<20} {'GOLD':<10} {'PREDICTED':<10} {'MATCH'}")
    print(f"  {'-'*20} {'-'*10} {'-'*10} {'-'*5}")

    for tok, gold, pred in zip(tokens, gold_labels, pred_labels):
        match = pred == gold
        color = GREEN if match else RED
        mark  = "OK" if match else "X"
        print(f"  {tok['form']:<20} {gold:<10} {color}{pred:<10}{RESET} {color}{mark}{RESET}")

    pct = correct / total * 100
    color = GREEN if pct == 100 else (YELLOW if pct >= 80 else RED)
    print(f"\n  Sentence accuracy: {color}{correct}/{total}  ({pct:.0f}%){RESET}")


def main():
    print(f"\n{BOLD}{'='*60}")
    print("  Evaluation on Manual Annotations")
    print(f"  File: my_annotations.conllu")
    print(f"{'='*60}{RESET}")

    crf = load_model()
    if crf is None:
        print(f"{RED}ERROR: No trained model found.")
        print("Run: python -X utf8 morpho_disambig.py{RESET}")
        return

    sentences = load_custom(CUSTOM_FILE)
    print(f"\n  Loaded {len(sentences)} manually annotated sentences.\n")

    all_gold = []
    all_pred = []

    for sent_data in sentences:
        tokens   = sent_data["tokens"]
        features = sent_to_features(tokens)
        pred     = crf.predict([features])[0]
        gold     = [t["upos"] for t in tokens]

        all_gold.extend(gold)
        all_pred.extend(pred)

        print_sentence_result(sent_data, pred)

    # ── Overall results ──────────────────────────────────────
    acc = accuracy_score(all_gold, all_pred)

    print(f"\n\n{BOLD}{'='*60}")
    print("  OVERALL RESULTS — Custom Annotation Set")
    print(f"{'='*60}{RESET}")
    print(f"\n  Total tokens : {len(all_gold)}")
    print(f"  Correct      : {sum(p==g for p,g in zip(all_pred,all_gold))}")
    color = GREEN if acc >= 0.90 else YELLOW
    print(f"  Accuracy     : {color}{BOLD}{acc*100:.2f}%{RESET}")

    print(f"\n{BOLD}  Per-class Results:{RESET}\n")
    labels = sorted(set(all_gold))
    print(classification_report(
        all_gold, all_pred,
        labels=labels,
        digits=4,
        zero_division=0
    ))

    # ── Save comparison to file ───────────────────────────────
    out_path = os.path.join(os.path.dirname(__file__), "results", "custom_evaluation.txt")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("Manual Annotation Evaluation\n")
        f.write("="*60 + "\n")
        f.write(f"Total tokens : {len(all_gold)}\n")
        f.write(f"Accuracy     : {acc*100:.2f}%\n\n")
        f.write(classification_report(all_gold, all_pred,
                                       labels=labels, digits=4, zero_division=0))
        f.write("\n\nToken-by-token:\n")
        for sent_data in sentences:
            tokens     = sent_data["tokens"]
            features   = sent_to_features(tokens)
            pred       = crf.predict([features])[0]
            gold       = [t["upos"] for t in tokens]
            f.write(f"\n# {sent_data['sent_id']}: {sent_data['text']}\n")
            for tok, g, p in zip(tokens, gold, pred):
                match = "OK" if p == g else "WRONG"
                f.write(f"  {tok['form']:<20} gold={g:<10} pred={p:<10} {match}\n")

    print(f"\n  Full results saved: results/custom_evaluation.txt\n")


if __name__ == "__main__":
    main()
