"""Terms of Service page."""

from unwatermark.pages.layout import page

TERMS_PAGE = page("Terms of Service", """
<h1 class="page-title">Terms of Service</h1>
<p class="page-subtitle">Last updated: March 9, 2026</p>

<div class="section prose">
  <h2 class="section-title">1. Acceptance of Terms</h2>
  <p>By accessing or using Unwatermark ("the Service"), provided by CushLabs AI Services ("we," "us," "our"), you agree to be bound by these Terms of Service. If you do not agree to these terms, do not use the Service.</p>
</div>

<div class="section prose">
  <h2 class="section-title">2. Description of Service</h2>
  <p>Unwatermark is an AI-powered tool that removes watermarks from uploaded images, PDFs, and PPTX files. The Service uses artificial intelligence to analyze images and apply image processing techniques to remove detected watermarks.</p>
</div>

<div class="section prose">
  <h2 class="section-title">3. Acceptable Use</h2>
  <p>You agree to use the Service only for lawful purposes. You are solely responsible for ensuring that your use of the Service complies with all applicable laws and regulations, including but not limited to copyright and intellectual property laws.</p>
  <p>You represent and warrant that:</p>
  <ul>
    <li>You own the files you upload, or have authorization from the copyright holder to modify them.</li>
    <li>You will not use the Service to infringe upon the intellectual property rights of others.</li>
    <li>You will not use the Service to remove watermarks from content you do not have the right to modify.</li>
    <li>You will not use the Service for any illegal, fraudulent, or deceptive purpose.</li>
  </ul>
</div>

<div class="section prose">
  <h2 class="section-title">4. Intellectual Property</h2>
  <p>The Service itself, including its design, code, and underlying algorithms, is the proprietary property of CushLabs AI Services and is protected by applicable intellectual property laws. You are granted a limited, non-exclusive, non-transferable license to use the Service for its intended purpose.</p>
</div>

<div class="section prose">
  <h2 class="section-title">5. File Handling</h2>
  <p>Files uploaded to the Service are processed in memory and are not permanently stored. Temporary files created during processing are automatically deleted. We do not retain, archive, or share your uploaded content.</p>
  <p>Images may be sent to third-party AI services (such as Anthropic's Claude API) for watermark detection analysis. These transmissions are governed by the respective provider's privacy and data handling policies.</p>
</div>

<div class="section prose">
  <h2 class="section-title">6. Disclaimer of Warranties</h2>
  <p>The Service is provided "as is" and "as available" without warranties of any kind, either express or implied. We do not guarantee that:</p>
  <ul>
    <li>Watermark removal will be complete or perfect in all cases.</li>
    <li>The Service will be uninterrupted, error-free, or secure.</li>
    <li>The results will meet your specific requirements.</li>
  </ul>
</div>

<div class="section prose">
  <h2 class="section-title">7. Limitation of Liability</h2>
  <p>To the maximum extent permitted by law, CushLabs AI Services shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising from your use of the Service, including but not limited to loss of data, revenue, or business opportunities.</p>
</div>

<div class="section prose">
  <h2 class="section-title">8. Changes to Terms</h2>
  <p>We reserve the right to modify these Terms at any time. Changes will be effective immediately upon posting. Continued use of the Service after changes constitutes acceptance of the updated Terms.</p>
</div>

<div class="section prose">
  <h2 class="section-title">9. Contact</h2>
  <p>For questions about these Terms, contact us at <a href="mailto:info@cushlabs.ai">info@cushlabs.ai</a>.</p>
</div>
""", active_nav="")
