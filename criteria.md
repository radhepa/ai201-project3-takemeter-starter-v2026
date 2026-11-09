# Acceptance criteria — TakeMeter

Five criteria that say what "working" means for this classifier, written in
unit 5 **before** anything was trained.

**All five are yours this time.** None are given. You've had two projects of
practice.

An acceptance criterion names a number. *"The model is accurate"* is an
opinion. *"Every label has an F1 of at least 0.60 on the held-out set"* is a
criterion.

Under each, write a sentence or two on **why that number**. A reason that says
something about your data or your taxonomy earns credit — *"I picked 0.60 F1
for `reaction` because it's my smallest label and I only have about 50
examples of it"*. A reason that could be attached to any project does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

Not numbers that sound impressive. Three labels means a coin-flip guesser gets
about 33%, so a target of 0.40 is barely a target. Your number should sit
somewhere you'd honestly call useful.

**Cover at least three of these five areas.** They're here as prompts, not as a
form to fill in — a criterion that fits none of them is fine if it names a
number.

| Area | A question it could answer |
|---|---|
| Overall accuracy | How often does it need to be right to be worth using? |
| Per-label performance | Is one label allowed to be much worse than the others? |
| Balance | How lopsided can your label counts get before it's a problem? |
| Consistency | If someone else labelled the same posts, how often should you agree? |
| Confidence | Should a confident prediction be right more often than an unsure one? |

Two things worth knowing before you pick numbers, because both will affect
whether you hit them:

- **Your smallest label will have the jumpiest score.** If a label has 50
  examples, about 8 land in the test split. An F1 computed on 8 examples moves
  a lot between seeds. A target for that label should be looser than one for
  your biggest label, and saying so is a good reason.
- **Unit 6 tests across three seeds, and the target has to hold across all
  three.** A target of 0.65 against results of 0.71, 0.62, 0.68 is a **miss**.
  Pick with that in mind — it is stricter than it first sounds.

---

## 1. Overall accuracy of at least 0.65 on the held-out test split

**Measurement:** `accuracy` in `results.json`: the share of test-split posts
whose predicted label equals the label in `labels.csv`.

**Target:** ≥ 0.65 on seed 42 (unit 5), and on every one of seeds 42, 7 and
2024 in `results_three_seeds_before.json` (unit 6).

**Why this target:** `hot_take` is 118 of my 220 posts (53.6%), so a model that
answers `hot_take` every time already scores about 0.54. With a 33-post test
split, 0.65 means about 22 right instead of the trivial guesser's 18. That is
the smallest gap I'd call a real signal rather than a lucky split, and I expect
it to be hard to hold across three seeds with only ~154 training posts.

**How to verify:** run notebook sections 1–5 (and section 6 in unit 6), then
read `accuracy` from `results.json` / each entry of
`results_three_seeds_before.json`.

---

## 2. Macro F1 of at least 0.55 on the held-out test split

**Measurement:** `f1_macro` in `results.json`: the unweighted mean of the three
per-label F1 scores.

**Target:** ≥ 0.55 on seed 42, and on all three seeds in unit 6.

**Why this target:** accuracy alone rewards leaning on `hot_take`. The
always-`hot_take` guesser gets F1 ≈ 0.70 on `hot_take` and 0 on the other two,
a macro F1 of about 0.23. Macro F1 weights my two smaller labels as much as the
big one, so 0.55 can only be reached if the model genuinely separates
`informed` and `chatter` from `hot_take`, not just by predicting the majority.

**How to verify:** read `f1_macro` from `results.json` /
`results_three_seeds_before.json`.

---

## 3. `informed` and `chatter` each reach an F1 of at least 0.45

**Measurement:** `per_label.informed.f1` and `per_label.chatter.f1` in
`results.json`.

**Target:** both ≥ 0.45 on seed 42, and on all three seeds in unit 6.

**Why this target:** these are my two smallest labels (56 and 46 posts), so
each has only about 8 and 7 posts in the test split, and one post changing
sides moves F1 by roughly 0.1. That's why this bar is looser than the macro F1
target. But 0.45 still requires the model to find about half of each label
with reasonable precision. `informed` vs `hot_take` is my hardest boundary, so
`informed` is the label most likely to be swallowed by `hot_take`, and this
criterion is the one that would catch it.

**How to verify:** read `per_label` → `f1` for both labels from `results.json`
(and per seed from `results_three_seeds_before.json`).

---

## 4. No label above 60% and no label below 20% of `labels.csv`

**Measurement:** each label's row count divided by the total rows in
`labels.csv`.

**Target:** largest share ≤ 0.60 and smallest share ≥ 0.20.

**Why this target:** the brief's cap is 70%, but at 70% a majority guesser
already gets 0.70 accuracy and criterion 1 stops meaning anything. At 60% it
stays meaningfully below my 0.65 accuracy target. The 20% floor is what keeps
roughly 7 or more posts of every label in a 15% test split of 220 rows
(0.20 × 220 × 0.15 ≈ 6.6), the minimum for an F1 that isn't pure noise. This is
a dataset criterion and I wrote it knowing the current counts (53.6% / 25.5% /
20.9%). It's here as a guardrail: any relabelling or added data in unit 6 has
to keep it.

**How to verify:** `python validate_labels.py` prints each label's share and
fails if either bound is broken; notebook section 2 prints the same counts.

---

## 5. The most-confident third is at least 0.15 more accurate than the least-confident third

**Measurement:** `confidence.accuracy_most_confident_third` minus
`confidence.accuracy_least_confident_third` in `results.json` (each third is
11 posts of the 33-post test split).

**Target:** difference ≥ 0.15 on seed 42, and on all three seeds in unit 6.

**Why this target:** the useful way to deploy a classifier like this on HN is
to trust its confident calls and send the unsure ones to a person. That only
works if confidence tracks correctness. With 11 posts per third, 0.15 is
about two more correct posts in the confident third. Anything smaller is
within the noise of a single post, and a model that is equally right whether
sure or unsure has a confidence score I can't use.

**How to verify:** read the two `confidence` fields from `results.json` (and
per seed from `results_three_seeds_before.json`) and subtract.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 6 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Every label performs acceptably

         The model performs well on all labels.

         **Why this target:** ...

         > **Revised in unit 6:** Every label has an F1 of at least 0.60 on
         > the held-out set.
         >
         > **Why revised:** "performs well" gave me nothing to check. I
         > couldn't produce a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "Overall accuracy of at least 0.65" → "at least 0.55", because
            0.65 turned out to be optimistic for 200 examples.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
