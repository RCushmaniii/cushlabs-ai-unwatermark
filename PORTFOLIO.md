---
# =============================================================================
# PORTFOLIO.MD — Unwatermark
# =============================================================================
portfolio_enabled: true
portfolio_priority: 6
portfolio_featured: false
portfolio_last_reviewed: "2026-03-09"

title: "Unwatermark"
tagline: "AI-powered watermark removal for images, PDFs, and PPTX files"
slug: "unwatermark"

category: "AI Automation"
target_audience: "Content creators and professionals who need clean exports from watermarked sources"
tags:
  - "python"
  - "image-processing"
  - "watermark-removal"
  - "pillow"
  - "pptx"
  - "pdf"
  - "fastapi"
  - "automation"

thumbnail: "/images/unwatermark-thumb.png"
hero_images:
  - "/images/unwatermark-01.png"
  - "/images/unwatermark-02.png"
  - "/images/unwatermark-03.png"
  - "/images/unwatermark-04.png"
  - "/images/unwatermark-05.png"
demo_video_url: ""

live_url: ""
demo_url: ""
case_study_url: ""

problem_solved: |
  Exported slide decks and documents often embed watermarks directly into raster images,
  making them impossible to remove through normal editing. Manual Photoshop cleanup doesn't
  scale when you have dozens of slides that all need the same treatment. Unwatermark automates
  the clone-stamp technique to produce clean files in seconds.

key_outcomes:
  - "Processes 14-slide PPTX exports in under 30 seconds"
  - "Seamless gradient blending with no visible artifacts"
  - "Supports 7+ file formats across images, PDFs, and presentations"
  - "Dual CLI and web interface for automation and ad-hoc use"

tech_stack:
  - "Python 3.10+"
  - "Pillow"
  - "NumPy"
  - "python-pptx"
  - "PyMuPDF"
  - "FastAPI"
  - "Click"

complexity: "Production"
---

## Overview

Unwatermark is a focused utility that removes baked-in watermarks from images, PDF documents, and PowerPoint presentations. It automates the clone-stamp approach that designers use manually in Photoshop — cloning pixels from adjacent regions, flipping them for natural edge alignment, and blending with a gradient alpha mask to eliminate visible seams.

The tool was built to solve a specific problem: NotebookLM exports produce slide decks where every slide is a single full-size PNG with a watermark composited into the corner. Unwatermark processes these files in bulk, replacing the watermarked image blobs directly inside the PPTX package.

## The Challenge

- **Baked-in watermarks** — the watermark pixels replace the original content, so there's no layer to delete
- **Scale** — manually cleaning 14+ slides in Photoshop is tedious and error-prone
- **Format diversity** — watermarks appear in PNGs, PDFs, and PPTX files, each requiring different extraction and reassembly logic
- **Quality expectations** — the output needs to look professional, not blurred or patchy

## The Solution

**Intelligent region detection:**
Configurable position-based detection targets the watermark location (bottom-right for NotebookLM, but supports all six corner/edge positions). An experimental auto-detection mode scans border regions for variance anomalies.

**Clone-stamp removal engine:**
Clones a strip of pixels from directly above the watermark, vertically flips it for natural edge continuity, and composites it using a gradient alpha mask that fades at all four edges.

**Format-specific handlers:**
Each file type gets its own handler — images are processed directly, PPTX files have their image blobs swapped in-place, and PDFs are rendered to high-res images, cleaned, and reassembled.

## Technical Highlights

- **Gradient alpha blending** — four-edge fade mask prevents hard seams at clone boundaries
- **In-place PPTX blob replacement** — modifies `image_part._blob` directly, preserving all slide layout and formatting
- **PDF round-trip pipeline** — PyMuPDF renders at configurable DPI, Pillow processes, then reassembles to PDF
- **Fallback strategy** — tries cloning from below if insufficient source above; applies Gaussian blur as last resort
- **Dual interface** — Click CLI for batch scripting, FastAPI web UI with drag-and-drop for ad-hoc use

## Results

**For the End User:**
- Clean PPTX exports from NotebookLM in seconds instead of hours of manual Photoshop work
- Professional-quality output with no visible artifacts at the removal boundary
- Simple drag-and-drop interface requires zero image editing knowledge

**Technical Demonstration:**
- Practical image processing pipeline combining NumPy array manipulation with PIL compositing
- Clean architecture with pluggable file-type handlers for easy format extension
- Production-ready FastAPI web interface served from a single embedded HTML page
