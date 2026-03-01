from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Dict, List, Optional


@dataclass(frozen=True)
class AgentSpec:
    name: str
    label: str
    command: str
    skills_dir: Path
    prompts_dir: Optional[Path] = None


HOME = Path.home()

AGENTS: Dict[str, AgentSpec] = {
    "pi": AgentSpec(
        name="pi",
        label="Pi",
        command="pi",
        skills_dir=HOME / ".pi/agent/skills",
        prompts_dir=HOME / ".pi/agent/prompts",
    ),
    "codex": AgentSpec(
        name="codex",
        label="OpenAI Codex",
        command="codex",
        skills_dir=HOME / ".codex/skills",
    ),
    "claude": AgentSpec(
        name="claude",
        label="Claude Code",
        command="claude",
        skills_dir=HOME / ".claude/skills",
    ),
    "gemini": AgentSpec(
        name="gemini",
        label="Gemini CLI",
        command="gemini",
        skills_dir=HOME / ".gemini/skills",
    ),
    "opencode": AgentSpec(
        name="opencode",
        label="OpenCode",
        command="opencode",
        skills_dir=HOME / ".config/opencode/skills",
    ),
    "openclaw": AgentSpec(
        name="openclaw",
        label="OpenClaw",
        command="openclaw",
        skills_dir=HOME / ".openclaw/skills",
    ),
}


def get_agent(name: str) -> AgentSpec:
    key = (name or "").strip().lower()
    if key not in AGENTS:
        raise KeyError(f"Unknown agent: {name}")
    return AGENTS[key]


def detect_agents() -> List[tuple[AgentSpec, bool, bool]]:
    """
    Returns list of tuples: (agent, command_found, dir_exists)
    """
    rows = []
    for spec in AGENTS.values():
        cmd_ok = shutil.which(spec.command) is not None
        dir_ok = spec.skills_dir.exists()
        rows.append((spec, cmd_ok, dir_ok))
    return rows


def available_agents() -> List[AgentSpec]:
    out: List[AgentSpec] = []
    for spec, cmd_ok, dir_ok in detect_agents():
        if cmd_ok or dir_ok:
            out.append(spec)
    return out
