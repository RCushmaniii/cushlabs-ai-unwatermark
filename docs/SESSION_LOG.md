# Session Log — cushlabs-ai-unwatermark

Entries are newest-first. Each entry documents one Claude Code working session.

---

<!-- New entries go above this line -->

## Session: 2026-10-26 (container runs as non-root; the site finally has an uptime monitor)

**Outcome:** PR #31 merged and deployed. The container runs as uid 1000 instead of root, the root
route answers HEAD, and unwatermark.cushlabs.ai is now watched by UptimeRobot.

### Accomplished

- **Non-root container.** `Dockerfile` creates an `app` user (uid 1000) and switches to it. Every
  runtime write already goes to `tempfile.gettempdir()` (/tmp): upload spool, previews, the download
  token store. The application tree stays root-owned and read-only to the process. Proved before
  editing by running the production image on the box with `--user 1000:1000` against the real env
  file: `/healthz` 200, landing page 200, Sentry initialized, output sweeper started.
- **Root route is GET+HEAD.** UptimeRobot's free tier probes with HEAD and the GET-only route
  returned 405, which is why this site had no monitor. Same fix cushlabs-vitals got in prod-server
  PR #17. Monitor `CushLabs — Unwatermark` (id 804434082) created via the API after deploy, e-mail
  alert contact attached.
- **`.dockerignore`** keeps tests, docs, scripts, public and env files out of the image.
- **Deployed** via `cushlabs-prod-server/scripts/deploy-service.sh unwatermark` (auto-rollback on
  failed healthcheck). Live: `uid=1000`, healthy, GET and HEAD on https://unwatermark.cushlabs.ai/
  both 200. The compose service also carries `no-new-privileges` and `cap_drop: ALL` since
  prod-server PR #30.

### Immediate Next Steps

- [x] `CLAUDE.md` showed the retired `docker compose up -d --build` deploy line — replaced with the
      real flow (merge → CI image → `deploy-service.sh unwatermark`) the same evening.
