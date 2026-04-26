"""Domain-specific exception types."""

from __future__ import annotations


class UserInputError(Exception):
    """The user submitted a file we won't process (too big, wrong shape, etc.).

    Raised by handlers when input fails a hard guard (page/slide count, etc.).
    The web layer logs these at WARNING so they don't pollute Sentry — they
    represent the system working as designed, not a bug.
    """
