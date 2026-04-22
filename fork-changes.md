# Cellpose Fork Changes

## 2026-04-22: Refactor as uv project

Migrated the project from the legacy setuptools-based configuration to a modern `uv` project.

- Created `pyproject.toml` with all project metadata, dependencies, and optional extras (`gui`, `docs`, `distributed`, `bioimageio`, `image`, `all`)
- Removed `setup.py` and `setup.cfg`, which are now fully superseded by `pyproject.toml`
- Preserved SCM-based versioning via `setuptools_scm`
- Used modern SPDX license expression (`BSD-3-Clause`) instead of the deprecated TOML table format
- Verified the build with `uv build` (produces both sdist and wheel)
- Confirmed the CLI runs via `uv run cellpose` and the GUI launches via `uv run --extra gui cellpose`
