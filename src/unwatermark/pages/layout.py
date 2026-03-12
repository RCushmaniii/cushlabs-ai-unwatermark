"""Shared page layout — nav, footer, base styles."""


def page(title: str, body: str, active_nav: str = "", full_width: bool = False) -> str:
    """Wrap page content in the shared layout shell."""
    main_class = "main main--full" if full_width else "main"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Unwatermark</title>
<meta name="description" content="AI-powered watermark removal for images, PDFs, and presentations. Fast, private, and free.">
<link rel="icon" href="/favicon.ico" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300..700&family=Inter:wght@300..700&display=swap" rel="stylesheet">
<style>
{BASE_CSS}
</style>
</head>
<body>

<nav class="nav" id="mainNav">
  <div class="nav-inner">
    <a href="/" class="nav-brand">
      <span class="nav-logo">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/><line x1="2" y1="2" x2="22" y2="22"/></svg>
      </span>
      Unwatermark
    </a>
    <div class="nav-links" id="navLinks">
      <a href="/" class="nav-link{' active' if active_nav == 'home' else ''}">Home</a>
      <a href="/app" class="nav-link{' active' if active_nav == 'app' else ''}">App</a>
      <a href="/help" class="nav-link{' active' if active_nav == 'help' else ''}">Help</a>
      <a href="/contact" class="nav-link{' active' if active_nav == 'contact' else ''}">Contact</a>
    </div>
    <div class="nav-actions">
      <a href="/app" class="nav-cta">Launch App</a>
      <button class="nav-toggle" id="navToggle" aria-label="Toggle navigation menu">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="4" y1="6" x2="20" y2="6"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="18" x2="20" y2="18"/></svg>
      </button>
    </div>
  </div>
  <div class="nav-mobile" id="navMobile">
    <a href="/" class="nav-mobile-link{' active' if active_nav == 'home' else ''}">Home</a>
    <a href="/app" class="nav-mobile-link{' active' if active_nav == 'app' else ''}">App</a>
    <a href="/help" class="nav-mobile-link{' active' if active_nav == 'help' else ''}">Help</a>
    <a href="/contact" class="nav-mobile-link{' active' if active_nav == 'contact' else ''}">Contact</a>
  </div>
</nav>

<main class="{main_class}">
{body}
</main>

<footer class="footer">
  <div class="footer-inner">
    <div class="footer-top">
      <div class="footer-brand-col">
        <div class="footer-brand">
          <span class="footer-logo">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/><line x1="2" y1="2" x2="22" y2="22"/></svg>
          </span>
          Unwatermark
        </div>
        <p class="footer-tagline">AI-powered watermark removal for images, PDFs, and presentations.</p>
        <a href="https://cushlabs.ai" class="footer-cushlabs" target="_blank" rel="noopener">
          A CushLabs AI product
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
        </a>
      </div>
      <div class="footer-links-grid">
        <div class="footer-col">
          <h4 class="footer-col-title">Product</h4>
          <a href="/app">Launch App</a>
          <a href="/help">Help Center</a>
        </div>
        <div class="footer-col">
          <h4 class="footer-col-title">Company</h4>
          <a href="/contact">Contact</a>
          <a href="https://cushlabs.ai" target="_blank" rel="noopener">CushLabs AI</a>
        </div>
        <div class="footer-col">
          <h4 class="footer-col-title">Legal</h4>
          <a href="/terms">Terms of Service</a>
          <a href="/privacy">Privacy Policy</a>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; 2026 CushLabs AI Services. All rights reserved.</span>
    </div>
  </div>
</footer>

<script>
(function() {{
  var toggle = document.getElementById('navToggle');
  var mobile = document.getElementById('navMobile');
  if (toggle && mobile) {{
    toggle.addEventListener('click', function() {{
      var open = mobile.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open);
    }});
  }}
}})();
</script>

</body>
</html>"""


BASE_CSS = """
/* ================================================================
   Design System — Unwatermark
   Inspired by Google Vids: clean, generous spacing, modern type
   ================================================================ */

