"""
UDP bridge to SteamVR driver.
"""

from __future__ import annotations

import asyncio
import json
import logging
import socket
import time
from dataclasses import dataclass

from .coordinate_fusion import VRFrameData

log = logging.getLogger(__name__)

DEFAULT_UDP_PORT = 57011


class SteamVRBridgeUDP:
    def __init__(self, host: str = "127.0.0.1", port: int = DEFAULT_UDP_PORT):
        self.host = host
        self.port = port
        self._socket: socket.socket | None = None
        self._connected = False

    async def connect(self) -> bool:
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.connect((self.host, self.port))
            self._connected = True
            log.info("UDP bridge connected to %s:%d", self.host, self.port)
            return True
        except Exception as e:
            log.warning("UDP connect failed: %s", e)
            self._connected = False
            return False

    async def send_frame(self, frame: VRFrameData) -> bool:
        if not self._connected:
            if not await self.connect():
                return False

        try:
            data = json.dumps(frame.to_dict(), separators=(",", ":")).encode("utf-8")
            self._socket.send(data)
            return True
        except Exception as e:
            log.warning("UDP send failed: %s", e)
            self._connected = False
            return False

    def close(self):
        if self._socket:
            self._socket.close()
        self._connected = False


async def send_loop(bridge: SteamVRBridgeUDP, queue: asyncio.Queue, running: asyncio.Event):
    """Send frames from queue to bridge."""
    while running.is_set() or not queue.empty():
        try:
            frame = await asyncio.wait_for(queue.get(), timeout=0.5)
            await bridge.send_frame(frame)
        except asyncio.TimeoutError:
            continue
        except Exception as e:
            log.error("Send error: %s", e)
            await asyncio.sleep(1)
