#!/bin/bash
# Run tracker with web viewer

set -e
cd "$(dirname "$0")"
source venv/bin/activate

echo "=== Budget VR Tracker ==="
echo "Web Interface: http://localhost:8765"
echo ""

# Start tracker in background
python -m tracker.main --no-phone &
TRACKER_PID=$!

sleep 2

# Start web viewer
python -m tracker.web_viewer --port 8765 &
VIEWER_PID=$!

echo "Tracker PID: $TRACKER_PID"
echo "Viewer PID: $VIEWER_PID"
echo "Press Ctrl+C to stop"

wait
