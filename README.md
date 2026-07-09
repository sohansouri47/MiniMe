# Mini-Me

Mini-Me is a FastAPI backend for a personal AI memory system. It stores journal entries, summarizes and embeds them, and answers questions with RAG over historical memories.

## Reference Patterns

This backend follows the local Fire Agent, Crime Agent, and Orchestrator Agent conventions:

- `src/common` contains shared config, DB, logging, exceptions, prompts, and provider connectors.
- `src/journal` contains journal-owned routing, services, repositories, schemas, and models.
- `src/user` contains the user-owned model and repository.
- Config is environment-driven and loaded once at the shared config boundary.
- Modules use class-based services/repositories with module-level `get_logger(...)`.
- External AI calls sit behind connector/provider classes, similar to Orchestrator's `AgentConnector` pattern.
- Docker uses the same `python:3.13-slim` plus `uv` approach.

Mini-Me deviates where required by the product scope: it uses REST routes instead of A2A executors, SQLAlchemy Async ORM instead of direct psycopg calls, Alembic migrations for PostgreSQL/pgvector, and feature folders instead of top-level layer folders.

## API

- `GET /health`
- `POST /api/v1/journal`
- `GET /api/v1/journal?user_email=you@example.com`
- `GET /api/v1/journal/{entry_id}?user_email=you@example.com`
- `DELETE /api/v1/journal/{entry_id}?user_email=you@example.com`
- `POST /api/v1/query`
- `POST /api/v1/reindex`

## Environment

Copy `.env.example` to `.env` and set either OpenAI-compatible or Google credentials.

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=...
```

or

```bash
LLM_PROVIDER=google
GOOGLE_API_KEY=...
```

The vector column is created as `vector(1536)` by the initial migration. Keep `EMBEDDING_DIMENSIONS=1536`, or create a new migration if you intentionally change dimensions.

## Run Locally

```bash
uv sync
uv run alembic upgrade head
uv run python3 main.py
```

Docker:

```bash
docker compose up --build
```

## Example Requests

```bash
curl -X POST http://localhost:8000/api/v1/journal \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "you@example.com",
    "title": "First day at the new job",
    "transcript": "I met the platform team and felt nervous but excited..."
  }'
```

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "you@example.com",
    "question": "What did I feel on my first day at work?",
    "top_k": 5
  }'
```

## Quality Checks

```bash
uv run ruff check .
uv run mypy .
uv run pytest
```
