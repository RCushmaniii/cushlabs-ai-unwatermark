# Lessons Learned — Unwatermark Development

## Phase 1: Core Pipeline (Initial Build)

### Critical Bug: python-pptx Blob Replacement
**Problem:** Watermarks were detected and removed in memory, but the output PPTX file contained the original unmodified images.

**Root cause:** `shape.image` in python-pptx returns a `pptx.parts.image.Image` wrapper object, NOT the actual `ImagePart` stored in the package. Setting `_blob` on the wrapper modifies a throwaway copy — `prs.save()` writes the original bytes.

**Fix:** Navigate through XML relationships to get the real `ImagePart`:
```python
pic = shape._element
blips = pic.findall(f".//{ns_a}blip")
r_embed = blips[0].get(f"{ns_r}embed")
actual_part = slide.part.related_part(r_embed)
actual_part._blob = new_bytes  # This persists
```

**Lesson:** Always verify that modifications actually persist to output files. Test by comparing input/output file sizes and pixel data, not just in-memory state.

### Download Tokens Lost on Server Reload
**Problem:** Long-running PPTX processing (30-60s) caused the dev server to auto-reload, wiping the in-memory `_downloads` dict. User clicked download → 404.

**Fix:** Persist download token metadata as JSON files in temp directory instead of in-memory dict.

**Lesson:** Any server state that must survive longer than a request should be persisted to disk, especially during development with auto-reload.

### Fake Analysis for Documents
**Problem:** The `/analyze` endpoint returned hardcoded 50% confidence for non-image files instead of actually analyzing them.

**Fix:** Extract first page/slide as a PIL Image via `_extract_preview()` and run real detection on it.

---

## Phase 2: Quality Improvements

### LaMa Inpainting is Essential
**Finding:** Solid fill, gradient fill, and clone stamp all leave visible artifacts on anything other than perfectly uniform backgrounds. LaMa neural inpainting produces dramatically better results across all background types.

**Decision:** Strategy selection now always returns `INPAINT` when LaMa is available. Other techniques are fallbacks only.

### Bounding Box Padding Matters
**Problem:** Initial 3% padding was too aggressive — included too much background, causing blurry regions and visible artifacts in the inpainted area.

**Fix:** Reduced to 1% padding (`pad_x = max(5, int(img_w * 0.01))`). Also added `padded_xy()` for separate horizontal/vertical padding since watermarks are typically wider than tall.

**Lesson:** Tight bounding boxes produce better inpainting. The LaMa model works best when it only has to reconstruct the watermark area, not large swaths of background.

### Icon/Logo Beside Text
**Problem:** OCR detects the text "NotebookLM" but not the broadcast icon to its left. The icon remains after removal.

**Fix:** Expand bounding box 50% leftward (since logos typically precede text in LTR layouts): `icon_margin = max(20, int(w * 0.5))`.

---

## Phase 3: Detection Reliability

### Vision LLMs are Non-Deterministic
**Problem:** Claude Vision API sometimes returned `watermark_found=false` on slides with obvious watermarks. Same image, different results across runs. This is fundamental to LLM sampling — not a bug, but an inherent limitation.

**Impact:** Out of 4 slides with identical NotebookLM watermarks, Claude would detect 2-3 on any given run, but which ones it missed was random.

**Lesson:** Never use a non-deterministic system as the sole detection mechanism for a product. LLMs are great for reasoning and fallback, but primary detection needs to be deterministic.

### EasyOCR as Primary Detector
**Solution:** Added EasyOCR as the first detection layer. Results:
- 14/14 slides detected, every time, same bounding box
- Zero API calls, zero cost
- Sub-second detection after initial model load
- AI Vision becomes a fallback for non-text watermarks only

**Architecture:** OCR (deterministic) → AI Vision (fallback) → Heuristic (last resort)

### OCR False Positives
**Problem 1:** Content text like "BioJalisco" (slide title) scored high enough to trigger as a watermark — it was in an edge position with high OCR confidence.

**Fix:** Raised scoring threshold. Pattern-matched text (known watermark brands) needs ≥ 5.0. Non-pattern text needs ≥ 4.5 (nearly impossible without a pattern match).

**Problem 2:** The regex pattern `comp(osite)?` matched "comp" inside the word "compromise" in a 9-word sentence, causing the entire title line to be detected as a watermark and destroyed by inpainting.

