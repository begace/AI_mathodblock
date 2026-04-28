# MethodBlock Registry

MethodBlock Registry is a lightweight procedural memory registry for AI agents.

This is not a prompt collection. A MethodBlock is a reusable procedural memory unit with applicability rules, task-solving steps, function contracts, failure modes, and verification criteria.

MethodBlock has two forms:

1. Source MethodBlock: human-readable YAML for review, editing, and contribution.
2. Compiled MethodBlock: AI-optimized `compact.md`, `graph.json`, and `index.json` files for retrieval, prompt injection, and agent planning.

이 프로젝트는 단순 프롬프트 모음이 아닙니다. MethodBlock은 적용 조건, 문제 해결 절차, 함수 계약, 실패 패턴, 검증 기준을 포함한 재사용 가능한 절차기억 단위입니다.

## v0.1 Scope

Implemented in this version:

- YAML MethodBlock source format
- JSON Schema validation
- Compiler from source YAML to `compact.md`, `graph.json`, and `index.json`
- Local CLI commands for list, show, search, validate, compile, compile-all, and prompt
- Keyword scoring search
- Prompt generation from a task and compact MethodBlock

Not included in v0.1:

- Remote registry server
- Agent-to-agent auto upload
- Automatic rating system
- Embedding search
- Multi-agent execution
- External LLM API calls

## Install For Development

```bash
python -m pip install -e .
```

The source layout also works without installation by setting `PYTHONPATH=src`.

```bash
PYTHONPATH=src python -m methodblock.cli list
```

## CLI Usage

```bash
methodblock list
methodblock show excel_processor_basic
methodblock search "clean duplicate SKUs in Excel"
methodblock validate methodblocks/coding/excel_processor.yaml
methodblock compile methodblocks/coding/excel_processor.yaml
methodblock compile-all
methodblock prompt excel_processor_basic --task "Build a Python Excel cleaner"
```

## Project Layout

```text
methodblocks/       Human-readable source YAML MethodBlocks
schema/             JSON Schemas for source and compiled artifacts
compiled/           Generated compact/graph/index artifacts
examples/           Example tasks, prompts, and outputs
src/methodblock/    Python package and CLI implementation
tests/              Unit tests
```

## Source MethodBlock

Source MethodBlocks live under `methodblocks/`. Each file should describe:

- applicability: `good_for`, `bad_for`, `forbidden_for`
- procedure: ordered human-readable steps
- function contracts: optional reusable implementation shape
- failure modes: common ways the task can fail
- verification: checks or tests expected for safe reuse

## Compiled Artifacts

`methodblock compile` writes three artifacts under `compiled/`:

- `*.compact.md`: compact prompt-injection form
- `*.graph.json`: procedure graph, contracts, failure modes, verification
- `*.index.json`: searchable metadata and artifact paths

Generated files are reproducible from source YAML. Review and edit the YAML source, then compile again.

## Search

v0.1 search intentionally stays simple:

- keyword match: +3
- task type match: +2
- title token match: +1
- summary token match: +1

This keeps behavior transparent and avoids embedding or remote service dependencies.

## Safety

MethodBlocks must not be used for credential theft, unauthorized data access, access control bypass, malware, evasion, or platform abuse. Every source MethodBlock should include `forbidden_for` entries, and contributors should read `SECURITY.md` before adding automation-related content.
