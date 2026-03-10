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
        # Build binary mask: white = area to inpaint, black = keep
        mask = self._build_mask(image.size, region)

        if self._backend == "local":
            return self._run_local(image, mask)
        elif self._backend == "replicate":
            return self._run_replicate(image, mask)
        elif self._backend == "modal":
            return self._run_modal(image, mask)
        else:
            raise ValueError(f"Unknown inpaint backend: {self._backend}")

    def _build_mask(
        self, image_size: tuple[int, int], region: WatermarkRegion
    ) -> Image.Image:
        """Create a binary mask — white where the watermark is, black everywhere else."""
        w, h = image_size
        mask = Image.new("L", (w, h), 0)
        # Draw white rectangle over the watermark region
        mask_arr = np.array(mask)
        mask_arr[region.y : region.y2, region.x : region.x2] = 255
        return Image.fromarray(mask_arr, mode="L")

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
            "andreasjansson/lama-cleaner:a]",
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
