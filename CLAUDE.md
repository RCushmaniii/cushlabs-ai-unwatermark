# CLAUDE.md — Unwatermark

## Project Overview
AI-powered watermark removal tool for images, PDFs, and PPTX files. Python package with CLI (Click) and web UI (FastAPI). Uses clone-stamp technique with vertical flip and gradient blending to seamlessly remove baked-in watermarks.

## Tech Stack
- Python 3.10+
- Pillow — image processing and compositing
- NumPy — gradient mask generation and array operations
- python-pptx — PowerPoint file manipulation
- PyMuPDF (fitz) — PDF rendering and assembly
- FastAPI + Uvicorn — web interface
- Click — CLI framework

## Project Structure
```
src/unwatermark/
├── __init__.py          # Package version
├── cli.py               # Click CLI entry point
├── web.py               # FastAPI web UI (inline HTML)
├── core/
│   ├── detector.py      # Watermark region detection (position-based + auto)
│   └── remover.py       # Clone-stamp removal with gradient blending
└── handlers/
    ├── image.py         # Standalone image processing
    ├── pdf.py           # PDF page render → clean → reassemble
    └── pptx.py          # PPTX image blob replacement
```

## Development Commands
```powershell
# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install in development mode (all extras)
pip install -e ".[web,dev]"

# Run CLI
unwatermark input.png -o output.png

# Run web server
uvicorn unwatermark.web:app --reload

# Run tests
pytest

# Lint
ruff check src/
```

## Key Patterns & Conventions
- Handlers follow a common signature: `process_X(input_path, output_path, position, width_ratio, height_ratio) -> Path`
- Core logic is separated from file-type handling — `detector.py` and `remover.py` work on PIL Images only
- PPTX handler replaces image blobs via `image_part._blob` to preserve slide layout
- PDF handler does a full render-to-image round trip via PyMuPDF
- Web UI is a single inline HTML string in `web.py` — no separate static files

## Current Focus
Initial scaffold complete. Next steps: testing with real NotebookLM PPTX files, tuning detection parameters, and potentially adding ML-based watermark detection.

## Known Issues
- Auto-detection (`detect_watermark_auto`) is experimental and may not reliably identify watermarks
- PDF round-trip loses vector content (converts everything to raster)
- No progress feedback for large files in web UI
