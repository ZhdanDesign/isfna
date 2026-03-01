# Testing isfna

## Local quick checks

```bash
python3 -m py_compile src/isfna/*.py
isfna detect
isfna prompt pi --repo .
isfna init pi --repo . --dry-run
```

## Container smoke (Podman or Docker)

Script auto-detects runtime:

```bash
./scripts/container-smoke.sh
```

Stages:
1. **isfna-only smoke** in Python container
2. **pi + isfna integration** in Node container (installs `pi`, runs `isfna init pi`)

If Podman is installed, it is preferred automatically.
