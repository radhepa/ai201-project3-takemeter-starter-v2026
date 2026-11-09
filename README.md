# TakeMeter

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, the
> notebook, the baseline, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> head -5 data/practice_labels.csv     # the shape your labels.csv needs
> ```
>
> Then open `takemeter.ipynb` **in this folder** — in VS Code, or with
> `jupyter notebook` if you prefer. Pick the kernel: the `.venv` inside this
> project. Run section 1, which reports the hardware you'll be training on.
> Everything else waits until you have data.
>
> Nothing to upload, nothing to connect, no accounts and no keys. The notebook
> runs on your machine and writes next to your code.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     Unit 5 asks for the first five sections. Unit 6 adds the five below them.

     Everything is pasted as TEXT. No screenshots, no images.

     ⚠️ The confusion matrix especially. The notebook prints one as a markdown
     table, ready to copy. A screenshot of a matrix earns nothing. Paste the
     table.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 5 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Your community, and what your classifier sorts posts into. Three or four
     sentences. -->

TakeMeter sorts Hacker News comments by what they give the reader. An
`informed` comment backs its point with something you could go and check. A
`hot_take` makes a claim with nothing behind it. `chatter` makes no claim about
the topic at all. HN looks serious on the surface, so the useful question isn't
"is this smart-sounding?" but "could I verify anything here?"

The distinction matters because almost every HN comment *sounds* reasoned. A
reader skimming a 300-comment thread wants the handful that give them a version
number, a benchmark, a statute or a first-hand account, and the label is about
exactly that, not about whether the poster is right or polite. Hacker News was
chosen over a Minecraft community because it is fully public with an open API
(Reddit returned 403 to scripted requests from this machine), it has no
spoilers, and its comments mix technical evidence, confident opinion and
off-topic banter in roughly the proportions a three-way split needs. The
community research and the four candidate distinctions I saw before settling
on these labels are in [notes.md](notes.md).

---

## Label Taxonomy

<!-- Each label: a one-sentence definition and two real examples from your
     reading. Then your decision rule for the hardest boundary.

     The decision rule is worth a point on its own and it's the thing most
     people leave out. Every taxonomy has a hardest boundary. Name yours. -->

### `informed`

**Definition:** Makes a claim and backs it with something a reader could
check (a number, a version, a named source or link that supports the point, or
a concrete account of something the poster did or saw), or its main point is
itself a specific, checkable fact.

**Example 1:**
> Kimi 3.1 is a 2.8T parameter model. You can't run it on a 12GB VRAM GPU. You need 1.4TB of VRAM just to store the parameters.

**Example 2:**
> There's also the basic problem that an attacker who can serve you a falsified A record for a domain can also serve you a falsified CAA record. This is why CAs are required to use "multiple perspectives" when validating domain ownership before issuing certs, whereas web clients generally don't have access to redundant infrastructure like that.

### `hot_take`

**Definition:** States an opinion, verdict, prediction, recommendation or
general assertion about the topic without offering anything a reader could
check.

**Example 1:**
> Vanilla CSS (rule engine based on files) is unusually hard for what it provides. It is quite bad abstraction. Aim of many styling solutions is to completely remove brittle CSS files .

**Example 2:**
> yeah anyone wise migrated away from PHP ages ago. The fact it got lipstick on back with PHP7 doesn't make it a well designed programming language. At least in my experience the vast majority of PHP websites nowadays are old abandoned PHP5 projects, which aren't much worse than just slopping a rewrite in something else

### `chatter`

**Definition:** Makes no assertion about the topic: a genuine question, a
joke, thanks, a personal feeling or status update, a bare link, or a remark
about the conversation itself.

**Example 1:**
> Reminds me of "foreign" and "[Applause]" frequently appearing on YT auto-subtitles.

**Example 2:**
> Is auto mode only in the IDE? I'm not seeing it in the CLI on my end, version 1.2.14.

### The hardest boundary

**Which two labels:** `informed` vs `hot_take`

**The decision rule I used every time:** two questions, in order.

1. **Does the post assert anything about the topic** (a fact, opinion,
   verdict, prediction or recommendation)? Rhetorical questions and sarcasm
   that imply a verdict count. Genuine questions, thanks, personal feelings or
   status updates, pointless jokes, bare links and remarks about the
   conversation do not. **No → `chatter`.**
2. **Is there a specific detail a reader could check** (a number, date or
   version; a named source, law or product *and what it says*; a link offered
   as evidence; a concrete first-hand account) **and would the main point
   collapse without it?** **Yes → `informed`. No → `hot_take`.**

Reasoning on its own is not support. A detail that only decorates a verdict
(a product name dropped, an unsourced "80–90% of people", a hypothetical
number) leaves the post a `hot_take`, however heated or calm the tone.

The rule was stress-tested on eight original borderline sentences (not real
posts, not in the dataset) before the full labelling pass; the tests, what they
changed, and one real borderline post are in
[boundary_tests.md](boundary_tests.md).


---

## The Dataset

<!-- Where you collected from, how you labelled, your counts, and three hard
     cases. -->

**Where the posts came from:** Hacker News comments, pulled with
`collect_hn.py` from the public Algolia HN API: up to 5 per story from 80
popular stories (300+ points, last 60 days), 400 in total, in
`data/raw_hn_posts.csv`. Of those, 220 are in `labels.csv`. Whole comments,
with HTML tags removed and paragraph breaks joined with a space.

**How I labelled them:** every label in `labels.csv` was produced by an AI
model (Claude), not by a person, and the `note` column says so on every row.

1. 200 rows were pre-labelled by Claude under the draft definitions.
2. After the taxonomy was finalized (see [boundary_tests.md](boundary_tests.md)),
   Claude did a second pass over all 200 under the final two-step rule. It
   kept 195 and changed 5 (3 `chatter`→`hot_take`, 1 `hot_take`→`chatter`,
   1 `informed`→`chatter`), with the reason written in each row's note.
3. 20 rows had been set aside for unaided human ("cold") labelling. That human
   pass did not happen. Claude labelled them under the final rule instead, and
   their notes say *this is NOT a human label*. No row is marked `cold`.

Nothing here has been checked by a human yet, so treat the labels as one
annotator's consistent application of the written rule, not as ground truth.

`python validate_labels.py` checks the file before training: ≥ 200 rows, exact
columns `text,label,note`, no blank text/label/note, only the notebook's
`LABELS`, no duplicate posts, no label over 70% (and criterion 4's 20–60%
band), and that every post appears verbatim in `data/raw_hn_posts.csv`. It
passes.

**Counts per label:**

| Label | Count | Share |
|---|---|---|
| `hot_take` | 118 | 53.6% |
| `informed` | 56 | 25.5% |
| `chatter` | 46 | 20.9% |
| **Total** | **220** | 100% |

**Three hard cases**

**1.** `informed` vs `hot_take`: heated tone, real figures
> *The post:* "Lol, your claim is "the numbers look bad for the Democrats, but they never explicitly said they want the country to be invaded with illegals, they just did it" That's the most brainwashed thing I've read all day Don't trust what the politicians say, look at what they do: - Illegal migrants under Biden: +7.3 million net illegal migrants - During Trump's first term? It's -34,000 (yes, that's a negative number) - How about the tally for Obama's second term? That's +493,000 net illegal migrants As shown by those numbers, border enforcement does not need special legislation. If the people in power want to curb it, they can do so. If they want to turn on the tap of illegals, they can. And the Democrats did turn up the tap to the max."
>
> *Could have been:* `hot_take` (insulting, partisan, ends on a sweeping verdict) or `informed`.
>
> *I chose `informed`, because:* rule step 2 ignores tone. The post gives three specific, checkable figures and its conclusion ("enforcement does not need special legislation") is argued *from* them. Remove the numbers and nothing is left. Hard because everything about the register says hot take, and a reader is tempted to label the politics instead of the structure.

**2.** `informed` vs `hot_take`: a number that isn't evidence
> *The post:* "Humans are bound by communication overhead and non-market-based incentives. Adding 3x engineers does not do anything. On an average workplace, you have 80-90% of dead weight who shuffle pointless information around and play social games to keep their children fed. Giving the 10% access to these tools is a crazy value multiplier, because they can run at lightning speed with their mental models and the right incentives for the company."
>
> *Could have been:* `informed` (it has percentages) or `hot_take`.
>
> *I chose `hot_take`, because:* "80-90% dead weight" has no source and no way to check it. It is an estimate dressed as a statistic, and it decorates the verdict rather than supporting it. Hard because a keyword reading ("has a number → informed") gets it wrong, and the model may well learn exactly that shortcut.

**3.** `chatter` vs `hot_take`: praise that turns into a verdict
> *The post:* "DDO website is refreshingly clean. Very reminiscent of early 2000's era, it just gets out of your way inviting you to browse through all the content. I wish more websites retained such functional design. The amount of visual stimulus thrown at you these days can be quite overbearing. While I just glanced through pentagram's site, I found myself spending a lot of time going through DDO's pages. They seem to have some really solid articles too. Thanks for sharing!"
>
> *Could have been:* `chatter` (a friendly thank-you, which is how it was first pre-labelled) or `hot_take`.
>
> *I chose `hot_take`, because:* step 1 asks whether the post asserts anything about the topic. "Thanks for sharing" doesn't, but "the amount of visual stimulus thrown at you these days can be quite overbearing" is a general design verdict with nothing checkable behind it. This case is what added the praise/verdict line to the rule. Hard because the tone is pure chatter.

**Known limitations**

- **Single, non-human annotator.** All labels are AI-produced; there is no
  inter-annotator agreement measured on these 220. Unit 6's `agreement.py`
  against the staff set is the first real consistency check.
- **Lopsided toward `hot_take` (53.6%).** That is honest to HN, but it means
  the trivial "always `hot_take`" guesser scores ~0.54 accuracy.
- **Small test split.** 15% of 220 is 33 posts, about 7–8 each for `informed`
  and `chatter`, so their F1 moves ~0.1 per post.
- **Time and topic window.** Comments come from 80 popular stories over 60
  days, mostly AI, security and US politics; other HN topics are under-represented.
- **Text cleaning.** HTML tags were stripped and paragraph breaks joined with
  a space, so quoted replies (`>`) and lists run together.

---

## The Training Run

<!-- Your starting model, your settings, and anything you changed and why. -->

**Base model:** `distilbert-base-uncased` (DistilBERT, 6 layers, with a
freshly initialized 3-way classification head), fine-tuned with the Hugging
Face `Trainer` in `takemeter.ipynb`.

**Device:** `cpu` (torch `2.15.0+cpu`). The laptop has an NVIDIA RTX 3060, but
the project's pinned `.venv` has the CPU-only PyTorch wheel, and `test.py` and
section 1 both report `cpu`. I kept the pinned environment rather than swap in
a CUDA build; on 154 training posts the run takes a few minutes on CPU.

**Settings:**

| Setting | Value |
|---|---|
| Epochs | 3 |
| Learning rate | 2e-5 |
| Batch size | 16 |
| Max tokens per post | 128 |
| Seed | 42 |
| Split | 70 / 15 / 15, stratified, done by the notebook |

**Anything I changed from the defaults, and why:** nothing. All hyperparameters
are the notebook defaults. The only notebook edits are `LABELS =
["informed", "hot_take", "chatter"]` and the `NAME`/`EMAIL` labels. Sections
1–5 were executed in order from the project `.venv` (via `nbclient`, so the
outputs are saved in the committed notebook); sections 6–7 were not run.

**Split sizes:** train 154 · val 33 · test 33.

| Label | Train | Val | Test |
|---|---|---|---|
| `informed` | 40 | 8 | 8 |
| `hot_take` | 82 | 18 | 18 |
| `chatter` | 32 | 7 | 7 |

`chatter` has only 7 test posts and `informed` 8, so each of their F1 scores
moves by roughly 0.1 when a single post changes. `test_split.csv` holds the 33
held-out posts; none of them appear in the train or validation splits
(re-derived from the same seed and checked).

**Training log** (from the notebook output):

| Epoch | Training loss | Validation loss | Val accuracy | Val macro F1 |
|---|---|---|---|---|
| 1 | 1.0427 | 0.9682 | 0.545 | 0.235 |
| 2 | 0.9169 | 0.9185 | 0.576 | 0.314 |
| 3 | 0.8651 | 0.9039 | 0.576 | 0.312 |

**Held-out test results** (`results.json`, seed 42, 33 posts):

| Measure | Value |
|---|---|
| Accuracy | 0.606 |
| Macro F1 | 0.378 |

| Label | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| `informed` | 1.000 | 0.250 | 0.400 | 8 |
| `hot_take` | 0.581 | 1.000 | 0.735 | 18 |
| `chatter` | 0.000 | 0.000 | 0.000 | 7 |

Confidence: the most-confident third (11 posts) was 0.818 accurate and the
least-confident third 0.545.

What this run shows, read plainly: the model predicts `hot_take` for 31 of 33
posts. Every real `chatter` post and 6 of 8 `informed` posts were called
`hot_take`. Loss is still falling at epoch 3, so three epochs × ~10 steps on
154 posts looks like too little training to pull the model away from the
majority label. Checking these numbers against `criteria.md` (MET / MISSED
across three seeds) is unit 6's job; the criteria were committed before this
run and are not changed here.



---

## How I Used AI

<!-- Two specific moments — what you asked, what came back, what you changed.

     ⚠️ Plus disclosure of any pre-labelling. If you had a model pre-label a
     batch and then read and corrected every one, say that. It's an allowed
     workflow and disclosing it costs you nothing. Not disclosing it is the
     problem. -->

This project was carried out end to end with Claude (Claude Code) doing the
work under my direction: the HN collection script, the taxonomy, the boundary
tests, the criteria, every label, the validation script, running the notebook
and this write-up.

**Moment 1: boundary testing the taxonomy**

- *What I asked for:* stress-test the draft `informed` / `hot_take` line before
  the full labelling pass.
- *What came back:* eight original borderline sentences (in
  [boundary_tests.md](boundary_tests.md), clearly marked as not real posts).
  Test 2 ("Python 3.12 removed `distutils`…") had no separate opinion at all,
  and the draft definition didn't clearly cover it.
- *What changed:* the `informed` definition gained "or its main point is itself
  a specific, checkable fact", and "named source" now requires saying *what*
  the source says (tests 5 vs 6).

**Moment 2: second-pass review of the pre-labels**

- *What I asked for:* re-check all 200 pre-labelled rows against the final
  two-step rule.
- *What came back:* five changes. The informative one was the praise post in
  hard case 3: the draft treated praise as `chatter`, but under step 1 a post
  that asserts a general verdict is `hot_take`, and a row like "I'm no stranger
  to doing talks, it's on my to-do-list" had been pre-labelled `informed` with
  nothing about the topic in it.
- *What changed:* the praise/verdict line was written into the rule and the
  five rows were relabelled, each with its reason in the note.

**Pre-labelling disclosure:** all 220 labels are AI-generated (Claude). 200 were
AI pre-labels re-checked by a second AI pass; the 20 rows reserved for human
cold labelling were also labelled by AI. No label has been reviewed by a human,
and none is presented as one. The `note` column records which path each row took.

<!-- ═══════════════════════ UNIT 6 — THE TEST ═══════════════════════

     Don't fill these in during unit 5.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Baseline vs. Trained

<!-- Both models on the same posts. `python baseline.py --trained results.json`
     prints this table for you. -->

| Measure | Baseline | Trained | Difference |
|---|---|---|---|
| Overall accuracy |  |  |  |
| Macro F1 |  |  |  |
| F1 — `label_one` |  |  |  |
| F1 — `label_two` |  |  |  |

**What I predicted before I looked:**
<!-- Milestone 1 asks you to write this BEFORE seeing the trained numbers. A
     prediction made afterwards isn't one. -->

**What the gap actually means:**
<!-- If the baseline matched your trained model, your fine-tuning added
     nothing — and that is a real finding, not a failure. Say it plainly. -->



---

## Run Log — Before

<!-- Five criteria across three seeds. The notebook's section 6 prints the
     spread table; the Target and Verdict columns are yours. -->

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

### Confusion matrix

<!-- ⚠️ TYPED AS A MARKDOWN TABLE. The notebook prints one ready to paste.
     An image of a matrix earns nothing. -->

| true \ predicted |  |  |  |
|---|---|---|---|
| **** |  |  |  |
| **** |  |  |  |
| **** |  |  |  |

**My biggest off-diagonal number, and what it means:**
<!-- Not "the model made mistakes" — WHICH boundary it didn't learn, and which
     direction. "7 real analysis posts were called hot_take and only 3 went the
     other way" is a direction, not just an error rate. -->



---

## Verdicts and Diagnoses

<!-- MET or MISSED against LAST UNIT's target. The target has to hold across
     all three seeds, not turn up sometimes. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**

<!-- For each miss: the cause, and how you know. The four common causes are:
     too few examples for a label, a boundary you applied inconsistently, a
     genuinely hard label pair, and a task the model can't reach from this
     much data.

     ⚠️ Use your agreement report as evidence. It is the only instrument you
     have that can tell a LABELLING problem from a MODEL problem, and this
     section is graded on whether you used it that way. -->



---

## Agreement Report

<!-- Your rate against the staff set, and every disagreement adjudicated.

     Remember you labelled these 30 under the STAFF taxonomy in
     data/staff_taxonomy.md, not your own — so every argument below is made
     from those definitions and those decision rules. -->

**Agreement rate:** ___ / 30 = ___%

<!-- Nobody grades this number. A 60% who argues every disagreement from the
     stated rules beats a 95% who wrote "staff was right" nine times. Several
     of the 30 were chosen because they're genuinely ambiguous — you should be
     winning some of these. -->

**Disagreements**

<!-- Three lines each: the post, both labels, and who you think is right and
     why — grounded in the staff definitions you were both applying.

     Then sort each into one of three piles:
       (a) the rule covered it and I applied it loosely → a consistency problem
       (b) the rule genuinely doesn't say               → a gap in the definitions
       (c) the rule is ambiguous here and my reading is defensible → argue it.
           This is a legitimate win.

     Pile (a) is the one that matters most for your diagnosis: if you applied a
     written rule two different ways on 30 posts, that is direct evidence about
     what you did across your own 200. -->

**1.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**2.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**What the pattern in my disagreements tells me:**



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Run Log — After

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it didn't, say so. Relabelling that didn't help is a genuinely
     interesting result and earns full credit. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped. -->



**The gap between what I meant my labels to capture and what the model
learned:**
<!-- Two sentences. Your confusion matrix is the evidence. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 5

       [ ] criteria.md has five numbered criteria, each naming a NUMBER
       [ ] Each has a reason underneath tied to your data or taxonomy
       [ ] labels.csv: at least 150 rows, text/label/note, ONE file not split
       [ ] No label above 70%
       [ ] All five unit 5 sections have real content
       [ ] Label Taxonomy includes the decision rule for your hardest boundary
       [ ] The Dataset includes three hard cases
       [ ] results.json and test_split.csv committed (the notebook does this)
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 6

       [ ] Baseline vs. Trained table, with your prediction written beforehand
       [ ] Run Log — Before, five criteria across three seeds
       [ ] Confusion matrix TYPED AS A MARKDOWN TABLE
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, using the agreement report as evidence
       [ ] Agreement Report with every disagreement adjudicated
       [ ] One improvement, with Run Log — After
       [ ] What's Still Broken
       [ ] results_three_seeds_before.json, results_three_seeds_after.json,
           baseline_results.json and
           agreement_results.json committed
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
