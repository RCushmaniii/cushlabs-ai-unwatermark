"""Main application page — the watermark removal tool."""

from unwatermark.pages.layout import page

APP_PAGE = page("App", """
<div class="steps-bar">
  <div class="step-indicator active" id="ind1"><span class="step-num">1</span>Upload</div>
  <div class="step-indicator" id="ind2"><span class="step-num">2</span>Annotate</div>
  <div class="step-indicator" id="ind3"><span class="step-num">3</span>Compare</div>
</div>

<!-- Step 1: Upload -->
<div class="step active" id="stepUpload">
  <div class="drop-zone" id="dropZone">
    <div class="drop-icon">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#3f3f46" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="17 8 12 3 7 8"/>
        <line x1="12" y1="3" x2="12" y2="15"/>
      </svg>
    </div>
    <p class="drop-title">Drop your file here or click to browse</p>
    <p class="drop-formats">PNG, JPG, BMP, TIFF, WebP, PDF, PPTX</p>
    <p class="drop-size">Max 50 MB</p>
    <input type="file" id="fileInput" accept=".png,.jpg,.jpeg,.bmp,.tiff,.webp,.pdf,.pptx">
  </div>
</div>

<!-- Step 2: Annotate + Analyze -->
<div class="step" id="stepAnnotate">
  <div class="annotate-layout">
    <div class="canvas-area">
      <div class="canvas-wrapper" id="canvasWrapper">
        <canvas id="annotCanvas"></canvas>
      </div>
      <p class="canvas-hint">Draw a rectangle around the watermark, or let AI find it automatically.</p>
    </div>
    <div class="controls-panel">
      <div class="control-group">
        <label class="control-label">Describe the watermark</label>
        <input type="text" class="control-input" id="descInput" placeholder="e.g. gray NotebookLM text in bottom-right">
      </div>
      <div class="btn-row">
        <button class="btn btn-secondary" id="btnBack" title="Go back to upload">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
          Back
        </button>
        <button class="btn btn-secondary" id="btnClearRect">Clear Selection</button>
      </div>
      <button class="btn btn-primary btn-full" id="btnAnalyze">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        Analyze with AI
      </button>
      <div id="analysisResult"></div>
      <div id="removeRow" style="display:none;">
        <div class="control-group" style="margin-bottom:0.75rem;">
          <label class="control-label">Removal strategy</label>
          <select class="control-input" id="strategySelect">
            <option value="">AI Recommended</option>
            <option value="solid_fill">Solid Fill</option>
            <option value="gradient_fill">Gradient Fill</option>
            <option value="clone_stamp">Clone Stamp</option>
            <option value="inpaint">Inpaint (LaMa)</option>
          </select>
        </div>
        <button class="btn btn-primary btn-full" id="btnRemove">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/><path d="M9 12l2 2 4-4"/></svg>
          Remove Watermark
        </button>
      </div>
      <div class="status" id="status"></div>
    </div>
  </div>
</div>

<!-- Step 3: Compare -->
<div class="step" id="stepCompare">
  <div class="compare-container" id="compareContainer">
    <img id="imgBefore" src="" alt="Before">
    <div class="compare-after" id="compareAfter">
      <img id="imgAfter" src="" alt="After">
    </div>
    <div class="compare-handle" id="compareHandle">
      <div class="compare-handle-line"></div>
      <div class="compare-handle-grip">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="#fff"><path d="M8 5l-5 7 5 7M16 5l5 7-5 7"/></svg>
      </div>
    </div>
    <span class="compare-tag before-tag">Before</span>
    <span class="compare-tag after-tag">After</span>
  </div>
  <div class="btn-row" style="justify-content:center;margin-top:1.5rem;">
    <button class="btn btn-secondary" id="btnRetry">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>
      Try Different Strategy
    </button>
    <button class="btn btn-secondary" id="btnRestart">Start Over</button>
    <button class="btn btn-primary" id="btnDownload">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
      Download Clean File
    </button>
  </div>
</div>

<style>
/* Steps */
.step { display: none; }
.step.active { display: block; }

/* Drop zone */
.drop-zone {
  border: 2px dashed #27272a; border-radius: 16px; padding: 4rem 2rem;
  text-align: center; cursor: pointer; transition: all 0.2s;
  background: #0c0c0e;
}
.drop-zone:hover, .drop-zone.dragover {
  border-color: #3b82f6; background: #0c1629;
}
.drop-icon { margin-bottom: 1rem; }
.drop-zone.dragover .drop-icon svg { stroke: #3b82f6; }
.drop-title { color: #a1a1aa; font-size: 1rem; font-weight: 500; margin-bottom: 0.4rem; }
.drop-formats { color: #52525b; font-size: 0.8rem; }
.drop-size { color: #3f3f46; font-size: 0.75rem; margin-top: 0.25rem; }
input[type="file"] { display: none; }

/* Annotate layout */
.annotate-layout { display: flex; gap: 1.5rem; }
.canvas-area { flex: 1; min-width: 0; }
.controls-panel { width: 280px; flex-shrink: 0; }
@media (max-width: 768px) {
  .annotate-layout { flex-direction: column; }
  .controls-panel { width: 100%; }
}

/* Canvas */
.canvas-wrapper {
  background: #0c0c0e; border: 1px solid #1e1e22; border-radius: 10px;
  overflow: hidden; position: relative;
}
.canvas-wrapper canvas { display: block; width: 100%; cursor: crosshair; }
.canvas-hint { font-size: 0.75rem; color: #3f3f46; margin-top: 0.5rem; }

/* Controls */
.control-group { margin-bottom: 1rem; }
.control-label { font-size: 0.8rem; font-weight: 500; color: #71717a; display: block; margin-bottom: 0.35rem; }
.control-input {
  width: 100%; background: #111113; border: 1px solid #27272a; color: #d4d4d8;
  padding: 0.55rem 0.75rem; border-radius: 8px; font-size: 0.85rem;
  font-family: inherit; transition: border-color 0.15s;
}
.control-input:focus { outline: none; border-color: #3b82f6; }
.control-input::placeholder { color: #3f3f46; }
.btn-full { width: 100%; }

/* Analysis card */
.analysis-card {
  background: #111113; border: 1px solid #1e1e22; border-radius: 10px;
  padding: 1rem; margin-top: 1rem;
}
.analysis-card h3 {
  font-size: 0.85rem; font-weight: 600; color: #fafafa;
  margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.4rem;
}
.analysis-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.analysis-item {}
.analysis-label { font-size: 0.7rem; color: #52525b; text-transform: uppercase; letter-spacing: 0.04em; font-weight: 600; }
.analysis-value { font-size: 0.85rem; color: #d4d4d8; margin-top: 0.15rem; }
.confidence-bar { height: 3px; border-radius: 2px; background: #1e1e22; margin-top: 0.3rem; }
.confidence-fill { height: 100%; border-radius: 2px; transition: width 0.4s ease; }
.confidence-high { background: #4ade80; }
.confidence-mid { background: #facc15; }
.confidence-low { background: #f87171; }
.reasoning { font-size: 0.8rem; color: #71717a; margin-top: 0.6rem; line-height: 1.5; grid-column: 1 / -1; }

/* Compare */
.compare-container {
  position: relative; max-width: 100%; border-radius: 10px;
  overflow: hidden; user-select: none; background: #0c0c0e;
  border: 1px solid #1e1e22;
}
.compare-container img { display: block; max-width: 100%; }
.compare-after {
  position: absolute; top: 0; left: 0; height: 100%;
  overflow: hidden; border-right: 2px solid #3b82f6;
}
.compare-after img { display: block; max-width: none; }
.compare-handle {
  position: absolute; top: 0; width: 40px; height: 100%;
  cursor: ew-resize; display: flex; align-items: center; justify-content: center;
  transform: translateX(-50%); z-index: 2;
}
.compare-handle-line { width: 2px; height: 100%; background: #3b82f6; position: absolute; }
.compare-handle-grip {
  width: 32px; height: 32px; border-radius: 50%; background: #3b82f6;
  display: flex; align-items: center; justify-content: center; z-index: 1;
  box-shadow: 0 2px 12px rgba(0,0,0,0.5);
}
.compare-tag {
  position: absolute; top: 10px; padding: 3px 10px; border-radius: 6px;
  font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em;
}
.before-tag { right: 10px; background: rgba(248,113,113,0.85); color: #fff; }
.after-tag { left: 10px; background: rgba(74,222,128,0.85); color: #000; }
</style>

<script>
// State
let uploadedFile = null;
let drawnRect = null;
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
const indicators = [document.getElementById('ind1'), document.getElementById('ind2'), document.getElementById('ind3')];
const steps = {
  upload: document.getElementById('stepUpload'),
  annotate: document.getElementById('stepAnnotate'),
  compare: document.getElementById('stepCompare'),
};

function showStep(name) {
  Object.values(steps).forEach(s => s.classList.remove('active'));
  steps[name].classList.add('active');
  const idx = name === 'upload' ? 0 : name === 'annotate' ? 1 : 2;
  indicators.forEach((ind, i) => {
    ind.classList.remove('active', 'done');
    if (i < idx) ind.classList.add('done');
    else if (i === idx) ind.classList.add('active');
  });
}

function setLoading(btn, loading) {
  if (loading) {
    btn._origHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Processing...';
  } else {
    btn.disabled = false;
    if (btn._origHTML) btn.innerHTML = btn._origHTML;
  }
}

// Step 1: Upload
dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop', e => {
  e.preventDefault(); dropZone.classList.remove('dragover');
  fileInput.files = e.dataTransfer.files; handleFile();
});
fileInput.addEventListener('change', handleFile);

function handleFile() {
  if (!fileInput.files.length) return;
  uploadedFile = fileInput.files[0];

  // Validate size
  if (uploadedFile.size > 50 * 1024 * 1024) {
    alert('File exceeds 50 MB limit.'); return;
  }

  const isImage = /\\.(png|jpe?g|bmp|tiff|webp)$/i.test(uploadedFile.name);
  if (isImage) {
    const reader = new FileReader();
    reader.onload = e => {
      const img = new Image();
      img.onload = () => {
        imgNatW = img.naturalWidth; imgNatH = img.naturalHeight;
        const wrapper = document.getElementById('canvasWrapper');
        const maxW = wrapper.clientWidth || 620;
        const scale = Math.min(1, maxW / imgNatW);
        canvas.width = Math.round(imgNatW * scale);
        canvas.height = Math.round(imgNatH * scale);
        canvas.dataset.scale = scale;
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        canvas.dataset.src = e.target.result;
        showStep('annotate');
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(uploadedFile);
  } else {
    // Non-image: show file info card
    canvas.width = 500; canvas.height = 120;
    canvas.dataset.scale = 1;
    const grad = ctx.createLinearGradient(0, 0, 500, 120);
    grad.addColorStop(0, '#111113'); grad.addColorStop(1, '#18181b');
    ctx.fillStyle = grad; ctx.fillRect(0, 0, 500, 120);
    ctx.fillStyle = '#71717a'; ctx.font = '500 13px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(uploadedFile.name, 250, 50);
    ctx.fillStyle = '#3f3f46'; ctx.font = '12px Inter, sans-serif';
    ctx.fillText((uploadedFile.size / 1024 / 1024).toFixed(1) + ' MB', 250, 72);
    ctx.fillText('AI will analyze each page independently', 250, 95);
    showStep('annotate');
  }
}

// Canvas drawing
canvas.addEventListener('mousedown', e => {
  isDrawing = true;
  const r = canvas.getBoundingClientRect();
  const scaleX = canvas.width / r.width;
  const scaleY = canvas.height / r.height;
  startX = (e.clientX - r.left) * scaleX;
  startY = (e.clientY - r.top) * scaleY;
});
canvas.addEventListener('mousemove', e => {
  if (!isDrawing) return;
  const r = canvas.getBoundingClientRect();
  const scaleX = canvas.width / r.width;
  const scaleY = canvas.height / r.height;
  const cx = (e.clientX - r.left) * scaleX;
  const cy = (e.clientY - r.top) * scaleY;
  redrawCanvas();
  ctx.strokeStyle = '#3b82f6'; ctx.lineWidth = 2; ctx.setLineDash([6, 4]);
  ctx.strokeRect(startX, startY, cx - startX, cy - startY);
  ctx.setLineDash([]);
});
canvas.addEventListener('mouseup', e => {
  if (!isDrawing) return;
  isDrawing = false;
  const r = canvas.getBoundingClientRect();
  const scaleX = canvas.width / r.width;
  const scaleY = canvas.height / r.height;
  const ex = (e.clientX - r.left) * scaleX;
  const ey = (e.clientY - r.top) * scaleY;
  const imgScale = parseFloat(canvas.dataset.scale) || 1;
  const rx = Math.min(startX, ex) / imgScale;
  const ry = Math.min(startY, ey) / imgScale;
  const rw = Math.abs(ex - startX) / imgScale;
  const rh = Math.abs(ey - startY) / imgScale;
  if (rw > 5 && rh > 5) {
    drawnRect = { x: Math.round(rx), y: Math.round(ry), w: Math.round(rw), h: Math.round(rh) };
    redrawCanvas();
    drawRect(drawnRect);
  }
});

// Touch support
canvas.addEventListener('touchstart', e => {
  e.preventDefault();
  const touch = e.touches[0];
  canvas.dispatchEvent(new MouseEvent('mousedown', { clientX: touch.clientX, clientY: touch.clientY }));
}, { passive: false });
canvas.addEventListener('touchmove', e => {
  e.preventDefault();
  const touch = e.touches[0];
  canvas.dispatchEvent(new MouseEvent('mousemove', { clientX: touch.clientX, clientY: touch.clientY }));
}, { passive: false });
canvas.addEventListener('touchend', e => {
  const touch = e.changedTouches[0];
  canvas.dispatchEvent(new MouseEvent('mouseup', { clientX: touch.clientX, clientY: touch.clientY }));
});

function redrawCanvas() {
  if (canvas.dataset.src) {
    const img = new Image(); img.src = canvas.dataset.src;
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
  }
}
function drawRect(r) {
  const scale = parseFloat(canvas.dataset.scale) || 1;
  const x = r.x * scale, y = r.y * scale, w = r.w * scale, h = r.h * scale;
  ctx.fillStyle = 'rgba(59, 130, 246, 0.08)';
  ctx.fillRect(x, y, w, h);
  ctx.strokeStyle = '#3b82f6'; ctx.lineWidth = 2; ctx.setLineDash([]);
  ctx.strokeRect(x, y, w, h);
  // Corner handles
  const hs = 5;
  ctx.fillStyle = '#3b82f6';
  [[x, y], [x + w, y], [x, y + h], [x + w, y + h]].forEach(([cx, cy]) => {
    ctx.fillRect(cx - hs, cy - hs, hs * 2, hs * 2);
  });
}

document.getElementById('btnClearRect').addEventListener('click', () => { drawnRect = null; redrawCanvas(); });
document.getElementById('btnBack').addEventListener('click', () => {
  drawnRect = null; analysisData = null;
  document.getElementById('analysisResult').innerHTML = '';
  document.getElementById('removeRow').style.display = 'none';
  status.textContent = '';
  showStep('upload');
});

// Analyze
document.getElementById('btnAnalyze').addEventListener('click', async () => {
  const btn = document.getElementById('btnAnalyze');
  setLoading(btn, true);
  status.className = 'status'; status.textContent = '';
  const fd = new FormData();
  fd.append('file', uploadedFile);
  fd.append('description', descInput.value);
  if (drawnRect) {
    fd.append('region_x', drawnRect.x); fd.append('region_y', drawnRect.y);
    fd.append('region_w', drawnRect.w); fd.append('region_h', drawnRect.h);
  }
  try {
    const resp = await fetch('/analyze', { method: 'POST', body: fd });
    if (!resp.ok) throw new Error('Analysis request failed');
    analysisData = await resp.json();
    renderAnalysis(analysisData);
    document.getElementById('removeRow').style.display = 'block';
    document.getElementById('strategySelect').value = '';
  } catch (err) {
    status.className = 'status error';
    status.textContent = err.message;
  }
  setLoading(btn, false);
});

function renderAnalysis(a) {
  if (a.watermark_found && a.region) {
    redrawCanvas();
    drawRect({ x: a.region.x, y: a.region.y, w: a.region.width, h: a.region.height });
  }
  const stratLabels = { solid_fill: 'Solid Fill', gradient_fill: 'Gradient Fill', clone_stamp: 'Clone Stamp', inpaint: 'LaMa Inpaint' };
  const bgLabels = { solid_color: 'Solid Color', gradient: 'Gradient', simple_texture: 'Simple Texture', complex_content: 'Complex', mixed: 'Mixed' };
  const conf = a.confidence || 0;
  const confClass = conf >= 0.75 ? 'confidence-high' : conf >= 0.4 ? 'confidence-mid' : 'confidence-low';

  document.getElementById('analysisResult').innerHTML = a.watermark_found ? `
    <div class="analysis-card">
      <h3>Watermark Detected</h3>
      <div class="analysis-grid">
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
          <div class="analysis-value">${Math.round(conf * 100)}%</div>
          <div class="confidence-bar"><div class="confidence-fill ${confClass}" style="width:${conf * 100}%"></div></div>
        </div>
        <div class="analysis-item">
          <div class="analysis-label">Description</div>
          <div class="analysis-value">${a.description || '\\u2014'}</div>
        </div>
        ${a.reasoning ? `<div class="reasoning">${a.reasoning}</div>` : ''}
      </div>
    </div>` : `
    <div class="analysis-card">
      <h3>No Watermark Found</h3>
      <p style="color:#71717a;font-size:0.85rem;">Try drawing a rectangle around the watermark or adding a description.</p>
    </div>`;
}

// Remove
document.getElementById('btnRemove').addEventListener('click', doRemove);
async function doRemove() {
  const btn = document.getElementById('btnRemove');
  setLoading(btn, true);
  status.className = 'status'; status.textContent = '';
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
  } catch (err) {
    status.className = 'status error';
    status.textContent = err.message;
  }
  setLoading(btn, false);
}

// Compare
function showCompare() {
  const isImage = /\\.(png|jpe?g|bmp|tiff|webp)$/i.test(uploadedFile.name);
  if (!isImage) { triggerDownload(); return; }
  const beforeUrl = URL.createObjectURL(uploadedFile);
  const afterUrl = URL.createObjectURL(cleanBlob);
  const beforeImg = document.getElementById('imgBefore');
  const afterImg = document.getElementById('imgAfter');
  beforeImg.src = beforeUrl;
  afterImg.src = afterUrl;
  beforeImg.onload = () => {
    afterImg.style.width = beforeImg.clientWidth + 'px';
    showStep('compare');
    initCompareSlider();
  };
}

function initCompareSlider() {
  const container = document.getElementById('compareContainer');
  const afterDiv = document.getElementById('compareAfter');
  const handle = document.getElementById('compareHandle');
  let isDragging = false;

  function setPosition(clientX) {
    const rect = container.getBoundingClientRect();
    const pct = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
    afterDiv.style.width = (pct * 100) + '%';
    handle.style.left = (pct * 100) + '%';
  }

  // Start at 50%
  requestAnimationFrame(() => {
    const rect = container.getBoundingClientRect();
    setPosition(rect.left + rect.width / 2);
  });

  handle.addEventListener('mousedown', e => { isDragging = true; e.preventDefault(); });
  document.addEventListener('mousemove', e => { if (isDragging) setPosition(e.clientX); });
  document.addEventListener('mouseup', () => isDragging = false);
  container.addEventListener('click', e => setPosition(e.clientX));

  // Touch
  handle.addEventListener('touchstart', e => { isDragging = true; e.preventDefault(); }, { passive: false });
  document.addEventListener('touchmove', e => { if (isDragging) setPosition(e.touches[0].clientX); });
  document.addEventListener('touchend', () => isDragging = false);
}

document.getElementById('btnDownload').addEventListener('click', triggerDownload);
function triggerDownload() {
  const url = URL.createObjectURL(cleanBlob);
  const a = document.createElement('a');
  a.href = url; a.download = 'clean_' + uploadedFile.name; a.click();
  URL.revokeObjectURL(url);
}

document.getElementById('btnRetry').addEventListener('click', () => {
  showStep('annotate');
});

document.getElementById('btnRestart').addEventListener('click', () => {
  uploadedFile = null; drawnRect = null; analysisData = null; cleanBlob = null;
  fileInput.value = ''; descInput.value = '';
  document.getElementById('analysisResult').innerHTML = '';
  document.getElementById('removeRow').style.display = 'none';
  status.textContent = '';
  showStep('upload');
});
</script>
""", active_nav="app")
