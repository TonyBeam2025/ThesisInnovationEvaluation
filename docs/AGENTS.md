# Repository Guidelines

This repository implements an AI‑assisted thesis innovation evaluation system in Python. Use this guide to navigate the codebase and contribute consistently.

## Project Structure & Module Organization
- Core package: `src/thesis_inno_eval/` (CLI, config, extractors, analyzers).
- Tests: `tests/` (pytest collection path). Legacy exploratory tests also exist at repo root as `test_*.py`.
- Configuration: `config/conf.yaml` (preferred) or `conf.yaml` (fallback).
- Docs and assets: `docs/`.
- Data and runtime artifacts: `data/`, `cache/`, `logs/`.

## Build, Test, and Development Commands
- Setup (recommended): `uv sync` or `uv sync --group dev` for dev tools.
- Alternative: `pip install -e .[dev]`.
- Run tests: `uv run pytest` (collects tests under `tests/`).
- Lint & format: `uv run black .` · `uv run isort .` · `uv run flake8 .` · `uv run mypy .`.
- Package/build (optional): `uv build` or `hatch build`.
- CLI examples: `uv run thesis-eval info` · `uv run thesis-eval evaluate path/to/file.docx`.

## Coding Style & Naming Conventions
- Python ≥ 3.10, 4‑space indentation.
- Formatting: Black (line length 88); imports via isort (profile=black).
- Linting & typing: flake8, mypy (prefer full type hints).
- Naming: modules/files `snake_case.py`; classes `PascalCase`; functions/variables `snake_case`.
- Place new code in `src/thesis_inno_eval/` and keep scripts minimal.

## Testing Guidelines
- Framework: pytest. Put new tests in `tests/` and name files `test_*.py`.
- Quick run: `uv run pytest -q`. Target focused files: `uv run pytest tests/test_config_system.py -q`.
- Optional coverage: `uv run pytest --cov=thesis_inno_eval` (requires `pytest-cov`).

## Commit & Pull Request Guidelines
- Commits: follow Conventional Commits, e.g., `feat: add cached evaluator`, `fix: handle docx encoding`.
- PRs: include a clear description (what/why), linked issue, test coverage for changes, and notes on config/CLI impacts. Add before/after snippets or command examples when helpful.

## Security & Configuration Tips
- Do not commit secrets. Use environment variables or `.env` for `OPENAI_API_KEY`, `GOOGLE_API_KEY`, CNKI credentials.
- Prefer editing `config/conf.yaml`; repo also supports `conf.yaml` for backward compatibility.
- Avoid committing large generated artifacts under `data/`, `cache/`, and `logs/`.

