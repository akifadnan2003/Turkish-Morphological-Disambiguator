"""
Flask web app for Turkish Morphological Disambiguation demo.
Run: python app.py
Then open: http://127.0.0.1:5000
"""

import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from morpho_disambig import load_model, predict_sentence, load_conllu, build_feats_dict

app = Flask(__name__)
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

@app.route("/results/<path:filename>")
def results_file(filename):
    return send_from_directory(RESULTS_DIR, filename)

# Load trained CRF model at startup
crf = load_model()

# Stage 2: FEATS dictionary built from training corpus
_train_path = os.path.join(os.path.dirname(__file__), "data", "tr_imst-ud-train.conllu")
FEATS_DICT = {}
if crf is not None and os.path.exists(_train_path):
    try:
        FEATS_DICT = build_feats_dict(load_conllu(_train_path))
    except Exception:
        FEATS_DICT = {}


def load_annotations():
    """Parse my_annotations.conllu and run model predictions for comparison display."""
    ann_path = os.path.join(os.path.dirname(__file__), "my_annotations.conllu")
    if not os.path.exists(ann_path) or crf is None:
        return []
    try:
        import conllu as conllu_lib
        from morpho_disambig import sent_to_features
        sentences = []
        with open(ann_path, encoding="utf-8") as f:
            for sent in conllu_lib.parse_incr(f):
                sent_id   = sent.metadata.get("sent_id", "")
                text      = sent.metadata.get("text", "")
                trans     = sent.metadata.get("translation", "")
                domain    = sent.metadata.get("domain", "general")
                raw_toks  = [t for t in sent if isinstance(t["id"], int)]
                if not raw_toks:
                    continue
                tok_dicts = [{"form": t["form"], "lemma": t["lemma"] or "_",
                              "upos": t["upos"] or "_", "feats": t["feats"] or {}}
                             for t in raw_toks]
                preds = crf.predict([sent_to_features(tok_dicts)])[0]
                tokens = []
                for t, p in zip(raw_toks, preds):
                    gold_upos  = t["upos"] or "_"
                    gold_feats = "|".join(f"{k}={v}" for k, v in (t["feats"] or {}).items()) or "_"
                    pred_feats = FEATS_DICT.get((t["form"].lower(), p), "_")
                    tokens.append({
                        "form":       t["form"],
                        "lemma":      t["lemma"] or "_",
                        "gold":       gold_upos,
                        "gold_feats": gold_feats,
                        "pred":       p,
                        "pred_feats": pred_feats,
                        "match":      gold_upos == p,
                    })
                correct = sum(1 for t in tokens if t["match"])
                sentences.append({
                    "id":          sent_id,
                    "text":        text,
                    "translation": trans,
                    "domain":      domain,
                    "tokens":      tokens,
                    "correct":     correct,
                    "total":       len(tokens),
                    "pct":         round(correct / len(tokens) * 100) if tokens else 0,
                })
        return sentences
    except Exception:
        return []


ANNOTATIONS = load_annotations()

STATS = {
    "train_sentences": 3435,
    "test_sentences":  1100,
    "test_accuracy":   90.93,
    "weighted_f1":     90.80,
    "algorithm":       "Conditional Random Fields (CRF)",
    "dataset":         "UD Turkish-IMST Treebank",
}

EXAMPLE_SENTENCES = [
    "Dün akşam toplantıdan erken çıktım .",
    "Hocasının önerdiği makaleyi kütüphanede dikkatlice okudum .",
    "Ankara Türkiye'nin başkentidir .",
    "Güzel bir gün geçirdik .",
    "Öğrenciler sınava hazırlanıyor .",
]

