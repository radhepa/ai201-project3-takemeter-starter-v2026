"""Check labels.csv before training. Exits non-zero on any problem.

    python validate_labels.py

Checks: >= 200 rows, exact columns text,label,note, no empty text/label/note,
only labels from the notebook's LABELS, no duplicate posts, no label above 70%
(the brief) and criterion 4's 60% / 20% bounds, and that every post is a real
comment from data/raw_hn_posts.csv.
"""
import ast
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent


def notebook_labels():
    """The LABELS list as written in takemeter.ipynb, section 2."""
    nb = json.loads((ROOT / "takemeter.ipynb").read_text(encoding="utf-8"))
    for cell in nb["cells"]:
        for line in "".join(cell["source"]).splitlines():
            if line.startswith("LABELS ="):
                return ast.literal_eval(line.split("=", 1)[1].split("#")[0].strip())
    raise SystemExit("LABELS not found in takemeter.ipynb")


def check(df, labels, raw_texts):
    problems = []
    if list(df.columns) != ["text", "label", "note"]:
        problems.append(f"columns are {list(df.columns)}, expected ['text', 'label', 'note']")
        return problems
    if len(df) < 200:
        problems.append(f"{len(df)} rows, need at least 200")
    for col in ("text", "label", "note"):
        empty = (df[col].fillna("").astype(str).str.strip() == "").sum()
        if empty:
            problems.append(f"{empty} rows with empty {col}")
    unknown = set(df["label"].dropna()) - set(labels)
    if unknown:
        problems.append(f"labels not in notebook LABELS {labels}: {sorted(unknown)}")
    missing = set(labels) - set(df["label"])
    if missing:
        problems.append(f"notebook LABELS never used in CSV: {sorted(missing)}")
    dups = df["text"].duplicated().sum()
    if dups:
        problems.append(f"{dups} duplicate posts")
    shares = df["label"].value_counts(normalize=True)
    if shares.max() > 0.70:
        problems.append(f"'{shares.idxmax()}' is {shares.max():.1%}, above the brief's 70% cap")
    if shares.max() > 0.60 or shares.min() < 0.20:
        problems.append(f"criterion 4 broken: shares {shares.round(3).to_dict()}")
    not_raw = (~df["text"].isin(raw_texts)).sum()
    if not_raw:
        problems.append(f"{not_raw} posts not found verbatim in data/raw_hn_posts.csv")
    return problems


def main():
    df = pd.read_csv(ROOT / "labels.csv", encoding="utf-8", keep_default_na=False)
    raw = set(pd.read_csv(ROOT / "data" / "raw_hn_posts.csv", encoding="utf-8")["text"])
    labels = notebook_labels()
    problems = check(df, labels, raw)

    print(f"{len(df)} rows, notebook LABELS = {labels}")
    for label, n in df["label"].value_counts().items():
        print(f"  {label:<10} {n:>4}  {n / len(df):.1%}")
    for p in problems:
        print(f"[FAIL] {p}")
    if problems:
        sys.exit(1)
    print("[PASS] all checks")


if __name__ == "__main__":
    # Self-check: the checker must catch a bad label, a duplicate and a missing column.
    _bad = pd.DataFrame({"text": ["a", "a"], "label": ["x", "x"], "note": ["n", "n"]})
    _p = " ".join(check(_bad, ["y"], {"a"}))
    assert "duplicate" in _p and "not in notebook LABELS" in _p and "200" in _p, _p
    assert "columns" in check(_bad.drop(columns="note"), ["y"], {"a"})[0]
    main()
