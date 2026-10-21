# /// script
# requires-python = ">=3.11"
# dependencies = ["pypdf>=5"]
# ///
"""Fail unless the built handbook PDF has the pages, sections and facts the eval relies on."""
import sys
from pathlib import Path

from pypdf import PdfReader

PDF = Path(__file__).with_name("handbook.pdf")

SECTIONS = [
    "1. About Wag & Whisker",
    "2. Safety Standards",
    "3. Product Catalogue",
    "4. Ordering and Payment",
    "5. Shipping",
    "6. Returns and Exchanges",
    "7. Damaged, Defective and Warranty",
    "8. Recalls and Safety Notices",
    "9. Pack Points Loyalty Programme",
    "10. Contact and Hours",
    "11. Frequently Asked Questions",
]

FACTS = [
    "WW-D-101",            # Tug Titan Rope
    "WW-D-102",            # Twisty Rope Ring
    "dogs over 30 kg",     # Tug Titan XL guidance
    "up to 20 kg",         # Twisty Rope Ring limit
    "$35",                 # free shipping threshold
    "30 days of delivery", # return window
    "100 Pack Points",     # = $5 off
    "12 weeks",            # Whisker Wand minimum kitten age
    "Canada, the United Kingdom and Australia",
]


def main() -> int:
    if not PDF.exists():
        print(f"missing {PDF}")
        return 1
    reader = PdfReader(PDF)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    problems = []
    if len(reader.pages) < 12:
        problems.append(f"only {len(reader.pages)} pages (need >= 12)")
    problems += [f"section heading missing: {s}" for s in SECTIONS if s not in text]
    problems += [f"fact missing: {f}" for f in FACTS if f not in text]
    for p in problems:
        print("FAIL:", p)
    if not problems:
        print(f"OK: {len(reader.pages)} pages, {len(SECTIONS)} sections, {len(FACTS)} facts")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
