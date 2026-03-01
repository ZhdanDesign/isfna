from __future__ import annotations

from pathlib import Path
import re
import subprocess


CACHE_DIR = Path.home() / ".isfna/cache"


def _run(cmd: list[str], cwd: Path | None = None) -> None:
    p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{p.stderr.strip()}")


def _repo_slug(repo: str) -> str:
    repo = repo.strip()
    repo = repo.replace("https://", "").replace("http://", "")
    repo = repo.replace("git@", "")
    repo = repo.replace(":", "/")
    repo = repo.replace(".git", "")
    repo = re.sub(r"[^a-zA-Z0-9._/-]+", "-", repo)
    repo = repo.strip("/-")
    return repo.replace("/", "__")[:180]


def fetch_repo(repo: str, ref: str = "main", update: bool = True) -> Path:
    """
    repo can be local path or git URL.
    """
    p = Path(repo).expanduser()
    if p.exists() and p.is_dir():
        return p.resolve()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    slug = _repo_slug(repo)
    dest = CACHE_DIR / slug

    if not dest.exists():
        _run(["git", "clone", "--depth", "1", "--branch", ref, repo, str(dest)])
        return dest

    if update:
        _run(["git", "fetch", "--all", "--prune"], cwd=dest)
        _run(["git", "checkout", ref], cwd=dest)
        _run(["git", "pull", "--ff-only", "origin", ref], cwd=dest)

    return dest
