"""
Flask web app for Turkish Morphological Disambiguation demo.
Run: python app.py
Then open: http://127.0.0.1:5000
"""

import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from morpho_disambig import load_model, predict_sentence

app = Flask(__name__)
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

@app.route("/results/<path:filename>")
def results_file(filename):
    return send_from_directory(RESULTS_DIR, filename)

# Load trained CRF model at startup
crf = load_model()

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


@app.route("/")
def index():
    model_ready = crf is not None
    return render_template(
        "index.html",
        model_ready=model_ready,
        stats=STATS,
        examples=EXAMPLE_SENTENCES,
    )


@app.route("/predict", methods=["POST"])
def predict():
    if crf is None:
        return jsonify({"error": "Model not loaded. Run python morpho_disambig.py first."}), 503

    data = request.get_json()
    text = (data or {}).get("text", "").strip()
    if not text:
        return jsonify({"error": "Empty input."}), 400

    tokens = predict_sentence(crf, text)

    # Build CoNLL-U lines for display
    conllu_lines = [f"# text = {text}"]
    for tok in tokens:
        conllu_lines.append(
            f"{tok['id']}\t{tok['form']}\t_\t{tok['pos']}\t{tok['pos']}\t_\t_\t_\t_\t_"
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
