"""Shared page layout — nav, footer, base styles. Light theme with indigo accent."""


def page(title: str, body: str, active_nav: str = "") -> str:
    """Wrap page content in the shared layout shell."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Unwatermark</title>
<link rel="icon" href="/favicon.ico" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
  rel="stylesheet">
<style>
{BASE_CSS}
</style>
</head>
<body>
<nav class="nav">
  <div class="nav-inner">
    <a href="/" class="nav-brand">
      <span class="nav-logo">U</span> Unwatermark
    </a>
    <div class="nav-links">
      <a href="/" class="nav-link{' active' if active_nav == 'app' else ''}">App</a>
      <a href="/help" class="nav-link{' active' if active_nav == 'help' else ''}">Help</a>
    </div>
  </div>
</nav>
<main class="main">
{body}
</main>
<footer class="footer">
  <div class="footer-inner">
    <div class="footer-brand">
      <span class="footer-name">Unwatermark</span>
      <span class="footer-sep">&middot;</span>
      <a href="https://cushlabs.ai" class="footer-cushlabs" target="_blank"
        rel="noopener">CushLabs AI</a>
    </div>
    <div class="footer-links">
      <a href="/help">Help</a>
      <a href="/terms">Terms</a>
      <a href="/privacy">Privacy</a>
    </div>
    <div class="footer-copy">
      &copy; 2026 Robert Cushman. All rights reserved.
    </div>
  </div>
</footer>
</body>
</html>"""


