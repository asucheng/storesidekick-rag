# Evaluation results

Cases and expected answers: [`questions.md`](questions.md). Raw answers and retrieved chunks: [`runs/`](runs/).

- **Retrieval OK:** a chunk containing the expected fact was among the chunks returned by `search_handbook`.
- **Pass/fail** is judged against the rules and expected answer, so the same kind of mistake always gets the same grade. **Severity** (high / low) is recorded separately for failures: how much harm the mistake could cause a customer. It decides what to fix first, not whether something counts as a failure.
- **Error type:** *retrieval* means the right chunk wasn't returned. *Generation* means it was returned but the answer or citation was wrong. *Agent* means the model's own decision (what to search, whether to clarify) caused the problem.

## Run 1 — `c800-o150` (chunk 800, overlap 150, top k 4) — 2026-10-21

| ID | Type | Retrieved (expected fact at position) | Retrieval OK | Answer OK | Refused correctly | Memory OK | Error type | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | direct | §5 Shipping (1st) | Y | Y | n.a. | n.a. | — | "$35 or more", cites Section 5. |
| D2 | direct | §9 Pack Points (1st, 2nd) | Y | Y | n.a. | n.a. | — | 100 points = $5, cites Section 9. |
| D3 | direct | §6 Returns (4th) | Y | Y | n.a. | n.a. | — | 30 days of delivery. The right chunk only ranked 4th of 4. |
| P1 | paraphrase | §3 Tug Titan facts (1st), Twisty limit (2nd) | Y | **N** | n.a. | n.a. | generation | Names the right toy (Tug Titan) but never says it comes in **XL** or that XL is the size for dogs over 30 kg. Instead it says the toy "is suitable for dogs over 30 kg", which could lead a customer to buy the Medium. Also recommends the Ultra Chew Ring, which isn't a rope toy, so it goes beyond the question. Pass bar: state the XL variant for dogs over 30 kg and stick to rope toys. The facts were retrieved but scattered: the Tug Titan's facts sat in a chunk without its name that ended with the Twisty Rope Ring heading. |
| P2 | paraphrase | §6 "Used toys" (2nd) | Y | Y | n.a. | n.a. | — | Correctly says used toys can't be returned unless defective. |
| A1 | ambiguous | §5 Shipping only | n.a. | **N** | n.a. | n.a. | agent | Assumed "it" meant shipping (searched "shipping time") instead of asking or covering refunds too. The shipping facts it gave are correct, but a question this vague should be clarified. The narrowing happened at the search step, before any evidence, so neither retrieval nor generation could recover. |
| U1 | unanswerable | (packaging, unrelated product chunks) | n.a. | Y | Y | n.a. | — | "I can't find that in the handbook" plus the contact email. |
| U2 | unanswerable | (Laser Lite Pointer, etc.) | n.a. | Y | Y | n.a. | — | Didn't confuse it with the similar-sounding Laser Lite Pointer. |
| F1 | follow-up | none on turn 2 (answered from turn-1 context) | n.a. | Y | n.a. | Y | generation (citation) | Resolved "it" to the Whisker Wand and gave the 12-week limit, but cited **Section 6** instead of Section 3. |

**Score:** 7/9 answers correct. 0 retrieval failures. 2 generation/agent failures (P1, A1), plus a wrong citation on F1.

**Pattern:** wrong section numbers (F1 here, and the Iron Jaw Bone smoke test, which also cited Section 6). Chunks from the catalogue rarely contain their section heading (`3. Product Catalogue` appears only once, at the start of the catalogue), so the model can't see which section a product chunk came from and guesses. P1's missing "XL" has a related cause: the Tug Titan's facts sit in a chunk that ends with the *next* product's heading (see [`../notes/chunks-c800-o150.md`](../notes/chunks-c800-o150.md)).

### Added after run 1: harder paraphrases (also on `c800-o150`)

Run 1 had no retrieval failures, so two cases worded unlike the handbook were added. "Wreck" never appears in the handbook. Raw output: [`runs/c800-o150-P3-P4.json`](runs/c800-o150-P3-P4.json).

| ID | Type | Retrieved (expected fact at position) | Retrieval OK | Answer OK | Error type | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| P3 | paraphrase | Iron Jaw Bone (1st) | Y | Y | generation (citation) | Right bone and facts, but cites **"Sections 1, 7"**. The product is in Section 3. |
| P4 | paraphrase | §4 order changes (1st) | Y | Y | — | Within 2 hours; cites Section 4. |

