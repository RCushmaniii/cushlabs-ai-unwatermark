"""Unit tests for the centralized Replicate retry helper.

Locks in:
- Rate-limit errors trigger retry with backoff.
- Non-rate-limit errors propagate immediately.
- Exhausted retries raise ReplicateRateLimitExhausted.
- Success on first attempt skips backoff.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from unwatermark.core.replicate_helpers import (
    ReplicateRateLimitExhausted,
    _is_rate_limit_error,
    run_with_retry,
)


class TestIsRateLimitError:
    def test_429_in_message(self):
        assert _is_rate_limit_error(Exception("HTTP 429: too many requests"))

    def test_throttled_keyword(self):
        assert _is_rate_limit_error(
            Exception("Request was throttled. Reset in 9s.")
        )

    def test_rate_limit_phrase(self):
        assert _is_rate_limit_error(Exception("Your rate limit is reduced"))

    def test_ratelimit_word(self):
        assert _is_rate_limit_error(Exception("RateLimit exceeded"))

    def test_unrelated_error(self):
        assert not _is_rate_limit_error(Exception("Connection refused"))
        assert not _is_rate_limit_error(ValueError("bad input"))


class TestRunWithRetry:
    def test_success_first_attempt_no_sleep(self, monkeypatch):
        sleep_calls = []
        monkeypatch.setattr(
            "unwatermark.core.replicate_helpers.time.sleep",
            lambda s: sleep_calls.append(s),
        )

        client = MagicMock()
        client.run.return_value = "result"

        result = run_with_retry(client, "model:hash", input={"x": 1})

        assert result == "result"
        assert client.run.call_count == 1
        assert sleep_calls == []

    def test_non_rate_limit_error_propagates_immediately(self, monkeypatch):
        sleep_calls = []
        monkeypatch.setattr(
            "unwatermark.core.replicate_helpers.time.sleep",
            lambda s: sleep_calls.append(s),
        )

        client = MagicMock()
        client.run.side_effect = ValueError("bad input")

        with pytest.raises(ValueError, match="bad input"):
            run_with_retry(client, "model:hash", input={})

        assert client.run.call_count == 1
        assert sleep_calls == []

    def test_rate_limit_then_success(self, monkeypatch):
        sleep_calls = []
        monkeypatch.setattr(
            "unwatermark.core.replicate_helpers.time.sleep",
            lambda s: sleep_calls.append(s),
        )

        client = MagicMock()
        client.run.side_effect = [
            Exception("Request was throttled. 429"),
            "result",
        ]

        result = run_with_retry(client, "model:hash", input={})

        assert result == "result"
        assert client.run.call_count == 2
        assert len(sleep_calls) == 1
        # First wait should be ~base_wait (8s) +/- 20% jitter
        assert 6.0 <= sleep_calls[0] <= 10.0

    def test_rate_limit_exhausted_raises_dedicated_exception(self, monkeypatch):
        monkeypatch.setattr(
            "unwatermark.core.replicate_helpers.time.sleep",
            lambda s: None,
        )

        client = MagicMock()
        client.run.side_effect = Exception("Request was throttled (429)")

        with pytest.raises(ReplicateRateLimitExhausted) as exc_info:
            run_with_retry(client, "vendor/model:hash", input={}, max_retries=2)

        assert "vendor/model" in str(exc_info.value)
        assert client.run.call_count == 3  # initial + 2 retries

    def test_retry_count_respects_max_retries(self, monkeypatch):
        monkeypatch.setattr(
            "unwatermark.core.replicate_helpers.time.sleep",
            lambda s: None,
        )

        client = MagicMock()
        client.run.side_effect = Exception("429 throttled")

        with pytest.raises(ReplicateRateLimitExhausted):
            run_with_retry(client, "m:h", input={}, max_retries=0)

        assert client.run.call_count == 1  # initial only, no retries

    def test_backoff_increases_with_attempts(self, monkeypatch):
        sleep_calls = []
        monkeypatch.setattr(
            "unwatermark.core.replicate_helpers.time.sleep",
            lambda s: sleep_calls.append(s),
        )

        client = MagicMock()
        client.run.side_effect = [
            Exception("throttled"),
            Exception("throttled"),
            Exception("throttled"),
            "result",
        ]

        run_with_retry(client, "m:h", input={}, max_retries=5, base_wait_seconds=10.0)

        # Three retries → three sleeps. Each should be larger than the previous
        # in expectation (base * (attempt + 1) * jitter), even with jitter.
        assert len(sleep_calls) == 3
        # attempt 0: 10 * 1 * [0.8, 1.2] = [8, 12]
        # attempt 1: 10 * 2 * [0.8, 1.2] = [16, 24]
        # attempt 2: 10 * 3 * [0.8, 1.2] = [24, 36]
        assert 8.0 <= sleep_calls[0] <= 12.0
        assert 16.0 <= sleep_calls[1] <= 24.0
        assert 24.0 <= sleep_calls[2] <= 36.0

    def test_passes_input_kwarg_to_client(self, monkeypatch):
        monkeypatch.setattr(
            "unwatermark.core.replicate_helpers.time.sleep", lambda s: None
        )

        client = MagicMock()
        client.run.return_value = "ok"

        payload = {"image": "uri", "prompt": "x"}
        run_with_retry(client, "model:hash", input=payload)

        client.run.assert_called_once_with("model:hash", input=payload)
