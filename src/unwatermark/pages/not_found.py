"""404 Not Found page."""

from unwatermark.pages.layout import page

NOT_FOUND_PAGE = page("Page Not Found", """
<style>
  .nf-hero {
    text-align: center;
    padding: 5rem 1rem 4rem;
    max-width: 540px;
    margin: 0 auto;
  }
  .nf-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 80px;
    height: 80px;
    border-radius: var(--radius-lg);
    background: var(--color-primary-light);
    color: var(--color-primary);
    margin-bottom: 2rem;
  }
  .nf-number {
    font-family: 'DM Sans', sans-serif;
    font-size: 7rem;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.04em;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, var(--color-primary) 0%, #7c3aed 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .nf-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-text);
    margin-bottom: 0.75rem;
    letter-spacing: -0.01em;
  }
  .nf-desc {
    font-size: 1.05rem;
    color: var(--color-text-muted);
    line-height: 1.6;
    margin-bottom: 2.5rem;
  }
  .nf-actions {
    display: flex;
    gap: 0.75rem;
    justify-content: center;
    flex-wrap: wrap;
  }
</style>

<div class="nf-hero">
  <div class="nf-icon">
    <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="11" cy="11" r="8"/>
      <line x1="21" y1="21" x2="16.65" y2="16.65"/>
      <line x1="8" y1="11" x2="14" y2="11"/>
    </svg>
  </div>
  <div class="nf-number">404</div>
  <h1 class="nf-title">Page not found</h1>
  <p class="nf-desc">This page has been removed... like a watermark. Whatever you were looking for isn't here, but we can help you get back on track.</p>
  <div class="nf-actions">
    <a href="/" class="btn btn-primary btn-lg">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
      Back to Home
    </a>
    <a href="/app" class="btn btn-secondary btn-lg">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
      Launch App
    </a>
  </div>
</div>
""", active_nav="")
