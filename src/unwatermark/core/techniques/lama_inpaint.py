"""LaMa inpainting technique — state-of-the-art object removal.

Supports three backends:
- local: Runs LaMa model on CPU/GPU via simple-lama-inpainting package
- replicate: Calls Replicate's hosted LaMa model (SaaS-ready)
- modal: Calls a Modal-deployed LaMa endpoint (SaaS-ready)

The backend is selected via config.inpaint_backend. The technique interface
is identical regardless of backend — callers don't know or care where the
model runs.
"""

from __future__ import annotations

import io
import logging

import numpy as np
from PIL import Image

from unwatermark.core.techniques.base import RemovalTechnique
from unwatermark.models.analysis import WatermarkAnalysis, WatermarkRegion

logger = logging.getLogger(__name__)


class LamaInpaintTechnique(RemovalTechnique):

    def __init__(self, backend: str = "local", **backend_kwargs):
        """Initialize with the specified backend.

        Args:
            backend: One of "local", "replicate", "modal".
            backend_kwargs: Backend-specific config (api tokens, model paths, etc.).
        """
        self._backend = backend
        self._backend_kwargs = backend_kwargs

    @property
    def name(self) -> str:
        return f"LaMa Inpaint ({self._backend})"

    def remove(
        self,
        image: Image.Image,
        region: WatermarkRegion,
        analysis: WatermarkAnalysis,
    ) -> Image.Image:
        # Use pixel-perfect SAM mask when available, otherwise build smart mask
        if analysis.mask is not None:
            mask = analysis.mask.convert("L")
            # Ensure mask matches image size
            if mask.size != image.size:
                mask = mask.resize(image.size, Image.NEAREST)
            logger.info("Using SAM pixel-perfect mask for inpainting")
        else:
            # Try threshold-based refinement to avoid eating into adjacent content
            mask = self._build_mask(image.size, region, image=image)

        if self._backend == "local":
            return self._run_local(image, mask)
        elif self._backend == "replicate":
            return self._run_replicate(image, mask)
        elif self._backend == "modal":
            return self._run_modal(image, mask)
        else:
            raise ValueError(f"Unknown inpaint backend: {self._backend}")

    def _build_mask(
        self, image_size: tuple[int, int], region: WatermarkRegion,
        image: Image.Image | None = None,
    ) -> Image.Image:
        """Create a binary mask — white where the watermark is, black everywhere else.

        When the source image is provided, attempts to refine the mask within the
        bounding box by detecting semi-transparent watermark pixels. This prevents
        the mask from eating into adjacent content (e.g., clipping letters near
        the watermark boundary).
        """
        w, h = image_size
        mask = Image.new("L", (w, h), 0)
        mask_arr = np.array(mask)

        if image is not None:
            refined = self._refine_mask_in_region(image, region)
            if refined is not None:
                mask_arr[region.y : region.y2, region.x : region.x2] = refined
                logger.info("Using refined mask (threshold-based) for inpainting")
                return Image.fromarray(mask_arr, mode="L")

        # Fallback: simple rectangle
        mask_arr[region.y : region.y2, region.x : region.x2] = 255
        return Image.fromarray(mask_arr, mode="L")

    @staticmethod
    def _refine_mask_in_region(
        image: Image.Image, region: WatermarkRegion
    ) -> np.ndarray | None:
        """Isolate watermark pixels within the bounding box using local deviation.

        Uses a median filter to estimate what the local background looks like
        without the watermark, then finds pixels that deviate from that estimate.
        Semi-transparent watermark text creates detectable local deviations even
        when the watermark and background have similar overall color properties.

        Critical: excludes dark pixels (content text like headings) from the mask.
        Watermarks are semi-transparent overlays — always lighter than solid content
        text. Without this, dark content letters overlapping the watermark bbox
        get flagged and damaged by inpainting.

        Returns a 2D uint8 array (region-sized) with 255 for watermark pixels
        and 0 for content pixels, or None if refinement isn't confident.
        """
        try:
            from scipy.ndimage import (
                binary_closing,
                binary_dilation,
                binary_opening,
                median_filter,
            )
        except ImportError:
            logger.debug("scipy not installed — skipping mask refinement")
            return None

        try:
            crop = image.crop((region.x, region.y, region.x2, region.y2))
            pixels = np.array(crop.convert("L"), dtype=np.float32)

            if pixels.size == 0 or min(pixels.shape) < 10:
                return None

            # Median filter estimates local background — the median "ignores"
            # watermark pixels when the kernel is larger than the text stroke width.
            # kernel_size=21 works for typical watermark text (stroke width ~3-8px).
            local_bg = median_filter(pixels, size=21)

            # Deviation from local background reveals watermark text
            deviation = np.abs(pixels - local_bg)

            # Threshold: pixels deviating more than 5 levels are likely watermark.
            # This value works well for semi-transparent gray text on light backgrounds.
            mask_bool = deviation > 5

            # Morphological cleanup: remove noise, fill text stroke gaps,
            # then dilate enough for LaMa to have context for clean fill
            struct = np.ones((3, 3))
            mask_bool = binary_opening(mask_bool, structure=struct, iterations=1)
            mask_bool = binary_closing(mask_bool, structure=struct, iterations=2)
            mask_bool = binary_dilation(mask_bool, structure=struct, iterations=3)

            # PROTECT DARK CONTENT TEXT (applied AFTER dilation so dilation
            # can't expand the mask back over protected pixels):
            # Watermarks are semi-transparent overlays — always lighter than
            # solid content text (headings, body text). Pixels darker than the
            # threshold are content, not watermark. This prevents the "D" in
            # "Document" from being damaged when "DRAFT" watermark overlaps it.
            dark_pixel_threshold = 120  # below this = solid content text
            is_dark_content = pixels < dark_pixel_threshold
            protected_count = np.sum(mask_bool & is_dark_content)
            mask_bool = mask_bool & ~is_dark_content
            if protected_count > 0:
                logger.info(
                    f"Dark-pixel protection: preserved {protected_count} content pixels "
                    f"from inpainting mask"
                )

            coverage = np.sum(mask_bool) / mask_bool.size
            if coverage < 0.01 or coverage > 0.85:
                # Too little = no watermark found in region; too much = false positive
                return None

            return (mask_bool.astype(np.uint8) * 255)

        except Exception as e:
            logger.debug(f"Mask refinement failed: {e}")
            return None

    # -------------------------------------------------------------------------
    # Backend: Local (simple-lama-inpainting)
    # -------------------------------------------------------------------------

    def _run_local(self, image: Image.Image, mask: Image.Image) -> Image.Image:
        """Run LaMa locally via the simple-lama-inpainting package."""
        try:
            from simple_lama_inpainting import SimpleLama
        except ImportError:
            raise RuntimeError(
                "LaMa inpainting requires the 'simple-lama-inpainting' package.\n"
                "Install it with: pip install simple-lama-inpainting\n"
                "Or install unwatermark with: pip install -e '.[inpaint]'"
            )

        model_path = self._backend_kwargs.get("model_path")
        lama = SimpleLama() if model_path is None else SimpleLama(model_path)

        result = lama(image.convert("RGB"), mask)
        return result

    # -------------------------------------------------------------------------
    # Backend: Replicate (hosted API — SaaS-ready)
    # -------------------------------------------------------------------------

    def _run_replicate(self, image: Image.Image, mask: Image.Image) -> Image.Image:
        """Run LaMa on Replicate's hosted infrastructure."""
        try:
            import replicate
        except ImportError:
            raise RuntimeError(
                "Replicate backend requires the 'replicate' package.\n"
                "Install it with: pip install replicate"
            )

        api_token = self._backend_kwargs.get("api_token")
        if api_token:
            client = replicate.Client(api_token=api_token)
        else:
            client = replicate.Client()

        # Encode images to bytes
        img_bytes = self._image_to_bytes(image, "PNG")
        mask_bytes = self._image_to_bytes(mask, "PNG")

        output = client.run(
            "twn39/lama",
            input={
                "image": io.BytesIO(img_bytes),
                "mask": io.BytesIO(mask_bytes),
            },
        )

        # Replicate returns a URL or file-like output
        if isinstance(output, str):
            import urllib.request
            with urllib.request.urlopen(output) as resp:
                return Image.open(io.BytesIO(resp.read()))
        elif hasattr(output, "read"):
            return Image.open(output)
        else:
            # Iterator of URLs
            for item in output:
                if isinstance(item, str):
                    import urllib.request
                    with urllib.request.urlopen(item) as resp:
                        return Image.open(io.BytesIO(resp.read()))

        raise RuntimeError("Unexpected Replicate output format")

    # -------------------------------------------------------------------------
    # Backend: Modal (custom deployment — SaaS-ready)
    # -------------------------------------------------------------------------

    def _run_modal(self, image: Image.Image, mask: Image.Image) -> Image.Image:
        """Call a Modal-deployed LaMa endpoint."""

        endpoint_url = self._backend_kwargs.get("endpoint_url")
        if not endpoint_url:
            raise ValueError(
                "Modal backend requires 'endpoint_url' in config.\n"
                "Set UNWATERMARK_MODAL_ENDPOINT_URL in your .env file."
            )

        img_bytes = self._image_to_bytes(image, "PNG")
        mask_bytes = self._image_to_bytes(mask, "PNG")

        # POST multipart to Modal endpoint
        import http.client
        from urllib.parse import urlparse

        boundary = "----UnwatermarkBoundary"
        body = self._build_multipart_body(
            boundary,
            [
                ("image", "image.png", "image/png", img_bytes),
                ("mask", "mask.png", "image/png", mask_bytes),
            ],
        )

        parsed = urlparse(endpoint_url)
        if parsed.scheme == "https":
            conn_cls = http.client.HTTPSConnection
        else:
            conn_cls = http.client.HTTPConnection
        conn = conn_cls(parsed.hostname, parsed.port)
        conn.request(
            "POST",
            parsed.path,
            body=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
        resp = conn.getresponse()
        if resp.status != 200:
            raise RuntimeError(f"Modal endpoint returned {resp.status}: {resp.read().decode()}")

        return Image.open(io.BytesIO(resp.read()))

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _image_to_bytes(image: Image.Image, fmt: str) -> bytes:
        buf = io.BytesIO()
        image.save(buf, format=fmt)
        return buf.getvalue()

    @staticmethod
    def _build_multipart_body(
        boundary: str,
        files: list[tuple[str, str, str, bytes]],
    ) -> bytes:
        """Build a multipart/form-data body."""
        parts = []
        for field_name, filename, content_type, data in files:
            parts.append(f"--{boundary}".encode())
            parts.append(
                f'Content-Disposition: form-data; name="{field_name}"; '
                f'filename="{filename}"'.encode()
            )
            parts.append(f"Content-Type: {content_type}".encode())
            parts.append(b"")
            parts.append(data)
        parts.append(f"--{boundary}--".encode())
        return b"\r\n".join(parts)


def is_lama_available() -> bool:
    """Check if the LaMa inpainting package is installed."""
    import importlib.util

    return importlib.util.find_spec("simple_lama_inpainting") is not None
