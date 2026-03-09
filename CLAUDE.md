# CLAUDE.md — Unwatermark

## Project Overview
AI-powered watermark removal tool for images, PDFs, and PPTX files. Two-stage pipeline: Claude Sonnet 4 (vision LLM) analyzes the watermark and recommends a strategy, then local image processing executes the removal. Supports CLI and FastAPI web UI with annotation canvas and before/after comparison.

## Tech Stack
- Python 3.10+
- Anthropic SDK — Claude vision analysis
- Pillow + NumPy — image processing
- python-pptx — PowerPoint file manipulation
- PyMuPDF (fitz) — PDF rendering and assembly
- FastAPI + Uvicorn — web interface
- Click — CLI framework
- Optional: simple-lama-inpainting (LaMa), replicate SDK, openai SDK

## Project Structure
```
src/unwatermark/
├── __init__.py
├── cli.py                  # Click CLI (--annotate, --strategy, --no-ai, --model)
├── web.py                  # FastAPI web UI (annotation canvas, before/after slider)
├── config.py               # API keys, provider/backend selection from .env
├── core/
│   ├── analyzer.py         # Vision LLM integration (Claude/OpenAI)
│   ├── detector.py         # Routes to analyzer or heuristic fallback
│   ├── remover.py          # Strategy router → technique dispatch
│   ├── strategies.py       # Strategy selection logic
│   └── techniques/
│       ├── base.py         # Abstract RemovalTechnique interface
│       ├── registry.py     # Strategy → technique mapping
│       ├── solid_fill.py   # Solid color and gradient fill
│       ├── clone_stamp.py  # Mirror/clone from adjacent area
│       └── lama_inpaint.py # LaMa inpainting (local/replicate/modal backends)
├── handlers/
│   ├── image.py            # Standalone image processing
│   ├── pdf.py              # PDF page render → clean → reassemble
│   └── pptx.py             # PPTX image blob replacement
└── models/
    ├── analysis.py         # WatermarkAnalysis, WatermarkRegion, enums
    └── annotation.py       # UserAnnotation dataclass
```

## Development Commands
```powershell
# Activate venv
.venv\Scripts\Activate.ps1

# Install base
pip install -e .

# Install with all extras
pip install -e ".[all,dev]"

# Run CLI
unwatermark image.png
unwatermark presentation.pptx --annotate "NotebookLM watermark bottom-right"
unwatermark image.png --strategy solid_fill --no-ai

# Run web server
uvicorn unwatermark.web:app --reload

# Lint
ruff check src/

# Tests
pytest
```

## Key Patterns & Conventions
- Two-stage pipeline: analyzer (AI) → remover (local processing)
- Technique plugin pattern: all techniques implement `RemovalTechnique.remove(image, region, analysis)`
- Handlers share signature: `process_X(input_path, output_path, config, annotation, force_strategy)`
- Inpaint backend is provider-agnostic: local/replicate/modal swap via config
- Config loads from .env via python-dotenv
- WatermarkRegion.padded() adds safety margin to AI-detected bounding boxes

## Environment Variables
See `.env.example`. Required: `ANTHROPIC_API_KEY`. Optional: `OPENAI_API_KEY`, `REPLICATE_API_TOKEN`, backend overrides.

## Current Focus
Phase 1 complete (core restructure with technique plugins and provider pattern). Next: test with real watermarked files, tune analysis prompt, build out LaMa integration.

## Known Issues
- LaMa inpainting requires `pip install simple-lama-inpainting` (pulls PyTorch ~2GB)
- PDF round-trip rasterizes vector content
- Replicate model ID in lama_inpaint.py is a placeholder — needs real model version
- Vision LLM bounding boxes are approximate — padded() compensates with 10px margin
