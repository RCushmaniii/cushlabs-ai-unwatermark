"""Main application page — the watermark removal tool."""

from unwatermark.pages.layout import page

APP_PAGE = page("Remove Watermarks", """
<style>
/* Steps */
.step { display: none; }
.step.active { display: block; }

/* Drop zone */
.drop-zone {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius);
  padding: 5rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s var(--ease);
  background: var(--color-bg-alt);
  position: relative;
}
.drop-zone:hover, .drop-zone.dragover {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
  box-shadow: 0 0 0 4px rgba(37,99,235,0.06);
}
.drop-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  border-radius: var(--radius-lg);
  background: var(--color-bg);
  box-shadow: var(--shadow-sm);
  margin: 0 auto 1.25rem;
  transition: all 0.25s var(--ease);
}
.drop-zone:hover .drop-icon,
.drop-zone.dragover .drop-icon {
  background: var(--color-primary-light);
  box-shadow: var(--shadow);
}
.drop-zone.dragover .drop-icon svg { stroke: var(--color-primary); }
.drop-title {
  font-family: 'DM Sans', sans-serif;
  color: var(--color-text);
  font-size: 1.15rem;
  font-weight: 600;
  margin-bottom: 0.35rem;
  letter-spacing: -0.01em;
}
.drop-formats {
  color: var(--color-text-muted);
  font-size: 0.9rem;
  margin-bottom: 0.15rem;
}
.drop-size {
  color: var(--color-text-faint);
  font-size: 0.82rem;
}
input[type="file"] { display: none; }

/* Processing view */
.processing-view {
  max-width: 600px;
  margin: 0 auto;
}
.processing-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.file-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--color-bg);
  padding: 0.75rem 1.25rem;
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  width: 100%;
}
.file-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.file-name {
  font-weight: 600;
  color: var(--color-text);
}
.file-size {
  color: var(--color-text-muted);
  font-size: 0.85rem;
  margin-left: auto;
}

/* Progress bar (processing view) */
.progress-track {
  height: 8px;
  background: var(--color-border-light);
  border-radius: var(--radius-full);
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: var(--radius-full);
  transition: width 0.3s var(--ease);
  width: 0%;
}

/* Activity feed */
.activity-feed {
  background: var(--color-bg);
  border-radius: var(--radius);
  padding: 1rem 1.25rem;
  box-shadow: var(--shadow-sm);
  margin-top: 1rem;
  max-height: 400px;
  overflow-y: auto;
}
.activity-item {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.5rem 0;
  font-size: 0.9rem;
  animation: slideIn 0.2s ease;
  border-bottom: 1px solid var(--color-border-light);
}
.activity-item:last-child {
  border-bottom: none;
}
.activity-item.active {
  color: var(--color-primary);
  font-weight: 500;
}
.activity-item.done {
  color: var(--color-text-muted);
}
.activity-icon {
  flex-shrink: 0;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}
@keyframes slideIn {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}
.spinner-sm {
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-border-light);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Error alert */
.error-alert {
  background: var(--color-error-light);
  border: 1px solid var(--color-error-border);
  border-radius: var(--radius-sm);
  padding: 0.85rem 1rem;
  margin-top: 1rem;
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
}
.error-alert svg { flex-shrink: 0; margin-top: 2px; }
.error-alert p { font-size: 0.9rem; color: #991b1b; line-height: 1.5; }

/* Compare */
.compare-container {
  position: relative;
  max-width: 100%;
  border-radius: var(--radius-lg);
  overflow: hidden;
  user-select: none;
  box-shadow: var(--shadow-md);
  background: var(--color-bg);
}
.compare-container img { display: block; max-width: 100%; }
.compare-after {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  overflow: hidden;
  border-right: 2px solid var(--color-primary);
}
.compare-after img { display: block; max-width: none; }
.compare-handle {
  position: absolute;
  top: 0;
  width: 40px;
  height: 100%;
  cursor: ew-resize;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateX(-50%);
  z-index: 2;
}
.compare-handle-line {
  width: 2px;
  height: 100%;
  background: var(--color-primary);
  position: absolute;
}
.compare-handle-grip {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
  box-shadow: var(--shadow);
  transition: transform 0.15s var(--ease);
}
.compare-handle-grip:hover {
  transform: scale(1.1);
}
.compare-tag {
  position: absolute;
  top: 12px;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.before-tag { right: 12px; background: rgba(220,38,38,0.85); color: #fff; }
.after-tag { left: 12px; background: rgba(5,150,105,0.85); color: #fff; }

/* Page navigation for multi-page documents */
.page-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}
.page-nav-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius);
  border: 1px solid var(--color-border);
  background: var(--color-bg);
  cursor: pointer;
  transition: all 0.15s var(--ease);
  color: var(--color-text-secondary);
}
.page-nav-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: var(--color-primary-light);
}
.page-nav-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
.page-nav-label {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  min-width: 100px;
  text-align: center;
}

/* Result buttons */
.result-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  margin-top: 1.5rem;
  flex-wrap: wrap;
}
</style>

<div class="steps-bar">
  <div class="step-indicator active" id="ind1"><span class="step-num">1</span>Upload</div>
  <div class="step-indicator" id="ind2"><span class="step-num">2</span>Processing</div>
  <div class="step-indicator" id="ind3"><span class="step-num">3</span>Result</div>
</div>

<!-- Step 1: Upload -->
<div class="step active" id="stepUpload">
  <div class="drop-zone" id="dropZone">
    <div class="drop-icon">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
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

<!-- Step 2: Processing -->
<div class="step" id="stepProcessing">
  <div class="processing-view">
    <div class="processing-header">
      <div class="file-info">
        <span class="file-icon" id="fileIcon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        </span>
        <span class="file-name" id="fileName"></span>
        <span class="file-size" id="fileSize"></span>
      </div>
    </div>
    <div class="progress-track">
      <div class="progress-fill" id="progressFill"></div>
    </div>
    <div class="activity-feed" id="activityFeed"></div>
    <div id="processingError"></div>
  </div>
</div>

<!-- Step 3: Result -->
<div class="step" id="stepResult">
  <!-- Image result: before/after slider -->
  <div id="imageResult" style="display:none;">
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
    <div class="result-actions" style="margin-top:1.5rem;">
      <button class="btn btn-secondary" id="btnRestart">Start Over</button>
      <button class="btn btn-primary" id="btnDownload">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        Download Clean File
      </button>
    </div>
  </div>

  <!-- Document result: before/after slider with page navigation -->
  <div id="docResult" style="display:none;">
    <div class="page-nav" id="pageNav">
      <button class="page-nav-btn" id="btnPrevPage" disabled>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
      </button>
      <span class="page-nav-label" id="pageLabel">Page 1 of 1</span>
      <button class="page-nav-btn" id="btnNextPage" disabled>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
      </button>
    </div>
    <div class="compare-container" id="docCompareContainer">
      <img id="docImgBefore" src="" alt="Before">
      <div class="compare-after" id="docCompareAfter">
        <img id="docImgAfter" src="" alt="After">
      </div>
      <div class="compare-handle" id="docCompareHandle">
        <div class="compare-handle-line"></div>
        <div class="compare-handle-grip">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="#fff"><path d="M8 5l-5 7 5 7M16 5l5 7-5 7"/></svg>
        </div>
      </div>
      <span class="compare-tag before-tag">Before</span>
      <span class="compare-tag after-tag">After</span>
    </div>
    <div class="result-actions" style="margin-top:1.5rem;">
      <button class="btn btn-secondary" id="btnRestartDoc">Start Over</button>
      <button class="btn btn-primary btn-lg" id="btnDownloadDoc">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        Download Clean File
      </button>
    </div>
  </div>
</div>

<script>
// State
let uploadedFile = null;
let cleanBlob = null;
let isImageFile = false;
let downloadToken = null;
let docPageCount = 0;
let docCurrentPage = 0;

// SVG icons
const checkSvg = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>';
const imageSvg = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>';
const docSvg = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>';

// Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const indicators = [document.getElementById('ind1'), document.getElementById('ind2'), document.getElementById('ind3')];
const steps = {
  upload: document.getElementById('stepUpload'),
  processing: document.getElementById('stepProcessing'),
  result: document.getElementById('stepResult'),
};

function showStep(name) {
  Object.values(steps).forEach(s => s.classList.remove('active'));
  steps[name].classList.add('active');
  const idx = name === 'upload' ? 0 : name === 'processing' ? 1 : 2;
  indicators.forEach((ind, i) => {
    ind.classList.remove('active', 'done');
    if (i < idx) ind.classList.add('done');
    else if (i === idx) ind.classList.add('active');
  });
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function showError(message) {
  document.getElementById('processingError').innerHTML =
    '<div class="error-alert">' +
    '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>' +
    '<p>' + message + '</p></div>' +
    '<div class="result-actions" style="margin-top:1rem;">' +
    '<button class="btn btn-secondary" onclick="doRestart()">Start Over</button></div>';
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

  // Set up processing view
  document.getElementById('fileName').textContent = uploadedFile.name;
  document.getElementById('fileSize').textContent = formatFileSize(uploadedFile.size);
  document.getElementById('fileIcon').innerHTML = isImageFile ? imageSvg : docSvg;
  document.getElementById('progressFill').style.width = '0%';
  document.getElementById('activityFeed').innerHTML = '';
  document.getElementById('processingError').innerHTML = '';

  showStep('processing');
  doProcess();
}

// Activity feed helpers
function addActivityItem(text, isActive) {
  const feed = document.getElementById('activityFeed');

  // Mark previous active item as done
  var prev = feed.querySelector('.activity-item.active');
  if (prev) {
    prev.classList.remove('active');
    prev.classList.add('done');
    prev.querySelector('.activity-icon').innerHTML = checkSvg;
  }

  var item = document.createElement('div');
  item.className = 'activity-item ' + (isActive ? 'active' : 'done');
  item.innerHTML =
    '<span class="activity-icon">' +
    (isActive ? '<div class="spinner-sm"></div>' : checkSvg) +
    '</span>' +
    '<span class="activity-text">' + escapeHtml(text) + '</span>';
  feed.appendChild(item);

  // Auto-scroll to bottom
  feed.scrollTop = feed.scrollHeight;
}

function markAllDone() {
  var feed = document.getElementById('activityFeed');
  var active = feed.querySelector('.activity-item.active');
  if (active) {
    active.classList.remove('active');
    active.classList.add('done');
    active.querySelector('.activity-icon').innerHTML = checkSvg;
  }
}

function escapeHtml(text) {
  var div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Process — streams NDJSON from /process
async function doProcess() {
  var fill = document.getElementById('progressFill');
  fill.style.width = '2%';
  addActivityItem('Starting processing...', true);

  var fd = new FormData();
  fd.append('file', uploadedFile);

  try {
    var resp = await fetch('/process', { method: 'POST', body: fd });
    if (!resp.ok) {
      var data = await resp.json().catch(function() { return null; });
      throw new Error(data && data.error ? data.error : 'Processing failed. Please try again.');
    }

    // Read the NDJSON stream line by line
    var reader = resp.body.getReader();
    var decoder = new TextDecoder();
    var buffer = '';
    downloadToken = null;

    while (true) {
      var result = await reader.read();
      if (result.done) break;
      buffer += decoder.decode(result.value, { stream: true });
      var lines = buffer.split('\\n');
      buffer = lines.pop();
      for (var i = 0; i < lines.length; i++) {
        var line = lines[i];
        if (!line.trim()) continue;
        var evt = JSON.parse(line);
        if (evt.type === 'progress') {
          fill.style.width = evt.pct + '%';
          addActivityItem(evt.message, true);
        } else if (evt.type === 'complete') {
          downloadToken = evt.download_token;
          docPageCount = evt.page_count || 0;
          fill.style.width = '100%';
          markAllDone();
          addActivityItem('Processing complete', false);
        } else if (evt.type === 'error') {
          throw new Error(evt.message);
        }
      }
    }

    if (!downloadToken) throw new Error('Processing completed but no download available.');

    // Download the result
    addActivityItem('Downloading result...', true);
    var dlResp = await fetch('/download/' + downloadToken);
    if (!dlResp.ok) throw new Error('Download failed.');
    cleanBlob = await dlResp.blob();
    markAllDone();

    showResult();
  } catch (err) {
    markAllDone();
    showError(err.message);
  }
}

// Result
function showResult() {
  if (!isImageFile && docPageCount > 0) {
    // Document: show before/after slider with page navigation
    document.getElementById('imageResult').style.display = 'none';
    document.getElementById('docResult').style.display = 'block';
    docCurrentPage = 0;
    updatePageNav();
    loadDocPage(0);
    showStep('result');
    return;
  }
  // Image: show before/after slider
  document.getElementById('imageResult').style.display = 'block';
  document.getElementById('docResult').style.display = 'none';
  var beforeUrl = URL.createObjectURL(uploadedFile);
  var afterUrl = URL.createObjectURL(cleanBlob);
  var beforeImg = document.getElementById('imgBefore');
  var afterImg = document.getElementById('imgAfter');
  beforeImg.src = beforeUrl;
  afterImg.src = afterUrl;
  beforeImg.onload = function() {
    afterImg.style.width = beforeImg.clientWidth + 'px';
    showStep('result');
    initCompareSlider('compareContainer', 'compareAfter', 'compareHandle');
  };
}

// Document page navigation
function updatePageNav() {
  var label = document.getElementById('pageLabel');
  var fileType = /\\.pptx$/i.test(uploadedFile.name) ? 'Slide' : 'Page';
  label.textContent = fileType + ' ' + (docCurrentPage + 1) + ' of ' + docPageCount;
  document.getElementById('btnPrevPage').disabled = docCurrentPage <= 0;
  document.getElementById('btnNextPage').disabled = docCurrentPage >= docPageCount - 1;
}

function loadDocPage(pageIdx) {
  var beforeImg = document.getElementById('docImgBefore');
  var afterImg = document.getElementById('docImgAfter');
  var beforeUrl = '/preview/' + downloadToken + '/before/' + pageIdx;
  var afterUrl = '/preview/' + downloadToken + '/after/' + pageIdx;
  beforeImg.src = beforeUrl;
  afterImg.src = afterUrl;
  beforeImg.onload = function() {
    afterImg.style.width = beforeImg.clientWidth + 'px';
    initCompareSlider('docCompareContainer', 'docCompareAfter', 'docCompareHandle');
  };
}

document.getElementById('btnPrevPage').addEventListener('click', function() {
  if (docCurrentPage > 0) {
    docCurrentPage--;
    updatePageNav();
    loadDocPage(docCurrentPage);
  }
});

document.getElementById('btnNextPage').addEventListener('click', function() {
  if (docCurrentPage < docPageCount - 1) {
    docCurrentPage++;
    updatePageNav();
    loadDocPage(docCurrentPage);
  }
});

// Generic compare slider — works for both image and document results
// Track active slider state to avoid stacking document-level listeners
var activeSlider = null;

function initCompareSlider(containerId, afterId, handleId) {
  var container = document.getElementById(containerId);
  var afterDiv = document.getElementById(afterId);
  var handle = document.getElementById(handleId);

  function setPosition(clientX) {
    var rect = container.getBoundingClientRect();
    var pct = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
    afterDiv.style.width = (pct * 100) + '%';
    handle.style.left = (pct * 100) + '%';
  }

  // Store as active slider so document-level handlers use the right elements
  activeSlider = { container: container, setPosition: setPosition, isDragging: false };

  requestAnimationFrame(function() {
    var rect = container.getBoundingClientRect();
    setPosition(rect.left + rect.width / 2);
  });

  // Remove old element-level listeners by cloning
  var newHandle = handle.cloneNode(true);
  handle.parentNode.replaceChild(newHandle, handle);
  handle = newHandle;

  handle.addEventListener('mousedown', function(e) { activeSlider.isDragging = true; e.preventDefault(); });
  container.addEventListener('click', function(e) { activeSlider.setPosition(e.clientX); });
  handle.addEventListener('touchstart', function(e) { activeSlider.isDragging = true; e.preventDefault(); }, { passive: false });
}

// Single set of document-level listeners for drag handling
document.addEventListener('mousemove', function(e) {
  if (activeSlider && activeSlider.isDragging) activeSlider.setPosition(e.clientX);
});
document.addEventListener('mouseup', function() {
  if (activeSlider) activeSlider.isDragging = false;
});
document.addEventListener('touchmove', function(e) {
  if (activeSlider && activeSlider.isDragging) activeSlider.setPosition(e.touches[0].clientX);
});
document.addEventListener('touchend', function() {
  if (activeSlider) activeSlider.isDragging = false;
});

function triggerDownload() {
  var url = URL.createObjectURL(cleanBlob);
  var a = document.createElement('a');
  a.href = url; a.download = 'clean_' + uploadedFile.name; a.click();
  URL.revokeObjectURL(url);
}

document.getElementById('btnDownload').addEventListener('click', triggerDownload);
document.getElementById('btnDownloadDoc').addEventListener('click', triggerDownload);

function doRestart() {
  uploadedFile = null; cleanBlob = null;
  isImageFile = false; downloadToken = null;
  docPageCount = 0; docCurrentPage = 0;
  fileInput.value = '';
  document.getElementById('activityFeed').innerHTML = '';
  document.getElementById('processingError').innerHTML = '';
  document.getElementById('progressFill').style.width = '0%';
  document.getElementById('imageResult').style.display = 'none';
  document.getElementById('docResult').style.display = 'none';
  showStep('upload');
}
document.getElementById('btnRestart').addEventListener('click', doRestart);
document.getElementById('btnRestartDoc').addEventListener('click', doRestart);
</script>
""", active_nav="app", description="Upload an image, PDF, or PPTX to remove watermarks with AI. Drop a file, watch AI process it in real time, and download your clean file instantly.", canonical_path="/app")
