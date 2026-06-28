# Lab Export Guide

Each lab is a self-contained module that can be copied into any compatible project with minimal wiring changes.

---

## Project layout

```
backend/
  modules/
    common/                  ← shared infra (copy to every target project)
      __init__.py            (version)
      db.py                  (SQLite connection, shared tables, init_db)
      export_md.py           (Markdown export helper)
    daily_session/           ← session + question + progress + settings endpoints
      __init__.py
      daily_session.py       (FastAPI APIRouter — no prefix)
    dsa_lab/                 ← copy this to export DSA Lab
      __init__.py
      schema.py              (creates dsa_topics table + seeds data)
      seed.py                (seed_dsa_topics, fetch_dsa_topics, save_dsa_topic)
      router.py              (FastAPI APIRouter, prefix="/dsa")
    cv_lab/                  ← copy this to export CV Lab
      __init__.py
      schema.py
      seed.py
      router.py              (prefix="/cv")
    system_design_lab/       ← copy this to export System Design Lab
      __init__.py
      schema.py
      seed.py
      router.py              (prefix="/system-design")
  main.py                    (pure wiring — include_router only)

frontend/src/
  modules/
    dsa-lab/                 ← copy this to export DSA Lab UI
      DSALabModule.tsx       (main interactive component)
      fallbackTopics.ts      (80 static fallback topics)
      types.ts               (DSATopic interface)
    cv-lab/                  ← copy this to export CV Lab UI
      CVLabModule.tsx
      types.ts
    system-design-lab/       ← copy this to export System Design Lab UI
      SystemDesignLabModule.tsx
      types.ts
```

---

## Shared dependencies (required in every target project)

### Backend — `modules/common/`

Always copy `modules/common/` in full. Every lab module imports from it:

```python
from modules.common.db import get_db_path, fetch_lab_sections, save_lab_section
```

`db.py` creates these shared tables on startup:

| Table | Purpose |
|---|---|
| `sessions` | One row per practice day |
| `questions` | Generated interview questions |
| `session_progress` | User answers per question |
| `user_settings` | LLM model + API key config |
| `lab_sections` | Section names per lab (shared by all labs) |

### Frontend — shared components

Each lab module imports via the `@/` alias (= `src/`):

| Import path | Component |
|---|---|
| `@/components/ui/AppIcon` | Heroicons wrapper |
| `@/components/common/LabCopilot` | AI sidebar (hint / deep-dive / ELI5) |
| `@/components/lab/OnDemandSection` | Lazy-rendered content section |
| `@/components/lab/QuizCarousel` | Quiz UI |

Copy `frontend/src/components/` to the target project.

---

## Exporting a single lab — step-by-step

> Replace `dsa_lab` / `DSALabModule` with `cv_lab` / `CVLabModule` or `system_design_lab` / `SystemDesignLabModule` as needed.

### 1 — Backend

```bash
# Required every time
cp -r backend/modules/common    <target>/backend/modules/common

# The lab itself
cp -r backend/modules/dsa_lab   <target>/backend/modules/dsa_lab
```

Register the router in `main.py`:

```python
from modules.dsa_lab.router import router as dsa_router
app.include_router(dsa_router)
```

Initialise the DB in your startup handler:

```python
from modules.common.db import init_db   # already handles all lab register() calls

@app.on_event("startup")
async def _startup():
    init_db()
```

`init_db()` will automatically call `dsa_register(cursor)` (and any other registered lab modules), create the `dsa_topics` table, and seed the initial data.

REST endpoints added:

| Method | Path | Description |
|---|---|---|
| GET | `/dsa/topics` | List all DSA topics (seeded + custom) |
| POST | `/dsa/topics` | Add a custom DSA topic |
| GET | `/dsa/sections` | List DSA sections |
| POST | `/dsa/sections` | Add a custom section |

### 2 — Frontend (Next.js App Router)

```bash
# Shared components
cp -r frontend/src/components    <target>/frontend/src/components

# The lab module
cp -r frontend/src/modules/dsa-lab   <target>/frontend/src/modules/dsa-lab
```

Create the route page at `app/dsa-lab/page.tsx`:

```tsx
import type { Metadata } from 'next';
import DSALabModule from '@/modules/dsa-lab/DSALabModule';
import Header from '@/components/common/Header';

export const metadata: Metadata = {
  title: 'DSA Lab',
  description: 'Interactive DSA practice lab.',
};

export default function DSALabPage() {
  return (
    <>
      <Header />
      <DSALabModule />
    </>
  );
}
```

Set your API URL in `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Minimal change checklist per lab

| File | What to change | Default |
|---|---|---|
| `router.py` | API prefix string | `/dsa` / `/cv` / `/system-design` |
| `DSALabModule.tsx` | `NEXT_PUBLIC_API_URL` env var | `http://localhost:8000` |
| `types.ts` | Interface fields if your schema differs | DSATopic / CVTopic / SDTopic |

---

## Lab-specific notes

### DSA Lab
- **80 static fallback topics** in `fallbackTopics.ts` — loaded when API is unreachable
- **16 section types**: prerequisites, theory, visual, implementation, hyperparameters, pitfalls, applications, interview, comparison, paper, quiz, references
- Topic briefs include LeetCode IDs: `LC #560 [Medium] — ...`

### CV Lab
- **35 seeded topics** — Fundamentals → Classical CV → Deep Learning → Generative AI → Transformers → MLOps → Projects
- Topics include prerequisite chains shown in the Prerequisites section

### System Design Lab
- **50 seeded topics** — Fundamentals, API & Microservices, HLD, LLD, Infrastructure & Ops
- `scale` field (e.g. `100k+ RPS`) and `isLLD` flag distinguish HLD from LLD topics

### Daily Session module
Owns all session/question/progress/settings endpoints (no prefix):

| Method | Path |
|---|---|
| POST | `/sessions` |
| POST | `/sessions/questions` |
| GET | `/questions` |
| PATCH | `/questions/{id}/performance` |
| GET/POST | `/session-progress` |
| GET | `/session-progress/stats` |
| GET/POST | `/settings` |
| GET | `/export` |

---

## Adding a brand new lab

1. `backend/modules/<your_lab>/` — add `__init__.py`, `schema.py`, `seed.py`, `router.py`
2. Add `from modules.<your_lab>.schema import register as x_register` + `x_register(cursor)` inside `init_db()` in `modules/common/db.py`
3. Add `app.include_router(your_router)` in `main.py`
4. `frontend/src/modules/<your-lab>/` — add `YourLabModule.tsx` and `types.ts`
5. Create `frontend/src/app/<your-lab>/page.tsx` importing from the module


// adding generated question to db 
# Migration & Import Roadmap

## TODO: DB Migration / Import Feature
When migrating to these to a new version of this app, give users the option to connect their existing SQLite database (or any supported DB) and import data into the new schema. Use AI to automatically match columns from the old table to the new schema (e.g. old `question_text` → new `text`, old `sub_type` → new `category`). The user should be able to preview the mapping, adjust mismatches, and confirm before migrating. This allows seamless upgrade paths without losing historical question/session data. also fix the db schema of question genrated in labs/topics matching the new app database tand table 