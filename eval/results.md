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
