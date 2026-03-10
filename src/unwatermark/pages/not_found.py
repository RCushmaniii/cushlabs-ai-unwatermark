"""404 Not Found page."""

from unwatermark.pages.layout import page

NOT_FOUND_PAGE = page("Page Not Found", """
<div style="text-align:center;padding:4rem 1rem;">
  <p style="font-size:4.5rem;font-weight:800;color:var(--text-heading);line-height:1;margin-bottom:0.5rem;">404</p>
  <h1 style="font-size:1.2rem;font-weight:600;color:var(--text-heading);margin-bottom:0.5rem;">Page not found</h1>
  <p style="color:var(--text-muted);margin-bottom:2rem;">The page you're looking for doesn't exist or has been moved.</p>
  <a href="/" class="btn btn-primary" style="text-decoration:none;">Back to Unwatermark</a>
</div>
""", active_nav="")
