from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import List

from .agents import AGENTS, available_agents, detect_agents, get_agent
from .bootstrap import load_bootstrap
from .gitops import fetch_repo
from .install import install_for_agent
from .tui import run_wizard


def _print_detect(_: argparse.Namespace | None = None) -> int:
    print("Detected agent environments:\n")
    for spec, cmd_ok, dir_ok in detect_agents():
        cmd = "✅" if cmd_ok else "❌"
        d = "✅" if dir_ok else "❌"
        print(f"- {spec.name:9s} | cmd {cmd} | dir {d} | {spec.skills_dir}")
    return 0


def _build_prompt(agent_name: str, repo_input: str) -> str:
    repo = fetch_repo(repo_input, update=False)
    cfg = load_bootstrap(repo)
    t = cfg.self_learn.instruction_template
    return t.format(
        repo=repo_input,
        repo_local=str(repo),
        entry_skill=cfg.self_learn.entry_skill,
        agent=agent_name,
    )


def _print_install_report(report: dict) -> None:
    print("\n📋 Installation report")
    print(f"- Dry-run: {report['dry_run']}")
    print(f"- Repositories: {len(report['repos'])}")
    for r in report["repos"]:
        print(f"  • {r}")
    print(f"- Skills copied : {len(report['skills'])}")
    print(f"- Prompts copied: {len(report['prompts'])}")
    print(f"- Context copied: {len(report['contexts'])}")


def _run_agent_command(agent_name: str, prompt: str) -> int:
    spec = get_agent(agent_name)
    cmd = [spec.command, "-p", prompt]
    print("\n🤖 Running agent bootstrap command:")
    print(" ", " ".join(cmd))
    p = subprocess.run(cmd)
    return p.returncode


def _cmd_init(args: argparse.Namespace) -> int:
    agent = get_agent(args.agent)

    report = install_for_agent(
        root_repo_input=args.repo,
        agent=agent,
        dry_run=args.dry_run,
        update=(not args.no_update),
    )
    _print_install_report(report)

    prompt = _build_prompt(agent.name, args.repo)
    print("\n🧠 Bootstrap prompt:")
    print(prompt)

    if args.run_agent and not args.dry_run:
        return _run_agent_command(agent.name, prompt)

    return 0


def _cmd_prompt(args: argparse.Namespace) -> int:
    p = _build_prompt(args.agent, args.repo)
    print(p)
    return 0


def _cmd_tui(_: argparse.Namespace) -> int:
    selection = run_wizard(available_agents())
    ns = argparse.Namespace(
        agent=selection.agent,
        repo=selection.repo,
        dry_run=selection.dry_run,
        no_update=False,
        run_agent=selection.run_agent,
    )
    return _cmd_init(ns)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="isfna",
        description="Init Skills For New Agent — universal bootstrap for agent systems",
    )

    sub = parser.add_subparsers(dest="command")

    p_detect = sub.add_parser("detect", help="Detect installed agent systems")
    p_detect.set_defaults(func=_print_detect)

    p_init = sub.add_parser("init", help="Install bootstrap skills for target agent")
    p_init.add_argument("agent", choices=sorted(AGENTS.keys()))
    p_init.add_argument("--repo", default=".", help="Git URL or local path to bootstrap repo")
    p_init.add_argument("--dry-run", action="store_true", help="Show plan without copying files")
    p_init.add_argument("--no-update", action="store_true", help="Do not update already cached repos")
    p_init.add_argument("--run-agent", action="store_true", help="Run target agent with generated bootstrap prompt")
    p_init.set_defaults(func=_cmd_init)

    p_prompt = sub.add_parser("prompt", help="Print bootstrap prompt for target agent")
    p_prompt.add_argument("agent", choices=sorted(AGENTS.keys()))
    p_prompt.add_argument("--repo", default=".", help="Git URL or local path to bootstrap repo")
    p_prompt.set_defaults(func=_cmd_prompt)

    p_tui = sub.add_parser("tui", help="Run interactive setup wizard")
    p_tui.set_defaults(func=_cmd_tui)

    return parser


def main(argv: List[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    # shorthand: isfna pi [repo]
    if argv and argv[0] in AGENTS:
        agent = argv[0]
        repo = "."
        extra = []
        if len(argv) >= 2 and not argv[1].startswith("-"):
            repo = argv[1]
            extra = argv[2:]
        else:
            extra = argv[1:]

        parser = _build_parser()
        args = parser.parse_args(["init", agent, "--repo", repo, *extra])
        return args.func(args)

    parser = _build_parser()
    args = parser.parse_args(argv)

    if not getattr(args, "command", None):
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
