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
  .best-for-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
  .best-for-card {
    padding: 1.5rem;
  }
  .best-for-card h3 {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .best-for-card ul {
    list-style: none;
    padding: 0;
  }
  .best-for-card li {
    font-size: 0.875rem;
    color: var(--color-text-secondary);
    line-height: 1.6;
    padding: 0.3rem 0;
    padding-left: 1.25rem;
    position: relative;
  }
  .best-for-card li::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0.65rem;
    width: 6px;
    height: 6px;
    border-radius: 50%;
  }
  .best-for-good li::before { background: #22c55e; }
  .best-for-limited li::before { background: #f59e0b; }
  @media (max-width: 640px) {
    .best-for-grid { grid-template-columns: 1fr; }
  }
</style>

<div class="page-header">
  <h1 class="page-title">Help Center</h1>
  <p class="page-subtitle">Everything you need to know about removing watermarks with Unwatermark.</p>
</div>

<div class="section">
  <h2 class="section-title">How It Works</h2>
  <p class="section-subtitle">Upload a file, and our AI pipeline automatically detects and removes watermarks.</p>
  <div class="card card--flat pipeline-card text-center">
    <div class="pipeline-steps">
      <div class="pipeline-step">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
        Upload
      </div>
      <div class="pipeline-arrow">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
      </div>
      <div class="pipeline-step">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        AI Detection
      </div>
      <div class="pipeline-arrow">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
      </div>
      <div class="pipeline-step">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
        Neural Inpainting
      </div>
      <div class="pipeline-arrow">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
      </div>
      <div class="pipeline-step">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        Download
      </div>
    </div>
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
      <div class="step-card-title">AI processes your file</div>
      <p>The detection pipeline automatically scans for watermarks using AI vision analysis. For multi-page files (PDF, PPTX), each page is processed individually with real-time progress updates.</p>
    </div>

    <div class="card step-card">
      <div class="step-card-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
      </div>
      <div class="step-card-num">Step 3</div>
      <div class="step-card-title">Download your clean file</div>
      <p>For images, compare before and after with an interactive slider. For documents and presentations, download the cleaned file directly. Click Start Over to process another file.</p>
    </div>
  </div>
</div>

<div class="section">
  <h2 class="section-title">Best Results</h2>
  <p class="section-subtitle">Unwatermark works best with certain types of watermarks. Here's what to expect.</p>
  <div class="best-for-grid">
    <div class="card best-for-card best-for-good">
      <h3>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        Works well
      </h3>
      <ul>
        <li>Small corner watermarks on simple backgrounds</li>
        <li>Stock photo text overlays (Shutterstock, Getty, etc.)</li>
        <li>Copyright text and "DRAFT" stamps</li>
        <li>Watermarks on solid or gradient backgrounds</li>
        <li>Single-image files (PNG, JPG)</li>
      </ul>
    </div>
    <div class="card best-for-card best-for-limited">
      <h3>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        May have limitations
      </h3>
      <ul>
        <li>Small watermarks near dense content text</li>
        <li>Large diagonal overlays covering the whole image</li>
        <li>Tiled/repeating watermark patterns</li>
        <li>Watermarks overlapping complex graphics or photos</li>
        <li>Multi-page PPTX with varied slide layouts</li>
      </ul>
    </div>
  </div>
</div>

<div class="section">
  <h2 class="section-title">Supported Formats</h2>
  <div class="card">
    <div class="prose">
      <ul>
        <li><strong>Images</strong> -- PNG, JPG, BMP, TIFF, WebP. Single image files up to 50 MB. Results include a before/after comparison slider.</li>
        <li><strong>PDF</strong> -- Multi-page documents (up to 15 pages). Each page is rendered to a high-resolution image, cleaned, and reassembled into a new PDF. Note: vector content is rasterized in this process.</li>
        <li><strong>PPTX</strong> -- PowerPoint presentations (up to 15 slides). Embedded slide images are processed in-place, preserving all slide layout and formatting.</li>
      </ul>
    </div>
  </div>
</div>

<div class="section">
  <h2 class="section-title">FAQ</h2>
  <div class="card" style="padding: 0; overflow: hidden;">
    <div class="faq-item">
      <div class="faq-q">Is my file sent to the cloud?</div>
      <p class="faq-a">Your file is sent to AI services for watermark detection (to locate the watermark). The actual removal uses neural inpainting via our processing pipeline. Files are not stored after processing -- they are discarded once you download the result.</p>
    </div>
    <div class="faq-item">
      <div class="faq-q">Why does processing take a while?</div>
      <p class="faq-a">The pipeline runs multiple detection passes and neural inpainting for each page. For multi-page files like PPTX, each slide is processed individually. Processing typically takes 15-60 seconds per page depending on complexity.</p>
    </div>
    <div class="faq-item">
      <div class="faq-q">What if the watermark isn't fully removed?</div>
      <p class="faq-a">Some watermarks, especially very small ones near dense content, are difficult to remove cleanly. The pipeline prioritizes preserving your content over aggressive removal -- it's better to leave a trace than to damage the surrounding text or graphics.</p>
    </div>
    <div class="faq-item">
      <div class="faq-q">Does this work with NotebookLM watermarks?</div>
      <p class="faq-a">Yes, NotebookLM watermarks are one of the primary use cases. The tool has specific detection logic for the small "NotebookLM" text that appears in the bottom-right corner of exported slides. Results vary depending on how close the watermark is to slide content.</p>
    </div>
    <div class="faq-item">
      <div class="faq-q">Is this free to use?</div>
      <p class="faq-a">Yes, completely free. No signup, no account, no usage limits. The tool is a portfolio project by CushLabs AI Services.</p>
    </div>
  </div>
</div>
""", active_nav="help", description="Learn how to use Unwatermark -- step-by-step guide, supported formats, best results tips, and frequently asked questions.", canonical_path="/help")
