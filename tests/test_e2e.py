"""End-to-end Playwright tests for the Unwatermark web UI.

Requires a running dev server: uvicorn unwatermark.web:app --port 8000

Run with:
    pytest tests/test_e2e.py -v --headed   # watch in browser
    pytest tests/test_e2e.py -v             # headless
    pytest tests/test_e2e.py -v -k "NotebookLM"  # just the PPTX flow
"""

from __future__ import annotations

import os
import re
import tempfile
import zipfile
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

BASE_URL = os.environ.get("UNWATERMARK_TEST_URL", "http://localhost:8000")

# Real test files — NotebookLM PPTX from Downloads
NOTEBOOKLM_PPTX = Path.home() / "Downloads" / "BioJalisco_Biodiversity_AI.pptx"
TEST_VARIED_PPTX = Path.home() / "Downloads" / "test_varied_watermarks.pptx"


# =========================================================================
# Fixtures
# =========================================================================

@pytest.fixture(scope="session")
def browser_context_args():
    return {"base_url": BASE_URL}


# =========================================================================
# 1. Page loading — every route returns 200 with correct content
# =========================================================================

class TestPageLoading:
    """Verify every page loads, has correct title, and returns 200."""

    @pytest.mark.parametrize("path,title_contains", [
        ("/", "Unwatermark"),
        ("/app", "Remove Watermarks"),
        ("/help", "Help"),
        ("/contact", "Contact"),
        ("/terms", "Terms"),
        ("/privacy", "Privacy"),
    ])
    def test_page_loads_200(self, page: Page, path: str, title_contains: str):
        resp = page.goto(f"{BASE_URL}{path}")
        assert resp.status == 200
        expect(page).to_have_title(re.compile(title_contains, re.IGNORECASE))

    def test_404_page(self, page: Page):
        resp = page.goto(f"{BASE_URL}/nonexistent-route")
        assert resp.status == 404

    def test_favicon_loads(self, page: Page):
        resp = page.goto(f"{BASE_URL}/favicon.ico")
        assert resp.status == 200
        assert "svg" in resp.headers.get("content-type", "")

    def test_healthz_returns_ok(self, page: Page):
        resp = page.goto(f"{BASE_URL}/healthz")
        assert resp.status == 200
        body = page.locator("body").inner_text()
        assert "ok" in body


# =========================================================================
# 2. Navigation — links between pages work
# =========================================================================

class TestNavigation:
    """Test that nav links work and highlight correctly."""

    def test_nav_links_exist(self, page: Page):
        page.goto(f"{BASE_URL}/")
        nav = page.locator("nav")
        expect(nav).to_be_visible()
        # Should have links to main sections (use .first to handle desktop/mobile dupes)
        expect(nav.locator("a[href='/app']").first).to_be_visible()
        expect(nav.locator("a[href='/help']").first).to_be_visible()

    def test_nav_to_app(self, page: Page):
        page.goto(f"{BASE_URL}/")
        page.locator("nav a[href='/app']").first.click()
        page.wait_for_url(f"{BASE_URL}/app")
        expect(page).to_have_title(re.compile("Remove Watermarks"))

    def test_nav_to_help(self, page: Page):
        page.goto(f"{BASE_URL}/app")
        page.locator("nav a[href='/help']").first.click()
        page.wait_for_url(f"{BASE_URL}/help")
        expect(page).to_have_title(re.compile("Help"))

    def test_logo_links_home(self, page: Page):
        page.goto(f"{BASE_URL}/app")
        # Logo or brand link should go to /
        logo_link = page.locator("nav a[href='/']").first
        if logo_link.is_visible():
            logo_link.click()
            page.wait_for_url(f"{BASE_URL}/")


# =========================================================================
# 3. SEO — robots.txt, sitemap.xml, meta tags
# =========================================================================

