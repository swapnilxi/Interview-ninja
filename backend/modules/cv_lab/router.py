from __future__ import annotations
from typing import List
from fastapi import APIRouter
from pydantic import BaseModel, Field
from modules.common.db import fetch_lab_sections, save_lab_section
from .seed import fetch_cv_topics, save_cv_topic


router = APIRouter(prefix="/cv", tags=["cv-lab"])


class CVSubtopicIn(BaseModel):
    id: str
    name: str
    brief: str


class CVTopicIn(BaseModel):
    id: str
    name: str
    brief: str
    category: str
    difficulty: str
    prerequisites: List[str] = Field(default_factory=list)
    subtopics: List[CVSubtopicIn] = Field(default_factory=list)


class LabSectionIn(BaseModel):
    name: str
    isCustom: bool = True


@router.get("/topics")
async def get_cv_topics() -> List[dict]:
    return fetch_cv_topics()


@router.post("/topics")
async def save_cv_topic_endpoint(payload: CVTopicIn) -> dict:
    save_cv_topic(payload.model_dump())
    return {"status": "success"}


@router.get("/sections")
async def get_cv_sections() -> List[dict]:
    return fetch_lab_sections("cv")


@router.post("/sections")
async def save_cv_section(payload: LabSectionIn) -> dict:
    save_lab_section("cv", payload.name, 1 if payload.isCustom else 0)
    return {"status": "success"}
