# Unwatermark

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-Image%20Processing-green)
![FastAPI](https://img.shields.io/badge/FastAPI-Web%20UI-009688?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-Proprietary-red)

> AI-powered watermark removal tool for images, PDFs, and PPTX files. Drop a file, get a clean version.

## Overview

Unwatermark is a focused utility that removes baked-in watermarks from images, PDF documents, and PowerPoint presentations. It was built to solve a specific, recurring problem: exported slide decks (particularly from NotebookLM) embed watermarks directly into the slide images, making them impossible to remove through normal editing.

The tool uses a clone-stamp approach with vertical flip and gradient blending to seamlessly paint over watermark regions. It works as both a CLI tool for batch processing and a drag-and-drop web interface for quick one-off jobs.

## The Challenge

Watermarks baked directly into raster images can't be removed by deleting a layer or element — the watermark pixels replace the original content. This is especially common with:

- **NotebookLM exports** — every slide is a single PNG with the watermark composited into the bottom-right corner
- **Stock photo previews** — watermarks overlaid across the entire image
- **PDF exports** — watermarks rendered into the page raster

Manual removal in Photoshop works but doesn't scale when you have 14+ slides that all need the same treatment.

## The Solution

Unwatermark automates the clone-stamp technique that a designer would use manually:

1. **Detect** the watermark region based on position heuristics (defaults to bottom-right for NotebookLM)
2. **Clone** a strip of pixels from directly above the watermark area
3. **Flip** the cloned strip vertically so the edge nearest the watermark blends naturally with surrounding content
4. **Blend** using a gradient alpha mask that fades at all edges, eliminating hard seams
5. **Replace** the image data in-place (for PPTX, swaps the blob directly via `image_part._blob`)

## Technical Highlights

- **Clone-stamp with gradient blending** — mirrors the manual Photoshop technique programmatically, with configurable blend margins
- **In-place PPTX modification** — replaces image blobs directly inside the PowerPoint package without re-rendering slides
- **PDF round-trip** — renders pages at configurable DPI via PyMuPDF, processes images, and reassembles a clean PDF
- **Fallback strategy** — if there isn't enough source material above the watermark, tries below; last resort applies Gaussian blur
- **Dual interface** — CLI for automation/scripting, FastAPI web UI for drag-and-drop convenience

## Getting Started

### Prerequisites

- Python >= 3.10

### Installation

```powershell
# Clone the repository
git clone https://github.com/RCushmaniii/cushlabs-ai-unwatermark.git
cd cushlabs-ai-unwatermark

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install with CLI support
pip install -e .

# Install with web UI support
pip install -e ".[web]"
```

### Usage — CLI

```powershell
# Remove watermark from an image (defaults to bottom-right)
unwatermark input.png

# Specify output path and watermark position
unwatermark presentation.pptx -o clean_presentation.pptx --position bottom-right

# Adjust watermark size detection
unwatermark document.pdf --width-ratio 0.3 --height-ratio 0.08
```

### Usage — Web UI

```powershell
uvicorn unwatermark.web:app --reload
```

Open `http://localhost:8000` — drag and drop a file, adjust settings, download the clean version.

## Project Structure

```
├── src/
│   └── unwatermark/
│       ├── cli.py              # Click CLI entry point
│       ├── web.py              # FastAPI drag-and-drop interface
│       ├── core/
│       │   ├── detector.py     # Watermark region detection
│       │   └── remover.py      # Clone-stamp removal engine
│       └── handlers/
│           ├── image.py        # PNG/JPG/BMP processing
│           ├── pdf.py          # PDF page extraction and reassembly
│           └── pptx.py         # PowerPoint image blob replacement
├── public/
│   ├── images/                 # Project screenshots and assets
│   └── video/                  # Demo videos
├── tests/
├── pyproject.toml
└── LICENSE
```

## Results

The tool was built to process a 14-slide NotebookLM PPTX export where every slide was a single full-size PNG with a watermark baked into the bottom-right corner. The clone-stamp approach produces clean slides that are visually indistinguishable from the original content — no blurring artifacts, no color mismatches at the seam.

| Metric | Detail |
|--------|--------|
| Supported formats | PNG, JPG, BMP, TIFF, WebP, PDF, PPTX |
| Processing time | ~1-2 seconds per slide/page |
| Blend quality | Seamless gradient — no visible seams |
| Watermark positions | 6 configurable positions |

## Contact

**Robert Cushman**
Business Solution Architect & Full-Stack Developer
Guadalajara, Mexico

📧 info@cushlabs.ai
🔗 [GitHub](https://github.com/RCushmaniii) • [LinkedIn](https://linkedin.com/in/robertcushman) • [Portfolio](https://cushlabs.ai)

## License

© 2026 Robert Cushman. All rights reserved.

---

*Last Updated: 2026-03-09*
