"""FastAPI web interface — upload, annotate, analyze, remove, compare."""

from __future__ import annotations

import io
import logging
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from PIL import Image

from unwatermark.cli import _get_handler
from unwatermark.config import load_config
from unwatermark.core.analyzer import analyze_watermark
from unwatermark.models.analysis import WatermarkRegion
from unwatermark.models.annotation import UserAnnotation
from unwatermark.pages import APP_PAGE, HELP_PAGE, NOT_FOUND_PAGE, PRIVACY_PAGE, TERMS_PAGE

logger = logging.getLogger(__name__)

app = FastAPI(title="Unwatermark", description="AI-powered watermark removal")

# Inline SVG favicon — indigo "U" on transparent background
FAVICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
    '<rect width="32" height="32" rx="6" fill="#4f46e5"/>'
    '<text x="16" y="24" text-anchor="middle" '
    'font-family="Inter,system-ui,sans-serif" font-weight="700" '
    'font-size="22" fill="#fff">U</text></svg>'
)


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index():
    return APP_PAGE


@app.get("/help", response_class=HTMLResponse)
async def help_page():
    return HELP_PAGE


@app.get("/terms", response_class=HTMLResponse)
async def terms_page():
    return TERMS_PAGE


@app.get("/privacy", response_class=HTMLResponse)
async def privacy_page():
    return PRIVACY_PAGE


@app.get("/favicon.ico")
async def favicon():
    return Response(content=FAVICON_SVG, media_type="image/svg+xml")


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

@app.post("/analyze")
async def analyze_file(
    file: UploadFile = File(...),
    description: str = Form(""),
    region_x: int = Form(-1),
    region_y: int = Form(-1),
    region_w: int = Form(-1),
    region_h: int = Form(-1),
):
    """Analyze an uploaded image for watermarks."""
    content = await file.read()
    image = Image.open(io.BytesIO(content))

    annotation = _build_annotation(
        description, region_x, region_y, region_w, region_h
    )
    config = load_config()

    try:
        analysis = analyze_watermark(image, config, annotation)
    except Exception as e:
        logger.exception("Analysis failed")
        return JSONResponse(
            {"error": _friendly_error(e)}, status_code=500
        )

    return JSONResponse({
        "watermark_found": analysis.watermark_found,
        "region": {
            "x": analysis.region.x,
            "y": analysis.region.y,
            "width": analysis.region.width,
            "height": analysis.region.height,
        },
        "description": analysis.description,
        "background_type": analysis.background_type.value,
        "strategy": analysis.strategy.value,
        "confidence": analysis.confidence,
        "reasoning": analysis.reasoning,
    })


@app.post("/process")
async def process_file(
    file: UploadFile = File(...),
    description: str = Form(""),
    strategy: str = Form(""),
    region_x: int = Form(-1),
    region_y: int = Form(-1),
    region_w: int = Form(-1),
    region_h: int = Form(-1),
):
    """Process an uploaded file — detect and remove watermark."""
    suffix = Path(file.filename).suffix.lower()
    handler = _get_handler(suffix)
    if handler is None:
        return JSONResponse(
            {"error": f"Unsupported file type: {suffix}"},
            status_code=400,
        )

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_in:
        content = await file.read()
        tmp_in.write(content)
        tmp_in.flush()
        input_path = Path(tmp_in.name)

    annotation = _build_annotation(
        description, region_x, region_y, region_w, region_h
    )
    config = load_config()
    force_strategy = strategy if strategy else None
    output_path = input_path.with_stem(input_path.stem + "_clean")

    try:
        handler(input_path, output_path, config, annotation, force_strategy)
    except Exception as e:
        logger.exception("Processing failed")
        return JSONResponse(
            {"error": _friendly_error(e)}, status_code=500
        )

    return FileResponse(
        path=str(output_path),
        filename=f"clean_{file.filename}",
        media_type="application/octet-stream",
    )


# ---------------------------------------------------------------------------
# 404 catch-all
# ---------------------------------------------------------------------------

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return HTMLResponse(NOT_FOUND_PAGE, status_code=404)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_annotation(
    description: str,
    region_x: int,
    region_y: int,
    region_w: int,
    region_h: int,
) -> UserAnnotation | None:
    """Build a UserAnnotation from form fields, or None if empty."""
    if not description and region_x < 0:
        return None
    region = None
    if region_x >= 0 and region_w > 0:
        region = WatermarkRegion(
            x=region_x, y=region_y, width=region_w, height=region_h
        )
    return UserAnnotation(description=description, region=region)


def _friendly_error(exc: Exception) -> str:
    """Convert exceptions into user-friendly error messages."""
    msg = str(exc).lower()
    if "api_key" in msg or "authentication" in msg or "401" in msg:
        return "API key is missing or invalid. Check your .env file."
    if "timeout" in msg or "timed out" in msg:
        return (
            "The AI service took too long to respond. Please try again."
        )
    if "rate" in msg and "limit" in msg:
        return "API rate limit reached. Wait a moment and try again."
    if "connection" in msg:
        return (
            "Could not connect to the AI service. Check your internet "
            "connection and try again."
        )
    return f"Something went wrong: {exc}"
