# Chunk inspection: hdr-v1 (heading-aware)

Workflow: [`workflows/ingest-headings.json`](../workflows/ingest-headings.json). The PDF text is extracted, then a Code node splits it at every section heading (`N. Title`) and product heading (`Name (SKU)`), and starts each chunk with a breadcrumb. Chunks are capped at 1,000 characters (longer sections are split at line boundaries, and each piece repeats the breadcrumb). A 2,000-character recursive splitter stays attached only as a safety net.

- **Chunks stored:** 44 (namespace `hdr-v1`), vs 34 in `c800-o150`
- **Chunk length:** min 174, average 493, max 1023 characters
- **Metadata:** `source`, `config=hdr-v1`, `section`, `product` (empty outside the catalogue)

[`eval/check_chunks.py`](../eval/check_chunks.py) passes: every chunk has a breadcrumb, and each fact the eval relies on sits in the same chunk as its product name. (On `c800-o150` the same check fails: 0/34 chunks had a breadcrumb, and three products' key facts were separated from their names.)

## Examples

A product chunk, complete in one piece:

```
Section 3. Product Catalogue > Tug Titan Rope (WW-D-101)
The Tug Titan is the toy that started Wag & Whisker. It is made from thick, double-braided
organic cotton with knotted ends that give dogs a firm grip for tug-of-war. The tight braid
also works like dental floss as dogs chew.
• Materials: double-braided organic cotton
• Sizes and prices: Medium $18, Large $22, Extra Large (XL) $26
• Chew rating: 3 Strong
• Size guidance: choose XL for dogs over 30 kg
• Care: machine-wash cold and air dry
```

A policy chunk:

```
Section 6. Returns and Exchanges
We want every toy to be the right fit. If something isn't right, here's how returns and
exchanges work.
Return window
You can return unused items in their original packaging within 30 days of delivery.
Used toys
For hygiene reasons, toys that have been used or played with can't be returned unless they
are defective. If a toy is defective, see Section 7.
How to start a return
Start a return from the link in your order email. Choose the items you're returning, then print
the return label and attach it to the parcel.
Return shipping cost
A $6 return label fee is deducted from your refund, unless the item is defective.
Refunds
Refunds are issued to your original 
```

## Trade-offs

- Every product is its own chunk, so a product's facts are never mixed with a neighbour's, and the section number is always visible to the model.
- The splitting relies on this handbook's consistent heading format. A different document would need its own heading patterns.
- More, smaller chunks (44 vs 34): a question spanning several products needs a higher top k to see them all.
