# Cellpose Fork Changes

## 2026-04-22

### Refactor as uv project

Migrated the project from the legacy setuptools-based configuration to a modern `uv` project.

- Created `pyproject.toml` with all project metadata, dependencies, and optional extras (`gui`, `docs`, `distributed`, `bioimageio`, `image`, `all`)
- Removed `setup.py` and `setup.cfg`, which are now fully superseded by `pyproject.toml`
- Preserved SCM-based versioning via `setuptools_scm`
- Used modern SPDX license expression (`BSD-3-Clause`) instead of the deprecated TOML table format
- Verified the build with `uv build` (produces both sdist and wheel)
- Confirmed the CLI runs via `uv run cellpose` and the GUI launches via `uv run --extra gui cellpose`

### Update minimum dependency versions

Bumped minimum version constraints in `pyproject.toml` to reflect modern baselines, replacing the outdated lower bounds inherited from the original `setup.py`.

| Package | Old minimum | New minimum | Latest installed |
|---|---|---|---|
| `torch` | `>=1.6` | `>=2.0` | 2.11.0 |
| `torchvision` | (none) | `>=0.15` | 0.26.0 |
| `numpy` | `>=1.20.0` | `>=2.0` | 2.4.4 |
| `scipy` | (none) | `>=1.11` | 1.17.1 |
| `opencv-python-headless` | (none) | `>=4.8` | 4.13.0.92 |
| `natsort` | (none) | `>=8.0` | 8.4.0 |
| `tqdm` | (none) | `>=4.60` | 4.67.3 |
| `pyqtgraph` | `>=0.12.4` | `>=0.13` | latest |
| `sphinx` | `>=3.0` | `>=7.0` | — |

Build and CLI verified successfully after the update.
