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
      <p><strong>Files you upload:</strong> When you upload an image, PDF, or PPTX file, it is processed in server memory. The image content may be sent to Anthropic's Claude API for watermark detection analysis. Temporary files created during processing are automatically deleted when your request completes.</p>
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
      <p>To analyze watermarks, uploaded images are sent to:</p>
      <ul>
        <li><strong>Anthropic (Claude API)</strong> — for vision-based watermark detection. Anthropic's data handling is governed by their <a href="https://www.anthropic.com/privacy" target="_blank" rel="noopener">privacy policy</a>. Per their commercial API terms, data sent via the API is not used for model training.</li>
      </ul>
      <p>If you use the CLI tool with the <code>--no-ai</code> flag, no data is sent to any external service.</p>
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
      <p>Uploaded files are held in server memory only for the duration of processing (typically a few seconds). No files, metadata, or processing results are retained after the HTTP response is sent.</p>
    </div>
  </div>
</div>

<div class="section">
  <div class="card">
    <h2 class="section-title">Security</h2>
    <div class="prose">
      <p>All communication with the Service uses HTTPS encryption in transit. Files are processed in isolated temporary storage and automatically cleaned up. We do not maintain a database of user data because we do not collect user data.</p>
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
      <p>For privacy-related questions, contact us at <a href="mailto:info@cushlabs.ai">info@cushlabs.ai</a>.</p>
    </div>
  </div>
</div>
""", active_nav="")
