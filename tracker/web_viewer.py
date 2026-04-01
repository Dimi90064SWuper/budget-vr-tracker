"""
Web-based 3D visualization for Budget VR Tracker.
"""

import argparse
import asyncio
import json
import logging
import socket
from websockets.asyncio.server import serve

log = logging.getLogger(__name__)

connected_clients = set()


def create_html() -> str:
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Budget VR Tracker - Viewer</title>
    <style>
        body { margin: 0; background: #1a1a2e; color: #fff; font-family: sans-serif; }
        #container { display: flex; height: 100vh; }
        #canvas-container { flex: 1; }
        #sidebar { width: 300px; background: rgba(0,0,0,0.3); padding: 20px; }
        .device { background: rgba(255,255,255,0.05); padding: 15px; margin: 10px 0; border-radius: 8px; }
        .device.active { border: 1px solid #00ff88; }
        h1 { color: #00d4ff; }
        h2 { color: #00d4ff; font-size: 16px; }
        .data-row { font-family: monospace; font-size: 12px; margin: 5px 0; }
        .label { color: #aaa; }
        .value { color: #00d4ff; }
    </style>
</head>
<body>
    <div id="container">
        <div id="canvas-container"><canvas id="canvas"></canvas></div>
        <div id="sidebar">
            <h1>🎮 Budget VR Tracker</h1>
            <h2>Devices</h2>
            <div class="device" id="left-ctrl"><div class="data-row"><span class="label">Left Ctrl:</span> <span class="value" id="left-ctrl-pos">-</span></div></div>
            <div class="device" id="right-ctrl"><div class="data-row"><span class="label">Right Ctrl:</span> <span class="value" id="right-ctrl-pos">-</span></div></div>
            <div class="device" id="left-foot"><div class="data-row"><span class="label">Left Foot:</span> <span class="value" id="left-foot-pos">-</span></div></div>
            <div class="device" id="right-foot"><div class="data-row"><span class="label">Right Foot:</span> <span class="value" id="right-foot-pos">-</span></div></div>
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        let scene, camera, renderer, devices = {};
        function init() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x1a1a2e);
            camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 100);
            camera.position.set(0, 1.5, 3);
            renderer = new THREE.WebGLRenderer({canvas: document.getElementById('canvas')});
            renderer.setSize(window.innerWidth, window.innerHeight);
            const light = new THREE.DirectionalLight(0xffffff, 1);
            light.position.set(5, 10, 7);
            scene.add(light);
            scene.add(new THREE.GridHelper(10, 20));
            ['left_ctrl', 'right_ctrl', 'left_foot', 'right_foot'].forEach(name => {
                const geo = new THREE.BoxGeometry(0.1, 0.1, 0.15);
                const mat = new THREE.MeshPhongMaterial({color: name.includes('left') ? 0x00ff88 : 0x00d4ff});
                const mesh = new THREE.Mesh(geo, mat);
                scene.add(mesh);
                devices[name] = mesh;
            });
            connectWS();
            animate();
        }
        function connectWS() {
            const ws = new WebSocket('ws://' + location.hostname + ':8765');
            ws.onmessage = (e) => {
                const data = JSON.parse(e.data);
                if (data.devices) {
                    ['left_ctrl', 'right_ctrl', 'left_foot', 'right_foot'].forEach(name => {
                        const dev = data.devices[name];
                        if (dev && devices[name]) {
                            devices[name].position.set(dev.pos[0], dev.pos[1], dev.pos[2]);
                            document.getElementById(name + '-pos').textContent = dev.pos.map(v => v.toFixed(2)).join(', ');
                            document.getElementById(name).classList.add('active');
                        }
                    });
                }
            };
        }
        function animate() {
            requestAnimationFrame(animate);
            renderer.render(scene, camera);
        }
        window.addEventListener('load', init);
    </script>
</body>
</html>'''


async def handler(websocket):
    connected_clients.add(websocket)
    log.info("Client connected")
    try:
        await websocket.wait_closed()
    finally:
        connected_clients.discard(websocket)


async def udp_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', 57012))
    sock.settimeout(1.0)
    log.info("UDP listener on port 57012")
    while True:
        try:
            data, _ = sock.recvfrom(4096)
            frame_data = json.loads(data.decode())
            if connected_clients:
                await asyncio.gather(
                    *[client.send(json.dumps(frame_data)) for client in connected_clients],
                    return_exceptions=True
                )
        except socket.timeout:
            continue
        except Exception as e:
            log.debug("UDP error: %s", e)


async def main_async(port: int = 8765):
    log.info("Starting web viewer on port %d", port)
    async with serve(handler, "0.0.0.0", port, process_request=lambda p, h: (200, [], create_html().encode()) if p == "/" else (404, [], b"")):
        log.info("Open http://localhost:%d in browser", port)
        await udp_listener()


def main():
    parser = argparse.ArgumentParser(description="Budget VR Tracker Web Viewer")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
    try:
        asyncio.run(main_async(args.port))
    except KeyboardInterrupt:
        log.info("Stopped")


if __name__ == "__main__":
    main()
