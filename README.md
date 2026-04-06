# IndexFlow

A backend document retrieval system built from scratch.

Not a CRUD app. A data transformation and retrieval system.

## What It Does

- Accepts raw documents via a REST API
- Asynchronously indexes them into a searchable representation
- Retrieves relevant documents based on user queries
- Ranks results by relevance using term frequency

## Architecture

### Three Paths

**Write Path**
Client → POST /documents → documents table → return document

**Processing Path**
Worker → fetch pending documents → transform → search_index → mark indexed

**Read Path**
Client → GET /documents/search?q= → search_index → ranked documents → return

### Key Design Decisions

- `documents` is the source of truth. `search_index` is always derived from it.
- Search never queries `documents` directly — only `search_index`.
- Indexing is async. The system is eventually consistent.
- Indexing logic never lives inside the API.

## Tech Stack

- Python 3.13
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL
- pydantic-settings
- uv

## Project Structure
1. Clone the repo and install dependencies
```bash
uv sync
```

2. Create `.env` in the project root
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/indexflow

3. Run the API
```bash
uv run uvicorn app.main:app --reload
```

4. Run the worker in a separate terminal
```bash
uv run python -m app.worker.indexer
```

5. Visit `http://localhost:8000/docs`

## API
POST /documents          # submit a document
GET  /documents/search?q=  # search documents

## Status

- Phase 1 — Core system ✅
- Phase 2 — Ranking + better retrieval (in progress)
- Phase 3 — Reliability
- Phase 4 — Full-text search
- Phase 5 — Semantic search / RAG