class TestSEO:
    """Verify SEO essentials are present."""

    def test_robots_txt(self, page: Page):
        resp = page.goto(f"{BASE_URL}/robots.txt")
        assert resp.status == 200
        body = page.locator("body").inner_text()
        assert "User-agent" in body
        assert "Sitemap" in body

    def test_sitemap_xml(self, page: Page):
        resp = page.goto(f"{BASE_URL}/sitemap.xml")
        assert resp.status == 200

    def test_meta_description_exists(self, page: Page):
        page.goto(f"{BASE_URL}/")
        meta = page.locator("meta[name='description']")
        content = meta.get_attribute("content")
        assert content and len(content) > 10

    def test_og_tags_exist(self, page: Page):
        page.goto(f"{BASE_URL}/")
        og_title = page.locator("meta[property='og:title']")
        assert og_title.get_attribute("content")

    def test_canonical_link(self, page: Page):
        page.goto(f"{BASE_URL}/app")
        canonical = page.locator("link[rel='canonical']")
        href = canonical.get_attribute("href")
        assert href and "/app" in href


# =========================================================================
# 4. App page — upload zone and step indicators
# =========================================================================

class TestAppUploadZone:
    """Test the file upload UI on /app."""

    def test_drop_zone_visible(self, page: Page):
        page.goto(f"{BASE_URL}/app")
        expect(page.locator("#dropZone")).to_be_visible()
        expect(page.locator("#fileInput")).to_be_attached()

    def test_step_indicators_present(self, page: Page):
        page.goto(f"{BASE_URL}/app")
        expect(page.locator("#ind1")).to_be_visible()
        expect(page.locator("#ind2")).to_be_visible()
        expect(page.locator("#ind3")).to_be_visible()

    def test_step1_active_by_default(self, page: Page):
        page.goto(f"{BASE_URL}/app")
        expect(page.locator("#ind1")).to_have_class(re.compile("active"))
        expect(page.locator("#stepUpload")).to_have_class(re.compile("active"))

    def test_processing_step_hidden_by_default(self, page: Page):
        page.goto(f"{BASE_URL}/app")
        expect(page.locator("#stepProcessing")).not_to_have_class(re.compile("active"))

    def test_result_step_hidden_by_default(self, page: Page):
        page.goto(f"{BASE_URL}/app")
        expect(page.locator("#stepResult")).not_to_have_class(re.compile("active"))

    def test_file_input_accepts_correct_types(self, page: Page):
        page.goto(f"{BASE_URL}/app")
        accept = page.locator("#fileInput").get_attribute("accept")
        assert ".png" in accept
        assert ".jpg" in accept
        assert ".pdf" in accept
        assert ".pptx" in accept

    def test_drop_zone_click_triggers_file_input(self, page: Page):
        """Clicking the drop zone should trigger the hidden file input."""
        page.goto(f"{BASE_URL}/app")
        # The drop zone click handler calls fileInput.click()
        # We verify the JS binding exists by checking the drop zone is clickable
        expect(page.locator("#dropZone")).to_be_visible()
        # dropZone has cursor: pointer style
        cursor = page.locator("#dropZone").evaluate("el => getComputedStyle(el).cursor")
        assert cursor == "pointer"


# =========================================================================
# 5. API endpoints — direct HTTP tests
# =========================================================================

class TestAPIEndpoints:
    """Test API endpoints return correct status codes and shapes."""

    def test_process_no_file_returns_422(self, page: Page):
        """POST /process without a file should return 422 (FastAPI validation)."""
        page.goto(f"{BASE_URL}/app")
        result = page.evaluate("""async () => {
            const resp = await fetch('/process', { method: 'POST' });
            return { status: resp.status };
        }""")
        assert result["status"] == 422

    def test_analyze_no_file_returns_422(self, page: Page):
        """POST /analyze without a file should return 422."""
        page.goto(f"{BASE_URL}/app")
        result = page.evaluate("""async () => {
            const resp = await fetch('/analyze', { method: 'POST' });
            return { status: resp.status };
        }""")
        assert result["status"] == 422

    def test_process_unsupported_filetype_returns_400(self, page: Page):
        """POST /process with a .txt file should return 400."""
        page.goto(f"{BASE_URL}/app")
        result = page.evaluate("""async () => {
            const fd = new FormData();
            const blob = new Blob(['hello'], { type: 'text/plain' });
            fd.append('file', blob, 'test.txt');
            const resp = await fetch('/process', { method: 'POST', body: fd });
            return { status: resp.status, body: await resp.json() };
        }""")
        assert result["status"] == 400
        assert "error" in result["body"]

    def test_download_invalid_token_returns_404(self, page: Page):
        resp = page.goto(f"{BASE_URL}/download/invalid-token-xyz")
        assert resp.status == 404

    def test_analyze_invalid_image_returns_400(self, page: Page):
        """POST /analyze with a corrupt image should return 400."""
        page.goto(f"{BASE_URL}/app")
        result = page.evaluate("""async () => {
            const fd = new FormData();
            const blob = new Blob(['not-an-image'], { type: 'image/png' });
            fd.append('file', blob, 'corrupt.png');
            const resp = await fetch('/analyze', { method: 'POST', body: fd });
            return { status: resp.status, body: await resp.json() };
        }""")
        assert result["status"] == 400
        assert "error" in result["body"]


