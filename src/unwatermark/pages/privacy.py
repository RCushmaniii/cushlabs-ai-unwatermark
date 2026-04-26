"""Privacy Policy page."""

from unwatermark.pages.layout import page

PRIVACY_PAGE = page("Privacy Policy", """
<div class="page-header">
  <h1 class="page-title">Privacy Policy</h1>
  <p class="page-subtitle">Last updated: March 11, 2026</p>
</div>

<div class="section">
  <div class="card">
    <h2 class="section-title">Overview</h2>
    <div class="prose">
      <p>CushLabs AI Services ("we," "us," "our") operates the Unwatermark service. This Privacy Policy explains how we handle information when you use our Service.</p>
      <p>The short version: <strong>we process your files, we don't keep them, and we don't track you.</strong></p>
    </div>
  </div>
</div>

<div class="section">
  <div class="card">
    <h2 class="section-title">Information We Process</h2>
    <div class="prose">
      <p><strong>Files you upload:</strong> When you submit a file, it is held in temporary storage only for the time needed to process it. Image content may be transmitted to third-party processing providers as part of the removal workflow. Your original upload is discarded as soon as processing finishes, and the cleaned output is available only for a short download window (see Data Retention).</p>
      <p><strong>We do not:</strong></p>
      <ul>
        <li>Permanently store your uploaded files</li>
        <li>Create copies or backups of your content</li>
        <li>Use your files for training AI models</li>
        <li>Share your files with third parties (beyond the AI analysis API call)</li>
      </ul>
    </div>
  </div>
</div>

<div class="section">
  <div class="card">
    <h2 class="section-title">Third-Party Services</h2>
    <div class="prose">
      <p>To carry out watermark removal, image content may be transmitted to third-party processing providers under their respective privacy policies and commercial terms. We use providers whose terms prohibit using submitted data to train their models. We send only the content needed to perform the requested processing &mdash; no account information, contact details, or other personal data.</p>
    </div>
  </div>
</div>

<div class="section">
  <div class="card">
    <h2 class="section-title">Cookies &amp; Tracking</h2>
    <div class="prose">
      <p>The Service does not use cookies, analytics trackers, or any form of user tracking. We do not collect IP addresses, browser fingerprints, or usage statistics.</p>
    </div>
  </div>
</div>

<div class="section">
  <div class="card">
    <h2 class="section-title">Data Retention</h2>
    <div class="prose">
      <p>Original uploads are discarded as soon as processing finishes (success or failure). Cleaned output files are retained only long enough for you to download them &mdash; up to one hour &mdash; after which they are automatically removed. We do not retain user files, processing results, or account data beyond this window.</p>
    </div>
  </div>
</div>

<div class="section">
  <div class="card">
    <h2 class="section-title">Security</h2>
    <div class="prose">
      <p>All communication with the Service uses HTTPS encryption in transit. Files are handled in isolated temporary storage and automatically removed within the retention window described above. Because we do not collect user accounts or personal data, there is no user data to safeguard beyond the brief processing window.</p>
    </div>
  </div>
</div>

<div class="section">
  <div class="card">
    <h2 class="section-title">Your Rights</h2>
    <div class="prose">
      <p>Since we do not store your data, there is nothing to access, correct, or delete. If you have concerns about data sent to the AI analysis API, you may contact Anthropic directly regarding their data retention policies.</p>
    </div>
  </div>
</div>

<div class="section">
  <div class="card">
    <h2 class="section-title">Changes to This Policy</h2>
    <div class="prose">
      <p>We may update this Privacy Policy from time to time. Changes will be posted on this page with an updated revision date.</p>
    </div>
  </div>
</div>

<div class="section">
  <div class="card">
    <h2 class="section-title">Contact</h2>
    <div class="prose">
      <p>For privacy-related questions, contact us via our <a href="/contact">contact page</a> or email <span id="privacyEmail"></span>.</p>
      <script>(function(){var e=document.getElementById('privacyEmail');if(e){var a=document.createElement('a');var p=['in','fo'];var d=['cush','labs','.','ai'];var addr=p.join('')+String.fromCharCode(64)+d.join('');a.href='ma'+'il'+'to:'+addr;a.textContent=addr;e.appendChild(a);}})()</script>
    </div>
  </div>
</div>
""", active_nav="", description="Privacy Policy for Unwatermark. We process your files and don't keep them. No cookies, no tracking, no user data collected.", canonical_path="/privacy")
