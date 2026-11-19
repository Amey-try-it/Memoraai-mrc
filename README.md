# MemoraAI-MRE

A local-first, privacy-preserving personal knowledge system with a redesigned Memora Retrieval Engine (MRE).

## Repository structure

- `frontend/`: migrated React + Vite interface from the original MemoraAI repository. The UI is preserved while the new backend is developed.
- `backend/`: new FastAPI backend and MRE implementation, built incrementally.
- `research/`: research formulation, experiment design, and literature review.
- `docs/`: architecture and implementation notes.

## Local-only design requirement

All document content, extracted text, metadata, embeddings, indexes, queries, retrieved evidence, generated answers, and history must remain on the user's device. Normal application operation must not require cloud AI APIs or remote storage. Local model runtimes are permitted. No cloud fallback is allowed.

The API should bind to loopback only (`127.0.0.1`) by default. Setup-time model/package downloads are separate from normal offline operation.

## Frontend migration

The original frontend is migrated from [Amey-try-it/memora-ai](https://github.com/Amey-try-it/memora-ai). It is preserved as-is initially, with the new backend expected to provide a compatibility layer for its current routes:

- `GET /api/dashboard`
- `GET /api/status`
- `GET /api/documents`
- `GET /api/documents/{id}`
- `DELETE /api/documents/{id}`
- `POST /upload`
- `POST /ask`
- `GET /api/memories`
- `POST /api/search`
- `GET /timeline/search`
- `GET /api/evaluations`
- `GET /api/evaluations/{id}`

The new backend will provide compatibility for these routes while exposing MRE-specific evidence, integrity, coverage, and retrieval trace metadata.

## Planned capabilities

- Heterogeneous ingestion: PDF, DOCX, PPTX, TXT, WhatsApp exports, spreadsheets, Markdown, HTML, JSON, images, audio, video, and additional formats in staged releases.
- File integrity and extraction-quality analysis: detect incomplete uploads, malformed containers, parser failures, truncation, and post-ingestion changes.
- Integrity-aware adaptive evidence retrieval and corroboration.
- Local answer generation with citations, provenance, and explicit evidence limitations.
- Reproducible evaluation against fixed Top-K, hybrid, and adaptive retrieval baselines.

## Development status

- [x] New repository established
- [x] Original frontend migrated
- [ ] New backend foundation
- [ ] API compatibility layer
- [ ] Integrity and extraction-quality pipeline
- [ ] MRE retrieval core
- [ ] Local AI integration
- [ ] Video ingestion MVP
- [ ] Evaluation framework

Research novelty claims remain subject to literature review and experimental validation.
