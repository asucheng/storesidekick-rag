# /// script
# requires-python = ">=3.11"
# dependencies = ["markdown-pdf>=1.3"]
# ///
"""Build handbook.pdf from handbook.md."""
from pathlib import Path

from markdown_pdf import MarkdownPdf, Section

HERE = Path(__file__).parent

pdf = MarkdownPdf(toc_level=2)
pdf.meta["title"] = "Wag & Whisker Store Handbook"
pdf.add_section(Section((HERE / "handbook.md").read_text(encoding="utf-8"), toc=True))
pdf.save(HERE / "handbook.pdf")
print("wrote", HERE / "handbook.pdf")
