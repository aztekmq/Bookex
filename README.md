# Book Codex Agent

A working starter kit for a **Custom “Codex‑style” Book Agent** that connects to **GitHub** and uses **ChatGPT via LangChain** (AutoGPT‑ish planning, Git branches/PRs, and a CLI).

## What you get

- **LangChain + ChatGPT (OpenAI)** for outline + chapter drafting
- **AutoGPT‑style controller** to run “outline”, “expand”, and “continuity” passes
- **Git integration** (create branch, commit, push)
- **GitHub PRs** (open pull requests automatically)
- **Typer CLI**: `book-agent init | outline | expand | continuity | branch | commit | pr`
- **Prompts** for outline & chapter expansion + a sample **style guide**
- Starter **manuscript/** with `outline.md`, `bible.md`, and `chapters/ch01.md`
- Optional **GitHub Action** to lint Markdown on PRs

## Quickstart

```bash
# 1) Install
pip install -e .

# 2) Configure
cp .env.example .env
# then edit .env with your keys
# OPENAI_API_KEY=...
# GITHUB_TOKEN=...
# GITHUB_REPO=owner/repo
# DEFAULT_BRANCH=main
# MODEL_NAME=gpt-4o

# 3) Initialize and outline
book-agent init
book-agent outline --synopsis "One-liner of your book…"

# 4) Draft a chapter
book-agent branch --name draft/ch01
book-agent expand --chapter 1 --target-words 1500
book-agent commit --message "draft: ch01"
book-agent pr --title "Draft Chapter 1" --body "Adds ch01 draft"
```

## Notes

- If you don’t have Git set up, commands will no‑op with helpful messages.
- GitHub PR creation requires `GITHUB_TOKEN` with `repo` scope and `GITHUB_REPO=owner/name`.
- The LLM calls are modular (see `book_agent/langchain_utils.py`)—swap in your provider easily.
