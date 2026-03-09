"""Technique registry — maps strategy names to technique instances."""

from __future__ import annotations

from unwatermark.config import Config, InpaintBackend
from unwatermark.core.techniques.base import RemovalTechnique
from unwatermark.core.techniques.clone_stamp import CloneStampTechnique
from unwatermark.core.techniques.solid_fill import SolidFillTechnique
from unwatermark.models.analysis import RemovalStrategy


def get_technique(strategy: RemovalStrategy, config: Config | None = None) -> RemovalTechnique:
    """Get the appropriate technique instance for a strategy.

    Args:
        strategy: Which removal strategy to use.
        config: Runtime config (needed for inpainting backend selection).

    Returns:
        An initialized RemovalTechnique ready to call .remove().
    """
    if strategy in (RemovalStrategy.SOLID_FILL, RemovalStrategy.GRADIENT_FILL):
        return SolidFillTechnique()

    if strategy == RemovalStrategy.CLONE_STAMP:
        return CloneStampTechnique()

    if strategy == RemovalStrategy.INPAINT:
        return _get_inpaint_technique(config)

    raise ValueError(f"Unknown strategy: {strategy}")


def _get_inpaint_technique(config: Config | None) -> RemovalTechnique:
    """Build the inpaint technique with the configured backend."""
    from unwatermark.core.techniques.lama_inpaint import LamaInpaintTechnique

    if config is None:
        return LamaInpaintTechnique(backend="local")

    backend = config.inpaint_backend.value
    kwargs: dict = {}

    if config.inpaint_backend == InpaintBackend.LOCAL:
        if config.lama_model_path:
            kwargs["model_path"] = config.lama_model_path

    elif config.inpaint_backend == InpaintBackend.REPLICATE:
        kwargs["api_token"] = config.replicate_api_token

    elif config.inpaint_backend == InpaintBackend.MODAL:
        import os
        kwargs["endpoint_url"] = os.getenv("UNWATERMARK_MODAL_ENDPOINT_URL", "")

    return LamaInpaintTechnique(backend=backend, **kwargs)
