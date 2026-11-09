# Boundary tests — `informed` vs `hot_take`

Written to stress the draft taxonomy **before** the full dataset was labelled.

> ⚠️ The eight posts below are **original test sentences written for this
> exercise**, in the style of Hacker News comments. They are *not* real posts
> and none of them are in `labels.csv`. Every row in `labels.csv` is a real,
> public HN comment from `data/raw_hn_posts.csv`.

`informed` vs `hot_take` is the hardest boundary because both labels make a
claim about the topic, and HN comments almost always *sound* reasoned. The
question is never "is it smart?" but "is there anything here I could check, and
does the point rest on it?"

## The eight tests

| # | Test post (original, not real) | Pull toward `informed` | Pull toward `hot_take` | Call | Why |
|---|---|---|---|---|---|
| 1 | "Postgres has been faster than MySQL for every workload I've thrown at it for a decade." | First-hand | No workload, no number, no version | `hot_take` | First-hand but general. "Every workload for a decade" is not a concrete thing the poster did that a reader could check. |
| 2 | "Python 3.12 removed `distutils`, so any old `setup.py` that imports it breaks on upgrade." | Version + named module | It's a short assertion with no link | `informed` | The main point *is* a specific, checkable fact. A claim that is itself checkable counts as support. |
| 3 | "Rust is about 30% slower to compile than Go, which is why nobody serious uses it for microservices." | A number | Number is unsourced and decorates a verdict | `hot_take` | The 30% has no source, and the actual point ("nobody serious uses it") is a sweeping verdict the number doesn't carry. |
| 4 | "We moved our CI from GitHub Actions to self-hosted runners last spring and our monthly bill dropped from about $4k to $900." | Concrete first-hand account with figures | Figures can't be audited by a reader | `informed` | A specific thing the poster did, with specifics. That is the "concrete account of something the poster did" clause. |
| 5 | "Anyone who's read the GDPR knows this is illegal." | Names a law | Doesn't say which article or why | `hot_take` | Name-dropping a source isn't support unless the post says what in it backs the claim. |
| 6 | "Article 17 of the GDPR gives users a right to erasure, so keeping the backups forever is a problem." | Names the specific article and what it says | It's still the poster's reading of the law | `informed` | The checkable detail (Art. 17, right to erasure) carries the conclusion. Removing it collapses the point. |
| 7 | "If a server costs $10k and saves two engineers an hour a day, it pays for itself in a month." | Numbers | Numbers are hypothetical | `hot_take` | Hypothetical numbers describe a thought experiment, not something a reader can verify. |
| 8 | "Here's the benchmark: https://example.com/bench — Bun wins on cold start, loses on sustained throughput." | A link | Could be a bare-link drop | `informed` | The link is offered as evidence *for* the stated claim. A link to the product itself, offered with a verdict and no reason, would be `hot_take`. |

## What the tests changed

1. **Test 2 exposed a gap.** The draft definition said `informed` "backs" a
   claim with something checkable, which read as if a bare checkable fact (no
   separate opinion) didn't qualify. Added: *a post whose main point is itself a
   specific, checkable fact is `informed`.*
2. **Tests 5 and 6 sharpened "named source".** Naming a law, product, or paper
   only counts when the post says *what* in it supports the point.
3. **Tests 1 and 4 sharpened "first-hand".** First-hand experience counts only
   when it is concrete (what was done, with what, and what happened), not "I've
   used it for years and it's better".
4. **Labelling the real data exposed a second gap, at `hot_take` vs `chatter`:**
   praise posts like "DDO website is refreshingly clean… thanks for sharing".
   Rule added: thanks and personal feelings alone are `chatter`, but once a post
   asserts something general about the topic (a design verdict, a
   recommendation) it is `hot_take`.

## Final decision rule (applied to every row, in order)

1. **Does the post assert anything about the topic** — a fact, opinion, verdict,
   prediction or recommendation? Rhetorical questions and sarcasm that imply a
   verdict count as assertions. Genuine questions, thanks, personal feelings or
   status updates, jokes with no point, bare links, and remarks about the
   conversation or other commenters do not.
   **No → `chatter`.**
2. **Does it contain a specific detail a reader could check** — a number, date
   or version, a named source/law/product *and what it says*, a link offered as
   evidence, or a concrete first-hand account of what the poster did or saw —
   **and would the main point collapse if that detail were removed?**
   **Yes → `informed`. No → `hot_take`.**

## A real borderline post

From `labels.csv` (0-based row index 63):

> I'm not them, but I'd say Conficker and those other windows file share worms were worse. They went after peoples personal computers rather than web servers so affected people less aware of how to deal with it. It's a little early to tell what this php one will all affect though.

- **Competing labels:** `hot_take` (a comparative verdict, "worse", opened with
  "I'd say") vs `informed` (names a specific worm and a checkable fact about
  it).
- **Rule applied:** step 2. The checkable detail is that Conficker spread
  through Windows file shares on personal computers, and the "worse" verdict
  rests entirely on that. Remove it and there is no argument left.
- **Final label:** `informed`.
