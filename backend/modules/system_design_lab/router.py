from __future__ import annotations
from typing import List
from fastapi import APIRouter
from pydantic import BaseModel, Field
from lab_ninja.db import fetch_lab_sections, save_lab_section
from .seed import fetch_system_design_topics, save_system_design_topic


router = APIRouter(prefix="/system-design", tags=["system-design-lab"])


class SDSubtopicIn(BaseModel):
    id: str
    name: str
    brief: str


class SDTopicIn(BaseModel):
    id: str
    name: str
    brief: str
    category: str
    scale: str
    difficulty: str
    isLLD: bool = False
    subtopics: List[SDSubtopicIn] = Field(default_factory=list)


class LabSectionIn(BaseModel):
    name: str
    isCustom: bool = True


@router.get("/topics")
async def get_system_design_topics() -> List[dict]:
    return fetch_system_design_topics()


@router.post("/topics")
async def save_system_design_topic_endpoint(payload: SDTopicIn) -> dict:
    save_system_design_topic(payload.model_dump())
    return {"status": "success"}


@router.get("/sections")
async def get_system_design_sections() -> List[dict]:
    return fetch_lab_sections("system_design")


@router.post("/sections")
async def save_system_design_section(payload: LabSectionIn) -> dict:
    save_lab_section("system_design", payload.name, 1 if payload.isCustom else 0)
    return {"status": "success"}
