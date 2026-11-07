# Milestone 1 — community and candidate distinctions

**Community:** Hacker News comments (news.ycombinator.com). Public, no login,
huge volume, and no single show or release, so there are no spoilers.
Collected with `collect_hn.py` through the public Algolia HN API: up to 5
comments from each of 80 popular stories from the last 60 days, 400 in all,
saved in `data/raw_hn_posts.csv` (text, story title, permalink).

Reddit was the first idea, but it returns 403 to scripted requests from this
machine, and copy-pasting 200 posts by hand wasn't worth it when HN has an
open API.

## Candidate distinctions seen in the text

1. **Some comments give the reader something to check, most don't.** A number,
   a version, a link that backs the point, or a concrete thing the poster did
   ("I ran a battery of tests against every available Opus…", "Kimi 3.1 is a
   2.8T parameter model… you need 1.4TB of VRAM"). Others make the same kind
   of claim with nothing behind it ("Vanilla CSS is unusually hard for what it
   provides").
2. **Some comments argue about the topic, some only talk about the
   conversation.** "Pal, I'm not going to keep discussing this…", "Who are you
   quoting?", or "fwiw the post mentioned Shopify and Spotify" carry no claim
   about the subject at all.
3. **Questions vs claims.** Real questions ("Is auto mode only in the IDE?")
   sit apart from rhetorical ones ("Why isn't this a 5-alarm fire?"), which are
   really claims.
4. **Reasoning without facts is common.** A long chain of logic with no
   checkable anchor ("If you're talking cattle, you're talking a different
   time of history…"). It reads more serious than a one-liner, but it gives
   the reader nothing more to check. This is the hardest line to draw.
