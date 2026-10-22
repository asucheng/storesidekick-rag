# Evaluation results

Cases and expected answers: [`questions.md`](questions.md). Raw answers and retrieved chunks: [`runs/`](runs/).

- **Retrieval OK:** a chunk containing the expected fact was among the chunks returned by `search_handbook`.
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

Retrieval still didn't fail. The recurring problem is **wrong section citations** (F1, P3, and the Iron Jaw smoke test) and **facts separated from their product name** (P1), both traced to chunks that don't carry their own context.

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
