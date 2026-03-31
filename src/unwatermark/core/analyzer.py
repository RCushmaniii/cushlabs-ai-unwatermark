"""Vision LLM integration — analyzes images to detect and characterize watermarks.

Supports Claude (Anthropic) and GPT-4o (OpenAI) as analysis providers.
Returns structured WatermarkAnalysis with bounding box, background type,
recommended strategy, and reasoning.
"""

from __future__ import annotations

import base64
import io
import json
import logging

from PIL import Image

from unwatermark.config import AnalysisProvider, Config
from unwatermark.models.analysis import (
    BackgroundType,
    RemovalStrategy,
    SurroundingContext,
    WatermarkAnalysis,
    WatermarkRegion,
)
from unwatermark.models.annotation import UserAnnotation

logger = logging.getLogger(__name__)

_ANALYSIS_PROMPT_TEMPLATE = (
    "You are a watermark detection expert. Your job is to find ANY watermark, "
    "logo, or overlay text in this image. Watermarks are VERY common — most "
    "images have them. Look carefully in ALL corners and edges, not just the center.\n"
    "\n"
    "Common watermark types:\n"
    "- Semi-transparent text overlays (e.g., stock photo sites, NotebookLM, Canva)\n"
    "- Small logos in corners (e.g., Getty, Shutterstock, YouTube)\n"
    "- 'Made with...' or 'Created by...' text, often in bottom corners\n"
    "- DIAGONAL or ROTATED text across the image (e.g., 'SAMPLE', 'PREVIEW', 'DRAFT' "
    "at 30-45 degree angles — these are VERY common and easy to miss). "
    "IMPORTANT: Diagonal watermarks span the ENTIRE image. Their bounding box "
    "should cover the full image dimensions (x=0, y=0, width=FULL, height=FULL).\n"
    "- Tiled/repeating watermark patterns across the entire image\n"
    "- Audio waveform labels like 'NotebookLM' on podcast/audio visuals\n"
    "\n"
    "COORDINATE SYSTEM:\n"
    "- Origin (0, 0) is the TOP-LEFT corner of the image\n"
    "- x increases going RIGHT, y increases going DOWN\n"
    "- The image is WIDTHxHEIGHT pixels\n"
    "- Your bounding box MUST use absolute pixel coordinates\n"
    "- The bounding box must TIGHTLY fit the watermark — include only the watermark "
    "text/logo itself plus 2-3 pixels of margin. Do NOT include large areas of "
    "background. A tight box produces much better removal results.\n"
    "- Example: a small 'NotebookLM' watermark in the bottom-right of a 1376x768 "
    'image might be at {"x": 1180, "y": 730, "width": 180, "height": 30}\n'
    "\n"
    "Return a JSON object with these exact fields:\n"
    "{\n"
    '  "watermark_found": true/false,\n'
    '  "bounding_box": {"x": int, "y": int, "width": int, "height": int},\n'
    '  "description": "what the watermark looks like and says",\n'
    '  "background_type": "solid_color" | "gradient" | "simple_texture"'
    ' | "complex_content" | "mixed",\n'
    '  "background_color": "#hex or null if not solid",\n'
    '  "recommended_strategy": "solid_fill" | "gradient_fill"'
    ' | "clone_stamp" | "inpaint",\n'
    '  "confidence": 0.0-1.0,\n'
    '  "reasoning": "brief explanation of why you chose this strategy",\n'
    '  "context": {\n'
    '    "above": "what is above the watermark",\n'
    '    "below": "what is below the watermark",\n'
    '    "left": "what is left of the watermark",\n'
    '    "right": "what is right of the watermark"\n'
    "  },\n"
    '  "clone_direction": "above" | "below" | "left" | "right"\n'
    "}\n"
    "\n"
    "IMPORTANT: Set watermark_found to true if there is ANY watermark or overlay. "
    "Err on the side of detecting watermarks — false negatives are worse than "
    "false positives for this use case.\n"
    "\n"
    "PRIORITY: If there are multiple watermarks, report the LARGEST and most "
    "prominent one first. A large diagonal 'SAMPLE PREVIEW' spanning the slide "
    "is far more important than a small logo in the corner. Always prioritize "
    "watermarks that cover a large area over small corner marks.\n"
    "\n"
    "Rules for strategy selection:\n"
    '- "solid_fill": Watermark on a uniform solid color background.\n'
    '- "gradient_fill": Watermark on a smooth color gradient.\n'
    '- "clone_stamp": Watermark on a background with similar content adjacent '
    "that can be mirrored over it (e.g., slide backgrounds, textures).\n"
    '- "inpaint": Watermark on complex backgrounds with text, photos, diagrams, '
    "or mixed content that can't be simply filled or cloned.\n"
    "\n"
    '"clone_direction": pick the direction with the most similar, '
    "clean content that can replace the watermark area.\n"
    "\n"
    "Return ONLY the JSON object, no markdown formatting or extra text."
)


