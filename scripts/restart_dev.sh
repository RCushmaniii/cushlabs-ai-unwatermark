#!/usr/bin/env bash
# Restart the dev server on port 8000.
# Kills any existing process on the port, waits for it to die, then starts fresh.

PORT=8000
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Restarting dev server on port $PORT ==="

# Find and kill whatever is on the port
PID=$(netstat -ano 2>/dev/null | grep ":$PORT" | grep LISTEN | awk '{print $5}' | head -1)
if [ -n "$PID" ] && [ "$PID" != "0" ]; then
    echo "Killing PID $PID on port $PORT..."
    taskkill //F //PID "$PID" > /dev/null 2>&1
    # Wait until the port is actually free
    for i in 1 2 3 4 5; do
        sleep 1
        CHECK=$(netstat -ano 2>/dev/null | grep ":$PORT" | grep LISTEN)
        if [ -z "$CHECK" ]; then
            echo "Port $PORT is free."
            break
        fi
    done
else
    echo "Port $PORT is already free."
fi

# Start the server
echo "Starting uvicorn..."
cd "$PROJECT_DIR"
python -m uvicorn unwatermark.web:app --host 127.0.0.1 --port $PORT --log-level info &
SERVER_PID=$!

# Wait for it to be ready
for i in 1 2 3 4 5 6 7 8; do
    sleep 1
    CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$PORT/" 2>/dev/null)
    if [ "$CODE" = "200" ]; then
        echo "Server running at http://127.0.0.1:$PORT/ (PID $SERVER_PID)"
        exit 0
    fi
done

echo "ERROR: Server failed to start. Check logs."
exit 1
