"""Marketing landing page for Unwatermark."""

from unwatermark.pages.layout import page

LANDING_PAGE = page("AI-Powered Watermark Removal", """
<style>
/* ================================================================
   Landing Page Sections
   ================================================================ */

/* ---- Hero ---- */
.hero {
  position: relative;
  padding: 7rem 2rem 6rem;
  text-align: center;
  overflow: hidden;
  background: var(--color-bg);
}
.hero::before {
  content: '';
  position: absolute;
  top: -40%;
  right: -10%;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(37,99,235,0.06) 0%, transparent 70%);
  pointer-events: none;
}
.hero::after {
  content: '';
  position: absolute;
  bottom: -30%;
  left: -5%;
  width: 500px;
  height: 500px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(37,99,235,0.04) 0%, transparent 70%);
  pointer-events: none;
}
.hero-inner {
  position: relative;
  z-index: 1;
  max-width: 800px;
  margin: 0 auto;
}
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-size: 0.82rem;
  font-weight: 600;
  padding: 0.4rem 1rem;
  border-radius: var(--radius-full);
  margin-bottom: 2rem;
  letter-spacing: 0.01em;
}
.hero h1 {
  font-size: 3.5rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1.1;
  margin-bottom: 1.5rem;
  color: var(--color-text);
}
.hero h1 span {
  color: var(--color-primary);
}
.hero-subtitle {
  font-size: 1.2rem;
  color: var(--color-text-muted);
  max-width: 560px;
  margin: 0 auto 2.5rem;
  line-height: 1.7;
}
.hero-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}
.hero-actions .btn-lg {
  padding: 0.9rem 2.25rem;
  font-size: 1.05rem;
}
.hero-actions .btn-secondary {
  background: transparent;
}

@media (max-width: 768px) {
  .hero { padding: 4rem 1.25rem 3.5rem; }
  .hero h1 { font-size: 2.25rem; }
  .hero-subtitle { font-size: 1.05rem; }
}
@media (max-width: 480px) {
  .hero h1 { font-size: 1.85rem; }
  .hero-actions { flex-direction: column; align-items: center; }
  .hero-actions .btn-lg { width: 100%; max-width: 300px; }
}

/* ---- Formats Section ---- */
.section-formats {
  background: var(--color-bg-alt);
  padding: 5rem 2rem;
}
.section-heading {
  text-align: center;
  margin-bottom: 3rem;
}
.section-heading h2 {
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin-bottom: 0.75rem;
}
.section-heading p {
  font-size: 1.05rem;
  color: var(--color-text-muted);
  max-width: 540px;
  margin: 0 auto;
}
.formats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  max-width: 960px;
  margin: 0 auto;
}
.format-card {
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  padding: 2.25rem 1.75rem;
  text-align: center;
  box-shadow: var(--shadow-sm);
  transition: all 0.25s var(--ease);
}
.format-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
.format-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: var(--radius);
  background: var(--color-primary-light);
  color: var(--color-primary);
  margin-bottom: 1.25rem;
}
.format-card h3 {
  font-size: 1.15rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}
.format-card p {
  font-size: 0.92rem;
  color: var(--color-text-muted);
  line-height: 1.6;
}
.format-types {
  display: flex;
  justify-content: center;
  gap: 0.4rem;
  flex-wrap: wrap;
  margin-top: 1rem;
}
.format-tag {
  background: var(--color-bg-subtle);
  color: var(--color-text-muted);
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.25rem 0.6rem;
  border-radius: var(--radius-full);
}

@media (max-width: 768px) {
  .section-formats { padding: 3.5rem 1.25rem; }
  .formats-grid { grid-template-columns: 1fr; max-width: 400px; }
  .section-heading h2 { font-size: 1.6rem; }
}

/* ---- How It Works ---- */
.section-how {
  background: var(--color-bg);
  padding: 5rem 2rem;
}
.steps-flow {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
  max-width: 960px;
  margin: 0 auto;
  position: relative;
}
.steps-flow::before {
  content: '';
  position: absolute;
  top: 32px;
  left: calc(16.67% + 28px);
  right: calc(16.67% + 28px);
  height: 2px;
  background: var(--color-border);
}
.step-item {
  text-align: center;
  position: relative;
  z-index: 1;
}
.step-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--color-primary);
  color: #ffffff;
  font-family: 'DM Sans', sans-serif;
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 1.25rem;
  box-shadow: 0 4px 12px rgba(37,99,235,0.25);
}
.step-item h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}
.step-item p {
  font-size: 0.92rem;
  color: var(--color-text-muted);
  line-height: 1.6;
  max-width: 260px;
  margin: 0 auto;
}

@media (max-width: 768px) {
  .section-how { padding: 3.5rem 1.25rem; }
  .steps-flow { grid-template-columns: 1fr; max-width: 360px; gap: 2.5rem; }
  .steps-flow::before { display: none; }
}

/* ---- Technology ---- */
.section-tech {
  background: var(--color-bg-alt);
  padding: 5rem 2rem;
}
.tech-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  max-width: 960px;
  margin: 0 auto;
}
.tech-card {
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  padding: 2rem 1.75rem;
  box-shadow: var(--shadow-xs);
  transition: all 0.25s var(--ease);
}
.tech-card:hover {
  box-shadow: var(--shadow);
  transform: translateY(-2px);
}
.tech-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: var(--radius);
  margin-bottom: 1.25rem;
}
.tech-icon--blue {
  background: var(--color-primary-light);
  color: var(--color-primary);
}
.tech-icon--green {
  background: var(--color-success-light);
  color: #16a34a;
}
.tech-icon--amber {
  background: #fffbeb;
  color: #d97706;
}
.tech-card h3 {
  font-size: 1.05rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}
.tech-card p {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  line-height: 1.65;
}

@media (max-width: 768px) {
  .section-tech { padding: 3.5rem 1.25rem; }
  .tech-grid { grid-template-columns: 1fr; max-width: 400px; }
}

/* ---- Privacy ---- */
.section-privacy {
  background: var(--color-bg);
  padding: 5rem 2rem;
}
.privacy-inner {
  max-width: 720px;
  margin: 0 auto;
  text-align: center;
}
.privacy-items {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
  margin-top: 2.5rem;
  text-align: left;
}
.privacy-item {
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
  padding: 1.25rem;
  background: var(--color-bg-alt);
  border-radius: var(--radius);
  transition: background 0.15s var(--ease);
}
.privacy-item:hover {
  background: var(--color-bg-subtle);
}
.privacy-check {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  min-width: 28px;
  border-radius: 50%;
  background: var(--color-success-light);
  color: #16a34a;
  margin-top: 1px;
}
.privacy-item-text h4 {
  font-size: 0.95rem;
  font-weight: 600;
  margin-bottom: 0.2rem;
}
.privacy-item-text p {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  line-height: 1.55;
}

@media (max-width: 640px) {
  .section-privacy { padding: 3.5rem 1.25rem; }
  .privacy-items { grid-template-columns: 1fr; }
}

/* ---- CTA ---- */
.section-cta {
  background: var(--color-primary);
  padding: 5rem 2rem;
  text-align: center;
}
.cta-inner {
  max-width: 600px;
  margin: 0 auto;
}
.section-cta h2 {
  font-size: 2rem;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 0.75rem;
  letter-spacing: -0.02em;
}
.section-cta p {
  font-size: 1.1rem;
  color: rgba(255,255,255,0.8);
  margin-bottom: 2.25rem;
}
.btn-cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: #ffffff;
  color: var(--color-primary);
  font-family: inherit;
  font-size: 1.05rem;
  font-weight: 700;
  padding: 0.9rem 2.5rem;
  border: none;
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all 0.2s var(--ease);
  text-decoration: none;
}
.btn-cta:hover {
  background: var(--color-primary-lighter);
  color: var(--color-primary-hover);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .section-cta { padding: 3.5rem 1.25rem; }
  .section-cta h2 { font-size: 1.6rem; }
  .section-cta p { font-size: 1rem; }
}
</style>

<!-- ============================================================
     Hero
     ============================================================ -->
<section class="hero">
  <div class="hero-inner">
    <div class="hero-badge">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
      Powered by AI
    </div>
    <h1>Remove watermarks <span>with AI</span></h1>
    <p class="hero-subtitle">
      Clean up images, PDFs, and presentations in seconds.
      State-of-the-art neural inpainting removes watermarks
      while preserving the content underneath.
    </p>
    <div class="hero-actions">
      <a href="/app" class="btn btn-primary btn-lg">Launch App</a>
      <a href="#how-it-works" class="btn btn-secondary btn-lg">Learn More</a>
    </div>
  </div>
</section>

<!-- ============================================================
     Supported Formats
     ============================================================ -->
<section class="section-formats">
  <div class="container">
    <div class="section-heading">
      <h2>Works with your files</h2>
      <p>Upload an image, PDF, or presentation and get a clean version back. No format conversion needed.</p>
    </div>
    <div class="formats-grid">

      <div class="format-card">
        <div class="format-icon">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
        </div>
        <h3>Images</h3>
        <p>Single image files with stock photo watermarks, draft stamps, or logo overlays.</p>
        <div class="format-types">
          <span class="format-tag">PNG</span>
          <span class="format-tag">JPG</span>
          <span class="format-tag">BMP</span>
          <span class="format-tag">TIFF</span>
          <span class="format-tag">WebP</span>
        </div>
      </div>

      <div class="format-card">
        <div class="format-icon">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
        </div>
        <h3>PDFs</h3>
        <p>Multi-page documents with repeating watermarks. Each page is processed independently.</p>
        <div class="format-types">
          <span class="format-tag">PDF</span>
        </div>
      </div>

      <div class="format-card">
        <div class="format-icon">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
        </div>
        <h3>Presentations</h3>
        <p>PowerPoint slides with watermarks on every page. Baseline detection cleans the entire deck.</p>
        <div class="format-types">
          <span class="format-tag">PPTX</span>
        </div>
      </div>

    </div>
  </div>
</section>

<!-- ============================================================
     How It Works
     ============================================================ -->
<section class="section-how" id="how-it-works">
  <div class="container">
    <div class="section-heading">
      <h2>How it works</h2>
      <p>Three simple steps from watermarked file to clean result.</p>
    </div>
    <div class="steps-flow">

      <div class="step-item">
        <div class="step-badge">1</div>
        <h3>Upload your file</h3>
        <p>Drag and drop or browse for your image, PDF, or PowerPoint file. Up to 50 MB supported.</p>
      </div>

      <div class="step-item">
        <div class="step-badge">2</div>
        <h3>AI analyzes it</h3>
        <p>Our detection pipeline locates watermarks using OCR and AI vision, then maps the regions to clean.</p>
      </div>

      <div class="step-item">
        <div class="step-badge">3</div>
        <h3>Download clean file</h3>
        <p>Neural inpainting removes watermarks while reconstructing the background. Download your clean file instantly.</p>
      </div>

    </div>
  </div>
</section>

<!-- ============================================================
     Technology
     ============================================================ -->
<section class="section-tech">
  <div class="container">
    <div class="section-heading">
      <h2>Built with serious AI</h2>
      <p>Not a blur filter. Real neural network inpainting that reconstructs what was behind the watermark.</p>
    </div>
    <div class="tech-grid">

      <div class="tech-card">
        <div class="tech-icon tech-icon--blue">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
        </div>
        <h3>LaMa Neural Inpainting</h3>
        <p>State-of-the-art large mask inpainting model from Samsung Research. Fills removed regions with plausible content that matches surrounding textures and patterns.</p>
      </div>

      <div class="tech-card">
        <div class="tech-icon tech-icon--green">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/></svg>
        </div>
        <h3>Smart Detection</h3>
        <p>Layered detection pipeline combines local OCR for text watermarks with AI vision analysis for logos and non-text marks. Fast and accurate with pattern matching.</p>
      </div>

      <div class="tech-card">
        <div class="tech-icon tech-icon--amber">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>
        </div>
        <h3>Multi-Pass Processing</h3>
        <p>Up to three detect-and-remove cycles per image. If residual watermark traces remain after the first pass, subsequent passes clean them automatically.</p>
      </div>

    </div>
  </div>
</section>

<!-- ============================================================
     Privacy & Trust
     ============================================================ -->
<section class="section-privacy">
  <div class="container">
    <div class="privacy-inner">
      <div class="section-heading">
        <h2>Your files stay private</h2>
        <p>We built this tool with privacy as a core principle, not an afterthought.</p>
      </div>
      <div class="privacy-items">

        <div class="privacy-item">
          <div class="privacy-check">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
          </div>
          <div class="privacy-item-text">
            <h4>Files never stored</h4>
            <p>Your uploads are processed in memory and discarded immediately after download. Nothing is saved to disk.</p>
          </div>
        </div>

        <div class="privacy-item">
          <div class="privacy-check">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
          </div>
          <div class="privacy-item-text">
            <h4>No tracking or cookies</h4>
            <p>No analytics scripts, no cookie banners, no user tracking. We do not collect any personal data.</p>
          </div>
        </div>

        <div class="privacy-item">
          <div class="privacy-check">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
          </div>
          <div class="privacy-item-text">
            <h4>No signup required</h4>
            <p>Start using the tool immediately. No account creation, no email verification, no friction.</p>
          </div>
        </div>

        <div class="privacy-item">
          <div class="privacy-check">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
          </div>
          <div class="privacy-item-text">
            <h4>Open detection pipeline</h4>
            <p>Primary detection uses open-source EasyOCR running locally. Your data does not leave the server unless AI fallback is needed.</p>
          </div>
        </div>

      </div>
    </div>
  </div>
</section>

<!-- ============================================================
     CTA
     ============================================================ -->
<section class="section-cta">
  <div class="cta-inner">
    <h2>Ready to remove watermarks?</h2>
    <p>Try it free -- no signup required.</p>
    <a href="/app" class="btn-cta">
      Launch App
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
    </a>
  </div>
</section>
""", active_nav="home", full_width=True, description="Remove watermarks from images, PDFs, and presentations with AI. Free, fast, and private — no signup required. Powered by LaMa neural inpainting.", canonical_path="/")