**Fix:** Two changes:
1. All generic patterns now use word boundaries (`\b`) — `\bsample\b`, `\bdraft\b`, `\bcomposite\b`
2. Added max 5-word filter — real watermarks are 1-4 words, not sentences

**Lesson:** OCR pattern matching must be conservative. False positives (destroying content) are far worse than false negatives (missing a watermark). Use word boundaries, word count limits, and require strong pattern matches.

### PPTX Baseline Reuse
**Problem:** Even with OCR, there's a chance detection fails on some slides (different backgrounds, lower contrast).

**Solution:** Track the first successful detection as a "baseline". If any subsequent slide fails detection, reuse the baseline bounding box. Works because watermarked presentations (NotebookLM, stock photos) put the same watermark in the same position on every slide.

---

## Phase 4: Multi-Pass Removal

### Multiple Watermarks Per Image
**Need:** Test file had two watermarks per slide (original NotebookLM + added test watermark). Single-pass only removed one.

**Solution:** `clean_image()` in `multipass.py` — runs up to 3 detect-remove cycles per image. Pass 1 uses full stack (OCR → AI). Pass 2+ uses OCR only (fast, no API calls, no risk of timeout).

### Multi-Pass Crash (Memory/API Overload)
**Problem:** With 4 slides × 3 passes each, pass 2+ fell through OCR (nothing found) → Claude Vision API. That's 8 extra API calls plus LaMa memory stacking. Server crashed with `ERR_CONNECTION_RESET`.

**Fix:** Pass 2+ restricted to OCR-only detection. Added `gc.collect()` between passes to free memory.

**Lesson:** Multi-pass systems must be careful about resource usage. Each additional pass multiplies API calls and memory. Restrict expensive operations to pass 1.

---

## Watermark Types and Detection Capabilities

| Watermark Type | Detection | Quality | Notes |
|---|---|---|---|
| Small corner text (NotebookLM) | Excellent (OCR) | Excellent | Primary use case |
| Brand text (Shutterstock, Getty) | Good (OCR) | Good | Pattern matching |
| Text in non-corner positions | Good (OCR) | Good | Edge position scoring helps |
| Semi-transparent text | Fair (OCR sometimes fails) | Good | Falls through to AI |
| Logo/icon beside text | Good | Good | Bounding box expansion catches it |
| Diagonal/rotated text | Poor (OCR can't read) | N/A | Needs AI or Florence-2 |
| Pure image/logo watermarks | Fair (AI only) | Good | Non-deterministic detection |
| Tiled/repeating watermarks | Not supported | N/A | Needs frequency domain approach |
| Watermark overlapping content | Good detection | Poor removal | Fundamental limitation — can't remove watermark without damaging content beneath |

---

## Infrastructure Lessons

### Dev Server Management
**Problem:** Stale processes on port 8000 caused frequent conflicts during development.

**Fix:** Created `scripts/restart_dev.sh` that finds PIDs on the port, kills them, waits for the port to free, starts uvicorn, and verifies a 200 response.

### Deployment Constraints
- **Vercel/Netlify/Hostinger:** Cannot run Python ML models (function size limits, no GPU, wrong runtime)
- **Recommended:** Lightweight API on Render/Railway ($7-25/mo) + ML inference on Replicate (pay per prediction)
- **Alternative:** Hugging Face Spaces (free tier, designed for ML apps)
- **Key insight:** Don't ship large models in deployment. Use hosted inference APIs (Replicate, Modal) and keep the deployment package small.

---

## v2 Architecture Plan

### Florence-2 + SAM + LaMa
Replace EasyOCR + Claude Vision with:
1. **Florence-2** — Microsoft's vision foundation model. Handles text AND logos AND rotated text. Local, deterministic, free. Replaces both EasyOCR and Claude Vision.
2. **SAM (Segment Anything)** — Produces pixel-perfect masks instead of bounding boxes. Only inpaints actual watermark pixels, not a rectangle.
3. **LaMa** — Keep existing inpainting (already works well).

### Expected Improvements
- Diagonal/rotated text detection (Florence-2 handles this)
- Logo/image watermark detection without AI API calls
- Pixel-perfect removal instead of rectangular regions
- Zero API cost for all detection
- Fully deterministic pipeline

### Trade-offs
- ~4GB model downloads (Florence-2 ~1.5GB, SAM ~2.5GB)
- Higher memory usage during inference
- For deployment: use Replicate-hosted versions to avoid shipping models
