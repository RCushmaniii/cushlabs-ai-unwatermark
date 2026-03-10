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
      <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
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
      <p class="canvas-hint" id="canvasHint">Draw a rectangle around the watermark, or let AI find it automatically.</p>
    </div>
    <div class="controls-panel">
      <div class="control-group">
        <label class="control-label">Describe the watermark</label>
        <input type="text" class="control-input" id="descInput"
          placeholder="e.g. gray NotebookLM text, bottom-right">
      </div>
      <div class="btn-row">
        <button class="btn btn-secondary" id="btnBack">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
          Back
        </button>
        <button class="btn btn-secondary" id="btnClearRect" disabled>Clear Selection</button>
      </div>
      <button class="btn btn-primary btn-full" id="btnAnalyze">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
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
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/><path d="M9 12l2 2 4-4"/></svg>
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
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>
      Try Different Strategy
    </button>
    <button class="btn btn-secondary" id="btnRestart">Start Over</button>
    <button class="btn btn-primary" id="btnDownload">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
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
  border: 2px dashed #cbd5e1; border-radius: 16px; padding: 4rem 2rem;
  text-align: center; cursor: pointer; transition: all 0.2s;
  background: #ffffff;
}
.drop-zone:hover, .drop-zone.dragover {
  border-color: #4f46e5; background: #f5f3ff;
}
.drop-icon { margin-bottom: 1rem; }
.drop-zone.dragover .drop-icon svg { stroke: #4f46e5; }
.drop-title { color: #334155; font-size: 1rem; font-weight: 500; margin-bottom: 0.3rem; }
.drop-formats { color: #64748b; font-size: 0.8rem; }
.drop-size { color: #94a3b8; font-size: 0.75rem; margin-top: 0.2rem; }
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
  background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px;
  overflow: hidden; position: relative;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.canvas-wrapper canvas { display: block; width: 100%; cursor: crosshair; }
.canvas-hint { font-size: 0.75rem; color: #94a3b8; margin-top: 0.5rem; }

/* Controls */
.control-group { margin-bottom: 1rem; }
.control-label {
  font-size: 0.8rem; font-weight: 600; color: #475569;
  display: block; margin-bottom: 0.35rem;
}
.control-input {
  width: 100%; background: #ffffff; border: 1px solid #e2e8f0; color: #0f172a;
  padding: 0.55rem 0.75rem; border-radius: 8px; font-size: 0.85rem;
  font-family: inherit; transition: border-color 0.15s;
}
.control-input:focus { outline: none; border-color: #4f46e5; box-shadow: 0 0 0 3px rgba(79,70,229,0.1); }
.control-input::placeholder { color: #94a3b8; }
.btn-full { width: 100%; }

/* Analysis card */
.analysis-card {
  background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px;
  padding: 1rem; margin-top: 1rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.analysis-card h3 {
  font-size: 0.85rem; font-weight: 600; color: #0f172a;
  margin-bottom: 0.75rem;
}
.analysis-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.analysis-item {}
.analysis-label {
  font-size: 0.7rem; color: #64748b; text-transform: uppercase;
  letter-spacing: 0.04em; font-weight: 600;
}
.analysis-value { font-size: 0.85rem; color: #0f172a; margin-top: 0.15rem; }
.confidence-bar { height: 3px; border-radius: 2px; background: #e2e8f0; margin-top: 0.3rem; }
.confidence-fill { height: 100%; border-radius: 2px; transition: width 0.4s ease; }
.confidence-high { background: #059669; }
.confidence-mid { background: #d97706; }
.confidence-low { background: #dc2626; }
.reasoning {
  font-size: 0.8rem; color: #64748b; margin-top: 0.6rem;
  line-height: 1.5; grid-column: 1 / -1;
}

/* Error alert */
.error-alert {
  background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px;
  padding: 0.75rem 1rem; margin-top: 1rem; display: flex; gap: 0.5rem;
  align-items: flex-start;
}
.error-alert svg { flex-shrink: 0; margin-top: 1px; }
.error-alert p { font-size: 0.85rem; color: #991b1b; line-height: 1.4; }

/* Compare */
.compare-container {
  position: relative; max-width: 100%; border-radius: 10px;
  overflow: hidden; user-select: none;
  border: 1px solid #e2e8f0; background: #ffffff;
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}
.compare-container img { display: block; max-width: 100%; }
.compare-after {
  position: absolute; top: 0; left: 0; height: 100%;
  overflow: hidden; border-right: 2px solid #4f46e5;
}
.compare-after img { display: block; max-width: none; }
.compare-handle {
  position: absolute; top: 0; width: 40px; height: 100%;
  cursor: ew-resize; display: flex; align-items: center; justify-content: center;
  transform: translateX(-50%); z-index: 2;
}
.compare-handle-line { width: 2px; height: 100%; background: #4f46e5; position: absolute; }
.compare-handle-grip {
  width: 32px; height: 32px; border-radius: 50%; background: #4f46e5;
  display: flex; align-items: center; justify-content: center; z-index: 1;
  box-shadow: 0 2px 8px rgba(79,70,229,0.35);
}
.compare-tag {
  position: absolute; top: 10px; padding: 3px 10px; border-radius: 6px;
  font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em;
}
.before-tag { right: 10px; background: rgba(220,38,38,0.85); color: #fff; }
.after-tag { left: 10px; background: rgba(5,150,105,0.85); color: #fff; }

/* File info card (non-image files) */
.file-info-card {
  background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 10px;
  padding: 2rem; text-align: center;
}
.file-info-name { font-weight: 600; color: #0f172a; font-size: 0.95rem; margin-bottom: 0.25rem; }
.file-info-size { color: #64748b; font-size: 0.8rem; margin-bottom: 0.5rem; }
.file-info-note { color: #94a3b8; font-size: 0.8rem; }
</style>

<script>
// State
let uploadedFile = null;
let drawnRect = null;
let analysisData = null;
let cleanBlob = null;
let imgNatW = 0, imgNatH = 0;
let isDrawing = false, startX = 0, startY = 0;
let isImageFile = false;

// Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const canvas = document.getElementById('annotCanvas');
const ctx = canvas.getContext('2d');
const descInput = document.getElementById('descInput');
const status = document.getElementById('status');
const canvasHint = document.getElementById('canvasHint');
const btnClearRect = document.getElementById('btnClearRect');
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
    btn.innerHTML = '<span class="spinner"></span> Processing\u2026';
  } else {
    btn.disabled = false;
    if (btn._origHTML) btn.innerHTML = btn._origHTML;
  }
}

function showError(message) {
  status.innerHTML = '';
  document.getElementById('analysisResult').innerHTML =
    '<div class="error-alert">' +
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>' +
    '<p>' + message + '</p></div>';
}

function updateClearButton() {
  btnClearRect.disabled = !drawnRect;
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

  if (uploadedFile.size > 50 * 1024 * 1024) {
    alert('File exceeds 50 MB limit.'); return;
  }

  isImageFile = /\\.(png|jpe?g|bmp|tiff|webp)$/i.test(uploadedFile.name);

  if (isImageFile) {
    canvasHint.textContent = 'Draw a rectangle around the watermark, or let AI find it automatically.';
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
        canvas.style.cursor = 'crosshair';
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        canvas.dataset.src = e.target.result;
        showStep('annotate');
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(uploadedFile);
  } else {
    // Non-image: show file info, hide drawing instructions
    canvasHint.textContent = 'AI will analyze each page independently for watermarks.';
    canvas.width = 500; canvas.height = 140;
    canvas.dataset.scale = 1;
    canvas.style.cursor = 'default';
    ctx.fillStyle = '#f1f5f9'; ctx.fillRect(0, 0, 500, 140);
    ctx.fillStyle = '#0f172a'; ctx.font = '600 14px Inter, system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(uploadedFile.name, 250, 55);
    ctx.fillStyle = '#64748b'; ctx.font = '13px Inter, system-ui, sans-serif';
    ctx.fillText((uploadedFile.size / 1024 / 1024).toFixed(1) + ' MB', 250, 78);
    ctx.fillStyle = '#94a3b8'; ctx.font = '12px Inter, system-ui, sans-serif';
    ctx.fillText('Each page will be analyzed independently', 250, 105);
    showStep('annotate');
  }
}

// Canvas drawing (only for images)
canvas.addEventListener('mousedown', e => {
  if (!isImageFile) return;
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
  ctx.strokeStyle = '#4f46e5'; ctx.lineWidth = 2; ctx.setLineDash([6, 4]);
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
    updateClearButton();
  }
});

// Touch support
canvas.addEventListener('touchstart', e => {
  if (!isImageFile) return;
  e.preventDefault();
  const touch = e.touches[0];
  canvas.dispatchEvent(new MouseEvent('mousedown', { clientX: touch.clientX, clientY: touch.clientY }));
}, { passive: false });
canvas.addEventListener('touchmove', e => {
  if (!isImageFile) return;
  e.preventDefault();
  const touch = e.touches[0];
  canvas.dispatchEvent(new MouseEvent('mousemove', { clientX: touch.clientX, clientY: touch.clientY }));
}, { passive: false });
canvas.addEventListener('touchend', e => {
  if (!isImageFile) return;
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
  ctx.fillStyle = 'rgba(79, 70, 229, 0.08)';
  ctx.fillRect(x, y, w, h);
  ctx.strokeStyle = '#4f46e5'; ctx.lineWidth = 2; ctx.setLineDash([]);
  ctx.strokeRect(x, y, w, h);
  const hs = 4;
  ctx.fillStyle = '#4f46e5';
  [[x, y], [x + w, y], [x, y + h], [x + w, y + h]].forEach(([cx, cy]) => {
    ctx.fillRect(cx - hs, cy - hs, hs * 2, hs * 2);
  });
}

btnClearRect.addEventListener('click', () => {
  drawnRect = null; redrawCanvas(); updateClearButton();
});
document.getElementById('btnBack').addEventListener('click', () => {
  drawnRect = null; analysisData = null;
  document.getElementById('analysisResult').innerHTML = '';
  document.getElementById('removeRow').style.display = 'none';
  status.textContent = '';
  updateClearButton();
  showStep('upload');
});

// Analyze
document.getElementById('btnAnalyze').addEventListener('click', async () => {
  const btn = document.getElementById('btnAnalyze');
  setLoading(btn, true);
  status.className = 'status'; status.textContent = '';
  document.getElementById('analysisResult').innerHTML = '';

  const fd = new FormData();
  fd.append('file', uploadedFile);
  fd.append('description', descInput.value);
  if (drawnRect) {
    fd.append('region_x', drawnRect.x); fd.append('region_y', drawnRect.y);
    fd.append('region_w', drawnRect.w); fd.append('region_h', drawnRect.h);
  }
  try {
    const resp = await fetch('/analyze', { method: 'POST', body: fd });
    const data = await resp.json();
    if (data.error) {
      showError(data.error);
    } else {
      analysisData = data;
      renderAnalysis(analysisData);
      document.getElementById('removeRow').style.display = 'block';
      document.getElementById('strategySelect').value = '';
    }
  } catch (err) {
    showError('Could not reach the server. Check your connection and try again.');
  }
  setLoading(btn, false);
});

function renderAnalysis(a) {
  if (a.watermark_found && a.region && isImageFile) {
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
      <p style="color:#64748b;font-size:0.85rem;">Try drawing a rectangle around the watermark or adding a description.</p>
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
    if (!resp.ok) {
      const data = await resp.json().catch(() => null);
      throw new Error(data?.error || 'Processing failed. Please try again.');
    }
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
  if (!isImageFile) { triggerDownload(); return; }
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

  requestAnimationFrame(() => {
    const rect = container.getBoundingClientRect();
    setPosition(rect.left + rect.width / 2);
  });

  handle.addEventListener('mousedown', e => { isDragging = true; e.preventDefault(); });
  document.addEventListener('mousemove', e => { if (isDragging) setPosition(e.clientX); });
  document.addEventListener('mouseup', () => isDragging = false);
  container.addEventListener('click', e => setPosition(e.clientX));

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

document.getElementById('btnRetry').addEventListener('click', () => { showStep('annotate'); });

document.getElementById('btnRestart').addEventListener('click', () => {
  uploadedFile = null; drawnRect = null; analysisData = null; cleanBlob = null;
  isImageFile = false;
  fileInput.value = ''; descInput.value = '';
  document.getElementById('analysisResult').innerHTML = '';
  document.getElementById('removeRow').style.display = 'none';
  status.textContent = '';
  updateClearButton();
  showStep('upload');
});
</script>
""", active_nav="app")
