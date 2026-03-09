"""Simple FastAPI web interface — drag and drop a file, get a clean version back."""

import io
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, HTMLResponse

from unwatermark.cli import _get_handler

app = FastAPI(title="Unwatermark", description="AI-powered watermark removal")


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_PAGE


@app.post("/process")
async def process_file(
    file: UploadFile = File(...),
    position: str = Form("bottom-right"),
    width_ratio: float = Form(0.25),
    height_ratio: float = Form(0.06),
):
    suffix = Path(file.filename).suffix.lower()
    handler = _get_handler(suffix)
    if handler is None:
        return {"error": f"Unsupported file type: {suffix}"}

    # Write upload to temp file
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_in:
        content = await file.read()
        tmp_in.write(content)
        tmp_in.flush()
        input_path = Path(tmp_in.name)

    output_path = input_path.with_stem(input_path.stem + "_clean")
    handler(input_path, output_path, position, width_ratio, height_ratio)

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
    display: flex; justify-content: center; align-items: center;
    min-height: 100vh; padding: 2rem;
  }
  .container { max-width: 560px; width: 100%; }
  h1 { font-size: 1.8rem; font-weight: 700; margin-bottom: 0.5rem; color: #fff; }
  .subtitle { color: #888; margin-bottom: 2rem; font-size: 0.95rem; }
  .drop-zone {
    border: 2px dashed #333; border-radius: 12px; padding: 3rem 2rem;
    text-align: center; cursor: pointer; transition: all 0.2s;
    background: #111; position: relative;
  }
  .drop-zone:hover, .drop-zone.dragover { border-color: #4f8fff; background: #0d1a2e; }
  .drop-zone p { color: #888; font-size: 0.95rem; }
  .drop-zone .formats { color: #555; font-size: 0.8rem; margin-top: 0.5rem; }
  input[type="file"] { display: none; }
  .options { margin-top: 1.5rem; display: flex; gap: 1rem; flex-wrap: wrap; }
  .options label { font-size: 0.85rem; color: #999; }
  .options select, .options input[type="number"] {
    background: #1a1a1a; border: 1px solid #333; color: #e0e0e0;
    padding: 0.4rem 0.6rem; border-radius: 6px; font-size: 0.85rem;
    width: 100%;
  }
  .field { flex: 1; min-width: 140px; }
  .btn {
    margin-top: 1.5rem; width: 100%; padding: 0.8rem;
    background: #4f8fff; color: #fff; border: none; border-radius: 8px;
    font-size: 1rem; font-weight: 600; cursor: pointer; transition: background 0.2s;
  }
  .btn:hover { background: #3a7ae8; }
  .btn:disabled { opacity: 0.4; cursor: not-allowed; }
  .status { margin-top: 1rem; text-align: center; font-size: 0.9rem; color: #888; }
  .status.error { color: #ff5555; }
  .status.success { color: #50fa7b; }
</style>
</head>
<body>
<div class="container">
  <h1>Unwatermark</h1>
  <p class="subtitle">Drop a file, get a clean version.</p>
  <form id="form" enctype="multipart/form-data">
    <div class="drop-zone" id="dropZone">
      <p id="dropText">Drop your file here or click to browse</p>
      <p class="formats">PNG, JPG, PDF, PPTX</p>
      <input type="file" id="fileInput" name="file" accept=".png,.jpg,.jpeg,.bmp,.tiff,.webp,.pdf,.pptx">
    </div>
    <div class="options">
      <div class="field">
        <label>Position</label>
        <select name="position">
          <option value="bottom-right" selected>Bottom Right</option>
          <option value="bottom-left">Bottom Left</option>
          <option value="bottom-center">Bottom Center</option>
          <option value="top-right">Top Right</option>
          <option value="top-left">Top Left</option>
          <option value="top-center">Top Center</option>
        </select>
      </div>
      <div class="field">
        <label>Width %</label>
        <input type="number" name="width_ratio" value="25" min="5" max="100" step="1">
      </div>
      <div class="field">
        <label>Height %</label>
        <input type="number" name="height_ratio" value="6" min="1" max="50" step="1">
      </div>
    </div>
    <button type="submit" class="btn" id="submitBtn" disabled>Remove Watermark</button>
  </form>
  <div class="status" id="status"></div>
</div>
<script>
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const dropText = document.getElementById('dropText');
const submitBtn = document.getElementById('submitBtn');
const status = document.getElementById('status');
const form = document.getElementById('form');

dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop', e => {
  e.preventDefault(); dropZone.classList.remove('dragover');
  fileInput.files = e.dataTransfer.files;
  onFileSelected();
});
fileInput.addEventListener('change', onFileSelected);

function onFileSelected() {
  if (fileInput.files.length > 0) {
    dropText.textContent = fileInput.files[0].name;
    submitBtn.disabled = false;
  }
}

form.addEventListener('submit', async e => {
  e.preventDefault();
  submitBtn.disabled = true;
  status.className = 'status';
  status.textContent = 'Processing...';

  const fd = new FormData();
  fd.append('file', fileInput.files[0]);
  fd.append('position', form.position.value);
  fd.append('width_ratio', (parseFloat(form.width_ratio.value) / 100).toString());
  fd.append('height_ratio', (parseFloat(form.height_ratio.value) / 100).toString());

  try {
    const resp = await fetch('/process', { method: 'POST', body: fd });
    if (!resp.ok) throw new Error('Processing failed');
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'clean_' + fileInput.files[0].name;
    a.click();
    URL.revokeObjectURL(url);
    status.className = 'status success';
    status.textContent = 'Done! Download started.';
  } catch (err) {
    status.className = 'status error';
    status.textContent = 'Error: ' + err.message;
  }
  submitBtn.disabled = false;
});
</script>
</body>
</html>
"""