:root {
  /* Primary */
  --color-primary: #2563eb;
  --color-primary-hover: #1d4ed8;
  --color-primary-light: #eff6ff;
  --color-primary-lighter: #dbeafe;

  /* Neutrals */
  --color-bg: #ffffff;
  --color-bg-alt: #f8fafc;
  --color-bg-subtle: #f1f5f9;
  --color-bg-dark: #0f172a;
  --color-text: #1e293b;
  --color-text-secondary: #475569;
  --color-text-muted: #64748b;
  --color-text-faint: #94a3b8;
  --color-border: #e2e8f0;
  --color-border-light: #f1f5f9;

  /* Semantic */
  --color-success: #22c55e;
  --color-success-light: #f0fdf4;
  --color-error: #ef4444;
  --color-error-light: #fef2f2;
  --color-error-border: #fecaca;
  --color-warning: #f59e0b;

  /* Radii */
  --radius-sm: 8px;
  --radius: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-xs: 0 1px 2px rgba(0,0,0,0.04);
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --shadow: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
  --shadow-md: 0 8px 16px -4px rgba(0,0,0,0.08), 0 4px 6px -2px rgba(0,0,0,0.04);
  --shadow-lg: 0 20px 40px -8px rgba(0,0,0,0.1), 0 8px 16px -4px rgba(0,0,0,0.06);

  /* Layout */
  --max-width: 1200px;
  --nav-height: 64px;

  /* Transitions */
  --ease: cubic-bezier(0.4, 0, 0.2, 1);
}

/* ---- Reset ---- */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; -webkit-text-size-adjust: 100%; }
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--color-bg);
  color: var(--color-text-secondary);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-size: 16px;
  line-height: 1.6;
}
h1, h2, h3, h4, h5, h6 {
  font-family: 'DM Sans', 'Inter', sans-serif;
  color: var(--color-text);
  font-weight: 600;
  line-height: 1.3;
  letter-spacing: -0.01em;
}
a { color: var(--color-primary); text-decoration: none; transition: color 0.15s var(--ease); }
a:hover { color: var(--color-primary-hover); }
img { max-width: 100%; display: block; }
button { font-family: inherit; cursor: pointer; }

/* ---- Navigation ---- */
.nav {
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-border-light);
  position: sticky;
  top: 0;
  z-index: 100;
}
.nav-inner {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--nav-height);
}
.nav-brand {
  font-family: 'DM Sans', sans-serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-text);
  display: flex;
  align-items: center;
  gap: 0.6rem;
  letter-spacing: -0.02em;
  flex-shrink: 0;
}
.nav-brand:hover { color: var(--color-text); }
.nav-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: var(--radius-sm);
  background: var(--color-primary);
  color: #ffffff;
}
.nav-links {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
.nav-link {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--color-text-muted);
  padding: 0.45rem 1rem;
  border-radius: var(--radius-full);
  transition: all 0.15s var(--ease);
}
.nav-link:hover {
  color: var(--color-text);
  background: var(--color-bg-alt);
}
.nav-link.active {
  color: var(--color-primary);
  background: var(--color-primary-light);
}
.nav-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.nav-cta {
  font-size: 0.875rem;
  font-weight: 600;
  color: #ffffff;
  background: var(--color-primary);
  padding: 0.5rem 1.25rem;
  border-radius: var(--radius-full);
  transition: all 0.15s var(--ease);
  white-space: nowrap;
}
.nav-cta:hover {
  background: var(--color-primary-hover);
  color: #ffffff;
  box-shadow: var(--shadow-sm);
}
.nav-toggle {
  display: none;
  background: none;
  border: none;
  color: var(--color-text);
  padding: 0.35rem;
  border-radius: var(--radius-sm);
}
.nav-toggle:hover { background: var(--color-bg-alt); }
.nav-mobile {
  display: none;
  flex-direction: column;
  padding: 0.5rem 2rem 1rem;
  border-top: 1px solid var(--color-border-light);
}
.nav-mobile.open { display: flex; }
.nav-mobile-link {
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  padding: 0.65rem 0;
  border-bottom: 1px solid var(--color-border-light);
}
.nav-mobile-link:last-child { border-bottom: none; }
.nav-mobile-link.active { color: var(--color-primary); }

