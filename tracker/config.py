"""
Конфигурация системы Budget VR Tracker.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import yaml

log = logging.getLogger(__name__)

# Константы
DEFAULT_PHONE_URL = "http://192.168.1.100:8080/video"
DEFAULT_UDP_PORT = 57011
DEFAULT_HAND_MODEL_PATH = "tracker/hand_landmarker.task"
DEFAULT_POSE_MODEL_PATH = "tracker/pose_landmarker_full.task"


@dataclass
class CameraConfig:
    webcam_index: int = 0
    phone_url: str = DEFAULT_PHONE_URL
    phone_enabled: bool = True


@dataclass
class TrackingConfig:
    hand_model_path: str = DEFAULT_HAND_MODEL_PATH
    pose_model_path: str = DEFAULT_POSE_MODEL_PATH
    min_hand_detection_confidence: float = 0.7
    min_pose_detection_confidence: float = 0.6


@dataclass
class BridgeConfig:
    mode: Literal["udp", "pipe"] = "udp"
    udp_port: int = DEFAULT_UDP_PORT


@dataclass
class SmoothingConfig:
    alpha: float = 0.7
    position_deadzone_m: float = 0.005


@dataclass
class Config:
    cameras: CameraConfig = field(default_factory=CameraConfig)
    tracking: TrackingConfig = field(default_factory=TrackingConfig)
    bridge: BridgeConfig = field(default_factory=BridgeConfig)
    smoothing: SmoothingConfig = field(default_factory=SmoothingConfig)

    @classmethod
    def from_yaml(cls, path: str) -> "Config":
        with open(path) as f:
            return cls(**yaml.safe_load(f))

    def save_yaml(self, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            yaml.dump({"cameras": self.cameras.__dict__, "tracking": self.tracking.__dict__}, f)