Retrieval still didn't fail. The process called for adding harder paraphrases *until one fails*. I stopped after two, because the failures that did occur pointed clearly at chunk content (attribution) rather than ranking, and the improvement targets that. Retrieval robustness beyond these cases is untested (see Limits below). The recurring problem is **wrong section citations** (F1, P3, and the Iron Jaw smoke test) and **facts separated from their product name** (P1), both traced to chunks that don't carry their own context.

## The improvement: heading-aware chunks

**Change (retrieval only):** a new ingest workflow, [`workflows/ingest-headings.json`](../workflows/ingest-headings.json):
1. It extracts the PDF text.
2. A Code node splits it at every section heading and product heading.
3. It starts each chunk with a breadcrumb, e.g. `Section 3. Product Catalogue > Tug Titan Rope (WW-D-101)`, and caps chunks at 1,000 characters.

It writes to a new namespace, `hdr-v1`, so run 1's chunks stay intact for comparison. The chat workflow, prompt, model and top k are unchanged; only `search_handbook`'s namespace points at `hdr-v1`.

**Checked before running the eval** ([`check_chunks.py`](check_chunks.py)): 44 chunks, every one with a breadcrumb, and every product in its own chunk with its facts. On `c800-o150` the same check fails: 0/34 chunks had a breadcrumb, and the Tug Titan, Twisty Rope Ring and Whisker Wand facts were never in the same chunk as their names.

## Run 2 — `hdr-v1` (heading-aware chunks, top k 4) — 2026-10-21

The first attempt at D1–D3 reached n8n before the updated workflow had loaded, and retrieved the old chunks. Those three were re-run, and the table uses the re-run.

| ID | Type | Retrieved (expected fact at position) | Retrieval OK | Answer OK | Citation OK | Refused correctly | Memory OK | Error type | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | direct | §5 (1st) | Y | Y | Y | n.a. | n.a. | — | |
| D2 | direct | §9 (1st) | Y | Y | Y | n.a. | n.a. | — | |
| D3 | direct | §6 (**2nd**, was 4th) | Y | Y | Y | n.a. | n.a. | — | Ranks higher now. |
| P1 | paraphrase | Tug Titan (1st), Twisty (2nd), Ultra Chew Ring (4th) | Y | **N** | Y | n.a. | n.a. | generation | **Now says XL is for dogs over 30 kg, and gives the XL price ($26).** Still recommends the Ultra Chew Ring and now calls it a "rope toy", which it isn't. |
| P2 | paraphrase | §6 (2nd) | Y | Y | Y | n.a. | n.a. | — | |
| P3 | paraphrase | Iron Jaw Bone (1st) | Y | Y | **Y** (was N) | n.a. | n.a. | — | Cites Sections 3 and 7, both correct. |
| P4 | paraphrase | §4 (1st) | Y | Y | Y | n.a. | n.a. | — | |
| A1 | ambiguous | §5 only | n.a. | **N** | Y | n.a. | n.a. | agent | Unchanged: still assumes shipping. A chunking change can't fix a search-query decision. |
| U1 | unanswerable | (unrelated chunks) | n.a. | Y | n.a. | Y | n.a. | — | |
| U2 | unanswerable | Laser Lite Pointer, etc. | n.a. | Y | n.a. | Y | n.a. | — | |
| F1 | follow-up | none on turn 2 | n.a. | Y | **Y** (was N) | n.a. | Y | — | Cites Section 3, correct. |

## Comparison

| | Run 1 `c800-o150` | Run 2 `hdr-v1` |
| --- | --- | --- |
| Retrieval failures | 0 / 7 cases with an expected chunk | 0 / 7 |
| Answers correct | 9 / 11 | 9 / 11 |
| Section citations correct | 7 / 9 | **9 / 9** |
| Chunks with section/product context | 0 / 34 | 44 / 44 |

**What changed:** every wrong citation from run 1 is fixed (P3, F1), and P1 now gives the key sizing fact (XL for dogs over 30 kg, $26), which run 1 left out. D3's evidence ranks higher (4th → 2nd). Retrieval was already finding the right area. The improvement is that each chunk now *says what it is*, so the model attributes facts correctly.

**What didn't change, and why:** two failures remain, and neither is a retrieval problem:
- **P1** still adds the Ultra Chew Ring, now even calling it a rope toy. That's a generation error, and the next fix would be in the prompt ("recommend only products that match what was asked").
- **A1** is an agent error: it narrows "how long does it take?" to shipping before searching. The fix would be the prompt's ambiguity rule ("if it's unclear what 'it' means, ask before searching").

