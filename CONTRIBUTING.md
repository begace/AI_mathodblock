# Contributing

Thanks for improving MethodBlock Registry.

## Contribution Rules

- Edit source YAML under `methodblocks/`; do not hand-edit generated files in `compiled/`.
- Keep v0.1 MethodBlocks small, reviewable, and task-specific.
- Include `good_for`, `bad_for`, and `forbidden_for` so applicability is explicit.
- Include failure modes and verification checks.
- Avoid instructions that enable credential theft, unauthorized access, evasion, malware, fraud, or platform abuse.

## Add A MethodBlock

1. Add a YAML file under the most relevant category in `methodblocks/`.
2. Validate it:

   ```bash
   methodblock validate methodblocks/<category>/<name>.yaml
   ```

3. Compile it:

   ```bash
   methodblock compile methodblocks/<category>/<name>.yaml
   ```

4. Add or update tests when behavior changes.

## Development Checks

```bash
PYTHONPATH=src python -m methodblock.cli compile-all
pytest
```

## Style

- Use clear, concrete procedure steps.
- Prefer stable function contracts over vague implementation advice.
- Keep generated prompt text concise enough to fit into an agent context window.
