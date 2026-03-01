from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
from typing import Dict, List, Any


BOOTSTRAP_FILENAME = "isfna.bootstrap.json"


@dataclass
class SourceRef:
    url: str
    ref: str = "main"


@dataclass
class TargetConfig:
    skill_paths: List[str] = field(default_factory=lambda: ["skills"])
    prompt_paths: List[str] = field(default_factory=lambda: ["prompts"])
    context_files: List[str] = field(default_factory=lambda: ["AGENTS.md"])


@dataclass
class SelfLearnConfig:
    entry_skill: str = "skills/master-init/SKILL.md"
    instruction_template: str = (
        "Прочти репозиторий {repo} и начни с {entry_skill}. "
        "Построй план инициализации навыков для {agent}, установи релевантное и выдай отчёт."
    )


@dataclass
class BootstrapConfig:
    version: int = 1
    name: str = "unnamed"
    sources: List[SourceRef] = field(default_factory=list)
    targets: Dict[str, TargetConfig] = field(default_factory=dict)
    self_learn: SelfLearnConfig = field(default_factory=SelfLearnConfig)

    def target_for(self, agent: str) -> TargetConfig:
        key = (agent or "").strip().lower()
        if key in self.targets:
            return self.targets[key]
        if "*" in self.targets:
            return self.targets["*"]
        return TargetConfig()


def _as_target_config(raw: Dict[str, Any]) -> TargetConfig:
    return TargetConfig(
        skill_paths=list(raw.get("skillPaths", ["skills"])),
        prompt_paths=list(raw.get("promptPaths", ["prompts"])),
        context_files=list(raw.get("contextFiles", ["AGENTS.md"])),
    )


def load_bootstrap(repo_root: Path) -> BootstrapConfig:
    path = repo_root / BOOTSTRAP_FILENAME
    if not path.exists():
        # implicit defaults
        return BootstrapConfig(name=repo_root.name, targets={"*": TargetConfig()})

    raw = json.loads(path.read_text(encoding="utf-8"))

    sources = [
        SourceRef(url=s.get("url", ""), ref=s.get("ref", "main"))
        for s in raw.get("sources", [])
        if s.get("url")
    ]

    targets: Dict[str, TargetConfig] = {}
    for name, cfg in raw.get("targets", {}).items():
        targets[name.strip().lower()] = _as_target_config(cfg or {})

    sl = raw.get("selfLearn", {}) or {}
    self_learn = SelfLearnConfig(
        entry_skill=sl.get("entrySkill", "skills/master-init/SKILL.md"),
        instruction_template=sl.get(
            "instructionTemplate",
            SelfLearnConfig().instruction_template,
        ),
    )

    return BootstrapConfig(
        version=int(raw.get("version", 1)),
        name=str(raw.get("name", repo_root.name)),
        sources=sources,
        targets=targets or {"*": TargetConfig()},
        self_learn=self_learn,
    )