@media (max-width: 768px) {
  .nav-inner { padding: 0 1.25rem; }
  .nav-links { display: none; }
  .nav-cta { display: none; }
  .nav-toggle { display: flex; }
}

/* ---- Main ---- */
.main {
  flex: 1;
  max-width: var(--max-width);
  width: 100%;
  margin: 0 auto;
  padding: 3rem 2rem;
}
.main--full {
  max-width: 100%;
  padding: 0;
}
@media (max-width: 768px) {
  .main { padding: 2rem 1.25rem; }
}

/* ---- Footer ---- */
.footer {
  background: var(--color-bg-dark);
  margin-top: auto;
  padding: 3.5rem 2rem 2rem;
}
.footer-inner {
  max-width: var(--max-width);
  margin: 0 auto;
}
.footer-top {
  display: flex;
  justify-content: space-between;
  gap: 3rem;
  padding-bottom: 2.5rem;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.footer-brand-col { max-width: 320px; }
.footer-brand {
  font-family: 'DM Sans', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}
.footer-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: var(--radius-sm);
  background: rgba(255,255,255,0.1);
  color: var(--color-primary-lighter);
}
.footer-tagline {
  font-size: 0.875rem;
  color: #94a3b8;
  line-height: 1.6;
  margin-bottom: 1rem;
}
.footer-cushlabs {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.82rem;
  font-weight: 600;
  color: #60a5fa;
  transition: color 0.15s var(--ease);
}
.footer-cushlabs:hover { color: #93bbfc; }
.footer-links-grid {
  display: flex;
  gap: 4rem;
}
.footer-col {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.footer-col-title {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.78rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 0.25rem;
}
.footer-col a {
  font-size: 0.875rem;
  color: #cbd5e1;
  transition: color 0.15s var(--ease);
}
.footer-col a:hover { color: #ffffff; }
.footer-bottom {
  padding-top: 1.75rem;
  text-align: center;
}
.footer-bottom span {
  font-size: 0.78rem;
  color: #475569;
}

@media (max-width: 768px) {
  .footer { padding: 2.5rem 1.25rem 1.5rem; }
  .footer-top { flex-direction: column; gap: 2rem; }
  .footer-brand-col { max-width: 100%; }
  .footer-links-grid { gap: 2rem; flex-wrap: wrap; }
}

/* ================================================================
   Shared Component Classes
   ================================================================ */

/* ---- Page Header ---- */
.page-header {
  margin-bottom: 2.5rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid var(--color-border-light);
}
.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 0.5rem;
  letter-spacing: -0.02em;
}
.page-subtitle {
  font-size: 1.05rem;
  color: var(--color-text-muted);
  max-width: 600px;
}
@media (max-width: 768px) {
  .page-title { font-size: 1.6rem; }
  .page-subtitle { font-size: 0.95rem; }
}

/* ---- Sections ---- */
.section { margin-bottom: 3rem; }
.section-title {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 1rem;
}
.section-subtitle {
  font-size: 0.95rem;
  color: var(--color-text-muted);
  margin-bottom: 1.5rem;
}

/* ---- Cards ---- */
.card {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 1.75rem;
  transition: box-shadow 0.2s var(--ease);
}
.card:hover { box-shadow: var(--shadow-sm); }
.card--flat { border: none; background: var(--color-bg-alt); }
.card--elevated {
  border: none;
  box-shadow: var(--shadow);
}
.card--elevated:hover { box-shadow: var(--shadow-md); }

/* ---- Buttons ---- */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.65rem 1.5rem;
  border: none;
  border-radius: var(--radius-full);
  font-family: inherit;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s var(--ease);
  white-space: nowrap;
  line-height: 1.4;
}
.btn-primary {
  background: var(--color-primary);
  color: #ffffff;
}
.btn-primary:hover {
  background: var(--color-primary-hover);
  color: #ffffff;
  box-shadow: var(--shadow-sm);
}
.btn-secondary {
  background: var(--color-bg);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}
.btn-secondary:hover {
  background: var(--color-bg-alt);
  color: var(--color-text);
  border-color: var(--color-text-faint);
}
.btn-ghost {
  background: transparent;
  color: var(--color-text-secondary);
}
.btn-ghost:hover {
  background: var(--color-bg-alt);
  color: var(--color-text);
}
.btn-lg {
  padding: 0.8rem 2rem;
  font-size: 1rem;
}
.btn-sm {
  padding: 0.4rem 1rem;
  font-size: 0.82rem;
}
.btn-full { width: 100%; }
.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  pointer-events: none;
}
.btn-row {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

/* ---- Form Controls ---- */
.control-group { margin-bottom: 1.25rem; }
.control-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
  display: block;
  margin-bottom: 0.4rem;
}
.control-input {
  width: 100%;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  padding: 0.65rem 1rem;
  border-radius: var(--radius-sm);
  font-size: 0.925rem;
  font-family: inherit;
  transition: all 0.15s var(--ease);
  line-height: 1.5;
}
.control-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(37,99,235,0.1);
}
.control-input::placeholder { color: var(--color-text-faint); }
textarea.control-input { resize: vertical; min-height: 120px; }
.input-help {
  font-size: 0.82rem;
  color: var(--color-text-faint);
  margin-top: 0.35rem;
}

