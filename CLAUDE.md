# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Project Overview

Cellpose-SAM is a cellular segmentation algorithm with superhuman generalization.
This fork includes recent refactoring work including migration to `uv` project
management, Ruff for linting/formatting, and descriptive variable naming.

## Development Commands

### Build and Install

```bash
# Install in development mode
uv pip install -e .

# Build package
uv build

# Install with GUI dependencies
uv pip install -e ".[gui]"
```

### Linting and Formatting

```bash
# Run linter
uv run --group dev ruff check

# Auto-fix linting issues
uv run --group dev ruff check --fix

# Format code
uv run --group dev ruff format
```

### Run Test

```bash
# Run all tests
pytest

# Run slow tests (marked with @pytest.mark.slow)
pytest --runslow

# Run with coverage
pytest --cov=cellpose --cov-report=xml

# Run with tox (cross-platform testing)
tox
```

### Running Cellpose

```bash
# Run CLI
uv run cellpose --help

# Run GUI
uv run --extra gui cellpose

# Run GUI in 3D mode
uv run --extra gui cellpose --Zstack
```

## Architecture

### Core Modules (`cellpose/`)

- **`core.py`**: GPU/CPU device assignment, network execution (`run_net`, `run_3D`)
- **`models.py`**: Model management, loading pre trained models (CPSAM),
  model path resolution
- **`dynamics.py`**: Flow field dynamics for cell segmentation
- **`transforms.py`**: Image transformations, normalization, augmentations
- **`train.py`**: Model training with human-in-the-loop support
- **`denoise.py`**: Image restoration (Cellpose3 feature)
- **`io.py`**: Image loading/saving, masks/flows I/O
- **`cli.py`**: Command-line argument parsing
- **`__main__.py`**: Main entry point, CLI execution, GUI launching
- **`vit_sam.py`**: Vision Transformer for SAM integration

### GUI Modules (`cellpose/gui/`)

- **`gui.py`**: Main 2D GUI window with file browser panel
- **`gui3d.py`**: 3D GUI for volumetric data
- **`guiparts.py`**: Reusable GUI components (sliders, buttons, etc.)
- **`menus.py`**: Menu bar definitions
- **`io.py`**: GUI-specific I/O utilities
- **`filebrowser.py`**: File browser panel with thumbnail previews (recent addition)

### Key Design Patterns

- **Device Management**: Uses `assign_device()` from `core.py` to detect and
  select GPU (CUDA) or MPS (Apple Silicon) or CPU
- **Model Loading**: Models downloaded to `~/.cellpose/models/` by default,
  can be overridden via `CELLPOSE_LOCAL_MODELS_PATH` env var
- **CLI/GUI Split**: CLI runs via `__main__.py`, GUI imports are conditional
  (fail gracefully if dependencies missing)
- **Variable Naming**: Recent refactoring replaced cryptic names
  (e.g., `bslc` → `batch_slice`, `yf` → `net_output`) for readability

## Dependencies

### Core

- `torch>=2.0`, `torchvision>=0.15`
- `numpy>=2.0`, `scipy>=1.11`
- `opencv-python-headless>=4.8`
- `segment_anything` (SAM integration)

### GUI (optional)

- `pyqt6`, `pyqtgraph>=0.13`, `qtpy`, `superqt`

### Optional Extras

- `distributed`: Dask-based distributed segmentation
- `image`: ND2, NRRD support
- `docs`: Sphinx documentation

## Testing

Tests use pytest with fixtures for test data (downloaded from OSF). Key fixtures:

- `data_dir`: Provides test images
- `cellposemodel_fixture_24layer`: Mock model with all transformer layers
- `cellposemodel_fixture_2layer`: Mock model with 2 transformer layers (faster)

Tests are in `tests/` directory, excluding contrib tests in CI.

## Important Notes

- This fork uses `uv` for package management (not pip/setuptools directly)
- Ruff is used for both linting and formatting (88-char line limit)
- Variable names have been systematically renamed from cryptic to descriptive
- Minimum dependency versions were updated to modern baselines
- The project supports 2D and 3D segmentation, with GPU acceleration

