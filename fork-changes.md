# Cellpose Fork Changes

## 2026-04-22

### Rename cryptic Tier 1 variable names

Renamed short, opaque variable names to descriptive equivalents across the codebase for improved readability:

| File | Old name | New name |
|------|----------|----------|
| `core.py` | `ypad1`, `ypad2` | `y_pad_before`, `y_pad_after` |
| `core.py` | `xpad1`, `xpad2` | `x_pad_before`, `x_pad_after` |
| `core.py` | `bslc` | `batch_slice` |
| `core.py` | `sstr` | `axis_labels` |
| `core.py` | `stylea` | `style_array` |
| `core.py` | `pm`, `ipm` | `axis_order`, `axis_order_inv` |
| `core.py`, `models.py` | `yf` | `net_output` |
| `train.py` | `td` | `train_sample` |
| `train.py` | `rperm` | `random_perm` |
| `train.py` | `lavg` | `loss_avg` |
| `train.py` | `nsum` | `n_samples` |
| `denoise.py` | `veci` | `flow_label` |

All renames verified with `ruff check` (zero violations) and `uv build` (successful).

### Fix remaining Ruff issues manually

Resolved all remaining ruff errors, reaching zero violations:

- **UP031 (33)**: Converted all `%`-format strings to f-strings
- **E722 (27)**: Replaced all bare `except:` with specific types (`ImportError`, `OSError`, `ValueError`, `Exception`); removed 5 dead try blocks
- **F841 (18)**: Removed all unused local variables
- **E711 (3)**: Changed `== None` to `is None`
- **E731 (2)**: Converted lambda assignments to `def` in `distributed_segmentation.py`
- **F821 (1)**: Added missing `convert_image` to imports in `train.py`; annotated three pre-existing references to the removed `CPnet` class in `denoise.py` with `# noqa: F821`
- **F401 (1)**: Replaced bare `import matplotlib` with `importlib.util.find_spec("matplotlib")`
- **F811 (1)**: Removed shadowed `center_of_mass` import from `scipy.ndimage` in `dynamics.py`

### Apply all auto-fixable Ruff issues

Ran `ruff check --fix` and `ruff format` across the entire `cellpose/` package, reducing pre-existing lint errors from 565 to 129. Reformatted 22 files.

The remaining 129 issues all require manual decisions:

| Rule      | Count | Description                                    |
|-----------|-------|------------------------------------------------|
| W291/W293 | 39    | Trailing whitespace inside docstrings/comments |
| UP031     | 33    | `%`-style formatting → f-strings               |
| E722      | 27    | Bare `except:` → specific exception types      |
| F841      | 18    | Unused local variables                         |
| F821      | 4     | Undefined names                                |
| E711      | 3     | `== None` → `is None`                          |
| E731      | 2     | Lambda assignments → `def`                     |
| F401      | 2     | Unused imports (may be intentional re-exports) |
| F811      | 1     | Redefined name                                 |

### Switch from YAPF to Ruff

Replaced the YAPF formatter with [Ruff](https://docs.astral.sh/ruff/), which handles both formatting and linting in a single fast tool.

- Removed `.style.yapf`
- Added `ruff` to the `[dependency-groups] dev` section in `pyproject.toml` (run via `uv run --group dev ruff`)
- Configured `[tool.ruff]` in `pyproject.toml` preserving the existing 88-character line limit
- Enabled rule sets: `E`/`W` (pycodestyle), `F` (pyflakes), `I` (isort), `UP` (pyupgrade)
- Ignored `E402` (conditional imports common in scientific code), `E501` (line length enforced by formatter, not linter), `E741` (single-letter variable names common in math/numpy code)

Pre-existing issues found in the codebase: 565 total, 350 auto-fixable with `ruff check --fix`.

### Refactor as an uv project

Migrated the project from the legacy setuptools-based configuration to a modern `uv` project.

- Created `pyproject.toml` with all project metadata, dependencies, and optional extras (`gui`, `docs`, `distributed`, `bioimageio`, `image`, `all`)
- Removed `setup.py` and `setup.cfg`, which are now fully superseded by `pyproject.toml`
- Preserved SCM-based versioning via `setuptools_scm`
- Used modern SPDX license expression (`BSD-3-Clause`) instead of the deprecated TOML table format
- Verified the build with `uv build` (produces both sdist and wheel)
- Confirmed the CLI runs via `uv run cellpose` and the GUI launches via `uv run --extra gui cellpose`

### Update minimum dependency versions

Bumped minimum version constraints in `pyproject.toml` to reflect modern baselines, replacing the outdated lower bounds inherited from the original `setup.py`.

| Package                  | Old minimum | New minimum | Latest installed |
|--------------------------|-------------|-------------|------------------|
| `torch`                  | `>=1.6`     | `>=2.0`     | 2.11.0           |
| `torchvision`            | (none)      | `>=0.15`    | 0.26.0           |
| `numpy`                  | `>=1.20.0`  | `>=2.0`     | 2.4.4            |
| `scipy`                  | (none)      | `>=1.11`    | 1.17.1           |
| `opencv-python-headless` | (none)      | `>=4.8`     | 4.13.0.92        |
| `natsort`                | (none)      | `>=8.0`     | 8.4.0            |
| `tqdm`                   | (none)      | `>=4.60`    | 4.67.3           |
| `pyqtgraph`              | `>=0.12.4`  | `>=0.13`    | latest           |
| `sphinx`                 | `>=3.0`     | `>=7.0`     | —                |

Build and CLI verified successfully after the update.
