# Web Viewer

3D visualization of tracking in real-time.

## Quick Start

```bash
# Terminal 1 - Tracker
python -m tracker.main --no-phone

# Terminal 2 - Web Viewer
python -m tracker.web_viewer --port 8765
```

Open http://localhost:8765 in browser.

## Features

- 3D visualization of all 4 devices
- Real-time position and rotation
- Grip/Trigger button display
- FPS counter
- Auto-reconnect
