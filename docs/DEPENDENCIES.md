# Dynamic dependencies via `sources[]`

`isfna` supports recursive skill-pack composition.

Example:

```json
{
  "version": 1,
  "name": "my-agent-pack",
  "sources": [
    { "url": "https://github.com/org/common-skills", "ref": "main" },
    { "url": "https://github.com/org/security-skills", "ref": "stable" }
  ],
  "targets": {
    "*": { "skillPaths": ["skills"] },
    "pi": { "skillPaths": ["skills/pi", "skills/common"] }
  }
}
```

Resolution rules:
1. Root repo first.
2. Each source repo is fetched and parsed for its own `isfna.bootstrap.json`.
3. Graph traversal is recursive with cycle protection.
4. For each node: target config is selected by agent key, fallback to `*`.
