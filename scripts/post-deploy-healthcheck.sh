#!/bin/bash
# Post-deploy health check for cushlabs-prod-01.
# Tests: every public vhost responds, unwatermark rate-limit fires at 11th /process POST.
# Exit code: 0 all good, 1 any check failed.

set -u
fail=0

check() {
  local label="$1" url="$2" expected="${3:-200}"
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" -L --max-time 10 "$url" 2>/dev/null || echo "ERR")
  if [ "$code" = "$expected" ]; then
    printf "  ✓ %-40s %s\n" "$label" "$code"
  else
    printf "  ✗ %-40s %s (expected %s)\n" "$label" "$code" "$expected"
    fail=1
  fi
}

echo "=== Public vhost health ==="
check "voice.cushlabs.ai"        "https://voice.cushlabs.ai/"
check "resume.cushlabs.ai"       "https://resume.cushlabs.ai/"
check "scraper.cushlabs.ai"      "https://scraper.cushlabs.ai/"
check "unwatermark /healthz"     "https://unwatermark.cushlabs.ai/healthz"
check "vitals tracker.js"        "https://vitals.cushlabs.ai/tracker.js"
check "marketsignal.cushlabs.ai" "https://marketsignal.cushlabs.ai/"

echo ""
echo "=== Rate-limit synthetic test (11x POST /process, expect 429 by 11th) ==="
hit_429=0
for i in $(seq 1 11); do
  # Empty body — will be rejected as 4xx by the app, but rate_limit fires BEFORE that
  code=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
    -H "Content-Type: multipart/form-data" \
    --max-time 5 \
    "https://unwatermark.cushlabs.ai/process" 2>/dev/null || echo "ERR")
  printf "  request %2d: %s\n" "$i" "$code"
  if [ "$code" = "429" ]; then
    hit_429=1
    break
  fi
done

if [ "$hit_429" = "1" ]; then
  echo "  ✓ Rate limit fired"
else
  echo "  ✗ Rate limit did NOT fire after 11 requests"
  fail=1
fi

echo ""
if [ "$fail" = "0" ]; then
  echo "ALL CHECKS PASSED"
  exit 0
else
  echo "ONE OR MORE CHECKS FAILED"
  exit 1
fi