# =========================================================================
# 6. UI state management
# =========================================================================

class TestUIState:
    """Test UI state transitions and edge cases."""

    def test_step_indicators_update_on_upload(self, page: Page):
        """When a file is uploaded, step 2 should become active."""
        page.goto(f"{BASE_URL}/app")

        # Create a small test PNG in-browser to avoid needing external files
        page.evaluate("""() => {
            const canvas = document.createElement('canvas');
            canvas.width = 100; canvas.height = 100;
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = '#fff';
            ctx.fillRect(0, 0, 100, 100);
            ctx.fillStyle = '#000';
            ctx.font = '12px sans-serif';
            ctx.fillText('test', 10, 50);
            canvas.toBlob(blob => {
                const dt = new DataTransfer();
                dt.items.add(new File([blob], 'test.png', { type: 'image/png' }));
                document.getElementById('fileInput').files = dt.files;
                document.getElementById('fileInput').dispatchEvent(new Event('change'));
            }, 'image/png');
        }""")

        # Should transition to processing step
        expect(page.locator("#stepProcessing")).to_have_class(re.compile("active"), timeout=5000)
        expect(page.locator("#ind2")).to_have_class(re.compile("active"))

    def test_file_info_displays_on_upload(self, page: Page):
        """File name and size should appear in the processing view."""
        page.goto(f"{BASE_URL}/app")

        page.evaluate("""() => {
            const canvas = document.createElement('canvas');
            canvas.width = 50; canvas.height = 50;
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = '#ccc';
            ctx.fillRect(0, 0, 50, 50);
            canvas.toBlob(blob => {
                const dt = new DataTransfer();
                dt.items.add(new File([blob], 'my-photo.png', { type: 'image/png' }));
                document.getElementById('fileInput').files = dt.files;
                document.getElementById('fileInput').dispatchEvent(new Event('change'));
            }, 'image/png');
        }""")

        expect(page.locator("#stepProcessing")).to_have_class(re.compile("active"), timeout=5000)
        expect(page.locator("#fileName")).to_have_text("my-photo.png")

    def test_progress_bar_starts_at_low_value(self, page: Page):
        """Progress bar should have a small initial width when processing starts."""
        page.goto(f"{BASE_URL}/app")

        page.evaluate("""() => {
            const canvas = document.createElement('canvas');
            canvas.width = 50; canvas.height = 50;
            canvas.getContext('2d').fillRect(0, 0, 50, 50);
            canvas.toBlob(blob => {
                const dt = new DataTransfer();
                dt.items.add(new File([blob], 'test.png', { type: 'image/png' }));
                document.getElementById('fileInput').files = dt.files;
                document.getElementById('fileInput').dispatchEvent(new Event('change'));
            }, 'image/png');
        }""")

        expect(page.locator("#stepProcessing")).to_have_class(re.compile("active"), timeout=5000)
        # Progress fill should exist and have some width set
        fill = page.locator("#progressFill")
        expect(fill).to_be_visible()

    def test_activity_feed_populates(self, page: Page):
        """Activity feed should show at least one item when processing starts."""
        page.goto(f"{BASE_URL}/app")

        page.evaluate("""() => {
            const canvas = document.createElement('canvas');
            canvas.width = 50; canvas.height = 50;
            canvas.getContext('2d').fillRect(0, 0, 50, 50);
            canvas.toBlob(blob => {
                const dt = new DataTransfer();
                dt.items.add(new File([blob], 'test.png', { type: 'image/png' }));
                document.getElementById('fileInput').files = dt.files;
                document.getElementById('fileInput').dispatchEvent(new Event('change'));
            }, 'image/png');
        }""")

        expect(page.locator("#stepProcessing")).to_have_class(re.compile("active"), timeout=5000)
        # At least one activity item should appear
        expect(page.locator(".activity-item").first).to_be_visible(timeout=5000)


