from __future__ import annotations
import os, pathlib
from typing import Tuple, Optional
from git import Repo, InvalidGitRepositoryError, NoSuchPathError, GitCommandError
from github import Github

def ensure_repo() -> Optional[Repo]:
    try:
        repo = Repo(pathlib.Path.cwd())
        _ = repo.git_dir  # throws if not a repo
        return repo
    except (InvalidGitRepositoryError, NoSuchPathError):
        return None

def create_branch(repo: Repo, name: str):
    git = repo.git
    try:
        git.checkout("-b", name)
    except GitCommandError:
        git.checkout(name)

def commit_all(repo: Repo, message: str):
    repo.git.add(all=True)
    if repo.is_dirty():
        repo.index.commit(message)

def push_current(repo: Repo) -> Tuple[bool, Optional[str]]:
    try:
        origin = repo.remote(name="origin")
    except ValueError:
        return False, None
    try:
        r = origin.push()
        return True, str(r)
    except Exception:
        return False, None

def open_pr(title: str, body: str="") -> Tuple[bool, Optional[str]]:
    token = os.getenv("GITHUB_TOKEN")
    repo_full = os.getenv("GITHUB_REPO")
    if not token or not repo_full:
        return False, None
    g = Github(token)
    repo = g.get_repo(repo_full)
    default_branch = os.getenv("DEFAULT_BRANCH", "main")
    # Detect current branch from HEAD
    local_repo = ensure_repo()
    if local_repo is None:
        return False, None
    head = local_repo.active_branch.name
    if head == default_branch:
        return False, None
    pr = repo.create_pull(title=title, body=body, head=head, base=default_branch)
    return True, pr.html_url
