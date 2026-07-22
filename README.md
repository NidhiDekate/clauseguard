# ClauseGuard

> **Understand a lease, insurance policy, or Terms of Service in under a minute — with every recommendation backed by the exact clause that produced it.**

ClauseGuard is an AI decision-intelligence system that reads legal-style documents, identifies clauses worth attention, explains them in plain English, and links every conclusion to the specific text it came from.

## Live Demo

🌐 **Try ClauseGuard:** https://clauseguard-ai.streamlit.app/

Upload a lease, insurance policy, or Terms of Service document to generate an evidence-backed analysis with clause-level citations.

## Why this project

This is built as an AI engineering case study, not just a document-processing application. The system is structured around a set of real engineering questions — chunking strategy, retrieval quality, model selection, whether a reviewer step actually reduces unsupported claims — each tested with real data and documented, not assumed. See `docs/ROADMAP.md` for the full list of questions and `docs/ENGINEERING_JOURNAL.md` for the reasoning and real bugs behind every completed decision.

## Core features

- Evidence-backed clause analysis, not summarization
- Retrieval-augmented generation over uploaded documents
- LangGraph multi-step workflow: Planner → Retriever → Reviewer → Calculator → Decision report
- Custom-built MCP server for clause retrieval
- Multi-model benchmarking to select the most accurate and practical model for production use
- Reviewer step gating unsupported claims before they reach the output
- LangSmith observability and structured SQLite request logging
- FastAPI backend, Streamlit frontend, Docker deployment

## Results

Real numbers from the actual experiments — not aspirational claims.

**Clause classifier:**
| Prompt version | Accuracy (real, hand-labeled clauses) | Notes |
|---|---|---|
| v1 (baseline) | 86.8% (46/53) | All errors were one-directional — boilerplate wrongly flagged as concerning |
| v2 (in use) | **88.7% (47/53)** | Fixed the bias; one correction generalized to an unseen clause |
| v3 (rejected) | 86.8% (46/53) | Same score, but introduced false negatives on genuinely concerning clauses — reverted |

**Model comparison:**
| Model | Accuracy | Avg latency | Notes |
|---|---|---|---|
| `gpt-oss-20b` | 79.2% (42/53) | 2.15s | Fastest, least accurate |
| **`gpt-oss-120b`** | **88.5% (46/52)** | 1.79s | **Selected** — best balance of accuracy, speed, and reliability |
| `qwen/qwen3.6-27b` | 89.4% (42/47) | 11.84s | Highest raw score, but hit its free-tier daily token limit mid-test — incomplete, not practically usable |

**Chunking strategy:** clause-boundary-aware chunking beat fixed-size chunking on every real retrieval test — fixed-size cut clauses mid-sentence and, in one case, returned a chunk dominated by an unrelated clause instead of the correct one.

**Full pipeline validation:** the end-to-end system's decision report matched the original hand-labeled ground truth on a real test document, including correctly identifying which clauses the document simply didn't address rather than guessing.

Full experiment write-ups: `docs/experiments/`. Full reasoning and real bugs hit along the way: `docs/ENGINEERING_JOURNAL.md`.

## Architecture

```
Document → Chunking → Embeddings → Vector Store
                                        ↓
                Planner → Retriever (custom MCP) → Reviewer → Calculator → Decision Report
```

Retriever runs before Calculator specifically because of a real bug found during development: an earlier version ran Calculator first, which produced a confident, specific dollar figure using a clause the Reviewer went on to reject as irrelevant moments later. Reordering the graph — not changing either node's internal logic — fixed it. Full story in `docs/ENGINEERING_JOURNAL.md`.

## Engineering experiments

This repository documents measurable comparisons across:
- Chunking strategies (fixed-size vs. clause-boundary-aware) — clause-boundary won
- Embedding models
- Vector stores (Chroma vs. Pinecone) — identical retrieval quality, Chroma chosen for local development speed
- Prompt versions — three real iterations, with the reasoning for reverting one documented, not hidden
- LLM providers — three models benchmarked head to head
- Reviewer step enabled vs. disabled — confirmed it catches both obvious and subtle irrelevant matches

Write-ups: `docs/experiments/`. Reasoning behind completed decisions: `docs/ENGINEERING_JOURNAL.md`.

## Tech stack

LangGraph, LangChain, MCP (FastMCP), FastAPI, Streamlit, Docker, LangSmith, SQLite, Chroma, Pinecone, HuggingFace (sentence-transformers), Groq.

## Repository structure

```
clauseguard/
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── requirements.txt
├── Dockerfile
│
├── src/
│   ├── agents/          # LangGraph nodes and graph definition
│   ├── rag/              # chunking, embeddings, retrieval
│   ├── prompts/
│   │   ├── system_prompts/
│   │   ├── few_shot_examples/
│   │   └── templates/
│   ├── models/            # model selection and comparison
│   ├── monitoring/         # LangSmith config
│   ├── config/
│   ├── utils/
│   └── schemas/
│
├── api/                     # FastAPI backend
├── frontend/                 # Streamlit UI
├── tests/
│
├── evaluation/
│   ├── datasets/              # test_set.json — the hand-labeled ground truth
│   ├── benchmarks/
│   ├── reports/
│   └── scripts/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample_docs/            # used by the "try a sample" UI option
│
├── deployment/                  # Docker, CI configuration
│
├── docs/
│   ├── ROADMAP.md
│   ├── ARCHITECTURE.md
│   ├── ENGINEERING_JOURNAL.md
│   ├── ClauseGuard_Project_Scope.md
│   └── experiments/               # real write-ups, one per experiment actually run
│
└── assets/
    ├── architecture.png
    ├── demo.gif
    └── screenshots/
```

## Roadmap

See `docs/ROADMAP.md` for current status and `docs/ENGINEERING_JOURNAL.md` for the decisions behind it.

## Future work

- RAGAS-based evaluation, replacing the current hand-scored benchmark
- Automated regression testing and CI/CD
- LLMOps dashboards for cost and latency over time
- Advanced model routing based on measured per-request performance, not a single fixed model

## Disclaimer

ClauseGuard is an educational AI engineering project. It does not provide legal advice.
