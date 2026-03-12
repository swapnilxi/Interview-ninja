# Interview-Ninja (CV-Aware Interview Coach)

Interview-Ninja is a monorepo containing a FastAPI backend and a Next.js frontend for an
agent-powered interview coach for software and computer vision engineers. It:

- Uses a system prompt tailored for daily interview training.
- Generates 10 questions per day (5 Core Interview, 5 Computer Vision).
- Is CV / Job Description aware (inputs provided by the host UI).
- Persists all questions in SQLite for review and filtering.
- Supports a UI with two main tabs:
  - **Curate Questions**: choose topics and start a new daily session.
  - **Previous Questions**: review past questions with filters.

## Monorepo Layout

- Backend (FastAPI API server)
  - `backend/main.py`: FastAPI app exposing health, sessions, questions, and export endpoints.
  - `interview_ninja/db.py`: SQLite schema and helpers for sessions and
    questions, optimized for the Previous Questions tab filters.
  - `interview_ninja/export_md.py`: Markdown export utilities used when
    the user chooses to export a day's questions.
  - `interview_ninja/rubrics.md`: answer-evaluation rubrics by question
    sub-type.
- Frontend (Next.js + TypeScript + Tailwind)
  - `frontend/`: Next.js app (App Router, TypeScript, Tailwind) that can
    talk to the FastAPI backend.

## Backend Core Components

- `agent_config.interview_ninja.json`: configuration and system prompt
  for the Interview-Ninja agent, including output schema and topic
  selection rules.

You can integrate this package into any agent runtime or UI stack
(web, desktop, or CLI). The UI is responsible for:

- Collecting CV text or uploaded files.
- Collecting job descriptions (pasted or uploaded).
- Letting the user select or edit topics in the Curate Questions tab.
- Calling the agent with those inputs and then saving questions via
  `interview_ninja.db`.
- Using `interview_ninja.export_md.render_markdown_for_day` to
  generate Markdown when the user opts to export.

## Running Locally

### Backend (FastAPI)

- Ensure your Python environment has the dependencies from `requirements.txt` installed.
- Initialize the SQLite DB (one-time convenience):
  - `python3 main.py`
- Run the API server (for local dev):
  - `uvicorn backend.main:app --reload --port 8000`

The API will be available at `http://localhost:8000` with an OpenAPI UI
at `http://localhost:8000/docs`.

### Frontend (Next.js)

- From the `frontend/` directory:
  - `npm install` (first time only, if needed)
  - `npm run dev`

By default the app runs at `http://localhost:3000`.

You can then wire the frontend to call the FastAPI endpoints under
`http://localhost:8000` for sessions, questions, and exports.
