# ClauseGuard Roadmap

Public-facing progress tracker. For the reasoning behind each decision, see `ENGINEERING_JOURNAL.md`.

**Current status:** Phase 1 is complete. Phase 2 is next.

| Phase | Objective | Success Criteria |
|---|---|---|
| 1. Evaluation Dataset | Build a high-quality labeled benchmark | 8+ real documents with labeled clauses |
| 2. Prompt Engineering | Versioned prompts, systematic comparison between versions | Prompt regression tests pass |
| 3. Model Benchmarking | Compare open models on quality, latency, and cost | Documented benchmark report |
| 4. Retrieval System | Build and optimize RAG, including chunking strategy and reranking | Precision@K / Recall@K measured across configurations |
| 5. Custom MCP Server | Expose clause retrieval as an MCP tool | LangGraph agent successfully calls the MCP server |
| 6. Multi-Agent Workflow | Planner → Retriever → Calculator → Reviewer → Report | End-to-end pipeline produces a decision report |
| 7. Trust & Verification | Evidence grounding and guardrails | Every claim in the output traces to a source clause |
| 8. Deployment | FastAPI + Streamlit + Docker | Public demo available |
| 9. Observability | LangSmith tracing + structured logging | Traces, latency, and cost visible per request |
| 10. LLMOps | Automated evaluation and CI/CD | Regression pipeline operational |

## Engineering questions this project is investigating

- Which chunking strategy retrieves legal clauses most accurately — fixed-size or clause-boundary-aware?
- Does a reranking step meaningfully improve retrieval quality over raw similarity search?
- Which open model provides the best quality per dollar for clause classification versus final decision reasoning?
- Does a dedicated reviewer agent measurably reduce unsupported claims?
- Is multi-agent orchestration worth its added complexity compared to a single well-prompted call?
- Does the Calculator node perform meaningful financial computation (e.g., total cost of early termination across a notice period), or is it redundant with what the LLM already extracts? This will be decided during Phase 6 based on what the fee-related clauses in the evaluation set actually require.

## Future work

- RAGAS-based evaluation, replacing the current hand-scored benchmark
- CI/CD with automatic regression testing on every prompt or retrieval change
- Cost-aware model routing based on measured performance, not assumption
- Expanded document coverage — the architecture is not lease-specific, and is expected to generalize to insurance policies, employment agreements, warranties, and NDAs; real evaluation data for these categories is a later addition, not part of the current scope
