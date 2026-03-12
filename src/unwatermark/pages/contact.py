"""Contact page."""

from unwatermark.pages.layout import page

# Replace with your Formspree form ID (e.g. "xAbCdEfG")
# Sign up at https://formspree.io and create a form to get your ID
FORMSPREE_ID = "xqeyqjyl"

CONTACT_PAGE = page("Contact", f"""
<style>
  .contact-layout {{
    display: grid;
    grid-template-columns: 1fr 340px;
    gap: 2.5rem;
    align-items: start;
  }}
  .contact-info-cards {{
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }}
  .contact-info-card {{
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.25rem 1.5rem;
  }}
  .contact-info-icon {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    border-radius: var(--radius-sm);
    background: var(--color-primary-light);
    color: var(--color-primary);
    flex-shrink: 0;
  }}
  .contact-info-label {{
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--color-text-muted);
    margin-bottom: 0.15rem;
  }}
  .contact-info-value {{
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--color-text);
  }}
  .contact-info-value a {{
    color: var(--color-primary);
    text-decoration: none;
  }}
  .contact-info-value a:hover {{
    text-decoration: underline;
    text-underline-offset: 2px;
  }}
  .success-card {{
    display: none;
    background: var(--color-success-light);
    border: 1px solid #bbf7d0;
    border-radius: var(--radius);
    padding: 2.5rem;
    text-align: center;
  }}
  .success-card.visible {{ display: block; }}
  .success-icon {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: #dcfce7;
    color: var(--color-success);
    margin-bottom: 1rem;
  }}
  .success-card h3 {{
    font-family: 'DM Sans', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #166534;
    margin-bottom: 0.5rem;
  }}
  .success-card p {{
    font-size: 0.95rem;
    color: #15803d;
  }}
  .form-error {{
    display: none;
    background: var(--color-error-light);
    border: 1px solid var(--color-error-border);
    border-radius: var(--radius-sm);
    padding: 0.85rem 1rem;
    margin-top: 1rem;
    font-size: 0.9rem;
    color: #991b1b;
  }}
  .form-error.visible {{ display: block; }}
  .contact-note {{
    font-size: 0.82rem;
    color: var(--color-text-faint);
    margin-top: 1.25rem;
    line-height: 1.6;
  }}
  @media (max-width: 768px) {{
    .contact-layout {{
      grid-template-columns: 1fr;
    }}
  }}
</style>

<div class="page-header">
  <h1 class="page-title">Contact Us</h1>
  <p class="page-subtitle">Have a question or want to work with us? We'd love to hear from you.</p>
</div>

<div class="contact-layout">
  <div>
    <div class="card card--elevated" id="contactFormCard">
      <form id="contactForm" action="https://formspree.io/f/{FORMSPREE_ID}" method="POST">
        <input type="hidden" name="_subject" value="Unwatermark Contact Form">
        <!-- Honeypot field for spam protection -->
        <input type="text" name="_gotcha" style="display:none" tabindex="-1" autocomplete="off">

        <div class="control-group">
          <label class="control-label" for="contactName">Name</label>
          <input type="text" id="contactName" name="name" class="control-input" placeholder="Your name" required>
        </div>

        <div class="control-group">
          <label class="control-label" for="contactEmail">Email</label>
          <input type="email" id="contactEmail" name="email" class="control-input" placeholder="you@example.com" required>
        </div>

        <div class="control-group">
          <label class="control-label" for="contactSubject">Subject</label>
          <select id="contactSubject" name="subject" class="control-input" required>
            <option value="" disabled selected>Select a topic</option>
            <option value="General Inquiry">General Inquiry</option>
            <option value="Bug Report">Bug Report</option>
            <option value="Feature Request">Feature Request</option>
            <option value="Business Inquiry">Business Inquiry</option>
          </select>
        </div>

        <div class="control-group">
          <label class="control-label" for="contactMessage">Message</label>
          <textarea id="contactMessage" name="message" class="control-input" placeholder="How can we help?" required></textarea>
        </div>

        <button type="submit" class="btn btn-primary btn-lg btn-full" id="contactSubmit">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
          Send Message
        </button>

        <div class="form-error" id="formError">
          Something went wrong. Please try again or email us directly.
        </div>
      </form>
    </div>

    <div class="success-card" id="contactSuccess">
      <div class="success-icon">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
      </div>
      <h3>Message sent!</h3>
      <p>Thank you for reaching out. We'll get back to you soon.</p>
    </div>

    <p class="contact-note">
      We typically respond within 1-2 business days. For urgent issues,
      please include "Urgent" in your subject line.
    </p>
  </div>

  <div class="contact-info-cards">
    <div class="card contact-info-card">
      <div class="contact-info-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
      </div>
      <div>
        <div class="contact-info-label">Email</div>
        <div class="contact-info-value"><a id="emailLink" href="#">Loading...</a></div>
      </div>
    </div>

    <div class="card contact-info-card">
      <div class="contact-info-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
      </div>
      <div>
        <div class="contact-info-label">Developer Website</div>
        <div class="contact-info-value"><a href="https://cushlabs.ai" target="_blank" rel="noopener">cushlabs.ai</a></div>
      </div>
    </div>

    <div class="card contact-info-card">
      <div class="contact-info-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
      </div>
      <div>
        <div class="contact-info-label">Product</div>
        <div class="contact-info-value" style="font-size:0.88rem;font-weight:500;color:var(--color-text-secondary);">Unwatermark by CushLabs AI</div>
      </div>
    </div>
  </div>
</div>

<script>
(function() {{
  // Obfuscate email from scrapers — assembled at runtime
  var el = document.getElementById('emailLink');
  if (el) {{
    var p = ['in','fo'];
    var d = ['cush','labs','.','ai'];
    var addr = p.join('') + String.fromCharCode(64) + d.join('');
    el.href = 'ma' + 'il' + 'to:' + addr;
    el.textContent = addr;
  }}

  // Formspree AJAX submission
  var form = document.getElementById('contactForm');
  var formCard = document.getElementById('contactFormCard');
  var successCard = document.getElementById('contactSuccess');
  var errorEl = document.getElementById('formError');
  var submitBtn = document.getElementById('contactSubmit');

  if (form && formCard && successCard) {{
    form.addEventListener('submit', function(e) {{
      e.preventDefault();
      errorEl.classList.remove('visible');
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner"></span> Sending...';

      var data = new FormData(form);

      fetch(form.action, {{
        method: 'POST',
        body: data,
        headers: {{ 'Accept': 'application/json' }}
      }})
      .then(function(resp) {{
        if (resp.ok) {{
          formCard.style.display = 'none';
          successCard.classList.add('visible');
        }} else {{
          return resp.json().then(function(d) {{
            throw new Error(d.error || 'Form submission failed');
          }});
        }}
      }})
      .catch(function(err) {{
        errorEl.classList.add('visible');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg> Send Message';
      }});
    }});
  }}
}})();
</script>
""", active_nav="contact", description="Contact CushLabs AI — get in touch about Unwatermark, report bugs, request features, or discuss business inquiries.")