def _build_prompt(width: int, height: int) -> str:
    return _ANALYSIS_PROMPT_TEMPLATE.replace("WIDTHxHEIGHT", f"{width}x{height}")


# Cached reference images (loaded once, reused across calls)
_reference_images_cache: list[str] | None = None


def _get_reference_images() -> list[str]:
    """Load NotebookLM watermark reference images as base64 strings.

    Returns a list of base64-encoded PNG images, or an empty list if
    the reference images aren't found (non-fatal — detection still works
    without them, just less precisely).
    """
    global _reference_images_cache
    if _reference_images_cache is not None:
        return _reference_images_cache

    from pathlib import Path

    assets_dir = Path(__file__).parent.parent / "assets"
    ref_files = [
        assets_dir / "notebooklm_watermark_dark.png",
        assets_dir / "notebooklm_watermark_light.png",
    ]

    result = []
    for ref_path in ref_files:
        if ref_path.exists():
            data = ref_path.read_bytes()
            result.append(base64.standard_b64encode(data).decode("utf-8"))
        else:
            logger.debug(f"Reference image not found: {ref_path}")

    _reference_images_cache = result
    if result:
        logger.info(f"Loaded {len(result)} NotebookLM watermark reference images")
    return result


def analyze_watermark(
    image: Image.Image,
    config: Config,
    annotation: UserAnnotation | None = None,
) -> WatermarkAnalysis:
    """Analyze an image using a vision LLM to detect and characterize watermarks.

    Args:
        image: PIL Image to analyze.
        config: Runtime config with API keys and provider selection.
        annotation: Optional user hints about the watermark.

    Returns:
        WatermarkAnalysis with detection results and recommended strategy.
    """
    if not config.can_use_ai:
        logger.warning("AI analysis unavailable (no API key). Falling back to heuristic.")
        return _heuristic_fallback(image, annotation)

    prompt = _build_prompt(image.width, image.height)

    if annotation and annotation.has_description:
        prompt += f"\n\nUser hint: {annotation.description}"

    if annotation and annotation.has_region:
        r = annotation.region
        prompt += (
            f"\n\nThe user drew a rectangle around the watermark at "
            f"x={r.x}, y={r.y}, width={r.width}, height={r.height}. "
            f"Use this as a strong hint but verify and refine the coordinates."
        )

    # Enhance contrast so faint watermarks are visible to vision models
    enhanced = _enhance_for_detection(image)

    try:
        if config.analysis_provider == AnalysisProvider.CLAUDE:
            return _analyze_with_claude(enhanced, prompt, config)
        elif config.analysis_provider == AnalysisProvider.OPENAI:
            return _analyze_with_openai(enhanced, prompt, config)
    except Exception as e:
        logger.error(f"AI analysis failed: {e}. Falling back to heuristic.")
        return _heuristic_fallback(image, annotation)


def _enhance_for_detection(image: Image.Image) -> Image.Image:
    """Boost contrast to make faint watermarks visible to vision models.

    Semi-transparent watermarks (SAMPLE PREVIEW, faint overlays) have very low
    contrast relative to the background — often just 5-15 levels on 0-255.
    Vision models miss them at normal contrast. 3x enhancement makes the
    watermark clearly visible without changing the detection coordinates.
    """
    from PIL import ImageEnhance

    return ImageEnhance.Contrast(image).enhance(3.0)


def _image_to_base64(image: Image.Image) -> str:
    """Encode a PIL Image as base64 JPEG for API transmission.

    JPEG at quality 85 is ~20x smaller than PNG — saves significant memory
    and upload time. Vision models handle JPEG fine for watermark detection.
    """
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="JPEG", quality=85)
    return base64.standard_b64encode(buf.getvalue()).decode("utf-8")


