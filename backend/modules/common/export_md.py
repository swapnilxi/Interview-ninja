from typing import List
from modules.common.db import QuestionRecord


def render_markdown_for_day(records: List[QuestionRecord], session_date: str) -> str:
    """Format today's interview/CV questions as Markdown."""
    lines = []
    lines.append(f"# Lab-Ninja Daily Questions - {session_date}")
    lines.append("")

    section_a = [r for r in records if r.section.upper() == "A"]
    section_b = [r for r in records if r.section.upper() == "B"]

    section_a.sort(key=lambda r: r.number)
    section_b.sort(key=lambda r: r.number)

    if section_a:
        lines.append("## Section A — Core Interview Track")
        lines.append("")
        for r in section_a:
            topics_str = ", ".join(t.strip() for t in r.topics.split(",") if t.strip())
            lines.append(f"### {r.number}. {r.sub_type} ({r.difficulty})")
            if topics_str:
                lines.append(f"**Topics**: *{topics_str}*")
                lines.append("")
            lines.append(r.question_text)
            lines.append("")

    if section_b:
        lines.append("## Section B — Computer Vision Excellence Track")
        lines.append("")
        for r in section_b:
            topics_str = ", ".join(t.strip() for t in r.topics.split(",") if t.strip())
            lines.append(f"### {r.number}. {r.sub_type} ({r.difficulty})")
            if topics_str:
                lines.append(f"**Topics**: *{topics_str}*")
                lines.append("")
            lines.append(r.question_text)
            lines.append("")

    return "\n".join(lines)
