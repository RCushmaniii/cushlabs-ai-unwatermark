"""Shared page layout — nav, footer, base styles. Clean architectural theme."""


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
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f8f8fa;
  --bg-dark: #2d2d31;
  --text-heading: #222222;
  --text-body: #555555;
  --text-muted: #888888;
  --text-faint: #aaaaaa;
  --border: #e0e0e0;
  --border-light: #eeeeee;
  --accent: #d4a017;
  --accent-hover: #b8860b;
  --accent-light: #fdf8e8;
  --accent-text: #8b6914;
  --success: #5a9a4e;
  --success-light: #eef6ec;
  --error: #d05050;
  --error-light: #fdf0f0;
  --radius: 4px;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg-secondary); color: var(--text-body);
  min-height: 100vh; display: flex; flex-direction: column;
  -webkit-font-smoothing: antialiased;
  font-weight: 400;
}
h1, h2, h3, h4 { color: var(--text-heading); font-weight: 600; letter-spacing: -0.02em; }
a { color: var(--accent-text); text-decoration: none; transition: color 0.15s; }
a:hover { color: var(--accent-hover); }

/* Nav */
.nav {
  background: var(--bg-primary); border-bottom: 1px solid var(--border);
  padding: 0 2rem; position: sticky; top: 0; z-index: 50;
}
.nav-inner {
  max-width: 960px; margin: 0 auto;
  display: flex; align-items: center; justify-content: space-between;
  height: 52px;
}
.nav-brand {
  font-size: 1rem; font-weight: 700; color: var(--text-heading);
  display: flex; align-items: center; gap: 0.5rem;
  letter-spacing: -0.02em;
}
.nav-brand:hover { color: var(--text-heading); }
.nav-logo {
  display: inline-flex; align-items: center; justify-content: center;
  width: 26px; height: 26px; border-radius: var(--radius);
  background: var(--bg-dark); color: #fff; font-size: 0.8rem; font-weight: 700;
}
.nav-links { display: flex; gap: 1.5rem; }
.nav-link {
  font-size: 0.82rem; font-weight: 500; color: var(--text-muted);
  padding: 0.25rem 0; border-bottom: 2px solid transparent;
  transition: all 0.15s;
}
.nav-link:hover { color: var(--text-heading); }
.nav-link.active { color: var(--accent-text); border-bottom-color: var(--accent); }

/* Main */
.main {
  flex: 1; max-width: 960px; width: 100%;
  margin: 0 auto; padding: 2rem;
}

/* Footer */
.footer {
  background: var(--bg-dark);
  padding: 1.5rem 2rem; margin-top: auto;
}
.footer-inner {
  max-width: 960px; margin: 0 auto;
  display: flex; flex-wrap: wrap; align-items: center;
  gap: 1.5rem; justify-content: space-between;
}
.footer-brand {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.82rem;
}
.footer-name { font-weight: 600; color: #ffffff; }
.footer-sep { color: #555555; }
.footer-cushlabs { color: #e8c34a; font-weight: 600; }
.footer-cushlabs:hover { color: #f0d76a; }
.footer-links { display: flex; gap: 1.25rem; font-size: 0.78rem; }
.footer-links a { color: #999999; }
.footer-links a:hover { color: #e8c34a; }
.footer-copy {
  font-size: 0.72rem; color: #666666; width: 100%;
  text-align: center; margin-top: 0.25rem;
}

/* Shared utilities */
.page-title {
  font-size: 1.5rem; font-weight: 700; color: var(--text-heading);
  margin-bottom: 0.3rem;
}
.page-subtitle { color: var(--text-muted); font-size: 0.92rem; margin-bottom: 2rem; }
.section { margin-bottom: 2.5rem; }
.section-title {
  font-size: 1.05rem; font-weight: 600; color: var(--text-heading);
  margin-bottom: 0.75rem;
}
.prose { line-height: 1.7; color: var(--text-body); }
.prose p { margin-bottom: 1rem; }
.prose ul, .prose ol { margin-bottom: 1rem; padding-left: 1.5rem; }
.prose li { margin-bottom: 0.4rem; }
.prose strong { color: var(--text-heading); font-weight: 600; }
.prose code {
  background: #f5f2e8; padding: 0.15rem 0.4rem; border-radius: 2px;
  font-size: 0.85em; color: #6b5510;
}
.card {
  background: var(--bg-primary); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1.5rem; margin-bottom: 1rem;
}

/* Buttons */
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem;
  padding: 0.55rem 1.2rem; border: none; border-radius: var(--radius);
  font-family: inherit; font-size: 0.85rem; font-weight: 600;
  cursor: pointer; transition: all 0.15s; white-space: nowrap;
}
.btn-primary { background: var(--accent); color: var(--text-heading); }
.btn-primary:hover { background: var(--accent-hover); color: var(--text-heading); }
.btn-secondary {
  background: var(--bg-primary); color: var(--text-body);
  border: 1px solid var(--border);
}
.btn-secondary:hover { background: var(--bg-secondary); color: var(--text-heading); }
.btn:disabled { opacity: 0.35; cursor: not-allowed; pointer-events: none; }
.btn-row { display: flex; gap: 0.75rem; margin-top: 1rem; flex-wrap: wrap; }

/* Loading spinner */
@keyframes spin { to { transform: rotate(360deg); } }
.spinner {
  width: 14px; height: 14px;
  border: 2px solid rgba(0,0,0,0.15);
  border-top-color: var(--text-heading); border-radius: 50%;
  animation: spin 0.6s linear infinite; display: inline-block;
}

/* Step progress — compact inline breadcrumb */
.steps-bar {
  display: flex; gap: 0; margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
}
.step-indicator {
  text-align: center; padding: 0.5rem 1.25rem;
  font-size: 0.72rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.06em; color: var(--text-faint);
  border-bottom: 2px solid transparent; transition: all 0.2s;
}
.step-indicator.active { color: var(--accent-text); border-bottom-color: var(--accent); }
.step-indicator.done { color: var(--success); border-bottom-color: var(--success); }
.step-num {
  display: inline-flex; align-items: center; justify-content: center;
  width: 18px; height: 18px; border-radius: 50%;
  background: var(--border-light); color: var(--text-faint); font-size: 0.65rem;
  margin-right: 0.35rem; font-weight: 700;
}
.step-indicator.active .step-num { background: var(--accent); color: var(--text-heading); }
.step-indicator.done .step-num { background: var(--success); color: #fff; }

/* Status */
.status {
  margin-top: 0.75rem; font-size: 0.82rem; color: var(--text-muted);
  text-align: center; min-height: 1.2rem;
}
.status.error { color: var(--error); }
.status.success { color: var(--success); }

/* Responsive */
@media (max-width: 640px) {
  .nav { padding: 0 1rem; }
  .main { padding: 1.5rem 1rem; }
  .page-title { font-size: 1.3rem; }
  .footer { padding: 1.25rem 1rem; }
  .footer-inner { flex-direction: column; text-align: center; }
  .step-indicator { padding: 0.5rem 0.75rem; font-size: 0.68rem; }
}
"""