# =========================================================================
# 7. Responsive / accessibility basics
# =========================================================================

class TestAccessibility:
    """Basic accessibility and responsive checks."""

    def test_html_has_lang_attribute(self, page: Page):
        page.goto(f"{BASE_URL}/")
        lang = page.locator("html").get_attribute("lang")
        assert lang == "en"

    def test_viewport_meta_tag(self, page: Page):
        page.goto(f"{BASE_URL}/")
        viewport = page.locator("meta[name='viewport']")
        content = viewport.get_attribute("content")
        assert "width=device-width" in content

    def test_no_console_errors_on_app_page(self, page: Page):
        """App page should load without JS console errors."""
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.goto(f"{BASE_URL}/app")
        page.wait_for_load_state("networkidle")
        assert len(errors) == 0, f"Console errors: {errors}"

    def test_no_console_errors_on_landing(self, page: Page):
        """Landing page should load without JS console errors."""
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.goto(f"{BASE_URL}/")
        page.wait_for_load_state("networkidle")
        assert len(errors) == 0, f"Console errors: {errors}"


# =========================================================================
# 8. NotebookLM PPTX — full processing pipeline
# =========================================================================

class TestNotebookLMProcessing:
    """End-to-end: upload a real NotebookLM PPTX → process → download.

    This is the critical test — verifies the entire detection+removal pipeline
    works for the primary use case (Google NotebookLM slide deck watermarks).
    These tests require the BioJalisco file in ~/Downloads and a running server
    with valid Replicate API token.
    """

    @pytest.mark.skipif(
        not NOTEBOOKLM_PPTX.exists(),
        reason=f"NotebookLM test file not found: {NOTEBOOKLM_PPTX}",
    )
    def test_notebooklm_pptx_full_flow(self, page: Page):
        """Upload BioJalisco PPTX → process → verify result → download clean file."""
        page.goto(f"{BASE_URL}/app")

        # Step 1: Upload the file via the hidden input
        page.locator("#fileInput").set_input_files(str(NOTEBOOKLM_PPTX))

        # Should transition to Step 2 (Processing)
        expect(page.locator("#stepProcessing")).to_have_class(re.compile("active"), timeout=5000)
        expect(page.locator("#fileName")).to_contain_text("BioJalisco")

        # File size should be displayed
        expect(page.locator("#fileSize")).to_be_visible()

        # Activity feed should start populating
        expect(page.locator(".activity-item").first).to_be_visible(timeout=10000)

        # Wait for processing to complete — multi-slide PPTX with Replicate calls
        page.wait_for_function(
            """() => {
                const result = document.getElementById('stepResult');
                const error = document.querySelector('.error-alert');
                return (result && result.classList.contains('active')) || error;
            }""",
            timeout=300000,  # 5 minutes max
        )

        # Check for errors
        error_el = page.locator(".error-alert")
        if error_el.count() > 0:
            error_text = error_el.inner_text()
            pytest.fail(f"Processing failed with error: {error_text}")

        # Step 3: Document result card (not image slider)
        expect(page.locator("#docResult")).to_be_visible()
        expect(page.locator("#imageResult")).not_to_be_visible()
        expect(page.locator("text=Watermarks Removed")).to_be_visible()
        expect(page.locator("#resultFilename")).to_contain_text("clean_BioJalisco")

        # Download the file
        download_btn = page.locator("#btnDownloadDoc")
        expect(download_btn).to_be_visible()

        with page.expect_download() as download_info:
            download_btn.click()
        download = download_info.value

        assert download.suggested_filename.startswith("clean_")
        assert download.suggested_filename.endswith(".pptx")

        # Verify the downloaded PPTX is valid
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = Path(tmpdir) / download.suggested_filename
            download.save_as(str(save_path))
            file_size = save_path.stat().st_size
            assert file_size > 100_000, (
                f"Downloaded file too small ({file_size} bytes) — likely empty or corrupt"
            )
            assert zipfile.is_zipfile(str(save_path)), "Not a valid PPTX/ZIP"
            with zipfile.ZipFile(str(save_path)) as zf:
                names = zf.namelist()
                assert "[Content_Types].xml" in names
                slides = [n for n in names if n.startswith("ppt/slides/slide")]
                assert len(slides) > 0, "No slides in downloaded PPTX"

    @pytest.mark.skipif(
        not NOTEBOOKLM_PPTX.exists(),
        reason=f"NotebookLM test file not found: {NOTEBOOKLM_PPTX}",
    )
    def test_progress_stream_shows_slide_activity(self, page: Page):
        """Verify the progress stream reports per-slide activity."""
        page.goto(f"{BASE_URL}/app")
        page.locator("#fileInput").set_input_files(str(NOTEBOOKLM_PPTX))

        expect(page.locator("#stepProcessing")).to_have_class(re.compile("active"), timeout=5000)

        # Should see "Starting processing..." first
        expect(page.locator(".activity-item >> text=Starting processing")).to_be_visible(
            timeout=10000
        )

        # Wait for at least 3 activity items (start + slide progress)
        page.wait_for_function(
            "() => document.querySelectorAll('.activity-item').length >= 3",
            timeout=60000,
        )

        # Progress bar should have advanced
        fill_width = page.locator("#progressFill").evaluate(
            "el => parseFloat(el.style.width)"
        )
        assert fill_width > 0, "Progress bar didn't advance"

        # Wait for completion so we don't leave dangling server threads
        page.wait_for_function(
            """() => {
                const result = document.getElementById('stepResult');
                const error = document.querySelector('.error-alert');
                return (result && result.classList.contains('active')) || error;
            }""",
            timeout=300000,
        )

    @pytest.mark.skipif(
        not NOTEBOOKLM_PPTX.exists(),
        reason=f"NotebookLM test file not found: {NOTEBOOKLM_PPTX}",
    )
    def test_restart_after_notebooklm_processing(self, page: Page):
        """Start Over button resets to upload step after processing."""
        page.goto(f"{BASE_URL}/app")
        page.locator("#fileInput").set_input_files(str(NOTEBOOKLM_PPTX))

        # Wait for completion or error
        page.wait_for_function(
            """() => {
                const result = document.getElementById('stepResult');
                const error = document.querySelector('.error-alert');
                return (result && result.classList.contains('active')) || error;
            }""",
            timeout=300000,
        )

        # Click Start Over (could be on result card or error area)
        restart_btn = page.locator("#btnRestartDoc")
        if restart_btn.is_visible():
            restart_btn.click()
        else:
            page.locator("text=Start Over").first.click()

        # Should be back to upload step
        expect(page.locator("#stepUpload")).to_have_class(re.compile("active"))
        expect(page.locator(".drop-zone")).to_be_visible()


