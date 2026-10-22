# StoreSidekick RAG — Wag & Whisker handbook chatbot

Stage 2 of the AI Engineer Residency: an n8n chatbot that answers questions about a fictional pet-toy store **only from its handbook**, using retrieval (RAG). It refuses when the handbook doesn't cover something and asks when a question is too vague.

- **Write-up:** [`WRITEUP.md`](WRITEUP.md) (chunking choice, a traced answer, retrieval vs generation errors, what changed)
- **Evaluation:** [`eval/results.md`](eval/results.md): 3 runs, 13 cases (answers 9/11 → 9/11 → 12/13; citations 7/9 → 9/9)
- **Demo:** [`screenshots/`](screenshots/)

Wag & Whisker, its products and its policies are invented.

## How it works

| Workflow | What it does |
| --- | --- |
| [`workflows/ingest-headings.json`](workflows/ingest-headings.json) | **Current ingest.** Reads `handbook/handbook.pdf`, extracts the text, and splits it at section and product headings. Each chunk starts with a breadcrumb (`Section 3. Product Catalogue > Tug Titan Rope (WW-D-101)`). Chunks are embedded with OpenAI `text-embedding-3-small` and stored in Pinecone namespace `hdr-v1`. |
| [`workflows/ingest.json`](workflows/ingest.json) | Run 1's baseline ingest: fixed 800-character chunks with 150 overlap into namespace `c800-o150`. Kept for comparison. |
| [`workflows/chat.json`](workflows/chat.json) | Hosted chat page → AI Agent (`gpt-4o-mini`, temperature 0) with a 5-exchange memory and a `search_handbook` tool (Pinecone, top 4, namespace `hdr-v1`). A system prompt keeps answers grounded and cited. |

## Setup

You need Node.js 20+, Python 3.11+ with [uv](https://docs.astral.sh/uv/), an OpenAI API key, and a free Pinecone account.

1. **Create the Pinecone index:** name `wag-whisker-handbook`, dimension `1536`, metric `cosine`, serverless (AWS us-east-1).
2. **Start n8n** (allowing it to read the handbook folder):
   ```bash
   N8N_RESTRICT_FILE_ACCESS_TO="$PWD/handbook" npx n8n
   ```
   Open http://localhost:5678 and create the local owner account.
3. **Add credentials** in n8n: **OpenAI** (your API key) and **Pinecone API** (your Pinecone key).
4. **Import the workflows:**
   ```bash
   npx n8n import:workflow --input=workflows/ingest-headings.json
   npx n8n import:workflow --input=workflows/chat.json
   ```
   Then open each workflow and select your credentials on the OpenAI and Pinecone nodes. The exported files reference credentials from the original machine.
5. **Update the file path** in the ingest workflow's *Read handbook PDF* node to your copy of `handbook/handbook.pdf`, then run the ingest workflow once.
6. **Publish the chat workflow** and open its chat URL: `http://localhost:5678/webhook/3b6f8f2e-7c1a-4d55-9a3e-2f0c9b7d4a11/chat`

## Handbook

`handbook/handbook.md` is the source. To rebuild and check the PDF:

```bash
uv run handbook/build_pdf.py
uv run handbook/check_pdf.py   # ≥12 pages, all sections, and every fact the eval relies on
```

## Evaluation

With the chat workflow published:

```bash
python3 eval/run_eval.py --questions               # regenerate eval/questions.md from eval/cases.json
python3 eval/run_eval.py --run <config-name>       # send every case to the chatbot; saves eval/runs/<config-name>.json
python3 eval/run_eval.py --run <name> --ids P1,A1  # only some cases
```

Each saved run records the answer, the search queries, and the exact chunks retrieved, which is how retrieval and generation errors are told apart. Grading is done by hand in [`eval/results.md`](eval/results.md). [`eval/check_chunks.py`](eval/check_chunks.py) checks an ingest run's chunks (every chunk has a breadcrumb, and facts stay with their product names).

## Repository layout

```
handbook/      handbook.md (source), handbook.pdf, build and check scripts
workflows/     n8n workflow exports (no keys)
eval/          cases.json, questions.md, run_eval.py, check_chunks.py, runs/, results.md
notes/         chunk inspections for each configuration
screenshots/   demo and workflow screenshots
WRITEUP.md     Stage 2 write-up
```

No API keys are stored in this repository. They live only in n8n's local credential store.
