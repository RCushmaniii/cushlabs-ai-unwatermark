"""About page — project journey, technology, and honest assessment."""

from unwatermark.pages.layout import page

ABOUT_PAGE = page("About", """
<style>
  .about-hero {
    text-align: center;
    padding-bottom: 2.5rem;
    border-bottom: 1px solid var(--color-border-light);
    margin-bottom: 2.5rem;
  }
  .about-hero h1 {
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin-bottom: 0.75rem;
  }
  .about-hero p {
    font-size: 1.05rem;
    color: var(--color-text-muted);
    max-width: 620px;
    margin: 0 auto;
    line-height: 1.7;
  }
  .journey-section {
    margin-bottom: 3rem;
  }
  .journey-section h2 {
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: 1rem;
    letter-spacing: -0.01em;
  }
  .journey-section .prose {
    max-width: 720px;
  }
  .timeline {
    position: relative;
    padding-left: 2rem;
  }
  .timeline::before {
    content: '';
    position: absolute;
    left: 7px;
    top: 4px;
    bottom: 4px;
    width: 2px;
    background: var(--color-border);
    border-radius: 1px;
  }
  .timeline-item {
    position: relative;
    padding-bottom: 1.75rem;
  }
  .timeline-item:last-child { padding-bottom: 0; }
  .timeline-dot {
    position: absolute;
    left: -2rem;
    top: 4px;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: var(--color-bg);
    border: 2px solid var(--color-primary);
  }
  .timeline-item:last-child .timeline-dot {
    border-color: #22c55e;
    background: #f0fdf4;
  }
  .timeline-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--color-text);
    margin-bottom: 0.35rem;
  }
  .timeline-desc {
    font-size: 0.9rem;
    color: var(--color-text-secondary);
    line-height: 1.65;
  }
  .tech-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1rem;
  }
  .tech-item {
    padding: 1.25rem;
  }
  .tech-item-name {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--color-text);
    margin-bottom: 0.3rem;
  }
  .tech-item-role {
    font-size: 0.82rem;
    color: var(--color-text-muted);
    line-height: 1.55;
  }
  .insight-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
  .insight-card {
    padding: 1.5rem;
  }
  .insight-card h3 {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--color-text);
    margin-bottom: 0.5rem;
  }
  .insight-card p {
    font-size: 0.875rem;
    color: var(--color-text-secondary);
    line-height: 1.65;
  }
  .cushlabs-card {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    padding: 2rem;
    background: var(--color-bg-alt);
    border-radius: var(--radius-lg);
    border: 1px solid var(--color-border-light);
  }
  .cushlabs-card-text h3 {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 0.4rem;
  }
  .cushlabs-card-text p {
    font-size: 0.9rem;
    color: var(--color-text-secondary);
    line-height: 1.6;
  }
  .cushlabs-logo-box {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 56px;
    height: 56px;
    min-width: 56px;
    border-radius: var(--radius);
    background: var(--color-primary);
    color: #fff;
  }
  @media (max-width: 640px) {
    .insight-grid { grid-template-columns: 1fr; }
    .cushlabs-card { flex-direction: column; text-align: center; }
  }
</style>

<div class="about-hero">
  <h1>About Unwatermark</h1>
  <p>An AI-powered watermark removal tool built as a deep exploration of computer vision, neural inpainting, and the real-world limits of AI precision.</p>
</div>

<div class="journey-section">
  <h2>The Journey</h2>
  <div class="prose">
    <p>Unwatermark started as a straightforward idea: use AI to automatically detect and remove watermarks from images and presentations. What followed was a deep technical journey that taught us more about the boundaries of current AI capabilities than any tutorial or course could.</p>
  </div>
  <div class="timeline mt-3">
    <div class="timeline-item">
      <div class="timeline-dot"></div>
      <div class="timeline-title">Detection Pipeline</div>
      <div class="timeline-desc">Built a layered detection system: EasyOCR for text watermarks, Claude and GPT-4o Vision for logos, Lang-SAM for pixel-perfect mask generation. Each layer handles cases the others miss.</div>
    </div>
    <div class="timeline-item">
      <div class="timeline-dot"></div>
      <div class="timeline-title">Neural Inpainting</div>
      <div class="timeline-desc">Integrated LaMa (Large Mask Inpainting) from Samsung Research -- a state-of-the-art model that reconstructs what was behind the watermark rather than just blurring it out.</div>
    </div>
    <div class="timeline-item">
      <div class="timeline-dot"></div>
      <div class="timeline-title">Multi-Format Support</div>
      <div class="timeline-desc">Extended beyond single images to handle PDFs (render, clean, reassemble) and PowerPoint files (process embedded slide images in-place while preserving all formatting).</div>
    </div>
    <div class="timeline-item">
      <div class="timeline-dot"></div>
      <div class="timeline-title">The Precision Problem</div>
      <div class="timeline-desc">Discovered the fundamental challenge: watermark removal requires pixel-perfect precision, but general-purpose AI models (Vision APIs, segmentation models) operate at a much coarser resolution. A 5% bounding box error that's fine for "find the cat" is catastrophic for "remove only these 20 pixels without touching the adjacent text."</div>
    </div>
    <div class="timeline-item">
      <div class="timeline-dot"></div>
      <div class="timeline-title">Content Preservation</div>
      <div class="timeline-desc">Implemented extensive safeguards -- region size limits, dark-pixel protection, SAM margin caps, multi-pass scanning with heuristic blocking -- all to prevent the removal process from damaging content near the watermark. The guiding principle: better to leave a watermark than destroy content.</div>
    </div>
    <div class="timeline-item">
      <div class="timeline-dot"></div>
      <div class="timeline-title">Current State</div>
      <div class="timeline-desc">The tool works well for simple watermark cases and provides a real-time streaming processing experience. Complex cases (small watermarks near dense content) remain challenging -- an honest reflection of where AI precision stands today.</div>
    </div>
  </div>
</div>

<div class="journey-section">
  <h2>Technology Stack</h2>
  <p class="section-subtitle">A serious AI pipeline, not a blur filter.</p>
  <div class="tech-list">
    <div class="card tech-item">
      <div class="tech-item-name">Claude Vision + GPT-4o</div>
      <div class="tech-item-role">AI watermark detection -- analyzes images to locate watermarks, identify backgrounds, and recommend removal strategies</div>
    </div>
    <div class="card tech-item">
      <div class="tech-item-name">LaMa Inpainting</div>
      <div class="tech-item-role">Samsung Research's large mask inpainting model -- reconstructs content behind watermarks using neural networks</div>
    </div>
    <div class="card tech-item">
      <div class="tech-item-name">Lang-SAM</div>
      <div class="tech-item-role">Text-prompted segmentation for pixel-perfect mask generation -- produces precise boundaries between watermark and content</div>
    </div>
    <div class="card tech-item">
      <div class="tech-item-name">EasyOCR</div>
      <div class="tech-item-role">Deterministic text detection -- catches text watermarks like "NotebookLM", "Shutterstock", "DRAFT" reliably and locally</div>
    </div>
    <div class="card tech-item">
      <div class="tech-item-name">FastAPI + NDJSON</div>
      <div class="tech-item-role">Web framework with streaming progress -- real-time updates as each slide or page is processed</div>
    </div>
    <div class="card tech-item">
      <div class="tech-item-name">Python + Pillow + NumPy</div>
      <div class="tech-item-role">Image processing foundation -- mask generation, threshold refinement, morphological operations, format conversion</div>
    </div>
  </div>
</div>

<div class="journey-section">
  <h2>What We Learned</h2>
  <p class="section-subtitle">Honest insights from building an AI-powered image editing tool.</p>
  <div class="insight-grid">
    <div class="card insight-card">
      <h3>Detection is harder than removal</h3>
      <p>LaMa inpainting produces excellent results when given an accurate mask. The entire quality challenge comes from detection precision -- knowing exactly which pixels are watermark and which are content.</p>
    </div>
    <div class="card insight-card">
      <h3>API-based AI has precision limits</h3>
      <p>General-purpose Vision APIs return bounding boxes with ~3-5% error. That's fine for object detection, but catastrophic for pixel-level editing where even small errors damage adjacent content.</p>
    </div>
    <div class="card insight-card">
      <h3>Each fix creates new edge cases</h3>
      <p>Tightening detection to prevent content damage means some watermarks survive. Loosening it catches more watermarks but risks content. Guard rails help, but the fundamental precision gap remains.</p>
    </div>
    <div class="card insight-card">
      <h3>Demo vs. production quality</h3>
      <p>AI watermark removal demos impressively on simple cases. Production-reliable results across varied real-world files require dedicated fine-tuned models and GPU infrastructure beyond what API wrappers can provide.</p>
    </div>
  </div>
</div>

<div class="journey-section">
  <h2>Built By</h2>
  <div class="cushlabs-card">
    <div class="cushlabs-logo-box">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
    </div>
    <div class="cushlabs-card-text">
      <h3>CushLabs AI Services</h3>
      <p>Unwatermark is a portfolio project by <a href="https://cushlabs.ai" target="_blank" rel="noopener">CushLabs AI Services</a>, exploring the real capabilities and limitations of AI-powered image processing. Built with Claude Code as a pair-programming partner.</p>
    </div>
  </div>
</div>
""", active_nav="about", description="The story behind Unwatermark -- how we built an AI watermark removal tool, the technology inside, and honest lessons about the limits of AI precision.", canonical_path="/about")
