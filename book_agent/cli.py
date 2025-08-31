from __future__ import annotations
import os, sys, subprocess, json, shutil, pathlib
import typer
from rich import print
from dotenv import load_dotenv
from typing import Optional

from .langchain_utils import generate_outline, expand_chapter, continuity_pass
from .git_utils import ensure_repo, create_branch, commit_all, push_current, open_pr

app = typer.Typer(help="Codex-style Book Agent CLI")

ROOT = pathlib.Path.cwd()
MANUSCRIPT = ROOT / "manuscript"
CHAPTERS = MANUSCRIPT / "chapters"
PROMPTS = pathlib.Path(__file__).parent / "prompts"

def require_file(p: pathlib.Path):
    if not p.exists():
        typer.echo(f"[!] Required file missing: {p}")
        raise typer.Exit(1)

@app.callback()
def main():
    load_dotenv()

@app.command()
def init():
    """Create starter manuscript + prompts."""
    MANUSCRIPT.mkdir(exist_ok=True)
    CHAPTERS.mkdir(parents=True, exist_ok=True)
    (MANUSCRIPT / "outline.md").write_text("# Outline\n\n- TBD\n", encoding="utf-8")
    (MANUSCRIPT / "bible.md").write_text("# Story Bible\n\n- Canon facts\n", encoding="utf-8")
    (CHAPTERS / "ch01.md").write_text("# Chapter 1\n\nDraft here...\n", encoding="utf-8")
    print(":sparkles: Created manuscript skeleton.")
    # copy prompts on init for convenience
    user_prompts = ROOT / "prompts"
    user_prompts.mkdir(exist_ok=True)
    for f in PROMPTS.glob("*.md"):
        target = user_prompts / f.name
        if not target.exists():
            target.write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
    print(":memo: Copied prompt templates to ./prompts")

@app.command()
def outline(synopsis: str = typer.Option(..., help="One-liner/short synopsis")):
    """Generate/refresh manuscript/outline.md using the LLM."""
    require_file(MANUSCRIPT / "bible.md")
    style = (ROOT / "prompts" / "style_guide.md").read_text(encoding="utf-8") if (ROOT / "prompts" / "style_guide.md").exists() else ""
    result = generate_outline(synopsis=synopsis, style_guide=style)
    (MANUSCRIPT / "outline.md").write_text(result, encoding="utf-8")
    print(":pencil: Wrote manuscript/outline.md")

@app.command()
def expand(chapter: int = typer.Option(..., min=1), target_words: int = typer.Option(1200, help="Approx target words")):
    """Draft a chapter using outline + bible."""
    require_file(MANUSCRIPT / "outline.md")
    require_file(MANUSCRIPT / "bible.md")
    outline_md = (MANUSCRIPT / "outline.md").read_text(encoding="utf-8")
    bible_md = (MANUSCRIPT / "bible.md").read_text(encoding="utf-8")
    style = (ROOT / "prompts" / "style_guide.md").read_text(encoding="utf-8") if (ROOT / "prompts" / "style_guide.md").exists() else ""
    draft = expand_chapter(chapter=chapter, target_words=target_words, outline=outline_md, bible=bible_md, style_guide=style)
    fname = CHAPTERS / f"ch{chapter:02d}.md"
    fname.parent.mkdir(parents=True, exist_ok=True)
    fname.write_text(draft, encoding="utf-8")
    print(f":books: Wrote {fname}")

@app.command()
def continuity():
    """Run a simple continuity pass and append notes to manuscript/bible.md."""
    require_file(MANUSCRIPT / "bible.md")
    notes = continuity_pass(manuscript_dir=str(MANUSCRIPT))
    (MANUSCRIPT / "bible.md").write_text((MANUSCRIPT / "bible.md").read_text(encoding="utf-8") + "\n\n" + notes, encoding="utf-8")
    print(":mag: Continuity notes appended to manuscript/bible.md")

@app.command()
def branch(name: str = typer.Option(..., help="Branch name")):
    repo = ensure_repo()
    if repo is None:
        print("[yellow]Git not available or not a repo; skipping.[/yellow]")
        raise typer.Exit()
    create_branch(repo, name)
    print(f":seedling: Switched to branch {name}")

@app.command()
def commit(message: str = typer.Option(..., help="Commit message")):
    repo = ensure_repo()
    if repo is None:
        print("[yellow]Git not available or not a repo; skipping.[/yellow]")
        raise typer.Exit()
    commit_all(repo, message)
    print(":white_check_mark: Committed changes.")

@app.command()
def pr(title: str = typer.Option(...), body: str = typer.Option("")):
    repo = ensure_repo()
    if repo is None:
        print("[yellow]Git not available or not a repo; skipping.[/yellow]")
        raise typer.Exit()
    ok, url = push_current(repo)
    if not ok:
        print("[red]Push failed—check remote.[/red]")
        raise typer.Exit(1)
    created, pr_url = open_pr(title=title, body=body)
    if created:
        print(f":link: Opened PR: {pr_url}")
    else:
        print("[red]Failed to open PR—check GITHUB_TOKEN/GITHUB_REPO.[/red]")
