# ClauseGuard

> **Understand a lease, insurance policy, or Terms of Service in under a minute — with every recommendation backed by the exact clause that produced it.**

ClauseGuard is an AI decision-intelligence system that reads legal-style documents, identifies clauses worth attention, explains them in plain English, and links every conclusion to the specific text it came from.

## Live Demo

🌐 **Try ClauseGuard:** https://clauseguard-ai.streamlit.app/

Upload a lease, insurance policy, or Terms of Service document to generate an evidence-backed analysis with clause-level citations.

> Demo: https://clauseguard-ai.streamlit.app/

## Why this project

This is built as an AI engineering case study, not just a document-processing application. The system is structured around a set of engineering questions — chunking strategy, retrieval quality, model selection, whether a reviewer agent actually reduces unsupported claims — each tested and documented rather than assumed. See `docs/ROADMAP.md` for the full list of questions under investigation and `docs/ENGINEERING_JOURNAL.md` for the reasoning behind completed decisions.

## Core features

- Evidence-backed clause analysis, not summarization
- Retrieval-augmented generation over uploaded documents
- LangGraph multi-agent workflow: Planner → Retriever → Calculator → Reviewer → Decision report
- Custom-built MCP server for clause retrieval
- Model comparison and cost-aware routing
- Reviewer agent gating unsupported claims before output
- LangSmith observability and structured request logging
- FastAPI backend, Streamlit frontend, Docker deployment

## Planned architecture

```
Document → Chunking → Embeddings → Vector Store
                                        ↓
                Planner → Retriever (custom MCP) → Calculator → Reviewer → Decision Report
```

## Engineering experiments

This repository documents measurable comparisons across:
- Chunking strategies (fixed-size vs. clause-boundary-aware)
- Embedding models
- Retrieval methods, including reranking
- Prompt versions
- LLM providers and routing strategies
- Reviewer agent enabled vs. disabled

Write-ups land in `docs/experiments/` as each one is actually run. Reasoning behind completed decisions is in `docs/ENGINEERING_JOURNAL.md`.

## Tech stack

LangGraph, LangChain, MCP, FastAPI, Streamlit, Docker, LangSmith, SQLite, HuggingFace, Groq.

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
│   ├── models/            # model selection and routing
│   ├── monitoring/         # LangSmith config, structured logging
│   ├── config/
│   ├── utils/
│   └── schemas/
│
├── api/                     # FastAPI backend
├── frontend/                 # Streamlit UI
├── tests/
│
├── evaluation/
│   ├── datasets/              # test_set.json and related labeled data
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
│   └── experiments/               # populated as each experiment is run
│
└── assets/
    ├── architecture.png
    ├── demo.gif
    └── screenshots/
```

## Roadmap

See `docs/ROADMAP.md` for current status and `docs/ENGINEERING_JOURNAL.md` for the decisions behind it.

## Future work

- RAGAS-based evaluation
- Automated regression testing and CI/CD
- LLMOps dashboards for cost and latency
- Advanced model routing based on measured performance

## Disclaimer

ClauseGuard is an educational AI engineering project. It does not provide legal advice.