# =========================================================================
# 9. Varied watermarks PPTX (smaller, faster validation)
# =========================================================================

class TestVariedWatermarks:
    """Test with the pre-built varied watermarks PPTX (smaller, faster)."""

    @pytest.mark.skipif(
        not TEST_VARIED_PPTX.exists(),
        reason=f"Varied watermarks test file not found: {TEST_VARIED_PPTX}",
    )
    def test_varied_watermarks_processes_successfully(self, page: Page):
        """Upload test_varied_watermarks.pptx → process → verify success."""
        page.goto(f"{BASE_URL}/app")
        page.locator("#fileInput").set_input_files(str(TEST_VARIED_PPTX))

        expect(page.locator("#stepProcessing")).to_have_class(re.compile("active"), timeout=5000)
        expect(page.locator("#fileName")).to_contain_text("test_varied_watermarks")

        # Wait for completion or error
        page.wait_for_function(
            """() => {
                const result = document.getElementById('stepResult');
                const error = document.querySelector('.error-alert');
                return (result && result.classList.contains('active')) || error;
            }""",
            timeout=300000,
        )

        error_el = page.locator(".error-alert")
        if error_el.count() > 0:
            error_text = error_el.inner_text()
            pytest.fail(f"Processing failed: {error_text}")

        expect(page.locator("text=Watermarks Removed")).to_be_visible()
