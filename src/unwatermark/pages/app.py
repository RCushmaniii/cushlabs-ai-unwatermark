"""Main application page — the watermark removal tool."""

from unwatermark.pages.layout import page

APP_PAGE = page("App", """
<div class="steps-bar">
  <div class="step-indicator active" id="ind1"><span class="step-num">1</span>Upload</div>
  <div class="step-indicator" id="ind2"><span class="step-num">2</span><span id="step2Label">Annotate</span></div>
  <div class="step-indicator" id="ind3"><span class="step-num">3</span>Compare</div>
</div>

<!-- Step 1: Upload -->
<div class="step active" id="stepUpload">
  <div class="drop-zone" id="dropZone">
    <div class="drop-icon">
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#aaaaaa" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
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

<!-- Step 2: Annotate (images) or Describe (documents) -->
<div class="step" id="stepAnnotate">
  <!-- Image layout: canvas + side controls -->
  <div class="annotate-layout" id="imageLayout">
    <div class="canvas-area">
      <div class="canvas-wrapper" id="canvasWrapper">
        <canvas id="annotCanvas"></canvas>
      </div>
      <p class="canvas-hint" id="canvasHint">Draw a rectangle around the watermark, or let AI find it automatically.</p>
    </div>
    <div class="controls-panel">
      <div class="control-group">
        <label class="control-label">Describe the watermark</label>
        <input type="text" class="control-input" id="descInputImage"
          placeholder='e.g. "gray NotebookLM text, bottom-right"'>
      </div>
      <div class="btn-row">
        <button class="btn btn-secondary" id="btnBackImage">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
          Back
        </button>
        <button class="btn btn-secondary" id="btnClearRect" disabled>Clear Selection</button>
      </div>
      <button class="btn btn-primary btn-full" id="btnAnalyzeImage">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
        Analyze with AI
      </button>
      <div id="analysisResultImage"></div>
      <div id="removeRowImage" style="display:none;">
        <div class="control-group" style="margin-bottom:0.75rem;">
          <label class="control-label">Removal strategy</label>
          <select class="control-input" id="strategySelectImage">
            <option value="">AI Recommended</option>
            <option value="solid_fill">Solid Fill</option>
            <option value="gradient_fill">Gradient Fill</option>
            <option value="clone_stamp">Clone Stamp</option>
            <option value="inpaint">Inpaint (LaMa)</option>
          </select>
        </div>
        <button class="btn btn-primary btn-full" id="btnRemoveImage">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/><path d="M9 12l2 2 4-4"/></svg>
          Remove Watermark
        </button>
      </div>
      <div class="status" id="statusImage"></div>
    </div>
  </div>

  <!-- Document layout: centered description form -->
  <div class="describe-layout" id="docLayout" style="display:none;">
    <div class="doc-card" id="docCard">
      <div class="doc-icon">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#888888" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
      </div>
      <p class="doc-name" id="docName"></p>
      <p class="doc-size" id="docSize"></p>
    </div>
    <div class="describe-form">
      <div class="control-group">
        <label class="control-label">Describe the watermark</label>
        <input type="text" class="control-input" id="descInputDoc"
          placeholder='e.g. "gray NotebookLM text, bottom-right corner"'>
        <p class="input-help">Each page will be analyzed and processed independently.</p>
      </div>
      <div class="describe-actions">
        <button class="btn btn-secondary" id="btnBackDoc">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
          Back
        </button>
        <button class="btn btn-primary" id="btnAnalyzeDoc">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
          Analyze with AI
        </button>
      </div>
      <div id="analysisResultDoc"></div>
      <div id="removeRowDoc" style="display:none;">
        <div class="control-group" style="margin-bottom:0.75rem;">
          <label class="control-label">Removal strategy</label>
          <select class="control-input" id="strategySelectDoc">
            <option value="">AI Recommended</option>
            <option value="solid_fill">Solid Fill</option>
            <option value="gradient_fill">Gradient Fill</option>
            <option value="clone_stamp">Clone Stamp</option>
            <option value="inpaint">Inpaint (LaMa)</option>
          </select>
        </div>
        <button class="btn btn-primary btn-full" id="btnRemoveDoc">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/><path d="M9 12l2 2 4-4"/></svg>
          Remove Watermark
        </button>
      </div>
      <div class="status" id="statusDoc"></div>
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
  <div class="btn-row" style="justify-content:center;margin-top:1.25rem;">
    <button class="btn btn-secondary" id="btnRetry">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>
      Try Different Strategy
    </button>
    <button class="btn btn-secondary" id="btnRestart">Start Over</button>
    <button class="btn btn-primary" id="btnDownload">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
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
  border: 2px dashed var(--border); border-radius: var(--radius); padding: 3.5rem 2rem;
  text-align: center; cursor: pointer; transition: all 0.2s;
  background: var(--bg-primary);
}
.drop-zone:hover, .drop-zone.dragover {
  border-color: var(--accent); background: var(--accent-light);
}
.drop-icon { margin-bottom: 0.75rem; }
.drop-zone.dragover .drop-icon svg { stroke: var(--accent); }
.drop-title { color: var(--text-heading); font-size: 0.95rem; font-weight: 500; margin-bottom: 0.25rem; }
.drop-formats { color: var(--text-muted); font-size: 0.78rem; }
.drop-size { color: var(--text-faint); font-size: 0.72rem; margin-top: 0.15rem; }
input[type="file"] { display: none; }

/* Annotate layout — image files */
.annotate-layout { display: flex; gap: 1.5rem; }
.canvas-area { flex: 1; min-width: 0; }
.controls-panel { width: 260px; flex-shrink: 0; }
@media (max-width: 768px) {
  .annotate-layout { flex-direction: column; }
  .controls-panel { width: 100%; }
}

/* Canvas */
.canvas-wrapper {
  background: var(--bg-primary); border: 1px solid var(--border);
  border-radius: var(--radius); overflow: hidden; position: relative;
}
.canvas-wrapper canvas { display: block; width: 100%; cursor: crosshair; }
.canvas-hint { font-size: 0.72rem; color: var(--text-faint); margin-top: 0.4rem; }

/* Describe layout — document files */
.describe-layout {
  max-width: 520px; margin: 0 auto;
}
.doc-card {
  background: var(--bg-primary); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1.75rem; text-align: center;
  margin-bottom: 1.25rem;
}
.doc-icon { margin-bottom: 0.5rem; }
.doc-name { font-weight: 600; color: var(--text-heading); font-size: 0.92rem; margin-bottom: 0.15rem; }
.doc-size { color: var(--text-muted); font-size: 0.78rem; }
.describe-form {}
.describe-actions { display: flex; gap: 0.75rem; margin-top: 1rem; }
.describe-actions .btn-primary { flex: 1; }
.input-help { font-size: 0.72rem; color: var(--text-faint); margin-top: 0.35rem; }

/* Controls */
.control-group { margin-bottom: 0.85rem; }
.control-label {
  font-size: 0.78rem; font-weight: 600; color: var(--text-body);
  display: block; margin-bottom: 0.3rem;
}
.control-input {
  width: 100%; background: var(--bg-secondary);
  border: 1px solid var(--border); color: var(--text-heading);
  padding: 0.5rem 0.7rem; border-radius: var(--radius); font-size: 0.85rem;
  font-family: inherit; transition: border-color 0.15s;
}
.control-input:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 2px rgba(79,70,229,0.12); }
.control-input::placeholder { color: var(--text-faint); }
.btn-full { width: 100%; }

/* Analysis card */
.analysis-card {
  background: var(--bg-primary); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1rem; margin-top: 0.85rem;
}
.analysis-card h3 {
  font-size: 0.82rem; font-weight: 600; color: var(--text-heading);
  margin-bottom: 0.6rem;
}
.analysis-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; }
.analysis-item {}
.analysis-label {
  font-size: 0.68rem; color: var(--text-muted); text-transform: uppercase;
  letter-spacing: 0.04em; font-weight: 600;
}
.analysis-value { font-size: 0.82rem; color: var(--text-heading); margin-top: 0.1rem; }
.confidence-bar { height: 3px; border-radius: 2px; background: var(--border-light); margin-top: 0.25rem; }
.confidence-fill { height: 100%; border-radius: 2px; transition: width 0.4s ease; }
.confidence-high { background: var(--success); }
.confidence-mid { background: #d97706; }
.confidence-low { background: var(--error); }
.reasoning {
  font-size: 0.78rem; color: var(--text-muted); margin-top: 0.5rem;
  line-height: 1.5; grid-column: 1 / -1;
}

/* Error alert */
.error-alert {
  background: var(--error-bg); border: 1px solid var(--error-border); border-radius: var(--radius);
  padding: 0.65rem 0.85rem; margin-top: 0.85rem; display: flex; gap: 0.4rem;
  align-items: flex-start;
}
.error-alert svg { flex-shrink: 0; margin-top: 1px; }
.error-alert p { font-size: 0.82rem; color: #991b1b; line-height: 1.4; }

/* Compare */
.compare-container {
  position: relative; max-width: 100%; border-radius: var(--radius);
  overflow: hidden; user-select: none;
  border: 1px solid var(--border); background: var(--bg-primary);
}
.compare-container img { display: block; max-width: 100%; }
.compare-after {
  position: absolute; top: 0; left: 0; height: 100%;
  overflow: hidden; border-right: 2px solid var(--accent);
}
.compare-after img { display: block; max-width: none; }
.compare-handle {
  position: absolute; top: 0; width: 40px; height: 100%;
  cursor: ew-resize; display: flex; align-items: center; justify-content: center;
  transform: translateX(-50%); z-index: 2;
}
.compare-handle-line { width: 2px; height: 100%; background: var(--accent); position: absolute; }
.compare-handle-grip {
  width: 30px; height: 30px; border-radius: 50%; background: var(--accent);
  display: flex; align-items: center; justify-content: center; z-index: 1;
}
.compare-tag {
  position: absolute; top: 8px; padding: 2px 8px; border-radius: 2px;
  font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;
}
.before-tag { right: 8px; background: rgba(220,38,38,0.85); color: #fff; }
.after-tag { left: 8px; background: rgba(5,150,105,0.85); color: #fff; }
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
const canvasHint = document.getElementById('canvasHint');
const btnClearRect = document.getElementById('btnClearRect');
const step2Label = document.getElementById('step2Label');
const imageLayout = document.getElementById('imageLayout');
const docLayout = document.getElementById('docLayout');
const indicators = [document.getElementById('ind1'), document.getElementById('ind2'), document.getElementById('ind3')];
const steps = {
  upload: document.getElementById('stepUpload'),
  annotate: document.getElementById('stepAnnotate'),
  compare: document.getElementById('stepCompare'),
};

// Active desc/status/result elements depend on file type
function getDescInput() { return isImageFile ? document.getElementById('descInputImage') : document.getElementById('descInputDoc'); }
function getStatus() { return isImageFile ? document.getElementById('statusImage') : document.getElementById('statusDoc'); }
function getAnalysisResult() { return isImageFile ? document.getElementById('analysisResultImage') : document.getElementById('analysisResultDoc'); }
function getRemoveRow() { return isImageFile ? document.getElementById('removeRowImage') : document.getElementById('removeRowDoc'); }
function getStrategySelect() { return isImageFile ? document.getElementById('strategySelectImage') : document.getElementById('strategySelectDoc'); }

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
  getStatus().innerHTML = '';
  getAnalysisResult().innerHTML =
    '<div class="error-alert">' +
    '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>' +
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
    step2Label.textContent = 'Annotate';
    imageLayout.style.display = 'flex';
    docLayout.style.display = 'none';
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
    step2Label.textContent = 'Describe';
    imageLayout.style.display = 'none';
    docLayout.style.display = 'block';
    document.getElementById('docName').textContent = uploadedFile.name;
    document.getElementById('docSize').textContent = (uploadedFile.size / 1024 / 1024).toFixed(1) + ' MB';
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

// Back buttons
document.getElementById('btnBackImage').addEventListener('click', goBack);
document.getElementById('btnBackDoc').addEventListener('click', goBack);
function goBack() {
  drawnRect = null; analysisData = null;
  getAnalysisResult().innerHTML = '';
  getRemoveRow().style.display = 'none';
  getStatus().textContent = '';
  updateClearButton();
  showStep('upload');
}

// Analyze — both layouts wire to the same logic
document.getElementById('btnAnalyzeImage').addEventListener('click', doAnalyze);
document.getElementById('btnAnalyzeDoc').addEventListener('click', doAnalyze);
async function doAnalyze() {
  const btn = isImageFile ? document.getElementById('btnAnalyzeImage') : document.getElementById('btnAnalyzeDoc');
  setLoading(btn, true);
  getStatus().className = 'status'; getStatus().textContent = '';
  getAnalysisResult().innerHTML = '';

  const fd = new FormData();
  fd.append('file', uploadedFile);
  fd.append('description', getDescInput().value);
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
      getRemoveRow().style.display = 'block';
      getStrategySelect().value = '';
    }
  } catch (err) {
    showError('Could not reach the server. Check your connection and try again.');
  }
  setLoading(btn, false);
}

function renderAnalysis(a) {
  if (a.watermark_found && a.region && isImageFile) {
    redrawCanvas();
    drawRect({ x: a.region.x, y: a.region.y, w: a.region.width, h: a.region.height });
  }
  const stratLabels = { solid_fill: 'Solid Fill', gradient_fill: 'Gradient Fill', clone_stamp: 'Clone Stamp', inpaint: 'LaMa Inpaint' };
  const bgLabels = { solid_color: 'Solid Color', gradient: 'Gradient', simple_texture: 'Simple Texture', complex_content: 'Complex', mixed: 'Mixed' };
  const conf = a.confidence || 0;
  const confClass = conf >= 0.75 ? 'confidence-high' : conf >= 0.4 ? 'confidence-mid' : 'confidence-low';

  getAnalysisResult().innerHTML = a.watermark_found ? `
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
      <p style="color:var(--text-muted);font-size:0.82rem;">Try adding a description of the watermark.</p>
    </div>`;
}

// Remove — both layouts
document.getElementById('btnRemoveImage').addEventListener('click', doRemove);
document.getElementById('btnRemoveDoc').addEventListener('click', doRemove);
async function doRemove() {
  const btn = isImageFile ? document.getElementById('btnRemoveImage') : document.getElementById('btnRemoveDoc');
  setLoading(btn, true);
  getStatus().className = 'status'; getStatus().textContent = '';

  const fd = new FormData();
  fd.append('file', uploadedFile);
  fd.append('description', getDescInput().value);
  fd.append('strategy', getStrategySelect().value);
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
    getStatus().className = 'status error';
    getStatus().textContent = err.message;
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
  fileInput.value = '';
  document.getElementById('descInputImage').value = '';
  document.getElementById('descInputDoc').value = '';
  document.getElementById('analysisResultImage').innerHTML = '';
  document.getElementById('analysisResultDoc').innerHTML = '';
  document.getElementById('removeRowImage').style.display = 'none';
  document.getElementById('removeRowDoc').style.display = 'none';
  document.getElementById('statusImage').textContent = '';
  document.getElementById('statusDoc').textContent = '';
  updateClearButton();
  showStep('upload');
});
</script>
""", active_nav="app")
