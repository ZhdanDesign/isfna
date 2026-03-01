from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .agents import AgentSpec


@dataclass
class WizardSelection:
    agent: str
    repo: str
    dry_run: bool
    run_agent: bool


def _ask_choice(title: str, options: List[str], default_idx: int = 0) -> int:
    print(f"\n{title}")
    for i, opt in enumerate(options, 1):
        marker = "*" if (i - 1) == default_idx else " "
        print(f"  {marker} {i}. {opt}")

    raw = input(f"Choose [1-{len(options)}] (default {default_idx+1}): ").strip()
    if not raw:
        return default_idx
    try:
        idx = int(raw) - 1
    except ValueError:
        return default_idx
    if 0 <= idx < len(options):
        return idx
    return default_idx


def run_wizard(available: List[AgentSpec]) -> WizardSelection:
    if not available:
        raise RuntimeError("No agents detected. Install at least one CLI (pi/codex/claude/...).")

    idx = _ask_choice(
        "🚀 Select target agent:",
        [f"{a.label} ({a.name})" for a in available],
        default_idx=0,
    )
    agent = available[idx].name

    repo = input("\n📦 Repository URL or local path [default: .]: ").strip() or "."

    mode = _ask_choice(
        "\n🧪 Execution mode:",
        [
            "Install now",
            "Dry-run (show planned changes only)",
            "Install + run target agent with bootstrap prompt",
        ],
        default_idx=0,
    )

    dry_run = mode == 1
    run_agent = mode == 2

    print("\n✅ Summary:")
    print(f"  Agent   : {agent}")
    print(f"  Repo    : {repo}")
    print(f"  Dry-run : {dry_run}")
    print(f"  Run CLI : {run_agent}")

    ok = input("\nProceed? [Y/n]: ").strip().lower()
    if ok in {"n", "no"}:
        raise RuntimeError("Canceled by user")

    return WizardSelection(agent=agent, repo=repo, dry_run=dry_run, run_agent=run_agent)
