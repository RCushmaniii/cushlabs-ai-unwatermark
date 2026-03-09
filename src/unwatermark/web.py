"""FastAPI web interface — upload, annotate, analyze, remove, compare."""

from __future__ import annotations

import base64
import io
import json
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from PIL import Image

from unwatermark.cli import _get_handler
from unwatermark.config import load_config
from unwatermark.core.analyzer import analyze_watermark
from unwatermark.models.analysis import WatermarkAnalysis, WatermarkRegion
from unwatermark.models.annotation import UserAnnotation

app = FastAPI(title="Unwatermark", description="AI-powered watermark removal")


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_PAGE


@app.post("/analyze")
async def analyze_file(
    file: UploadFile = File(...),
    description: str = Form(""),
    region_x: int = Form(-1),
    region_y: int = Form(-1),
    region_w: int = Form(-1),
    region_h: int = Form(-1),
):
    """Analyze an uploaded image for watermarks. Returns detection results as JSON."""
    content = await file.read()
    image = Image.open(io.BytesIO(content))

    annotation = None
    if description or region_x >= 0:
        region = None
        if region_x >= 0 and region_w > 0:
            region = WatermarkRegion(x=region_x, y=region_y, width=region_w, height=region_h)
        annotation = UserAnnotation(description=description, region=region)

    config = load_config()
    analysis = analyze_watermark(image, config, annotation)

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
        return JSONResponse({"error": f"Unsupported file type: {suffix}"}, status_code=400)

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_in:
        content = await file.read()
        tmp_in.write(content)
        tmp_in.flush()
        input_path = Path(tmp_in.name)

    annotation = None
    if description or region_x >= 0:
        region = None
        if region_x >= 0 and region_w > 0:
            region = WatermarkRegion(x=region_x, y=region_y, width=region_w, height=region_h)
        annotation = UserAnnotation(description=description, region=region)

    config = load_config()
    force_strategy = strategy if strategy else None
    output_path = input_path.with_stem(input_path.stem + "_clean")

    handler(input_path, output_path, config, annotation, force_strategy)

    return FileResponse(
        path=str(output_path),
        filename=f"clean_{file.filename}",
        media_type="application/octet-stream",
    )


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Unwatermark</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: #0a0a0a; color: #e0e0e0;
    min-height: 100vh; padding: 2rem;
    display: flex; justify-content: center;
  }
  .app { max-width: 900px; width: 100%; }
  h1 { font-size: 1.8rem; font-weight: 700; color: #fff; margin-bottom: 0.3rem; }
  .subtitle { color: #888; margin-bottom: 2rem; font-size: 0.95rem; }

  /* Steps */
  .step { display: none; }
  .step.active { display: block; }
  .step-label { font-size: 0.75rem; color: #555; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem; }

  /* Drop zone */
  .drop-zone {
    border: 2px dashed #333; border-radius: 12px; padding: 4rem 2rem;
    text-align: center; cursor: pointer; transition: all 0.2s; background: #111;
  }
  .drop-zone:hover, .drop-zone.dragover { border-color: #4f8fff; background: #0d1a2e; }
  .drop-zone p { color: #888; }
  .drop-zone .formats { color: #555; font-size: 0.8rem; margin-top: 0.5rem; }
  input[type="file"] { display: none; }

  /* Canvas area */
  .canvas-wrapper {
    position: relative; display: inline-block; max-width: 100%;
    border-radius: 8px; overflow: hidden; background: #111;
  }
  .canvas-wrapper canvas { display: block; max-width: 100%; cursor: crosshair; }
  .canvas-hint { font-size: 0.8rem; color: #666; margin-top: 0.5rem; }

  /* Annotation */
  .annotation-bar {
    display: flex; gap: 0.75rem; margin-top: 1rem; align-items: flex-end; flex-wrap: wrap;
  }
  .annotation-bar .field { flex: 1; min-width: 200px; }
  .annotation-bar label { font-size: 0.8rem; color: #999; display: block; margin-bottom: 0.3rem; }
  .annotation-bar input, .annotation-bar select {
    width: 100%; background: #1a1a1a; border: 1px solid #333; color: #e0e0e0;
    padding: 0.5rem 0.7rem; border-radius: 6px; font-size: 0.9rem;
  }

  /* Buttons */
  .btn {
    padding: 0.7rem 1.5rem; border: none; border-radius: 8px;
    font-size: 0.95rem; font-weight: 600; cursor: pointer; transition: all 0.2s;
  }
  .btn-primary { background: #4f8fff; color: #fff; }
  .btn-primary:hover { background: #3a7ae8; }
  .btn-secondary { background: #222; color: #ccc; border: 1px solid #333; }
  .btn-secondary:hover { background: #2a2a2a; }
  .btn:disabled { opacity: 0.4; cursor: not-allowed; }
  .btn-row { display: flex; gap: 0.75rem; margin-top: 1.5rem; }

  /* Analysis result */
  .analysis-card {
    background: #111; border: 1px solid #222; border-radius: 10px;
    padding: 1.25rem; margin-top: 1.25rem;
  }
  .analysis-card h3 { font-size: 0.95rem; color: #fff; margin-bottom: 0.75rem; }
  .analysis-row { display: flex; gap: 2rem; flex-wrap: wrap; }
  .analysis-item { flex: 1; min-width: 150px; }
  .analysis-label { font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 0.05em; }
  .analysis-value { font-size: 0.95rem; color: #e0e0e0; margin-top: 0.2rem; }
  .confidence-bar { height: 4px; border-radius: 2px; background: #222; margin-top: 0.4rem; }
  .confidence-fill { height: 100%; border-radius: 2px; background: #4f8fff; transition: width 0.3s; }
  .reasoning { font-size: 0.85rem; color: #999; margin-top: 0.75rem; line-height: 1.5; }

  /* Before/After */
  .compare-container {
    position: relative; display: inline-block; max-width: 100%;
    border-radius: 8px; overflow: hidden; user-select: none;
  }
  .compare-container img { display: block; max-width: 100%; }
  .compare-after {
    position: absolute; top: 0; left: 0; height: 100%;
    overflow: hidden; border-right: 2px solid #4f8fff;
  }
  .compare-after img { display: block; max-width: none; }
  .compare-handle {
    position: absolute; top: 0; width: 36px; height: 100%;
    cursor: ew-resize; display: flex; align-items: center; justify-content: center;
    transform: translateX(-50%);
  }
  .compare-handle-line {
    width: 2px; height: 100%; background: #4f8fff; position: absolute;
  }
  .compare-handle-grip {
    width: 28px; height: 28px; border-radius: 50%; background: #4f8fff;
    display: flex; align-items: center; justify-content: center; z-index: 1;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
  }
  .compare-handle-grip svg { width: 14px; height: 14px; fill: #fff; }
  .compare-label {
    position: absolute; top: 8px; padding: 2px 8px; border-radius: 4px;
    font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;
  }
  .compare-label.before { right: 8px; background: rgba(255,85,85,0.8); color: #fff; }
  .compare-label.after { left: 8px; background: rgba(80,250,123,0.8); color: #000; }

  .status { margin-top: 1rem; font-size: 0.9rem; color: #888; text-align: center; }
  .status.error { color: #ff5555; }
  .status.success { color: #50fa7b; }
</style>
</head>
<body>
<div class="app">
  <h1>Unwatermark</h1>
  <p class="subtitle">Upload. Annotate. Remove. Compare.</p>

  <!-- Step 1: Upload -->
  <div class="step active" id="stepUpload">
    <div class="step-label">Step 1 — Upload</div>
    <div class="drop-zone" id="dropZone">
      <p>Drop your file here or click to browse</p>
      <p class="formats">PNG, JPG, PDF, PPTX</p>
      <input type="file" id="fileInput" accept=".png,.jpg,.jpeg,.bmp,.tiff,.webp,.pdf,.pptx">
    </div>
  </div>

  <!-- Step 2: Annotate + Analyze -->
  <div class="step" id="stepAnnotate">
    <div class="step-label">Step 2 — Mark the watermark (optional) and analyze</div>
    <div class="canvas-wrapper">
      <canvas id="annotCanvas"></canvas>
    </div>
    <p class="canvas-hint">Click and drag to draw a rectangle around the watermark. Or skip and let AI find it.</p>
    <div class="annotation-bar">
      <div class="field">
        <label>Describe the watermark</label>
        <input type="text" id="descInput" placeholder="e.g. gray NotebookLM text in bottom-right">
      </div>
    </div>
    <div class="btn-row">
      <button class="btn btn-secondary" id="btnClearRect">Clear Selection</button>
      <button class="btn btn-primary" id="btnAnalyze">Analyze with AI</button>
    </div>
    <div id="analysisResult"></div>
    <div class="btn-row" id="removeRow" style="display:none;">
      <div class="field" style="max-width:200px;">
        <label>Strategy</label>
        <select id="strategySelect">
          <option value="">AI Recommended</option>
          <option value="solid_fill">Solid Fill</option>
          <option value="gradient_fill">Gradient Fill</option>
          <option value="clone_stamp">Clone Stamp</option>
          <option value="inpaint">Inpaint (LaMa)</option>
        </select>
      </div>
      <button class="btn btn-primary" id="btnRemove" style="align-self:flex-end;">Remove Watermark</button>
    </div>
    <div class="status" id="status"></div>
  </div>

  <!-- Step 3: Compare -->
  <div class="step" id="stepCompare">
    <div class="step-label">Step 3 — Compare</div>
    <div class="compare-container" id="compareContainer">
      <img id="imgBefore" src="" alt="Before">
      <div class="compare-after" id="compareAfter">
        <img id="imgAfter" src="" alt="After">
      </div>
      <div class="compare-handle" id="compareHandle">
        <div class="compare-handle-line"></div>
        <div class="compare-handle-grip">
          <svg viewBox="0 0 24 24"><path d="M8 5l-5 7 5 7M16 5l5 7-5 7"/></svg>
        </div>
      </div>
      <span class="compare-label before">Before</span>
      <span class="compare-label after">After</span>
    </div>
    <div class="btn-row">
      <button class="btn btn-secondary" id="btnRestart">Start Over</button>
      <button class="btn btn-primary" id="btnDownload">Download Clean File</button>
    </div>
  </div>
</div>

<script>
// State
let uploadedFile = null;
let drawnRect = null; // {x, y, w, h} in image coords
let analysisData = null;
let cleanBlob = null;
let imgNatW = 0, imgNatH = 0;
let isDrawing = false, startX = 0, startY = 0;

// Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const canvas = document.getElementById('annotCanvas');
const ctx = canvas.getContext('2d');
const descInput = document.getElementById('descInput');
const status = document.getElementById('status');
const steps = { upload: document.getElementById('stepUpload'), annotate: document.getElementById('stepAnnotate'), compare: document.getElementById('stepCompare') };

function showStep(name) {
  Object.values(steps).forEach(s => s.classList.remove('active'));
  steps[name].classList.add('active');
}

// Step 1: Upload
dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop', e => { e.preventDefault(); dropZone.classList.remove('dragover'); fileInput.files = e.dataTransfer.files; handleFile(); });
fileInput.addEventListener('change', handleFile);

function handleFile() {
  if (!fileInput.files.length) return;
  uploadedFile = fileInput.files[0];
  const isImage = /\\.(png|jpe?g|bmp|tiff|webp)$/i.test(uploadedFile.name);
  if (isImage) {
    const reader = new FileReader();
    reader.onload = e => {
      const img = new Image();
      img.onload = () => {
        imgNatW = img.naturalWidth; imgNatH = img.naturalHeight;
        const maxW = 860;
        const scale = Math.min(1, maxW / imgNatW);
        canvas.width = imgNatW * scale; canvas.height = imgNatH * scale;
        canvas.dataset.scale = scale;
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        canvas.dataset.src = e.target.result;
        showStep('annotate');
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(uploadedFile);
  } else {
    // Non-image files skip annotation
    canvas.width = 400; canvas.height = 100;
    ctx.fillStyle = '#1a1a1a'; ctx.fillRect(0, 0, 400, 100);
    ctx.fillStyle = '#888'; ctx.font = '14px Inter, sans-serif';
    ctx.textAlign = 'center'; ctx.fillText(uploadedFile.name, 200, 55);
    showStep('annotate');
  }
}

// Canvas drawing
canvas.addEventListener('mousedown', e => {
  isDrawing = true;
  const r = canvas.getBoundingClientRect();
  startX = e.clientX - r.left; startY = e.clientY - r.top;
});
canvas.addEventListener('mousemove', e => {
  if (!isDrawing) return;
  const r = canvas.getBoundingClientRect();
  const cx = e.clientX - r.left, cy = e.clientY - r.top;
  redrawCanvas();
  ctx.strokeStyle = '#4f8fff'; ctx.lineWidth = 2; ctx.setLineDash([6, 4]);
  ctx.strokeRect(startX, startY, cx - startX, cy - startY);
  ctx.setLineDash([]);
});
canvas.addEventListener('mouseup', e => {
  if (!isDrawing) return;
  isDrawing = false;
  const r = canvas.getBoundingClientRect();
  const ex = e.clientX - r.left, ey = e.clientY - r.top;
  const scale = parseFloat(canvas.dataset.scale) || 1;
  const rx = Math.min(startX, ex) / scale, ry = Math.min(startY, ey) / scale;
  const rw = Math.abs(ex - startX) / scale, rh = Math.abs(ey - startY) / scale;
  if (rw > 5 && rh > 5) {
    drawnRect = { x: Math.round(rx), y: Math.round(ry), w: Math.round(rw), h: Math.round(rh) };
    redrawCanvas();
    drawRect(drawnRect);
  }
});

function redrawCanvas() {
  if (canvas.dataset.src) {
    const img = new Image(); img.src = canvas.dataset.src;
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
  }
}
function drawRect(r) {
  const scale = parseFloat(canvas.dataset.scale) || 1;
  ctx.strokeStyle = '#4f8fff'; ctx.lineWidth = 2;
  ctx.strokeRect(r.x * scale, r.y * scale, r.w * scale, r.h * scale);
  ctx.fillStyle = 'rgba(79, 143, 255, 0.1)';
  ctx.fillRect(r.x * scale, r.y * scale, r.w * scale, r.h * scale);
}

document.getElementById('btnClearRect').addEventListener('click', () => { drawnRect = null; redrawCanvas(); });

// Analyze
document.getElementById('btnAnalyze').addEventListener('click', async () => {
  const btn = document.getElementById('btnAnalyze');
  btn.disabled = true; status.className = 'status'; status.textContent = 'Analyzing with AI...';
  const fd = new FormData();
  fd.append('file', uploadedFile);
  fd.append('description', descInput.value);
  if (drawnRect) {
    fd.append('region_x', drawnRect.x); fd.append('region_y', drawnRect.y);
    fd.append('region_w', drawnRect.w); fd.append('region_h', drawnRect.h);
  }
  try {
    const resp = await fetch('/analyze', { method: 'POST', body: fd });
    analysisData = await resp.json();
    renderAnalysis(analysisData);
    document.getElementById('removeRow').style.display = 'flex';
    if (analysisData.strategy) document.getElementById('strategySelect').value = '';
    status.textContent = '';
  } catch (err) { status.className = 'status error'; status.textContent = 'Analysis failed: ' + err.message; }
  btn.disabled = false;
});

function renderAnalysis(a) {
  // Draw detected region on canvas
  if (a.watermark_found && a.region) {
    redrawCanvas();
    drawRect({ x: a.region.x, y: a.region.y, w: a.region.width, h: a.region.height });
  }
  const stratLabels = { solid_fill: 'Solid Fill', gradient_fill: 'Gradient Fill', clone_stamp: 'Clone Stamp', inpaint: 'Inpaint (LaMa)' };
  const bgLabels = { solid_color: 'Solid Color', gradient: 'Gradient', simple_texture: 'Simple Texture', complex_content: 'Complex Content', mixed: 'Mixed' };
  document.getElementById('analysisResult').innerHTML = `
    <div class="analysis-card">
      <h3>${a.watermark_found ? 'Watermark Detected' : 'No Watermark Found'}</h3>
      ${a.watermark_found ? `
      <div class="analysis-row">
        <div class="analysis-item">
          <div class="analysis-label">Description</div>
          <div class="analysis-value">${a.description || '—'}</div>
        </div>
        <div class="analysis-item">
          <div class="analysis-label">Background</div>
          <div class="analysis-value">${bgLabels[a.background_type] || a.background_type}</div>
        </div>
        <div class="analysis-item">
          <div class="analysis-label">Strategy</div>
          <div class="analysis-value">${stratLabels[a.strategy] || a.strategy}</div>
        </div>
        <div class="analysis-item">
          <div class="analysis-label">Confidence</div>
          <div class="analysis-value">${Math.round(a.confidence * 100)}%</div>
          <div class="confidence-bar"><div class="confidence-fill" style="width:${a.confidence * 100}%"></div></div>
        </div>
      </div>
      ${a.reasoning ? `<div class="reasoning">${a.reasoning}</div>` : ''}
      ` : '<p style="color:#888;">Try drawing a rectangle around the watermark or adding a description.</p>'}
    </div>`;
}

// Remove
document.getElementById('btnRemove').addEventListener('click', async () => {
  const btn = document.getElementById('btnRemove');
  btn.disabled = true; status.className = 'status'; status.textContent = 'Removing watermark...';
  const fd = new FormData();
  fd.append('file', uploadedFile);
  fd.append('description', descInput.value);
  fd.append('strategy', document.getElementById('strategySelect').value);
  if (drawnRect) {
    fd.append('region_x', drawnRect.x); fd.append('region_y', drawnRect.y);
    fd.append('region_w', drawnRect.w); fd.append('region_h', drawnRect.h);
  }
  try {
    const resp = await fetch('/process', { method: 'POST', body: fd });
    if (!resp.ok) throw new Error('Processing failed');
    cleanBlob = await resp.blob();
    showCompare();
  } catch (err) { status.className = 'status error'; status.textContent = 'Error: ' + err.message; }
  btn.disabled = false;
});

// Step 3: Compare
function showCompare() {
  const isImage = /\\.(png|jpe?g|bmp|tiff|webp)$/i.test(uploadedFile.name);
  if (!isImage) {
    // Non-image: just download
    triggerDownload(); return;
  }
  const beforeUrl = URL.createObjectURL(uploadedFile);
  const afterUrl = URL.createObjectURL(cleanBlob);
  document.getElementById('imgBefore').src = beforeUrl;
  document.getElementById('imgAfter').src = afterUrl;
  showStep('compare');
  initCompareSlider();
}

function initCompareSlider() {
  const container = document.getElementById('compareContainer');
  const afterDiv = document.getElementById('compareAfter');
  const handle = document.getElementById('compareHandle');
  let isDragging = false;

  function setPosition(x) {
    const rect = container.getBoundingClientRect();
    const pct = Math.max(0, Math.min(1, (x - rect.left) / rect.width));
    afterDiv.style.width = (pct * 100) + '%';
    handle.style.left = (pct * 100) + '%';
  }
  setPosition(container.getBoundingClientRect().left + container.getBoundingClientRect().width / 2);

  handle.addEventListener('mousedown', () => isDragging = true);
  document.addEventListener('mousemove', e => { if (isDragging) setPosition(e.clientX); });
  document.addEventListener('mouseup', () => isDragging = false);
  container.addEventListener('click', e => setPosition(e.clientX));
}

document.getElementById('btnDownload').addEventListener('click', triggerDownload);
function triggerDownload() {
  const url = URL.createObjectURL(cleanBlob);
  const a = document.createElement('a');
  a.href = url; a.download = 'clean_' + uploadedFile.name; a.click();
  URL.revokeObjectURL(url);
}

document.getElementById('btnRestart').addEventListener('click', () => {
  uploadedFile = null; drawnRect = null; analysisData = null; cleanBlob = null;
  fileInput.value = ''; descInput.value = '';
  document.getElementById('analysisResult').innerHTML = '';
  document.getElementById('removeRow').style.display = 'none';
  status.textContent = '';
  showStep('upload');
});
</script>
</body>
</html>
"""
