# Architecture — Unwatermark

## Two-Stage Pipeline

The system uses a **vision LLM to analyze** the watermark, then **local image processing to remove** it. Vision models are excellent at understanding images but can't manipulate pixels. Inpainting models can manipulate pixels but need to be told what to do. This split plays to each model's strength.

```
Upload → AI Analysis → Strategy Selection → Removal Technique → Preview → Download
```

### Stage 1: Vision LLM Analysis

The AI examines the image and returns structured JSON:
- Exact bounding box of the watermark (pixel coordinates)
- What the watermark says/looks like
- What's above, below, left, right of the watermark
- Whether the surrounding area is solid color, gradient, texture, or complex content
- Recommended removal strategy + confidence score

### Stage 2: Local Removal

The strategy router dispatches to the appropriate technique — no API calls needed for the actual pixel work.

---

## Model Recommendations

### For Analysis (Stage 1)

| Model | Quality | Cost/Image | Notes |
|-------|---------|-----------|-------|
| **Claude Sonnet 4** ✓ | Best | ~$0.005 | Best spatial reasoning, reliable structured JSON |
| GPT-4o | Good | ~$0.007 | Solid alternative |
| GPT-4o-mini | Adequate | ~$0.001 | May miss subtle watermarks |

**Recommendation: Claude Sonnet 4.** At pennies per image, the quality-to-cost ratio is unbeatable. The analysis prompt is the most valuable part of the pipeline — getting the strategy right matters more than saving $0.004.

### For Removal (Stage 2)

| Technique | Cost | GPU? | When to Use |
|-----------|------|------|-------------|
| **Solid fill** | Free | No | Watermark on solid/gradient background |
| **Clone stamp** | Free | No | Repetitive patterns, simple content |
| **LaMa inpainting** ✓ | Free | No (CPU ok) | Complex textures, detailed backgrounds |
| Stable Diffusion | Free | Yes (practical) | Overkill — almost never needed |
| DALL-E API | $0.04-0.08 | No | Fallback if local inpainting unavailable |

**Recommendation: LaMa as primary inpainting engine.** It's state-of-the-art for object removal, runs on CPU, open source, and specifically designed for this use case. Solid fill and clone stamp handle easy cases without the PyTorch dependency.

---

## Required API Keys

| Key | Required? | Purpose | Where to Get |
|-----|-----------|---------|--------------|
| `ANTHROPIC_API_KEY` | **Yes** | Claude vision analysis | [console.anthropic.com](https://console.anthropic.com) |
| `OPENAI_API_KEY` | Optional | GPT-4o alternative / DALL-E fallback | [platform.openai.com](https://platform.openai.com) |

**No other services needed.** LaMa and all image processing runs locally.

### Cost Per Job

| Scenario | Cost |
|----------|------|
| Single image | ~$0.005 |
| 14-slide PPTX | ~$0.07 |
| 50-page PDF | ~$0.25 |

---

## Removal Strategies

The AI picks the best strategy based on what surrounds the watermark:

| Surrounding Content | Strategy | Technique | Quality |
|--------------------|----------|-----------|---------|
| Solid color | `SOLID_FILL` | Sample border pixels, flood fill | Perfect |
| Gradient | `GRADIENT_FILL` | Sample corners, interpolate | Excellent |
| Simple texture/pattern | `CLONE_STAMP` | Clone from adjacent area, mirror + blend | Good |
| Complex content (text, diagrams) | `INPAINT` | LaMa inpainting | Excellent |
| Mixed | `INPAINT` | LaMa (safest general-purpose) | Good-Excellent |

---

## Project Structure (Target)

```
src/unwatermark/
├── __init__.py
├── cli.py                      # Enhanced CLI with --auto, --annotate, --strategy
├── web.py                      # Web UI with annotation canvas + before/after
├── config.py                   # API key management, model selection
├── core/
│   ├── analyzer.py             # Vision LLM integration (Claude/OpenAI)
│   ├── detector.py             # Calls analyzer, falls back to heuristic
│   ├── remover.py              # Strategy router → dispatches to techniques
│   ├── strategies.py           # Strategy enum + selection logic
│   └── techniques/
│       ├── base.py             # Abstract RemovalTechnique interface
│       ├── solid_fill.py       # Color sampling + fill
│       ├── clone_stamp.py      # Mirror/clone from adjacent area
│       └── lama_inpaint.py     # LaMa inpainting wrapper
├── handlers/
│   ├── image.py                # Standalone image processing
│   ├── pdf.py                  # PDF page render → clean → reassemble
│   └── pptx.py                 # PPTX image blob replacement
└── models/
    ├── analysis.py             # WatermarkAnalysis, RemovalStrategy dataclasses
    └── annotation.py           # UserAnnotation dataclass
```

---

## Implementation Phases

### Phase 1: Core Restructure
Extract clone-stamp into `techniques/clone_stamp.py`, create base technique interface, create strategy enums, create data models. Everything still works without AI.

### Phase 2: Vision Analysis
Build `analyzer.py` with Claude integration. Wire into detector as new default. Old heuristic becomes `--no-ai` fallback.

### Phase 3: Solid Fill Technique
Handle the most common easy case (watermark on solid background) without needing LaMa.

### Phase 4: LaMa Inpainting
Handle the hard cases. PyTorch is an optional dependency (`pip install -e ".[inpaint]"`).

### Phase 5: Web UI Annotation
Canvas overlay for drawing watermark region, text annotation field, preview with detected region highlighted, before/after comparison slider.

### Phase 6: Full Pipeline
Wire everything: upload → analyze → choose strategy → execute → preview → download.