Both are deliberately left for a separate change, so this comparison measures only the retrieval change.

## Run 3 — `hdr-v1` + prompt v2 (generation/agent fix) — 2026-10-21

**Change (prompt only):** same chunks and namespace as run 2. Two rules in the system prompt were written generally, naming no product or topic from the test:
- **Rule 5 (was: "ask or answer each meaning"):** if it's unclear what the user means ("it" or "that" with nothing earlier to refer to, or a question that fits several topics or products), don't search and don't guess; ask one short clarifying question first.
- **New rule 7:** only recommend products that match what was asked for (kind of product, animal, size or other requirement). Don't add products of a different kind. Say so if nothing matches.

**Held-out cases:** P5 and A2 were added *before* the prompt change, to check the rules generalize beyond the two cases they target. Their baseline on the run 2 prompt is in [`runs/hdr-v1-A2-P5.json`](runs/hdr-v1-A2-P5.json): P5 passed, and A2 failed the same way as A1 (it picked three products instead of asking, and missed the machine-washable Tug Titan).

| ID | Type | Retrieval OK | Answer OK | Citation OK | Refused / clarified | Memory OK | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | direct | Y | Y | Y | n.a. | n.a. | |
| D2 | direct | Y | Y | Y | n.a. | n.a. | |
| D3 | direct | Y | Y | Y | n.a. | n.a. | |
| P1 | paraphrase | Y | **N** | Y | n.a. | n.a. | Fixed what failed before: only the Tug Titan Rope, XL for dogs over 30 kg, $26, no other product types. **New failure (generation, unsupported claim; severity high: the customer gets a false expectation of the product):** it ends "This toy is designed for strong chewers and should hold up well for your dog." The dog "shreds everything", which is the handbook's rating-4 description ("dogs that destroy most toys"). The Tug Titan is rated 3, and the handbook says "No toy is indestructible". The reassurance is invented. |
| P2 | paraphrase | Y | Y | Y | n.a. | n.a. | |
| P3 | paraphrase | Y | Y | Y | n.a. | n.a. | |
| P4 | paraphrase | Y | Y | Y | n.a. | n.a. | |
| P5 | paraphrase (held out) | Y | Y | Y | n.a. | n.a. | Only the Bounce Buddy Ball. |
| A1 | ambiguous | n.a. | **Y** (was N) | n.a. | clarified | n.a. | "Are you referring to shipping times, order processing, or something else?" No search before asking. |
| A2 | ambiguous (held out) | n.a. | **Y** (was N in baseline) | n.a. | clarified | n.a. | "Could you please clarify which product you are referring to?" |
| U1 | unanswerable | n.a. | Y | n.a. | refused | n.a. | |
| U2 | unanswerable | n.a. | Y | n.a. | refused | n.a. | |
| F1 | follow-up | n.a. | Y | Y | n.a. | Y | **No over-triggering:** "it" refers to the earlier message, so the bot answered directly instead of asking. |

**Score:** 12/13 answers correct; all citations correct. P1's earlier failure (missing XL, off-question product) is fixed, but the answer adds an unsupported durability promise.

## Summary across runs

| | Run 1 | Run 2 (retrieval fix) | Run 3 (prompt fix) |
| --- | --- | --- | --- |
| Change | baseline, chunk 800 / overlap 150 | heading-aware chunks | stricter ambiguity rule + "recommend only what was asked" |
| Answers correct (original 11 cases) | 9 / 11 | 9 / 11 | **10 / 11** |
| Citations correct | 7 / 9 | 9 / 9 | 9 / 9 |
| Held-out cases (P5, A2) | — | 1 / 2 (baseline) | **2 / 2** |

Each change fixed the kind of error it targeted, and one generation weakness remains: P1 now answers the question correctly but adds a reassurance ("should hold up well") that the handbook doesn't support. The next fix would be a prompt rule against promises or judgements beyond what the handbook states, re-tested the same way. The **retrieval** change fixed attribution: wrong citations, and facts separated from their product. The **prompt** change fixed the **generation** error (an off-question product suggestion) and the **agent** error (guessing what a vague question meant). Neither change could have fixed the other's errors.

**Limits of this evidence:**
- Each case was run once (temperature 0), and the set is small (13 cases), so 12/13 shows how the bot handles these questions, not that it's reliable in general.
- The two held-out cases are the main guard against tuning to the test. A larger held-out set would be the next step.

