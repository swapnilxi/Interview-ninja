"""FastAPI backend for Interview-Ninja.

This service exposes HTTP endpoints for:
- Health checks
- Fetching previous questions (with filters)
- Exporting a day's questions in Markdown
- Creating sessions and persisting generated questions

The actual LLM/agent call is expected to happen in a separate
component or within additional endpoints you add later.
"""

from __future__ import annotations

from datetime import date
from typing import List, Literal, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from interview_ninja import __version__ as core_version
from interview_ninja.db import (
    Category,
    QuestionRecord,
    create_session,
    fetch_questions,
    insert_questions,
    init_db,
)
from interview_ninja.export_md import render_markdown_for_day


app = FastAPI(title="Interview-Ninja API", version=core_version)


@app.on_event("startup")
async def _startup() -> None:  # pragma: no cover - simple wiring
    init_db()


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


class QuestionBatchCreate(BaseModel):
    session_id: int
    questions: List[QuestionIn]


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "service": "interview-ninja-api",
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
    category: Optional[Category] = Query(
        default=None,
        description="Filter by category: interview | cv_skill. Omit for all.",
    ),
    session_date: Optional[str] = Query(
        default=None,
        description="Filter by question_date (YYYY-MM-DD).",
    ),
    topic: Optional[str] = Query(
        default=None,
        description="Optional topic token to filter on (e.g. cv_deep_learning).",
    ),
) -> List[QuestionOut]:
    records = list(
        fetch_questions(
            category=category,
            session_date=session_date,
            topic=topic,
        )
    )

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
            )
        )
    return out


@app.get("/export", response_model=str)
async def export_markdown(
    session_date: Optional[str] = Query(
        default=None,
        description=(
            "Date for which to export questions (YYYY-MM-DD). If omitted, "
            "today's date is used."
        ),
    ) -> str:
    if session_date is None:
        session_date = date.today().isoformat()

    records = list(fetch_questions(session_date=session_date))
    if not records:
        raise HTTPException(status_code=404, detail="No questions found for this date")

    return render_markdown_for_day(records, session_date=session_date)


# To run locally:
#   uvicorn backend.main:app --reload --port 8000
