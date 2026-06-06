"""
Download Turkish UD Treebank (UD_Turkish-IMST) from GitHub.
Run once before training.
"""
import urllib.request
import os

BASE = "https://raw.githubusercontent.com/UniversalDependencies/UD_Turkish-IMST/master"
FILES = {
    "tr_imst-ud-train.conllu": f"{BASE}/tr_imst-ud-train.conllu",
    "tr_imst-ud-dev.conllu":   f"{BASE}/tr_imst-ud-dev.conllu",
    "tr_imst-ud-test.conllu":  f"{BASE}/tr_imst-ud-test.conllu",
}

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

for filename, url in FILES.items():
    dest = os.path.join(DATA_DIR, filename)
    if os.path.exists(dest):
        print(f"  already exists: {filename}")
        continue
    print(f"  downloading {filename} ...", end=" ", flush=True)
    urllib.request.urlretrieve(url, dest)
    print("done")

print("Data ready in ./data/")