BASE_CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #f8fafc; color: #334155;
  min-height: 100vh; display: flex; flex-direction: column;
  -webkit-font-smoothing: antialiased;
  font-weight: 400;
}
h1, h2, h3, h4 { color: #0f172a; font-weight: 600; letter-spacing: -0.02em; }
a { color: #4f46e5; text-decoration: none; transition: color 0.15s; }
a:hover { color: #6366f1; }

/* Nav */
.nav {
  background: #ffffff; border-bottom: 1px solid #e2e8f0;
  padding: 0 2rem; position: sticky; top: 0; z-index: 50;
}
.nav-inner {
  max-width: 960px; margin: 0 auto;
  display: flex; align-items: center; justify-content: space-between;
  height: 56px;
}
.nav-brand {
  font-size: 1.05rem; font-weight: 700; color: #0f172a;
  display: flex; align-items: center; gap: 0.5rem;
  letter-spacing: -0.02em;
}
.nav-brand:hover { color: #0f172a; }
.nav-logo {
  display: inline-flex; align-items: center; justify-content: center;
  width: 28px; height: 28px; border-radius: 6px;
  background: #4f46e5; color: #fff; font-size: 0.85rem; font-weight: 700;
}
.nav-links { display: flex; gap: 1.5rem; }
.nav-link {
  font-size: 0.85rem; font-weight: 500; color: #64748b;
  padding: 0.25rem 0; border-bottom: 2px solid transparent;
  transition: all 0.15s;
}
.nav-link:hover { color: #0f172a; }
.nav-link.active { color: #4f46e5; border-bottom-color: #4f46e5; }

/* Main */
.main {
  flex: 1; max-width: 960px; width: 100%;
  margin: 0 auto; padding: 2.5rem 2rem;
}

/* Footer */
.footer {
  background: #ffffff; border-top: 1px solid #e2e8f0;
  padding: 1.75rem 2rem; margin-top: auto;
}
.footer-inner {
  max-width: 960px; margin: 0 auto;
  display: flex; flex-wrap: wrap; align-items: center;
  gap: 1.5rem; justify-content: space-between;
}
.footer-brand {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.85rem;
}
.footer-name { font-weight: 600; color: #334155; }
.footer-sep { color: #cbd5e1; }
.footer-cushlabs { color: #4f46e5; font-weight: 600; }
.footer-cushlabs:hover { color: #6366f1; }
.footer-links { display: flex; gap: 1.25rem; font-size: 0.8rem; }
.footer-links a { color: #94a3b8; }
.footer-links a:hover { color: #4f46e5; }
.footer-copy {
  font-size: 0.75rem; color: #94a3b8; width: 100%;
  text-align: center; margin-top: 0.25rem;
}

/* Shared utilities */
.page-title {
  font-size: 1.6rem; font-weight: 700; color: #0f172a;
  margin-bottom: 0.4rem;
}
.page-subtitle { color: #64748b; font-size: 0.95rem; margin-bottom: 2rem; }
.section { margin-bottom: 2.5rem; }
.section-title {
  font-size: 1.1rem; font-weight: 600; color: #0f172a;
  margin-bottom: 0.75rem;
}
.prose { line-height: 1.7; color: #475569; }
.prose p { margin-bottom: 1rem; }
.prose ul, .prose ol { margin-bottom: 1rem; padding-left: 1.5rem; }
.prose li { margin-bottom: 0.4rem; }
.prose strong { color: #0f172a; font-weight: 600; }
.prose code {
  background: #eef2ff; padding: 0.15rem 0.4rem; border-radius: 4px;
  font-size: 0.85em; color: #4338ca;
}
.card {
  background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px;
  padding: 1.5rem; margin-bottom: 1rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* Buttons */
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem;
  padding: 0.6rem 1.25rem; border: none; border-radius: 8px;
  font-family: inherit; font-size: 0.9rem; font-weight: 600;
  cursor: pointer; transition: all 0.15s; white-space: nowrap;
}
.btn-primary { background: #4f46e5; color: #fff; }
.btn-primary:hover { background: #4338ca; box-shadow: 0 4px 12px rgba(79,70,229,0.25); }
.btn-secondary {
  background: #ffffff; color: #475569;
  border: 1px solid #e2e8f0;
}
.btn-secondary:hover { background: #f1f5f9; color: #0f172a; }
.btn:disabled { opacity: 0.4; cursor: not-allowed; pointer-events: none; }
.btn-row { display: flex; gap: 0.75rem; margin-top: 1.25rem; flex-wrap: wrap; }

/* Loading spinner */
@keyframes spin { to { transform: rotate(360deg); } }
.spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff; border-radius: 50%;
  animation: spin 0.6s linear infinite; display: inline-block;
}

/* Step progress */
.steps-bar {
  display: flex; gap: 0; margin-bottom: 2rem;
  background: #ffffff; border: 1px solid #e2e8f0;
  border-radius: 10px; overflow: hidden;
}
.step-indicator {
  flex: 1; text-align: center; padding: 0.7rem 0.5rem;
  font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.05em; color: #94a3b8;
  border-bottom: 2px solid transparent; transition: all 0.2s;
}
.step-indicator.active { color: #4f46e5; border-bottom-color: #4f46e5; background: #f5f3ff; }
.step-indicator.done { color: #059669; border-bottom-color: #059669; background: #ecfdf5; }
.step-num {
  display: inline-flex; align-items: center; justify-content: center;
  width: 20px; height: 20px; border-radius: 50%;
  background: #e2e8f0; color: #94a3b8; font-size: 0.7rem;
  margin-right: 0.4rem; font-weight: 700;
}
.step-indicator.active .step-num { background: #4f46e5; color: #fff; }
.step-indicator.done .step-num { background: #059669; color: #fff; }

/* Status */
.status {
  margin-top: 1rem; font-size: 0.85rem; color: #64748b;
  text-align: center; min-height: 1.5rem;
}
.status.error { color: #dc2626; }
.status.success { color: #059669; }

/* Responsive */
@media (max-width: 640px) {
  .nav { padding: 0 1rem; }
  .main { padding: 1.5rem 1rem; }
  .page-title { font-size: 1.3rem; }
  .footer { padding: 1.5rem 1rem; }
  .footer-inner { flex-direction: column; text-align: center; }
}
"""
