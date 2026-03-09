# User Journey — Unwatermark

## Web UI Flow

### 1. Upload
User opens `localhost:8000`, drags in a file (image, PDF, or PPTX). The first page/slide/image renders in a canvas.

### 2. Annotate (Optional)
- **Draw a rectangle** over the watermark region on the canvas
- **Type a description** in the text field: "gray NotebookLM text in bottom-right corner"
- Either or both are optional — the AI can find watermarks without hints, but hints improve accuracy on tricky cases

### 3. Analyze
User clicks "Analyze." The vision LLM examines the image + annotations and returns:
- Detected watermark region (highlighted on the canvas)
- Description of what it found
- Recommended removal strategy with confidence score
- Preview of the detection before any changes are made

The user can **accept** the detection or **adjust** the bounding box and re-analyze.

### 4. Remove
User clicks "Remove Watermark." The selected technique executes locally (no additional API calls).

### 5. Review
A **before/after slider** lets the user drag left/right to compare the original and cleaned versions. If the result isn't perfect, the user can:
- Try a different strategy from a dropdown
- Adjust the region and re-process
- Add more annotation context and re-analyze

### 6. Download
User downloads the clean file. For PPTX/PDF, all pages/slides are processed and the full file is returned.

---

## CLI Flow

### Quick (Fully Automatic)
```powershell
unwatermark presentation.pptx
```
AI detects watermarks on each slide, picks optimal strategy per-image, outputs `presentation_clean.pptx`.

### With Hints
```powershell
unwatermark photo.jpg --annotate "stock photo watermark diagonally across center"
```
Gives the AI context for tricky watermarks.

### Force Strategy
```powershell
unwatermark slide.png --strategy solid_fill
```
Skip AI analysis, use a specific technique directly.

### Offline Mode
```powershell
unwatermark image.png --no-ai --position bottom-right
```
Falls back to position-based heuristic detection (no API calls). Uses the current clone-stamp technique.

---

## Multi-Page Processing

For **PPTX** and **PDF** files, each page/slide is processed independently because:
- Different slides may have different backgrounds (one might be solid dark, another might have a photo)
- The watermark position might shift slightly between pages
- Each page may need a different removal strategy

The AI analyzes each page in sequence (or parallel with async), picks the best strategy per-page, and assembles the clean output file.

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| No API key configured | Falls back to `--no-ai` mode with warning |
| AI can't find watermark | Shows "No watermark detected" — user can draw region manually |
| Removal looks bad | User can switch strategies or adjust region |
| LaMa not installed | Falls back to clone-stamp with warning |
| Unsupported file type | Clear error message listing supported formats |
