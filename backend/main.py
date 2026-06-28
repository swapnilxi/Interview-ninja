"""FastAPI backend for Lab-Ninja.

This service exposes HTTP endpoints for:
- Health checks
- Fetching previous questions (with filters)
- Exporting a day's questions in Markdown
- Creating sessions and persisting generated questions
- Updating question performance ratings
- Saving and fetching daily session answers
- Managing API models and key settings
- Lab-specific endpoints are served by pluggable module routers
"""

from __future__ import annotations

from datetime import date
from typing import List, Literal, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from lab_ninja import __version__ as core_version
from lab_ninja.db import (
    Category,
    QuestionRecord,
    create_session,
    fetch_questions,
    insert_questions,
    init_db,
    update_question_performance,
    save_session_progress,
    fetch_session_progress,
    fetch_progress_stats,
    fetch_settings,
    save_settings,
)
from lab_ninja.export_md import render_markdown_for_day

# Lab module routers
from modules.dsa_lab.router import router as dsa_router
from modules.cv_lab.router import router as cv_router
from modules.system_design_lab.router import router as sd_router


app = FastAPI(title="Lab-Ninja API", version=core_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register lab module routers
app.include_router(dsa_router)
app.include_router(cv_router)
app.include_router(sd_router)


@app.on_event("startup")
async def _startup() -> None:  # pragma: no cover
    init_db()


# ── Pydantic models ──────────────────────────────────────────────────────────

class SessionCreate(BaseModel):
    difficulty_hint: Optional[str] = Field(
        default=None, description="Optional difficulty hint: easy, medium, hard, mixed."
    )
    cv_present: bool = Field(
        default=False,
        description="True if CV text or file was provided for this session.",
    )
    jd_present: bool = Field(
        default=False,
        description="True if a job description was provided for this session.",
    )


class SessionCreateResponse(BaseModel):
    session_id: int
    session_date: str


class QuestionIn(BaseModel):
    section: Literal["A", "B"]
    number: int
    category: Category
    sub_type: str
    difficulty: str
    topics: List[str] = Field(default_factory=list)
    question_text: str
    question_type: Optional[str] = None


class QuestionOut(BaseModel):
    id: int
    session_id: int
    question_date: str
    section: str
    number: int
    category: Category
    sub_type: str
    difficulty: str
    topics: List[str]
    question_text: str
    user_performance: Optional[int] = None
    last_reviewed: Optional[str] = None
    question_type: Optional[str] = None


class QuestionBatchCreate(BaseModel):
    session_id: int
    questions: List[QuestionIn]


class PerformanceUpdatePayload(BaseModel):
    user_performance: int


class SessionAnswerIn(BaseModel):
    questionId: Optional[str] = None
    questionText: str
    answerText: str
    category: str
    difficulty: str
    questionType: str
    isCompleted: bool
    sessionDate: str


class UserSettingsSchema(BaseModel):
    questionModel: str
    answerModel: str
    openaiKey: str
    geminiKey: str
    anthropicKey: str


# ── Core endpoints ────────────────────────────────────────────────────────────

@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "service": "lab-ninja-api",
        "version": core_version,
    }


@app.post("/sessions", response_model=SessionCreateResponse)
async def create_session_endpoint(payload: SessionCreate) -> SessionCreateResponse:
    session_date = date.today().isoformat()
    session_id = create_session(
        session_date=session_date,
        difficulty_hint=payload.difficulty_hint,
        cv_present=payload.cv_present,
        jd_present=payload.jd_present,
    )
    return SessionCreateResponse(session_id=session_id, session_date=session_date)


@app.post("/sessions/questions")
async def persist_questions(payload: QuestionBatchCreate) -> dict:
    if not payload.questions:
        raise HTTPException(status_code=400, detail="questions list must not be empty")

    ids = insert_questions(
        session_id=payload.session_id,
        questions=[q.model_dump() for q in payload.questions],
    )
    return {"inserted_ids": ids}


@app.get("/questions", response_model=List[QuestionOut])
async def list_questions(
    category: Optional[Category] = Query(default=None),
    session_date: Optional[str] = Query(default=None),
    topic: Optional[str] = Query(default=None),
) -> List[QuestionOut]:
    records = list(fetch_questions(category=category, session_date=session_date, topic=topic))

    out: List[QuestionOut] = []
    for r in records:
        topics = [t for t in (r.topics or "").split(",") if t]
        out.append(
            QuestionOut(
                id=r.id or 0,
                session_id=r.session_id,
                question_date=r.question_date,
                section=r.section,
                number=r.number,
                category=r.category,  # type: ignore[arg-type]
                sub_type=r.sub_type,
                difficulty=r.difficulty,
                topics=topics,
                question_text=r.question_text,
                user_performance=r.user_performance,
                last_reviewed=r.last_reviewed,
                question_type=r.question_type or r.sub_type,
            )
        )
    return out


@app.patch("/questions/{question_id}/performance")
async def update_performance_endpoint(question_id: int, payload: PerformanceUpdatePayload) -> dict:
    update_question_performance(
        question_id=question_id,
        user_performance=payload.user_performance,
        last_reviewed=date.today().isoformat(),
    )
    return {"status": "success"}


@app.post("/session-progress")
async def save_session_progress_endpoint(payload: List[SessionAnswerIn]) -> dict:
    save_session_progress([item.model_dump() for item in payload])
    return {"status": "success"}


@app.get("/session-progress")
async def get_session_progress_endpoint(session_date: str = Query(...)) -> List[dict]:
    return fetch_session_progress(session_date)


@app.get("/session-progress/stats")
async def get_progress_stats_endpoint() -> dict:
    return fetch_progress_stats()


@app.get("/settings", response_model=UserSettingsSchema)
async def get_settings_endpoint() -> UserSettingsSchema:
    return UserSettingsSchema(**fetch_settings())


@app.post("/settings")
async def save_settings_endpoint(payload: UserSettingsSchema) -> dict:
    save_settings(payload.model_dump())
    return {"status": "success"}


@app.get("/export", response_model=str)
async def export_markdown(
    session_date: Optional[str] = Query(default=None),
) -> str:
    if session_date is None:
        session_date = date.today().isoformat()

    records = list(fetch_questions(session_date=session_date))
    if not records:
        raise HTTPException(status_code=404, detail="No questions found for this date")

    return render_markdown_for_day(records, session_date=session_date)


# To run locally:
#   uvicorn backend.main:app --reload --port 8000
#   or from backend/: uvicorn main:app --reload --port 8000