/* ---- Prose (long-form text) ---- */
.prose { line-height: 1.75; color: var(--color-text-secondary); }
.prose p { margin-bottom: 1rem; }
.prose ul, .prose ol { margin-bottom: 1rem; padding-left: 1.5rem; }
.prose li { margin-bottom: 0.5rem; }
.prose strong { color: var(--color-text); font-weight: 600; }
.prose code {
  background: var(--color-primary-light);
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-size: 0.85em;
  color: var(--color-primary-hover);
}
.prose a { text-decoration: underline; text-underline-offset: 2px; }

/* ---- Status ---- */
.status {
  margin-top: 0.75rem;
  font-size: 0.875rem;
  color: var(--color-text-muted);
  min-height: 1.2rem;
}
.status.error { color: var(--color-error); }
.status.success { color: var(--color-success); }

/* ---- Error Alert ---- */
.error-alert {
  background: var(--color-error-light);
  border: 1px solid var(--color-error-border);
  border-radius: var(--radius-sm);
  padding: 0.85rem 1rem;
  display: flex;
  gap: 0.6rem;
  align-items: flex-start;
}
.error-alert svg { flex-shrink: 0; margin-top: 2px; }
.error-alert p { font-size: 0.9rem; color: #991b1b; line-height: 1.5; }

/* ---- Loading Spinner ---- */
@keyframes spin { to { transform: rotate(360deg); } }
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  display: inline-block;
}

/* ---- Step Progress Bar ---- */
.steps-bar {
  display: flex;
  gap: 0;
  margin-bottom: 2rem;
  border-bottom: 1px solid var(--color-border-light);
}
.step-indicator {
  font-family: 'DM Sans', sans-serif;
  text-align: center;
  padding: 0.6rem 1.5rem;
  font-size: 0.78rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-text-faint);
  border-bottom: 2px solid transparent;
  transition: all 0.2s var(--ease);
}
.step-indicator.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}
.step-indicator.done {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}
.step-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--color-border);
  color: var(--color-text-faint);
  font-size: 0.68rem;
  margin-right: 0.4rem;
  font-weight: 700;
}
.step-indicator.active .step-num {
  background: var(--color-primary);
  color: #fff;
}
.step-indicator.done .step-num {
  background: var(--color-primary);
  color: #fff;
}

/* ---- Utility ---- */
.text-center { text-align: center; }
.mt-1 { margin-top: 0.5rem; }
.mt-2 { margin-top: 1rem; }
.mt-3 { margin-top: 1.5rem; }
.mt-4 { margin-top: 2rem; }
.mb-1 { margin-bottom: 0.5rem; }
.mb-2 { margin-bottom: 1rem; }
.mb-3 { margin-bottom: 1.5rem; }
.container {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 0 2rem;
}
@media (max-width: 768px) {
  .container { padding: 0 1.25rem; }
}

/* ---- Reduced Motion ---- */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}

/* ---- Responsive Text ---- */
@media (max-width: 640px) {
  .step-indicator { padding: 0.5rem 0.75rem; font-size: 0.7rem; }
}
"""
