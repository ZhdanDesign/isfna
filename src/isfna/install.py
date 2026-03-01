from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import shutil
from typing import Dict, List, Set, Tuple

from .agents import AgentSpec
from .bootstrap import BootstrapConfig, TargetConfig, load_bootstrap
from .gitops import fetch_repo


@dataclass
class InstallStats:
    skills: List[str] = field(default_factory=list)
    prompts: List[str] = field(default_factory=list)
    contexts: List[str] = field(default_factory=list)


def _copy_dir(src: Path, dst: Path, dry_run: bool) -> None:
    if dry_run:
        return
    shutil.copytree(src, dst, dirs_exist_ok=True)


def _copy_file(src: Path, dst: Path, dry_run: bool) -> None:
    if dry_run:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _discover_skill_dirs(base: Path) -> List[Path]:
    out: List[Path] = []
    if not base.exists() or not base.is_dir():
        return out

    # 1) recursive directories containing SKILL.md
    for skill_md in sorted(base.rglob("SKILL.md")):
        out.append(skill_md.parent)

    # 2) top-level markdown files become single-file skills
    for md in sorted(base.glob("*.md")):
        out.append(md)

    # deduplicate preserving order
    seen: Set[str] = set()
    uniq: List[Path] = []
    for p in out:
        k = str(p.resolve()) if p.exists() else str(p)
        if k in seen:
            continue
        seen.add(k)
        uniq.append(p)
    return uniq


def _install_from_repo(
    repo: Path,
    target_cfg: TargetConfig,
    agent: AgentSpec,
    dry_run: bool,
) -> InstallStats:
    stats = InstallStats()

    agent.skills_dir.mkdir(parents=True, exist_ok=True)
    if agent.prompts_dir:
        agent.prompts_dir.mkdir(parents=True, exist_ok=True)

    # skills
    for rel in target_cfg.skill_paths:
        base = repo / rel
        for item in _discover_skill_dirs(base):
            if item.is_dir():
                dst = agent.skills_dir / item.name
                _copy_dir(item, dst, dry_run=dry_run)
                stats.skills.append(f"{item} -> {dst}")
            elif item.is_file() and item.suffix.lower() == ".md":
                dst = agent.skills_dir / item.name
                _copy_file(item, dst, dry_run=dry_run)
                stats.skills.append(f"{item} -> {dst}")

    # prompts
    if agent.prompts_dir:
        for rel in target_cfg.prompt_paths:
            base = repo / rel
            if not base.exists() or not base.is_dir():
                continue
            for md in sorted(base.glob("*.md")):
                dst = agent.prompts_dir / md.name
                _copy_file(md, dst, dry_run=dry_run)
                stats.prompts.append(f"{md} -> {dst}")

    # context files
    for rel in target_cfg.context_files:
        src = repo / rel
        if not src.exists() or not src.is_file():
            continue
        dst = agent.skills_dir.parent / src.name
        _copy_file(src, dst, dry_run=dry_run)
        stats.contexts.append(f"{src} -> {dst}")

    return stats


def resolve_repo_graph(root_repo_input: str, update: bool = True) -> List[Tuple[Path, BootstrapConfig]]:
    root = fetch_repo(root_repo_input, update=update)
    root_cfg = load_bootstrap(root)

    ordered: List[Tuple[Path, BootstrapConfig]] = []
    visited: Set[str] = set()

    def dfs(repo: Path, cfg: BootstrapConfig) -> None:
        key = str(repo.resolve())
        if key in visited:
            return
        visited.add(key)
        ordered.append((repo, cfg))

        for src in cfg.sources:
            child_repo = fetch_repo(src.url, ref=src.ref, update=update)
            child_cfg = load_bootstrap(child_repo)
            dfs(child_repo, child_cfg)

    dfs(root, root_cfg)
    return ordered


def install_for_agent(
    root_repo_input: str,
    agent: AgentSpec,
    dry_run: bool = False,
    update: bool = True,
) -> Dict:
    graph = resolve_repo_graph(root_repo_input, update=update)

    aggregate = InstallStats()
    details = []

    for repo, cfg in graph:
        tcfg = cfg.target_for(agent.name)
        stats = _install_from_repo(repo, tcfg, agent, dry_run=dry_run)
        aggregate.skills.extend(stats.skills)
        aggregate.prompts.extend(stats.prompts)
        aggregate.contexts.extend(stats.contexts)
        details.append(
            {
                "repo": str(repo),
                "bootstrap": cfg.name,
                "skills": len(stats.skills),
                "prompts": len(stats.prompts),
                "contexts": len(stats.contexts),
            }
        )

    return {
        "repos": [str(r) for r, _ in graph],
        "details": details,
        "skills": aggregate.skills,
        "prompts": aggregate.prompts,
        "contexts": aggregate.contexts,
        "dry_run": dry_run,
    }