## Memory evidence on the final config (`hdr-v1` + prompt v2)

Recorded after the final review, with the runner now saving every turn: [`runs/hdr-v1-prompt2-F1-M1.json`](runs/hdr-v1-prompt2-F1-M1.json).

| ID | Turn 1 | Turn 2 | Memory OK | Notes |
| --- | --- | --- | --- | --- |
| F1 | "Tell me about the Whisker Wand." → searched, retrieved `Section 3 > Whisker Wand (WW-C-201)`, listed "not suitable for kittens under 12 weeks" | "Is it okay for my 8-week-old kitten?" → no new search; "not suitable for kittens under 12 weeks… wait until they are older" (Section 3) | Y | "It" resolved from history. The turn-2 fact comes from the handbook chunk retrieved in turn 1. |
| M1 | "The Iron Jaw Bone costs $5, right?" → searched, retrieved `Section 3 > Iron Jaw Bone`, **"actually costs $24"** | "So how much is it?" → no new search; **"$24"** (Section 3) | Y | The user's false claim was never treated as a store fact. Turn 1 also volunteered an unasked suggestion ("the Apple Stick Bundle, which is priced at $5"). This is the same kind of off-question product suggestion as P1 in runs 1–2: **answer fail (generation), severity low**. It's odd and irrelevant (a small-pet chew offered for a dog-toy price question), but it doesn't mislead the customer about anything they're buying. |

**Final config, all 14 cases:** 12/14 answers correct. Memory behaviour correct in both multi-turn cases. Remaining failures, by severity:
- **P1 (high):** invented durability promise. This is the next fix: a prompt rule against claims beyond the handbook, and possibly a code check.
- **M1 (low):** unasked product suggestion. A prompt rule only reduces this; a reliable fix needs a code check that compares recommended products with what was asked.

## Run 4 — `hdr-v1` + prompt v3 (one focused change for P1) — 2026-10-22

**Why:** the Stage 2 review suggested one focused prompt change for P1's unsupported durability claim, then a re-test.

**Change (prompt only):** one rule was added to prompt v2, again worded generally:

> 8. Do not add promises, guarantees or judgements the handbook does not state, such as how long a product will last or whether it will suit a particular pet. If what the user describes goes beyond what a product is rated or recommended for, say so plainly using the handbook's own wording.

All 14 cases were re-run ([`runs/hdr-v1-prompt3.json`](runs/hdr-v1-prompt3.json)). P1 and M1 were then repeated 3 more times to check whether the results were stable or run-to-run noise ([`runs/hdr-v1-prompt3-repeat*`](runs/)).

| ID | Run 3 (v2) | Run 4 (v3) | Repeats (v3) | Notes |
| --- | --- | --- | --- | --- |
| P1 | ❌ "should hold up well" (high) | ❌ **regressed** | 3/3 same | The durability promise is gone, but the Ultra Chew Ring (rubber, rating 4) is back, listed under "rope toys", with "Both options are suitable for strong chewers like your dog". Still high severity: a rubber toy is presented as a rope toy, plus a suitability judgement. |
| M1 | ❌ unasked $5 product (low) | ✅ | 3/3 pass | "$24" in both turns; no unasked product. |
| Other 12 | ✅ | ✅ | — | No change. |

**Score:** 13/14 with prompt v3 (12/14 with v2). But the one remaining failure, P1, is the high-severity one, and it got a different failure rather than a fix.

**Why it regressed (most likely):** rule 8 tells the bot to act when a user's needs go beyond a product's rating. The bot recognised that a dog that "shreds everything" fits rating 4, but resolved it by *recommending* the rating-4 product instead of *stating* that the rope toy is only rated 3. That breaks rule 7 ("only recommend products that match what was asked"). The two rules pulled in opposite directions, and the model resolved the conflict the wrong way. The 3/3 repeats show this is caused by the prompt, not by chance.

**Decision:** prompt v2 stays live (it's what `workflows/chat.json` contains). v3 is recorded here so the test can be reproduced. Neither prompt fixes P1. Adding one rule per failure risks rules that conflict, as happened here. A reliable fix likely needs either one combined rule written with the conflict in mind, or a code check after the model answers (e.g. block any recommended product that doesn't match the requested type, and any sentence that predicts durability). That's left as the next step beyond Stage 2.

**Lesson:** prompt rules interact. Every prompt change needs the full regression set, plus repeats on the cases it touches. A single run of only the targeted case would have missed this regression.
