# CLAUDE.md — Unwatermark

## Project Overview
AI-powered watermark removal tool for images, PDFs, and PPTX files. Layered detection pipeline: EasyOCR (deterministic, local) → Claude Vision AI (fallback for logos) → heuristic. Removal via LaMa neural inpainting with multi-pass support. FastAPI web UI with NDJSON streaming progress.

## Tech Stack
- Python 3.10+
- EasyOCR — primary watermark detection (deterministic, local, free)
- Anthropic SDK — Claude vision analysis (fallback for non-text watermarks)
- simple-lama-inpainting — neural inpainting for watermark removal
- Pillow + NumPy — image processing
- python-pptx — PowerPoint file manipulation
- PyMuPDF (fitz) — PDF rendering and assembly
- FastAPI + Uvicorn — web interface
- Click — CLI framework
- Optional: replicate SDK, openai SDK

## Project Structure
```
src/unwatermark/
├── __init__.py
├── cli.py                  # Click CLI (--annotate, --strategy, --no-ai, --model)
├── web.py                  # FastAPI web UI (NDJSON streaming, file-based download tokens)
├── config.py               # API keys, provider/backend selection from .env
├── core/
│   ├── analyzer.py         # Vision LLM integration (Claude/OpenAI)
│   ├── ocr_detector.py     # EasyOCR-based detection (primary detector)
│   ├── detector.py         # Layered routing: OCR → AI → heuristic
│   ├── multipass.py        # Multi-pass detect-remove loop (up to 3 passes)
│   ├── remover.py          # Strategy router → technique dispatch
│   ├── strategies.py       # Strategy selection (always prefers LaMa)
│   └── techniques/
│       ├── base.py         # Abstract RemovalTechnique interface
│       ├── registry.py     # Strategy → technique mapping
│       ├── solid_fill.py   # Solid color and gradient fill
│       ├── clone_stamp.py  # Mirror/clone from adjacent area
│       └── lama_inpaint.py # LaMa inpainting (local/replicate/modal backends)
├── handlers/
│   ├── image.py            # Standalone image processing (multi-pass)
│   ├── pdf.py              # PDF page render → clean → reassemble (multi-pass)
│   └── pptx.py             # PPTX image blob replacement (multi-pass + baseline)
├── models/
│   ├── analysis.py         # WatermarkAnalysis, WatermarkRegion, enums
│   └── annotation.py       # UserAnnotation dataclass
└── pages/
    └── app.py              # Inline HTML/JS for the web UI
```

## Detection Architecture (v1)
```
Image → OCR (EasyOCR, deterministic, local, free)
           ↓ found text watermark? → use it
           ↓ nothing found?
        AI Vision (Claude/GPT-4o, non-deterministic, $0.02/call)
           ↓ found watermark? → use it
           ↓ nothing found?
        Heuristic fallback (bottom-right guess)
```

### Multi-pass removal
Each image gets up to 3 detect-remove cycles. Pass 1 uses full stack (OCR → AI → heuristic). Pass 2+ uses OCR only (fast, no API calls). Stops when no more watermarks are found.

### PPTX baseline reuse
First successful detection on any slide is saved as baseline. If detection fails on a later slide, the baseline is reused (common case: same watermark, same position on every slide).

## Development Commands
```powershell
# Activate venv
.venv\Scripts\Activate.ps1

# Install with all extras
pip install -e ".[all,dev]"

# Run web server
uvicorn unwatermark.web:app --reload

# Restart dev server (kills stale processes)
bash scripts/restart_dev.sh

# Run CLI
unwatermark image.png
unwatermark presentation.pptx --annotate "NotebookLM watermark bottom-right"

# Lint
ruff check src/

# Tests
pytest
```

## Key Patterns & Conventions
- Layered detection: OCR (deterministic) → AI (fallback) → heuristic
- Multi-pass cleaning via `clean_image()` in `core/multipass.py`
- Technique plugin pattern: all techniques implement `RemovalTechnique.remove(image, region, analysis)`
- Handlers share signature: `process_X(input_path, output_path, config, annotation, force_strategy, on_progress)`
- Strategy selection always prefers LaMa inpainting when available
- Inpaint backend is provider-agnostic: local/replicate/modal swap via config
- PPTX blob replacement: must use `slide.part.related_part(rId)` not `shape.image._blob`
- Download tokens persisted to disk (survives server reloads during long processing)
- Config loads from .env via python-dotenv
- EasyOCR reader is lazy-loaded singleton (heavy init, ~2s first call)

## Environment Variables
See `.env.example`. Required: `ANTHROPIC_API_KEY`. Optional: `OPENAI_API_KEY`, `REPLICATE_API_TOKEN`, backend overrides.

## Known Issues & Limitations
- OCR can't detect rotated/diagonal watermarks or pure image/logo watermarks (falls through to AI)
- When watermark physically overlaps content text, removal damages the content (unavoidable)
- PDF round-trip rasterizes vector content
- LaMa + EasyOCR + PyTorch use significant memory (~2-3GB)
- First OCR call takes ~2s for model initialization
- EasyOCR model files download on first use (~100MB)

## OCR Pattern Matching
`ocr_detector.py` scores detected text against known watermark patterns (NotebookLM, Shutterstock, Getty, DRAFT, etc.). Key rules:
- All generic patterns use word boundaries (`\b`) to avoid matching inside words
- Max 5-word filter prevents content sentences from matching
- Pattern match scores +5.0 (dominant signal), non-pattern text needs score ≥ 4.5
- Bounding box expands 50% leftward to capture icons/logos beside text

## Planned: v2 Detection Architecture
```
Florence-2 (replaces both EasyOCR AND Claude Vision — handles text, logos, rotated text)
     → SAM (Segment Anything — pixel-perfect mask instead of rectangle)
          → LaMa inpainting (only inpaints actual watermark pixels)
```
Benefits: fully local, deterministic, handles all watermark types, pixel-perfect masks.
Trade-off: ~4GB model downloads, higher memory usage.

## Deployment Strategy
- **Web frontend + API** → Render or Railway ($7-25/mo)
- **ML inference** → Replicate API (pay per prediction, no model hosting)
- Florence-2 and SAM available on Replicate — no need to ship large models
- Vercel/Netlify/Hostinger won't work (can't run Python ML models)
