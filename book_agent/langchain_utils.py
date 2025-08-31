from __future__ import annotations
import os
from typing import Optional
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

MODEL_ENV = os.getenv("MODEL_NAME", "gpt-4o")

def _model():
    # Uses OpenAI via langchain init_chat_model (works with openai>=1.*, langchain>=0.2.*)
    # Requires OPENAI_API_KEY in env.
    return init_chat_model(MODEL_ENV)

def generate_outline(synopsis: str, style_guide: str = "") -> str:
    llm = _model()
    messages = [
        SystemMessage(content="You draft concise, well-structured non-fiction book outlines in Markdown."),
        HumanMessage(content=f"Synopsis: {synopsis}\n\nStyle Guide (optional):\n{style_guide}\n\nReturn a detailed outline in Markdown with sections and bullets.")
    ]
    resp = llm.invoke(messages)
    return resp.content

def expand_chapter(chapter: int, target_words: int, outline: str, bible: str, style_guide: str = "") -> str:
    llm = _model()
    messages = [
        SystemMessage(content="You are a long-form book ghostwriter. Write in clean Markdown, no front-matter."),
        HumanMessage(content=(
            f"Use the outline and story bible to write Chapter {chapter}. Target length approx {target_words} words.\n\n"
            f"=== OUTLINE ===\n{outline}\n\n=== BIBLE ===\n{bible}\n\n=== STYLE GUIDE ===\n{style_guide}"
        ))
    ]
    resp = llm.invoke(messages)
    return f"# Chapter {chapter}\n\n{resp.content}"

def continuity_pass(manuscript_dir: str) -> str:
    # Simple placeholder that could be upgraded to run checks across chapters.
    return "## Continuity Notes\n\n- [TODO] Add name/place consistency checks.\n- [TODO] Flag time jumps or contradictions.\n"
