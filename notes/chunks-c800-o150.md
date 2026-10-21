# Chunk inspection: c800-o150

Settings: Recursive Character Text Splitter, chunk size 800, overlap 150. PDF loaded as one document (`splitPages: false`).

- **Chunks stored:** 34 (Pinecone namespace `c800-o150`)
- **Chunk length:** min 136, average 686, max 798 characters
- **Metadata on each chunk:** `source=handbook`, `config=c800-o150`, plus the line range and PDF info added by the loader

## What the chunks look like

PDF extraction kept the structure readable. Headings come through as plain lines (for example `2. Safety Standards`, `Iron Jaw Bone (WW-D-104)`), and bullet lists stay one per line with `•`. No merged words or broken tables.

Example (chunk 14, trimmed):

```
Iron Jaw Bone (WW-D-104)
Part of our Built Tough line, the Iron Jaw Bone is moulded from our densest natural rubber ...
• Price: $24
• Chew rating: 4 Power (Built Tough)
• Weight guidance: for dogs 15–45 kg
Snuffle Mat Meadow (WW-D-105)
...
```

## Problems found

1. **Product names get separated from their own facts.** An 800-character window regularly ends right after a product heading, so the heading lands in one chunk and the product's bullet list lands in the next:
   - Tug Titan Rope: name and SKU in chunk 11, but "choose XL for dogs over 30 kg" in chunk 12.
   - Twisty Rope Ring: heading at the end of chunk 12, but "suitable for dogs up to 20 kg" in chunk 13, which never names the product.
   - Whisker Wand: name and SKU in chunk 17, but "not for kittens under 12 weeks" in chunk 18.

   A chunk that says "suitable for dogs up to 20 kg" without saying *which* toy is risky. Retrieval can return it for the wrong product, and the model has to guess what it belongs to. Eval cases P1 (rope toy for a 35 kg dog) and F1 (Whisker Wand for a kitten) are exactly where this should show up.
2. **Chunks often mix two products** (e.g. chunk 14 holds the end of Iron Jaw Bone and the start of Snuffle Mat Meadow). That's less harmful, but it dilutes each chunk's meaning.
3. **Section boundaries are not respected.** Chunks 5 and 26 span the end of one section and the start of the next.

## Likely improvement to test (Task 8)

Make each product entry fit in one chunk with its name. Options: a larger chunk size (a full product entry is roughly 400–600 characters, so ~1,200 with more overlap would usually keep a heading with its facts), or splitting on headings. Decide after run 1 shows which cases actually fail.
