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

ANALYSIS_PROMPT = """You are a watermark detection expert. Analyze this image and identify any watermarks.

Return a JSON object with these exact fields:
{
  "watermark_found": true/false,
  "bounding_box": {"x": int, "y": int, "width": int, "height": int},
  "description": "what the watermark looks like and says",
  "background_type": "solid_color" | "gradient" | "simple_texture" | "complex_content" | "mixed",
  "background_color": "#hex or null if not solid",
  "recommended_strategy": "solid_fill" | "gradient_fill" | "clone_stamp" | "inpaint",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation of why you chose this strategy",
  "context": {
    "above": "what's above the watermark",
    "below": "what's below the watermark",
    "left": "what's left of the watermark",
    "right": "what's right of the watermark"
  },
  "clone_direction": "above" | "below" | "left" | "right"
}

Rules for strategy selection:
- "solid_fill": Use when the watermark sits on a solid color background. Cheapest and most perfect result.
- "gradient_fill": Use when background is a smooth gradient.
- "clone_stamp": Use when there's similar content adjacent that can be mirrored over the watermark.
- "inpaint": Use for complex backgrounds with text, photos, or diagrams behind the watermark.

For "clone_direction": pick the direction that has the most similar content to what's likely behind the watermark.

The image dimensions are {width}x{height} pixels. Return pixel coordinates for the bounding box.

Return ONLY the JSON object, no markdown formatting or extra text."""


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

    prompt = ANALYSIS_PROMPT.format(width=image.width, height=image.height)

    if annotation and annotation.has_description:
        prompt += f"\n\nUser hint: {annotation.description}"

    if annotation and annotation.has_region:
        r = annotation.region
        prompt += (
            f"\n\nThe user drew a rectangle around the watermark at "
            f"x={r.x}, y={r.y}, width={r.width}, height={r.height}. "
            f"Use this as a strong hint but verify and refine the coordinates."
        )

    try:
        if config.analysis_provider == AnalysisProvider.CLAUDE:
            return _analyze_with_claude(image, prompt, config)
        elif config.analysis_provider == AnalysisProvider.OPENAI:
            return _analyze_with_openai(image, prompt, config)
    except Exception as e:
        logger.error(f"AI analysis failed: {e}. Falling back to heuristic.")
        return _heuristic_fallback(image, annotation)


def _image_to_base64(image: Image.Image) -> str:
    """Encode a PIL Image as base64 PNG for API transmission."""
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="PNG")
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

    return WatermarkAnalysis(
        watermark_found=True,
        region=region.padded(10, image.width, image.height),
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
    """Send image to Claude for analysis."""
    import anthropic

    client = anthropic.Anthropic(api_key=config.anthropic_api_key)
    img_b64 = _image_to_base64(image)

    message = client.messages.create(
        model=config.analysis_model,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": img_b64,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )

    raw_text = message.content[0].text
    logger.debug(f"Claude response: {raw_text}")
    return _parse_analysis_json(raw_text, image)


# ---------------------------------------------------------------------------
# Provider: OpenAI (GPT-4o)
# ---------------------------------------------------------------------------

def _analyze_with_openai(
    image: Image.Image, prompt: str, config: Config
) -> WatermarkAnalysis:
    """Send image to GPT-4o for analysis."""
    from openai import OpenAI

    client = OpenAI(api_key=config.openai_api_key)
    img_b64 = _image_to_base64(image)

    response = client.chat.completions.create(
        model=config.analysis_model if "gpt" in config.analysis_model else "gpt-4o",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_b64}",
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
