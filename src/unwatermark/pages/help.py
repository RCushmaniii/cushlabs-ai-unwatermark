"""Help page — how to use the tool."""

from unwatermark.pages.layout import page

HELP_PAGE = page("Help", """
<h1 class="page-title">Help</h1>
<p class="page-subtitle">Everything you need to know about removing watermarks with Unwatermark.</p>

<div class="section">
  <h2 class="section-title">How It Works</h2>
  <div class="prose">
    <p>Unwatermark uses a two-stage AI pipeline to remove watermarks from your files:</p>
    <ol>
      <li><strong>AI Analysis</strong> — Claude's vision model examines your image to find the watermark, understand what's behind it, and recommend the best removal technique.</li>
      <li><strong>Local Removal</strong> — The selected technique runs on the server with no additional API calls. Your files are processed and returned immediately.</li>
    </ol>
  </div>
</div>

<div class="section">
  <h2 class="section-title">Step-by-Step Guide</h2>
  <div class="card">
    <h3 style="color:var(--text-heading);font-size:0.92rem;margin-bottom:0.5rem;">Step 1 — Upload</h3>
    <div class="prose">
      <p>Drag and drop a file onto the upload zone, or click to browse. Supported formats:</p>
      <ul>
        <li><strong>Images:</strong> PNG, JPG, BMP, TIFF, WebP</li>
        <li><strong>Documents:</strong> PDF (each page processed independently)</li>
        <li><strong>Presentations:</strong> PPTX (each slide image processed independently)</li>
      </ul>
      <p>Maximum file size is 50 MB.</p>
    </div>
  </div>
  <div class="card">
    <h3 style="color:var(--text-heading);font-size:0.92rem;margin-bottom:0.5rem;">Step 2 — Annotate or Describe</h3>
    <div class="prose">
      <p>For image files, you'll see your image in an interactive canvas. You have two optional tools:</p>
      <ul>
        <li><strong>Draw a rectangle</strong> — Click and drag to mark where the watermark is. This gives the AI a strong hint and improves accuracy.</li>
        <li><strong>Text description</strong> — Describe the watermark in plain language, e.g. "gray NotebookLM text in the bottom-right corner."</li>
      </ul>
      <p>For PDFs and PPTX files, you'll describe the watermark in a text field. Each page or slide is analyzed independently.</p>
      <p>Click <strong>Analyze with AI</strong> and the system will detect the watermark, highlight it on your image, and recommend the best removal strategy.</p>
    </div>
  </div>
  <div class="card">
    <h3 style="color:var(--text-heading);font-size:0.92rem;margin-bottom:0.5rem;">Step 3 — Result</h3>
    <div class="prose">
      <p>For images, a before/after slider lets you drag left and right to compare the original and cleaned versions. For documents, you'll see a success screen with your clean file ready to download.</p>
      <ul>
        <li>Click <strong>Try Again</strong> to go back and adjust your description or annotations.</li>
        <li>Click <strong>Start Over</strong> to upload a new file.</li>
      </ul>
      <p>When you're happy, click <strong>Download Clean File</strong>.</p>
    </div>
  </div>
</div>

<div class="section">
  <h2 class="section-title">Removal Techniques</h2>
  <div class="prose">
    <p>The AI automatically selects the best technique for each watermark based on the background:</p>
  </div>
  <div class="card">
    <div class="prose">
      <ul>
        <li><strong>Solid Fill</strong> — Samples the color around the watermark and fills it in. Perfect for watermarks on solid-color backgrounds.</li>
        <li><strong>Gradient Fill</strong> — Interpolates colors from all four edges of the watermark region. Works well on gradient backgrounds.</li>
        <li><strong>Clone Stamp</strong> — Copies pixels from an adjacent area (above, below, left, or right), mirrors them, and blends with a gradient mask. Good for simple textures and patterns.</li>
        <li><strong>Inpaint (LaMa)</strong> — Uses a state-of-the-art neural inpainting model to reconstruct the content behind the watermark. Best for complex backgrounds with text, photos, or diagrams.</li>
      </ul>
    </div>
  </div>
</div>

<div class="section">
  <h2 class="section-title">CLI Usage</h2>
  <div class="prose">
    <p>Unwatermark also works as a command-line tool for batch processing:</p>
  </div>
  <div class="card" style="font-family:monospace;font-size:0.82rem;color:var(--accent-hover);white-space:pre-wrap;line-height:1.6;background:var(--accent-light);">unwatermark image.png
unwatermark presentation.pptx -o clean.pptx
unwatermark document.pdf --annotate "watermark in bottom-right"
unwatermark photo.jpg --strategy solid_fill --no-ai</div>
  <div class="prose" style="margin-top:0.75rem;">
    <p>Run <code>unwatermark --help</code> for all options.</p>
  </div>
</div>

<div class="section">
  <h2 class="section-title">Tips for Best Results</h2>
  <div class="card">
    <div class="prose">
      <ul>
        <li><strong>Draw a tight rectangle</strong> — For images, the closer your selection fits the actual watermark, the cleaner the removal. Don't include too much surrounding content.</li>
        <li><strong>Describe both what and where</strong> — Use both fields: "What does it look like?" (e.g., "gray NotebookLM text with icon") and "Where is it?" (e.g., "bottom-right corner, white on dark backgrounds"). The more detail you give, the better the AI performs.</li>
        <li><strong>Mention color variations</strong> — If the watermark changes color depending on the background (e.g., "white on dark slides, gray on light slides"), mention that. The AI uses this to find it on every page.</li>
        <li><strong>Use high-res source files</strong> — Higher resolution images give all techniques more surrounding context to work with.</li>
      </ul>
    </div>
  </div>
</div>

<div class="section">
  <h2 class="section-title">FAQ</h2>
  <div class="card">
    <div class="prose">
      <p><strong>Is my file sent to the cloud?</strong></p>
      <p>Your image is sent to Claude's API for analysis only (to detect the watermark). The actual removal happens entirely on the server — no image data is stored after processing.</p>
      <p><strong>What about PDFs and PPTX files?</strong></p>
      <p>PDFs are rendered to high-resolution images, cleaned, and reassembled. PPTX files have their embedded images processed in-place — all slide layout, text, and formatting is preserved.</p>
      <p><strong>How does the AI decide which technique to use?</strong></p>
      <p>Claude's vision model examines the background behind the watermark. Solid backgrounds get a color fill, gradients get interpolated fills, and complex backgrounds (photos, text, diagrams) use LaMa neural inpainting for the best results.</p>
    </div>
  </div>
</div>
""", active_nav="help")
