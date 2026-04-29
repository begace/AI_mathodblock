# MethodBlock Registry

MethodBlock Registry v1.0 is a local-first procedural memory toolkit for AI agents, providing a human-readable MethodBlock format, schema validation, AI-optimized compilation, local search, and prompt injection.

This is not a prompt collection. A MethodBlock is a reusable procedural memory unit with applicability rules, task-solving steps, function contracts, failure modes, and verification criteria.

이 프로젝트는 단순 프롬프트 모음이 아닙니다. MethodBlock은 적용 조건, 문제 해결 절차, 함수 계약, 실패 패턴, 검증 기준을 포함한 재사용 가능한 절차기억 단위입니다.

## What It Does

MethodBlock has two forms:

1. Source MethodBlock: human-readable YAML for review, editing, and contribution.
2. Compiled MethodBlock: AI-optimized `compact.md`, `graph.json`, and `index.json` files for retrieval, prompt injection, and agent planning.

v1.0 focuses on local files and deterministic tooling. It does not run an external LLM, host a server, use a vector database, or automate browsers.

## Long-Term Vision

The long-term vision of MethodBlock Registry is to become a shared "how to work" memory layer for AI agents.

Before starting a task, an AI agent should search for an existing MethodBlock. If a suitable MethodBlock exists, the agent uses it as procedural guidance. If no suitable MethodBlock exists, the agent completes the task and drafts a new MethodBlock from what it learned.

Over time, agents can build a reusable network of task-solving methods: not just answers, prompts, or code snippets, but reviewed procedures for how work should be approached, verified, and safely repeated.

장기적으로 MethodBlock Registry는 AI 에이전트들이 공유하는 "일하는 법 네트워크"를 목표로 한다.

AI는 작업을 시작하기 전에 먼저 관련 MethodBlock을 검색한다. 적합한 MethodBlock이 있으면 그 절차를 따라 작업하고, 없다면 작업을 수행한 뒤 새 MethodBlock 초안을 작성한다.

이렇게 축적된 MethodBlock은 단순한 답변이나 프롬프트가 아니라, 반복 가능한 작업 방식, 실패 패턴, 검증 기준을 담은 절차기억이 된다.

## Install

```bash
python -m pip install -e .
```

During development, you can also run the package directly:

```bash
PYTHONPATH=src python -m methodblock.cli --help
```

## CLI Usage

```bash
methodblock init
methodblock list
methodblock show excel_processor_basic
methodblock show excel_processor_basic --source
methodblock show excel_processor_basic --compact
methodblock show excel_processor_basic --graph
methodblock validate methodblocks/coding/excel_processor.yaml
methodblock validate-all
methodblock compile methodblocks/coding/excel_processor.yaml
methodblock compile-all
methodblock search "build an excel inventory cleanup tool"
methodblock prompt excel_processor_basic --task "Build a Python tool that merges duplicate SKUs in an Excel file"
methodblock prompt excel_processor_basic --task "Build a Python Excel cleaner" --format json --output prompt.json
methodblock draft --from-text notes.txt
methodblock new payment_system_basic
```

## MethodBlock YAML

Source files live under `methodblocks/`. v1.0 requires these fields:

- `id`
- `title`
- `summary`
- `version`
- `task_type`
- `keywords`
- `good_for`
- `bad_for`
- `forbidden_for`
- `procedure`
- `failure_modes`
- `verification`

Supported optional fields include `contract_pattern`, `examples`, `model_notes`, `lineage`, `author`, `created_by`, `license`, and `tags`.

## Compilation

`methodblock compile-all` writes generated artifacts under `compiled/`:

- `*.compact.md`: compact prompt-injection form
- `*.graph.json`: structured procedure graph
- `*.index.json`: searchable metadata and artifact paths

Generated artifacts are reproducible from source YAML. Review and edit the YAML source, then compile again.

## Search

v1.0 search is local and explainable. It scores:

- `id`
- `title`
- `summary`
- `keywords`
- `task_type`
- `good_for`
- `procedure`

Scores are normalized to `0.00` through `1.00` for CLI output.

## Prompt Generation

`methodblock prompt` combines a task with a compact MethodBlock and emits Markdown, plain text, or JSON:

```bash
methodblock prompt excel_processor_basic \
  --task "Build a Python tool that merges duplicate SKUs in an Excel file" \
  --format markdown
```

## Drafting

`methodblock draft --from-text <path>` creates a conservative YAML draft under `drafts/`. It is template-based and does not call an LLM. Unknown fields are filled with TODO-style placeholders so a human can review and refine the draft before moving it into `methodblocks/`.

## Repository Layout

```text
methodblocks/       Human-readable source YAML MethodBlocks
compiled/           Generated compact/graph/index artifacts
schema/             JSON Schemas for source and compiled artifacts
examples/           Example tasks, prompts, and outputs
drafts/             Local draft MethodBlocks
src/methodblock/    Python package and CLI implementation
tests/              Unit and CLI smoke tests
.github/workflows/  CI configuration
```

## Safety

MethodBlocks must not be used for credential theft, unauthorized data access, access control bypass, malware, evasion, payment bypass, DRM bypass, anti-cheat bypass, or platform abuse. Every source MethodBlock must include `forbidden_for`.

## Development Checks

```bash
methodblock validate-all
methodblock compile-all
pytest
```

GitHub Actions runs the same core checks on push and pull request.
