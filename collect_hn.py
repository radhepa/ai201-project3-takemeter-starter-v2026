"""Collect public Hacker News comments for labelling.

Uses the public Algolia HN API (no login, no key). Pulls comments from
high-traffic stories and writes data/raw_hn_posts.csv with the full comment
text, so labels.csv can be built from it. Run once:

    python collect_hn.py
"""
import csv
import html
import json
import random
import re
import time
import urllib.request

API = "https://hn.algolia.com/api/v1/"
PER_STORY = 5          # few per thread, so no single discussion dominates
STORIES = 80
MIN_LEN, MAX_LEN = 60, 1500   # skip one-word replies and essays


def get(path):
    with urllib.request.urlopen(API + path, timeout=30) as r:
        return json.load(r)


def clean(raw):
    text = re.sub(r"<p>", " ", raw or "")
    text = re.sub(r"<[^>]+>", "", text)          # drop links/italics markup, keep their text
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def main():
    rng = random.Random(159)
    # Popular stories from the last ~60 days, so threads are full but not stale.
    since = int(time.time()) - 60 * 86400
    stories = get(f"search?tags=story&numericFilters=points>300,created_at_i>{since}"
                  f"&hitsPerPage={STORIES}")["hits"]
    rows, seen = [], set()
    for s in stories:
        hits = get(f"search?tags=comment,story_{s['objectID']}&hitsPerPage=100")["hits"]
        pool = []
        for h in hits:
            t = clean(h.get("comment_text"))
            if MIN_LEN <= len(t) <= MAX_LEN and t not in seen and not t.startswith(">"):
                pool.append((t, h["objectID"]))
        for t, cid in rng.sample(pool, min(PER_STORY, len(pool))):
            seen.add(t)
            rows.append({"text": t, "story": s["title"],
                         "url": f"https://news.ycombinator.com/item?id={cid}"})
        time.sleep(0.2)   # be polite to the API
    rng.shuffle(rows)
    with open("data/raw_hn_posts.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["text", "story", "url"])
        w.writeheader()
        w.writerows(rows)
    assert len(rows) == len({r["text"] for r in rows}), "duplicate posts slipped through"
    print(f"{len(rows)} comments from {len(stories)} stories -> data/raw_hn_posts.csv")


if __name__ == "__main__":
    main()