PER_CLASS_METRICS = {
    "test": [
        {"tag": "PUNCT",  "precision": 99.9,  "recall": 100.0, "f1": 99.95, "support": 1933},
        {"tag": "AUX",    "precision": 94.4,  "recall": 96.2,  "f1": 95.3,  "support": 211},
        {"tag": "CCONJ",  "precision": 96.4,  "recall": 96.4,  "f1": 96.4,  "support": 356},
        {"tag": "VERB",   "precision": 93.8,  "recall": 94.1,  "f1": 93.9,  "support": 1928},
        {"tag": "PRON",   "precision": 94.5,  "recall": 92.9,  "f1": 93.7,  "support": 464},
        {"tag": "ADP",    "precision": 95.6,  "recall": 90.5,  "f1": 92.9,  "support": 357},
        {"tag": "DET",    "precision": 84.2,  "recall": 96.2,  "f1": 89.8,  "support": 344},
        {"tag": "NOUN",   "precision": 84.3,  "recall": 92.5,  "f1": 88.2,  "support": 2430},
        {"tag": "ADV",    "precision": 88.8,  "recall": 77.0,  "f1": 82.5,  "support": 461},
        {"tag": "NUM",    "precision": 90.7,  "recall": 71.4,  "f1": 79.9,  "support": 192},
        {"tag": "ADJ",    "precision": 84.9,  "recall": 75.8,  "f1": 80.1,  "support": 960},
        {"tag": "PROPN",  "precision": 83.3,  "recall": 70.9,  "f1": 76.6,  "support": 374},
    ],
    "custom": [
        {"tag": "PUNCT",  "precision": 100.0, "recall": 100.0, "f1": 100.0, "support": 25},
        {"tag": "ADP",    "precision": 100.0, "recall": 100.0, "f1": 100.0, "support": 2},
        {"tag": "CCONJ",  "precision": 100.0, "recall": 100.0, "f1": 100.0, "support": 1},
        {"tag": "DET",    "precision": 100.0, "recall": 100.0, "f1": 100.0, "support": 11},
        {"tag": "PRON",   "precision": 100.0, "recall": 100.0, "f1": 100.0, "support": 2},
        {"tag": "VERB",   "precision": 93.8,  "recall": 100.0, "f1": 96.8,  "support": 30},
        {"tag": "NUM",    "precision": 75.0,  "recall": 100.0, "f1": 85.7,  "support": 3},
        {"tag": "PROPN",  "precision": 75.0,  "recall": 100.0, "f1": 85.7,  "support": 6},
        {"tag": "NOUN",   "precision": 85.7,  "recall": 82.8,  "f1": 84.2,  "support": 58},
        {"tag": "ADJ",    "precision": 63.6,  "recall": 77.8,  "f1": 70.0,  "support": 18},
        {"tag": "ADV",    "precision": 100.0, "recall": 46.2,  "f1": 63.2,  "support": 13},
    ],
}


@app.route("/")
def index():
    model_ready = crf is not None
    return render_template(
        "index.html",
        model_ready=model_ready,
        stats=STATS,
        examples=EXAMPLE_SENTENCES,
        per_class=PER_CLASS_METRICS,
        annotations=ANNOTATIONS,
    )


@app.route("/predict", methods=["POST"])
def predict():
    if crf is None:
        return jsonify({"error": "Model not loaded. Run python morpho_disambig.py first."}), 503

    data = request.get_json()
    text = (data or {}).get("text", "").strip()
    if not text:
        return jsonify({"error": "Empty input."}), 400

    tokens = predict_sentence(crf, text, feats_dict=FEATS_DICT)

    # Build CoNLL-U lines for display
    conllu_lines = [f"# text = {text}"]
    for tok in tokens:
        conllu_lines.append(
            f"{tok['id']}\t{tok['form']}\t_\t{tok['pos']}\t{tok['pos']}\t{tok.get('feats','_')}\t_\t_\t_\t_"
        )

    return jsonify({
        "tokens":  tokens,
        "conllu":  "\n".join(conllu_lines),
    })


if __name__ == "__main__":
    if crf is None:
        print("=" * 60)
        print("  ERROR: No trained model found.")
        print("  Run this first:")
        print("    python -X utf8 morpho_disambig.py")
        print("=" * 60)
    else:
        print("Model loaded. Starting server at http://127.0.0.1:5000")
        app.run(debug=True)
