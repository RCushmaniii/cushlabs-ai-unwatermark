"""Centralized Replicate API call helpers — retry, rate-limit handling, error mapping."""

from __future__ import annotations

import logging
import random
import time

logger = logging.getLogger(__name__)


class ReplicateRateLimitExhausted(Exception):
    """Raised when Replicate rate-limit retries have all failed.

    The web layer maps this to HTTP 429 instead of 500, and Sentry's
    before_send filter drops it so legitimate user-side throttling does
    not page on-call.
    """


def _is_rate_limit_error(exc: BaseException) -> bool:
    msg = str(exc).lower()
    return (
        "429" in msg
        or "throttled" in msg
        or "rate limit" in msg
        or "ratelimit" in msg
    )


def run_with_retry(
    client,
    model: str,
    *,
    input: dict,
    max_retries: int = 5,
    base_wait_seconds: float = 8.0,
):
    """Call client.run(model, input=...) with exponential backoff on rate-limit errors.

    Backoff: base_wait * (attempt + 1) with +/-20% jitter.
    Default schedule: 8, 16, 24, 32, 40s — sums to ~120s, longer than
    Replicate's 60s sliding window so a sustained throttle clears.

    Non-rate-limit errors propagate immediately (likely real bugs).

    Args:
        client: A replicate.Client instance.
        model: Replicate model identifier (with version hash).
        input: Model input payload.
        max_retries: Number of retry attempts after the first call (default 5).
        base_wait_seconds: Base backoff (default 8s).

    Returns:
        Whatever client.run() returns (URL, FileOutput, iterator).

    Raises:
        ReplicateRateLimitExhausted: When rate-limit retries are exhausted.
        Exception: Any non-rate-limit error from client.run() is re-raised.
    """
    last_exc: BaseException | None = None
    model_label = model.split(":", 1)[0]

    for attempt in range(max_retries + 1):
        try:
            return client.run(model, input=input)
        except Exception as e:
            if not _is_rate_limit_error(e):
                raise
            last_exc = e
            if attempt >= max_retries:
                break
            wait = base_wait_seconds * (attempt + 1) * random.uniform(0.8, 1.2)
            logger.warning(
                "Replicate rate limited on %s (attempt %d/%d), waiting %.1fs",
                model_label,
                attempt + 1,
                max_retries + 1,
                wait,
            )
            time.sleep(wait)

    raise ReplicateRateLimitExhausted(
        f"Replicate rate limit not cleared after {max_retries + 1} attempts on {model_label}"
    ) from last_exc
