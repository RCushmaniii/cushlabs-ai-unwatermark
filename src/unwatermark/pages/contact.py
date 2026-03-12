"""Contact page."""

from unwatermark.pages.layout import page

CONTACT_PAGE = page("Contact", """
<style>
  .contact-layout {
    display: grid;
    grid-template-columns: 1fr 360px;
    gap: 2rem;
    align-items: start;
  }
  .contact-info-cards {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  .contact-info-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.25rem 1.5rem;
  }
  .contact-info-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    border-radius: var(--radius-sm);
    background: var(--color-primary-light);
    color: var(--color-primary);
    flex-shrink: 0;
  }
  .contact-info-label {
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--color-text-muted);
    margin-bottom: 0.15rem;
  }
  .contact-info-value {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--color-text);
  }
  .contact-info-value a {
    color: var(--color-primary);
    text-decoration: none;
  }
  .contact-info-value a:hover {
    text-decoration: underline;
    text-underline-offset: 2px;
  }
  .success-card {
    display: none;
    background: var(--color-success-light);
    border: 1px solid #bbf7d0;
    border-radius: var(--radius);
    padding: 2rem;
    text-align: center;
  }
  .success-card.visible { display: block; }
  .success-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: #dcfce7;
    color: var(--color-success);
    margin-bottom: 1rem;
  }
  .success-card h3 {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #166534;
    margin-bottom: 0.5rem;
  }
  .success-card p {
    font-size: 0.95rem;
    color: #15803d;
  }
  @media (max-width: 768px) {
    .contact-layout {
      grid-template-columns: 1fr;
    }
  }
</style>

<div class="page-header">
  <h1 class="page-title">Contact Us</h1>
  <p class="page-subtitle">Get in touch with the CushLabs AI team</p>
</div>

<div class="contact-layout">
  <div>
    <div class="card card--elevated" id="contactFormCard">
      <form id="contactForm">
        <div class="control-group">
          <label class="control-label" for="contactName">Name</label>
          <input type="text" id="contactName" class="control-input" placeholder="Your name" required>
        </div>

        <div class="control-group">
          <label class="control-label" for="contactEmail">Email</label>
          <input type="email" id="contactEmail" class="control-input" placeholder="you@example.com" required>
        </div>

        <div class="control-group">
          <label class="control-label" for="contactSubject">Subject</label>
          <select id="contactSubject" class="control-input" required>
            <option value="" disabled selected>Select a topic</option>
            <option value="general">General</option>
            <option value="bug">Bug Report</option>
            <option value="feature">Feature Request</option>
            <option value="business">Business Inquiry</option>
          </select>
        </div>

        <div class="control-group">
          <label class="control-label" for="contactMessage">Message</label>
          <textarea id="contactMessage" class="control-input" placeholder="How can we help?" required></textarea>
        </div>

        <button type="submit" class="btn btn-primary btn-lg btn-full">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
          Send Message
        </button>
      </form>
    </div>

    <div class="success-card" id="contactSuccess">
      <div class="success-icon">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
      </div>
      <h3>Message sent!</h3>
      <p>Thank you! We'll get back to you soon.</p>
    </div>
  </div>

  <div class="contact-info-cards">
    <div class="card contact-info-card">
      <div class="contact-info-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
      </div>
      <div>
        <div class="contact-info-label">Email</div>
        <div class="contact-info-value"><a href="mailto:info@cushlabs.ai">info@cushlabs.ai</a></div>
      </div>
    </div>

    <div class="card contact-info-card">
      <div class="contact-info-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
      </div>
      <div>
        <div class="contact-info-label">Website</div>
        <div class="contact-info-value"><a href="https://cushlabs.ai" target="_blank" rel="noopener">cushlabs.ai</a></div>
      </div>
    </div>
  </div>
</div>

<script>
(function() {
  var form = document.getElementById('contactForm');
  var formCard = document.getElementById('contactFormCard');
  var successCard = document.getElementById('contactSuccess');
  if (form && formCard && successCard) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      formCard.style.display = 'none';
      successCard.classList.add('visible');
    });
  }
})();
</script>
""", active_nav="contact")
