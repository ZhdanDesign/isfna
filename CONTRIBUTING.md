# Contributing to isfna

Спасибо за вклад в `isfna`.

## Local setup

```bash
git clone https://github.com/ZhdanDesign/isfna.git
cd isfna
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -e .
```

## Minimal verification before PR

```bash
python3 -m py_compile src/isfna/*.py
isfna detect
isfna prompt pi --repo .
isfna init pi --repo . --dry-run
```

## Commit & PR guidelines

- Keep changes focused and minimal.
- Update docs when behavior changes.
- If bootstrap logic changes, include a short validation note in PR description.
- Use clear commit messages (`feat:`, `fix:`, `docs:`, `chore:`).

## Security notes

- Do not commit secrets/tokens.
- Treat third-party skill repositories as privileged input.
- Prefer `--dry-run` first when testing unknown repositories.
