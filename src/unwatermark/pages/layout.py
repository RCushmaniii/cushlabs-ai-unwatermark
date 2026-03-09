"""Shared page layout — nav, footer, base styles."""


def page(title: str, body: str, active_nav: str = "") -> str:
    """Wrap page content in the shared layout shell."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Unwatermark</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
{BASE_CSS}
</style>
</head>
<body>
<nav class="nav">
  <div class="nav-inner">
    <a href="/" class="nav-brand">Unwatermark</a>
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
      <span class="footer-logo">Unwatermark</span>
      <span class="footer-sep">by</span>
      <a href="https://cushlabs.ai" class="footer-cushlabs" target="_blank" rel="noopener">CushLabs AI</a>
    </div>
    <div class="footer-links">
      <a href="/help">Help</a>
      <a href="/terms">Terms</a>
      <a href="/privacy">Privacy</a>
    </div>
    <div class="footer-copy">&copy; 2026 Robert Cushman. All rights reserved.</div>
  </div>
</footer>
</body>
</html>"""


BASE_CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #08080a; color: #d4d4d8;
  min-height: 100vh; display: flex; flex-direction: column;
  -webkit-font-smoothing: antialiased;
}
a { color: #60a5fa; text-decoration: none; transition: color 0.15s; }
a:hover { color: #93c5fd; }

/* Nav */
.nav {
  border-bottom: 1px solid #18181b; padding: 0 2rem;
  position: sticky; top: 0; z-index: 50;
  background: rgba(8, 8, 10, 0.85); backdrop-filter: blur(12px);
}
.nav-inner {
  max-width: 960px; margin: 0 auto;
  display: flex; align-items: center; justify-content: space-between;
  height: 56px;
}
.nav-brand {
  font-size: 1.1rem; font-weight: 700; color: #fafafa;
  letter-spacing: -0.02em;
}
.nav-brand:hover { color: #fafafa; }
.nav-links { display: flex; gap: 1.5rem; }
.nav-link {
  font-size: 0.85rem; font-weight: 500; color: #71717a;
  padding: 0.25rem 0; border-bottom: 2px solid transparent;
  transition: all 0.15s;
}
.nav-link:hover { color: #d4d4d8; }
.nav-link.active { color: #fafafa; border-bottom-color: #3b82f6; }

/* Main */
.main {
  flex: 1; max-width: 960px; width: 100%;
  margin: 0 auto; padding: 2.5rem 2rem;
}

/* Footer */
.footer {
  border-top: 1px solid #18181b; padding: 2rem;
  margin-top: auto;
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
.footer-logo { font-weight: 600; color: #a1a1aa; }
.footer-sep { color: #3f3f46; }
.footer-cushlabs { color: #60a5fa; font-weight: 600; }
.footer-cushlabs:hover { color: #93c5fd; }
.footer-links {
  display: flex; gap: 1.25rem; font-size: 0.8rem;
}
.footer-links a { color: #52525b; }
.footer-links a:hover { color: #a1a1aa; }
.footer-copy { font-size: 0.75rem; color: #3f3f46; width: 100%; text-align: center; margin-top: 0.5rem; }

/* Shared utilities */
.page-title { font-size: 1.6rem; font-weight: 700; color: #fafafa; margin-bottom: 0.4rem; }
.page-subtitle { color: #71717a; font-size: 0.95rem; margin-bottom: 2rem; }
.section { margin-bottom: 2.5rem; }
.section-title { font-size: 1.1rem; font-weight: 600; color: #e4e4e7; margin-bottom: 0.75rem; }
.prose { line-height: 1.7; color: #a1a1aa; }
.prose p { margin-bottom: 1rem; }
.prose ul, .prose ol { margin-bottom: 1rem; padding-left: 1.5rem; }
.prose li { margin-bottom: 0.4rem; }
.prose strong { color: #d4d4d8; font-weight: 600; }
.prose code {
  background: #18181b; padding: 0.15rem 0.4rem; border-radius: 4px;
  font-size: 0.85em; color: #a5b4fc;
}
.card {
  background: #111113; border: 1px solid #1e1e22; border-radius: 12px;
  padding: 1.5rem; margin-bottom: 1rem;
}

/* Buttons */
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem;
  padding: 0.6rem 1.25rem; border: none; border-radius: 8px;
  font-family: inherit; font-size: 0.9rem; font-weight: 600;
  cursor: pointer; transition: all 0.15s; white-space: nowrap;
}
.btn-primary { background: #3b82f6; color: #fff; }
.btn-primary:hover { background: #2563eb; }
.btn-secondary { background: #1e1e22; color: #a1a1aa; border: 1px solid #27272a; }
.btn-secondary:hover { background: #27272a; color: #d4d4d8; }
.btn:disabled { opacity: 0.35; cursor: not-allowed; }
.btn-row { display: flex; gap: 0.75rem; margin-top: 1.25rem; flex-wrap: wrap; }

/* Loading spinner */
@keyframes spin { to { transform: rotate(360deg); } }
.spinner {
  width: 18px; height: 18px; border: 2px solid rgba(255,255,255,0.2);
  border-top-color: #fff; border-radius: 50%;
  animation: spin 0.6s linear infinite; display: inline-block;
}

/* Step progress */
.steps-bar { display: flex; gap: 0; margin-bottom: 2rem; }
.step-indicator {
  flex: 1; text-align: center; padding: 0.6rem 0.5rem;
  font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.06em; color: #3f3f46;
  border-bottom: 2px solid #1e1e22; transition: all 0.2s;
}
.step-indicator.active { color: #fafafa; border-bottom-color: #3b82f6; }
.step-indicator.done { color: #4ade80; border-bottom-color: #4ade80; }
.step-num {
  display: inline-flex; align-items: center; justify-content: center;
  width: 20px; height: 20px; border-radius: 50%;
  background: #1e1e22; color: #52525b; font-size: 0.7rem;
  margin-right: 0.4rem; font-weight: 700;
}
.step-indicator.active .step-num { background: #3b82f6; color: #fff; }
.step-indicator.done .step-num { background: #4ade80; color: #000; }

/* Status */
.status { margin-top: 1rem; font-size: 0.85rem; color: #71717a; text-align: center; min-height: 1.5rem; }
.status.error { color: #f87171; }
.status.success { color: #4ade80; }

/* Responsive */
@media (max-width: 640px) {
  .nav-inner, .footer-inner { padding: 0 0.5rem; }
  .main { padding: 1.5rem 1rem; }
  .page-title { font-size: 1.3rem; }
  .footer-inner { flex-direction: column; text-align: center; }
}
"""
