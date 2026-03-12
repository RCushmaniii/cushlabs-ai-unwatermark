"""Help page — how to use the tool."""

from unwatermark.pages.layout import page

HELP_PAGE = page("Help Center", """
<style>
  .help-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.25rem;
  }
  .step-card {
    padding: 1.75rem;
  }
  .step-card-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    border-radius: var(--radius);
    background: var(--color-primary-light);
    color: var(--color-primary);
    margin-bottom: 1.25rem;
  }
  .step-card-num {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--color-primary);
    margin-bottom: 0.4rem;
  }
  .step-card-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--color-text);
    margin-bottom: 0.6rem;
  }
  .step-card p {
    font-size: 0.9rem;
    color: var(--color-text-secondary);
    line-height: 1.65;
  }
  .technique-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 1.25rem;
  }
  .technique-card {
    padding: 1.5rem;
  }
  .technique-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: var(--radius-sm);
    background: var(--color-bg-alt);
    color: var(--color-text-muted);
    margin-bottom: 1rem;
  }
  .technique-name {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--color-text);
    margin-bottom: 0.4rem;
  }
  .technique-desc {
    font-size: 0.875rem;
    color: var(--color-text-secondary);
    line-height: 1.6;
  }
  .code-block {
    background: #0f172a;
    color: #e2e8f0;
    border-radius: var(--radius);
    padding: 1.5rem;
    font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
    font-size: 0.85rem;
    line-height: 1.7;
    white-space: pre-wrap;
    overflow-x: auto;
  }
  .code-block .cmd {
    color: #94a3b8;
  }
  .faq-item {
    padding: 1.5rem 1.75rem;
  }
  .faq-item + .faq-item {
    border-top: 1px solid var(--color-border-light);
  }
  .faq-q {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--color-text);
    margin-bottom: 0.5rem;
  }
  .faq-a {
    font-size: 0.9rem;
    color: var(--color-text-secondary);
    line-height: 1.65;
  }
  .pipeline-card {
    padding: 2rem;
  }
  .pipeline-steps {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
    justify-content: center;
  }
  .pipeline-step {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.65rem 1.25rem;
    background: var(--color-primary-light);
    border-radius: var(--radius-full);
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--color-primary);
  }
  .pipeline-arrow {
    color: var(--color-text-faint);
    flex-shrink: 0;
  }
</style>

<div class="page-header">
  <h1 class="page-title">Help Center</h1>
  <p class="page-subtitle">Everything you need to know about removing watermarks with Unwatermark.</p>
</div>

<div class="section">
  <h2 class="section-title">How It Works</h2>
  <p class="section-subtitle">Unwatermark uses a two-stage AI pipeline to remove watermarks from your files.</p>
  <div class="card card--flat pipeline-card text-center">
    <div class="pipeline-steps">
      <div class="pipeline-step">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        AI Detection
      </div>
      <div class="pipeline-arrow">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
      </div>
      <div class="pipeline-step">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
        Local Removal
      </div>
    </div>
  </div>
  <div class="prose mt-2">
    <ol>
      <li><strong>AI Analysis</strong> -- Claude's vision model examines your image to find the watermark, understand what's behind it, and recommend the best removal technique.</li>
      <li><strong>Local Removal</strong> -- The selected technique runs on the server with no additional API calls. Your files are processed and returned immediately.</li>
    </ol>
  </div>
</div>

<div class="section">
  <h2 class="section-title">Step-by-Step Guide</h2>
  <div class="help-grid">
    <div class="card step-card">
      <div class="step-card-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
      </div>
      <div class="step-card-num">Step 1</div>
      <div class="step-card-title">Upload your file</div>
      <p>Drag and drop a file onto the upload zone, or click to browse. Supports PNG, JPG, BMP, TIFF, WebP, PDF, and PPTX files up to 50 MB.</p>
    </div>

    <div class="card step-card">
      <div class="step-card-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
      </div>
      <div class="step-card-num">Step 2</div>
      <div class="step-card-title">Annotate or describe</div>
      <p>For images, draw a rectangle around the watermark and/or describe it in plain language. For PDFs and PPTX, describe the watermark in the text field. Click Analyze with AI to detect and highlight it.</p>
    </div>

    <div class="card step-card">
      <div class="step-card-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
      </div>
      <div class="step-card-num">Step 3</div>
      <div class="step-card-title">Download result</div>
      <p>For images, compare before/after with a slider. For documents, download your clean file. Use Try Again to refine, or Start Over for a new file.</p>
    </div>
  </div>
</div>

<div class="section">
  <h2 class="section-title">Removal Techniques</h2>
  <p class="section-subtitle">The AI automatically selects the best technique for each watermark based on the background.</p>
  <div class="technique-grid">
    <div class="card technique-card">
      <div class="technique-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/></svg>
      </div>
      <div class="technique-name">Solid Fill</div>
      <p class="technique-desc">Samples the color around the watermark and fills it in. Perfect for watermarks on solid-color backgrounds.</p>
    </div>

    <div class="card technique-card">
      <div class="technique-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 12h8"/><path d="M12 8v8"/></svg>
      </div>
      <div class="technique-name">Gradient Fill</div>
      <p class="technique-desc">Interpolates colors from all four edges of the watermark region. Works well on gradient backgrounds.</p>
    </div>

    <div class="card technique-card">
      <div class="technique-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
      </div>
      <div class="technique-name">Clone Stamp</div>
      <p class="technique-desc">Copies pixels from an adjacent area, mirrors them, and blends with a gradient mask. Good for simple textures and patterns.</p>
    </div>

    <div class="card technique-card">
      <div class="technique-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3h7a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-7m0-18H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h7m0-18v18"/></svg>
      </div>
      <div class="technique-name">Inpaint (LaMa)</div>
      <p class="technique-desc">Uses a state-of-the-art neural inpainting model to reconstruct content behind the watermark. Best for complex backgrounds with text, photos, or diagrams.</p>
    </div>
  </div>
</div>

<div class="section">
  <h2 class="section-title">CLI Usage</h2>
  <p class="section-subtitle">Unwatermark also works as a command-line tool for batch processing.</p>
  <div class="code-block"><span class="cmd">$</span> unwatermark image.png
<span class="cmd">$</span> unwatermark presentation.pptx -o clean.pptx
<span class="cmd">$</span> unwatermark document.pdf --annotate "watermark in bottom-right"
<span class="cmd">$</span> unwatermark photo.jpg --strategy solid_fill --no-ai</div>
  <div class="prose mt-2">
    <p>Run <code>unwatermark --help</code> for all available options.</p>
  </div>
</div>

<div class="section">
  <h2 class="section-title">Tips for Best Results</h2>
  <div class="card">
    <div class="prose">
      <ul>
        <li><strong>Draw a tight rectangle</strong> -- For images, the closer your selection fits the actual watermark, the cleaner the removal. Don't include too much surrounding content.</li>
        <li><strong>Describe both what and where</strong> -- Use both fields: "What does it look like?" (e.g., "gray NotebookLM text with icon") and "Where is it?" (e.g., "bottom-right corner, white on dark backgrounds"). The more detail you give, the better the AI performs.</li>
        <li><strong>Mention color variations</strong> -- If the watermark changes color depending on the background (e.g., "white on dark slides, gray on light slides"), mention that. The AI uses this to find it on every page.</li>
        <li><strong>Use high-res source files</strong> -- Higher resolution images give all techniques more surrounding context to work with.</li>
      </ul>
    </div>
  </div>
</div>

<div class="section">
  <h2 class="section-title">FAQ</h2>
  <div class="card" style="padding: 0; overflow: hidden;">
    <div class="faq-item">
      <div class="faq-q">Is my file sent to the cloud?</div>
      <p class="faq-a">Your image is sent to Claude's API for analysis only (to detect the watermark). The actual removal happens entirely on the server -- no image data is stored after processing.</p>
    </div>
    <div class="faq-item">
      <div class="faq-q">What about PDFs and PPTX files?</div>
      <p class="faq-a">PDFs are rendered to high-resolution images, cleaned, and reassembled. PPTX files have their embedded images processed in-place -- all slide layout, text, and formatting is preserved.</p>
    </div>
    <div class="faq-item">
      <div class="faq-q">How does the AI decide which technique to use?</div>
      <p class="faq-a">Claude's vision model examines the background behind the watermark. Solid backgrounds get a color fill, gradients get interpolated fills, and complex backgrounds (photos, text, diagrams) use LaMa neural inpainting for the best results.</p>
    </div>
  </div>
</div>
""", active_nav="help", description="Learn how to use Unwatermark — step-by-step guide, removal techniques, CLI usage, and tips for best results.", canonical_path="/help")
