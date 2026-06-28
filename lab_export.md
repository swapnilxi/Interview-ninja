# Lab Export Guide

Each lab is a self-contained module that can be copied into any compatible project with minimal wiring changes.

---

## Project layout (after modularisation)

```
backend/
  lab_ninja/               ← shared infra (DB connection, sessions, settings)
    db.py
    export_md.py
  modules/
    dsa_lab/               ← copy this to export DSA Lab
      __init__.py
      schema.py            (creates dsa_topics table + seeds data)
      seed.py              (seed_dsa_topics, fetch_dsa_topics, save_dsa_topic)
      router.py            (FastAPI APIRouter, prefix="/dsa")
    cv_lab/                ← copy this to export CV Lab
      __init__.py
      schema.py
      seed.py
      router.py            (prefix="/cv")
    system_design_lab/     ← copy this to export System Design Lab
      __init__.py
      schema.py
      seed.py
      router.py            (prefix="/system-design")
  main.py

frontend/src/
  modules/
    dsa-lab/               ← copy this to export DSA Lab UI
      DSALabModule.tsx     (main interactive component)
      fallbackTopics.ts    (80 static fallback topics)
      types.ts             (DSATopic interface)
    cv-lab/                ← copy this to export CV Lab UI
      CVLabModule.tsx
      types.ts
    system-design-lab/     ← copy this to export System Design Lab UI
      SystemDesignLabModule.tsx
      types.ts
```

---

## Shared dependencies (required in the target project)

### Backend shared infra

The module routers import two functions from the shared layer:

```python
from lab_ninja.db import get_db_path, fetch_lab_sections, save_lab_section
```

Your target project must provide `lab_ninja/db.py` with at minimum:

| Function | Purpose |
|---|---|
| `get_db_path() -> str` | Returns the path to the SQLite file |
| `fetch_lab_sections(lab_name: str) -> List[dict]` | Reads rows from `lab_sections` table |
| `save_lab_section(lab_name, name, is_custom)` | Inserts a row into `lab_sections` |

The `lab_sections` table DDL (must exist before calling a lab router):

```sql
CREATE TABLE IF NOT EXISTS lab_sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lab_name TEXT NOT NULL,
    name TEXT NOT NULL,
    is_custom INTEGER NOT NULL DEFAULT 0,
    UNIQUE(lab_name, name)
);
```

### Frontend shared components

Each lab module imports these shared components via `@/` alias (resolves to `src/`):

| Import | Used for |
|---|---|
| `@/components/ui/AppIcon` | Heroicons wrapper |
| `@/components/common/LabCopilot` | AI sidebar |
| `@/components/lab/OnDemandSection` | Lazy section renderer |
| `@/components/lab/QuizCarousel` | Quiz UI |

Copy these four files/folders from the source project's `frontend/src/components/`.

---

## Exporting a single lab — step-by-step

Replace `dsa_lab` / `DSALabModule` with the appropriate lab name for CV or System Design.

### 1 — Backend

```bash
# Copy the module folder
cp -r backend/modules/dsa_lab  <target>/backend/modules/dsa_lab
```

Register the router in the target's `main.py`:

```python
from modules.dsa_lab.router import router as dsa_router
app.include_router(dsa_router)
```

Call `register` during startup so the DB table is created and seeded:

```python
from modules.dsa_lab.schema import register as dsa_register

@app.on_event("startup")
async def _startup():
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        dsa_register(cursor)          # creates dsa_topics table + seeds it
        # seed lab_sections from topic categories:
        cursor.execute("""
            INSERT OR IGNORE INTO lab_sections (lab_name, name, is_custom)
            SELECT DISTINCT 'dsa', category, 0 FROM dsa_topics WHERE is_custom = 0
        """)
        conn.commit()
    finally:
        conn.close()
```

That's it. The following REST endpoints will be live:

| Method | Path | Description |
|---|---|---|
| GET | `/dsa/topics` | List all DSA topics (seeded + custom) |
| POST | `/dsa/topics` | Add a custom DSA topic |
| GET | `/dsa/sections` | List DSA sections |
| POST | `/dsa/sections` | Add a custom DSA section |

For CV Lab use prefix `/cv` and lab_name `cv`.
For System Design Lab use prefix `/system-design` and lab_name `system_design`.

### 2 — Frontend (Next.js App Router)

```bash
# Copy the module folder
cp -r frontend/src/modules/dsa-lab  <target>/frontend/src/modules/dsa-lab

# Copy shared components (if not already present)
cp -r frontend/src/components/ui       <target>/frontend/src/components/ui
cp -r frontend/src/components/lab      <target>/frontend/src/components/lab
cp frontend/src/components/common/LabCopilot.tsx \
      <target>/frontend/src/components/common/
```

Create the Next.js route page at `app/dsa-lab/page.tsx`:

```tsx
import type { Metadata } from 'next';
import DSALabModule from '@/modules/dsa-lab/DSALabModule';
import Header from '@/components/common/Header';   // or your own header

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

Add the route to your navigation. Done.

---

## Minimal changes checklist

### For each exported lab, update these values in the module if needed:

| File | What to change | Default |
|---|---|---|
| `router.py` | API prefix string | `/dsa`, `/cv`, `/system-design` |
| `DSALabModule.tsx` | `BACKEND_URL` (if your API is not at `http://localhost:8000`) | reads from `process.env.NEXT_PUBLIC_API_URL` or falls back to `localhost:8000` |
| `types.ts` | Interface fields if your data model differs | DSATopic / CVTopic / SDTopic |

### Environment variable (frontend)

Set in `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Lab-specific notes

### DSA Lab
- **80 static fallback topics** in `fallbackTopics.ts` — used when the API is unreachable
- **16 section types**: prerequisites, theory, visual, implementation, hyperparameters, pitfalls, applications, interview, comparison, paper, quiz, references
- Topics carry LeetCode problem IDs in the `brief` field (format: `LC #560 [Medium] — ...`)

### CV Lab
- **35 seeded topics** across: Fundamentals, Classical CV, Geometry & Stereo, Deep Learning, Generative AI, Transformers & Attention, MLOps, Projects
- Topics include prerequisite chains — displayed in the Prerequisites section

### System Design Lab
- **50 seeded topics** across: Fundamentals, API & Microservices, System Design (HLD), Low-Level Design (LLD), Infrastructure & Ops
- Topics include a `scale` field (e.g. `100k+ RPS`) and an `isLLD` flag
- LLD topics are visually distinguished from HLD topics in the UI

---

## Adding a brand new lab

1. Create `backend/modules/<your_lab>/` with `__init__.py`, `schema.py`, `seed.py`, `router.py`
2. Create `frontend/src/modules/<your-lab>/` with `YourLabModule.tsx` and `types.ts`
3. Add `app.include_router(your_router)` in `main.py`
4. Call `your_register(cursor)` inside `init_db` in `lab_ninja/db.py`
5. Add the route page at `frontend/src/app/<your-lab>/page.tsx`
