# Repository Guidelines

This document helps contributors work consistently across the Next.js frontend and the Python/CrewAI backend. Keep changes focused, small, and well‑described.

## Project Structure & Module Organization
- Root: orchestration docs and scripts (`start-system.sh`, `START-SYSTEM.md`, `TESTING.md`).
- `frontend/`: Next.js 14 + TypeScript. Source in `src/` (`app/`, `components/`, `lib/`, `styles/`, `types/`).
- `python-crewai/`: FastAPI + CrewAI backend. Key dirs: `agents/`, `api/`, `models/`, `tests/`, `tools/`, `utils/`. Entry points: `main.py`, API via `api/`.
- `gatekeeper-api/`: Authentication microservice with database integration. Core: `app/database.py`, `app/models.py`, `app/services/`.
- **Database**: MongoDB + Beanie ODM for persistent data (users, context, containers, shipments).
- Config: `.env` files at root and in `python-crewai/`; Dockerfiles and compose files in both apps.

## Build, Test, and Development Commands
- **Database**: Ensure MongoDB is running locally (`mongod`) or via Docker.
- Frontend dev: `cd frontend && npm run dev` (Next dev server on `:3000`).
- Frontend build: `cd frontend && npm run build && npm start` (production).
- Frontend lint/types: `npm run lint` and `npm run type-check`.
- Backend dev (CLI): `cd python-crewai && python main.py`.
- Backend API: `cd python-crewai && python -m uvicorn api.main:app --reload` (default `:8000`).
- Gatekeeper API: `cd gatekeeper-api && python -m uvicorn app.main:app --reload --port 8001`.
- Backend tests: `cd python-crewai && pytest -q` or `pytest --cov`.
- Full system (auto): `./start-system.sh` (installs deps, starts services).

## Coding Style & Naming Conventions
- TypeScript/React: follow ESLint rules in `frontend/.eslintrc.json` (no `any`, no unused vars, `prefer-const`, `no-var`). Components `PascalCase`, hooks/utilities `camelCase`. Keep files under `src/` and use path aliases (`@/…`).
- Python: PEP 8 (4‑space indents), `snake_case` for modules/functions, `PascalCase` for classes, type hints required for new/edited code. Keep logic in `agents/`, I/O in `api/`, database models in `models/`.
- **Database Models**: Use Beanie ODM with Pydantic for MongoDB documents. Define indexes and relationships properly.
- Commits and PRs must pass `npm run lint` and `npm run type-check` (frontend) and run `pytest` locally when touching backend.

## Testing Guidelines
- Framework: `pytest` (see `python-crewai/tests/`). Name tests as `tests/test_*.py`, functions `test_*`.
- **Database Testing**: Mock database operations or use test database instance. Test model validation and CRUD operations.
- Add unit tests for new logic and happy + edge cases. Prefer small, isolated tests over broad integration unless necessary.
- Run coverage when feasible: `pytest --cov` (HTML via `--cov-report=html`).
- **Integration Tests**: Include database connections, API endpoints, and agent interactions.

## Commit & Pull Request Guidelines
- Commit messages: Conventional Commits style (e.g., `feat:`, `fix:`, `docs:`) as used in history (e.g., `feat: add GraphQL API…`).
- PRs: clear description, scope, and rationale; link issues; list commands to validate; include screenshots/GIFs for UI changes and API examples for backend changes.
- Keep PRs focused; update docs when behavior or commands change.

## Security & Configuration
- Never commit secrets. Use `.env` and `.env.test` locally; document new variables in READMEs.
- **Database Security**: Use proper MongoDB authentication in production. Configure connection strings with credentials in environment variables.
- **Environment Variables**: 
  - `MONGODB_URL`: Database connection string
  - `DATABASE_NAME`: Database name (default: `mit_logistics`)
  - `OPENAI_API_KEY`: OpenAI API access
  - `GEMINI_API_KEY`: Google Gemini API access
- Ollama/LLM config lives in env files; some compose files use `network_mode: host`—confirm before exposing services.

## Database Architecture
- **MongoDB + Beanie ODM**: Async, typed document operations
- **Core Models**: User, Client, Context, Container, Shipment, TrackingEvent
- **Features**: Auto-indexing, relationships via Links, validation with Pydantic
- **Context Persistence**: All agent interactions stored for learning and history
- **Connection Management**: Health checks, auto-reconnection, proper error handling
