# isfna — Init Skills For New Agent

`isfna` — универсальный bootstrap-CLI + набор стартовых навыков для быстрой инициализации **любой агентной или мультиагентной системы** одной командой.

Идея: вместо «хранилища всех скиллов мира» даём агенту **мета-навык самообучения**, который:
- читает `isfna.bootstrap.json`;
- рекурсивно подтягивает зависимости (другие репозитории);
- выбирает релевантные навыки под текущую платформу;
- устанавливает минимально нужное;
- выдаёт проверяемый отчёт.

---

## One-command UX

```bash
isfna pi --repo https://github.com/<you>/<repo>
```

или сокращённо:

```bash
isfna pi https://github.com/<you>/<repo>
```

После установки `isfna` автоматически покажет «первую инструкцию» (bootstrap prompt), которую можно скормить агенту.

---

## Что уже есть в этом репо

- `skills/master-init/SKILL.md` — Master Init Skill (ядро самообучения)
- `skills/self-learning-loop/SKILL.md` — цикл эволюции навыков через eval
- `isfna.bootstrap.json` — манифест bootstrap + зависимости
- Python CLI `isfna` (TUI/wizard, detect, init, prompt)
- `docs/DEPENDENCIES.md` — как работает рекурсивный dependency graph

---

## Быстрый старт (локально)

### Вариант A: запуск без установки пакета

```bash
~/Projects/isfna/bin/isfna detect
```

### Вариант B: установить как пакет

```bash
cd ~/Projects/isfna
python3 -m pip install -e .
isfna detect
```

---

## Команды CLI

### 1) Определить доступные агентные системы

```bash
isfna detect
```

### 2) Инициализировать конкретного агента

```bash
isfna init pi --repo <url-or-local-path>
```

Опции:
- `--dry-run` — показать, что будет установлено, без копирования
- `--no-update` — не делать `git pull/fetch` для уже скачанных зависимостей
- `--run-agent` — сразу запустить целевого агента с bootstrap prompt

### 3) Сгенерировать только bootstrap prompt

```bash
isfna prompt pi --repo <url-or-local-path>
```

### 4) Интерактивный TUI/wizard

```bash
isfna tui
```

### 5) Short mode

```bash
isfna pi --repo <url-or-local-path>
```

---

## Структура `isfna.bootstrap.json`

```json
{
  "version": 1,
  "name": "my-skill-pack",
  "sources": [
    { "url": "https://github.com/org/shared-skills", "ref": "main" }
  ],
  "targets": {
    "*": {
      "skillPaths": ["skills"],
      "promptPaths": ["prompts"],
      "contextFiles": ["AGENTS.md"]
    },
    "pi": {
      "skillPaths": ["skills/pi", "skills/common"]
    }
  },
  "selfLearn": {
    "entrySkill": "skills/master-init/SKILL.md",
    "instructionTemplate": "Прочти {repo} ..."
  }
}
```

---

## Как работает dependency graph

`isfna`:
1. Берёт root repo (локальный путь или git URL)
2. Читает `isfna.bootstrap.json`
3. Рекурсивно обходит `sources[]`
4. Для каждой ноды графа берёт target-конфиг (`agent` или `*`)
5. Копирует skills/prompts/context в директории целевого агента

Кэш репозиториев хранится в `~/.isfna/cache`.

---

## Поддерживаемые агенты (из коробки)

- `pi`
- `codex`
- `claude`
- `gemini`
- `opencode`
- `openclaw`

Если агент не найден по бинарю, но есть его skill-директория — он тоже считается доступным.

---

## Безопасность

- Любые skills = исполняемые инструкции для агента.
- Перед установкой из внешних репо проверяй содержимое.
- Для CI лучше включать `--dry-run` на первом проходе.

---

## Дорожная карта

- policy-фильтры доверенных источников
- подписи/хэши bootstrap-манифестов
- registry-плагины для AgenticSkills / SkillsIndex / FindMCP
- richer TUI (Textual)

---

## Лицензия

MIT