def _parse_analysis_json(raw: str, image: Image.Image) -> WatermarkAnalysis:
    """Parse the LLM's JSON response into a WatermarkAnalysis."""
    # Strip markdown code fences if present
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
        text = text.strip()

    data = json.loads(text)

    if not data.get("watermark_found", False):
        return WatermarkAnalysis(
            watermark_found=False,
            region=WatermarkRegion(0, 0, 0, 0),
            description="No watermark detected",
            confidence=data.get("confidence", 0.0),
        )

    bb = data["bounding_box"]
    region = WatermarkRegion(
        x=max(0, int(bb["x"])),
        y=max(0, int(bb["y"])),
        width=min(int(bb["width"]), image.width),
        height=min(int(bb["height"]), image.height),
    )

    bg_type = BackgroundType(data.get("background_type", "mixed"))
    strategy_str = data.get("recommended_strategy", "clone_stamp")
    # Map gradient_fill to the enum
    if strategy_str == "gradient_fill":
        strategy = RemovalStrategy.GRADIENT_FILL
    else:
        strategy = RemovalStrategy(strategy_str)

    ctx = data.get("context", {})

    # Diagonal expansion is DISABLED — it expands small watermarks (like "DRAFT"
    # in a corner) to full-image dimensions just because Claude used the word
    # "diagonal", which then gets blocked by the 8% safety guard. Trust the
    # bounding box from Vision AI instead.
    desc_lower = data.get("description", "").lower()

    # Padding gives LaMa context around the watermark for cleaner fills.
    # 1.5% is a modest increase from the original 1% — enough to catch
    # watermark edges without eating into adjacent content text.
    pad_x = max(8, int(image.width * 0.015))
    pad_y = max(8, int(image.height * 0.015))
    padded_region = region.padded_xy(pad_x, pad_y, image.width, image.height)

    return WatermarkAnalysis(
        watermark_found=True,
        region=padded_region,
        description=data.get("description", ""),
        background_type=bg_type,
        background_color=data.get("background_color"),
        strategy=strategy,
        confidence=data.get("confidence", 0.5),
        reasoning=data.get("reasoning", ""),
        context=SurroundingContext(
            above=ctx.get("above", ""),
            below=ctx.get("below", ""),
            left=ctx.get("left", ""),
            right=ctx.get("right", ""),
        ),
        clone_direction=data.get("clone_direction", "above"),
    )


# ---------------------------------------------------------------------------
# Provider: Anthropic (Claude)
# ---------------------------------------------------------------------------

def _analyze_with_claude(
    image: Image.Image, prompt: str, config: Config
) -> WatermarkAnalysis:
    """Send image to Claude for analysis, including NotebookLM watermark reference images."""
    import anthropic

    client = anthropic.Anthropic(
        api_key=config.anthropic_api_key,
        timeout=30.0,
    )
    img_b64 = _image_to_base64(image)

    # Build message content: reference images + target image + prompt
    content = []

    # Include NotebookLM watermark reference images so Claude knows exactly
    # what to look for — two variants (dark bg with white text, light bg with dark text)
    ref_images = _get_reference_images()
    if ref_images:
        content.append({
            "type": "text",
            "text": (
                "Here are reference images of the NotebookLM watermark "
                "(appears in two variants — dark and light backgrounds). "
                "Look for this exact watermark in the target image below:"
            ),
        })
        for ref_b64 in ref_images:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": ref_b64,
                },
            })

    # Target image to analyze
    content.append({
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": img_b64,
        },
    })
    content.append({"type": "text", "text": prompt})

    message = client.messages.create(
        model=config.analysis_model,
        max_tokens=1024,
        messages=[{"role": "user", "content": content}],
    )

    raw_text = message.content[0].text
    logger.info(f"Claude raw response: {raw_text}")
    result = _parse_analysis_json(raw_text, image)
    logger.info(
        f"Detection result: found={result.watermark_found}, "
        f"region=({result.region.x},{result.region.y},{result.region.width}x{result.region.height}), "
        f"strategy={result.strategy.value}, confidence={result.confidence}"
    )
    return result


# ---------------------------------------------------------------------------
# Provider: OpenAI (GPT-4o)
# ---------------------------------------------------------------------------

def _analyze_with_openai(
    image: Image.Image, prompt: str, config: Config
) -> WatermarkAnalysis:
    """Send image to GPT-4o for analysis."""
    from openai import OpenAI

    client = OpenAI(api_key=config.openai_api_key, timeout=30.0)
    img_b64 = _image_to_base64(image)

    response = client.chat.completions.create(
        model=config.analysis_model if "gpt" in config.analysis_model else "gpt-4o",
        max_tokens=1024,
        timeout=30.0,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_b64}",
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )

    raw_text = response.choices[0].message.content
    logger.debug(f"OpenAI response: {raw_text}")
    return _parse_analysis_json(raw_text, image)


# ---------------------------------------------------------------------------
# Fallback: Heuristic (no AI)
# ---------------------------------------------------------------------------

def _heuristic_fallback(
    image: Image.Image,
    annotation: UserAnnotation | None = None,
) -> WatermarkAnalysis:
    """Position-based heuristic when AI is unavailable."""
    if annotation and annotation.has_region:
        region = annotation.region
    else:
        # Default: bottom-right, 25% width, 6% height
        img_w, img_h = image.size
        wm_w = int(img_w * 0.25)
        wm_h = int(img_h * 0.06)
        region = WatermarkRegion(
            x=img_w - wm_w, y=img_h - wm_h, width=wm_w, height=wm_h
        )

    return WatermarkAnalysis(
        watermark_found=True,
        region=region,
        description="Heuristic detection — bottom-right region assumed",
        background_type=BackgroundType.MIXED,
        strategy=RemovalStrategy.CLONE_STAMP,
        confidence=0.3,
        reasoning="No AI analysis available. Using position-based heuristic.",
        clone_direction="above",
    )
