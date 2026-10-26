FROM python:3.11-slim

WORKDIR /app

# FFmpeg for video watermark removal
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Unprivileged runtime user (uid 1000 matches the `deploy` user on the Hetzner
# box). Created with a home directory so libraries that cache under $HOME have
# somewhere writable.
RUN useradd --create-home --uid 1000 --user-group --shell /usr/sbin/nologin app

COPY . .

RUN pip install --no-cache-dir -e ".[deploy]"

# All runtime writes go under tempfile.gettempdir() (/tmp, world-writable):
# upload spool, previews and the download token store in web.py. The
# application tree stays root-owned and read-only to the app, which is the
# point. Verified 2026-10-26 by running the production image with
# --user 1000:1000: /healthz 200, landing page 200, sweeper started.
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')" || exit 1

CMD ["uvicorn", "unwatermark.web:app", "--host", "0.0.0.0", "--port", "8000"]
