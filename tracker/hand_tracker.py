"""
Hand tracking with MediaPipe Hands (Tasks API).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Optional, List

import cv2
import mediapipe as mp
import numpy as np
from scipy.spatial.transform import Rotation as R

from .config import Config

log = logging.getLogger(__name__)

# Finger landmark indices
WRIST = 0
INDEX_FINGER_TIP = 8
MIDDLE_FINGER_TIP = 12
RING_FINGER_TIP = 16
PINKY_TIP = 20
INDEX_FINGER_MCP = 5
MIDDLE_FINGER_MCP = 9
RING_FINGER_MCP = 13
PINKY_MCP = 17


@dataclass
class HandLandmarks:
    positions: np.ndarray  # (21, 3)
    confidences: np.ndarray  # (21,)
    wrist_pos: np.ndarray
    hand_type: str
    timestamp: float


@dataclass
class HandData:
    left_hand: Optional[HandLandmarks] = None
    right_hand: Optional[HandLandmarks] = None
    timestamp: float = field(default_factory=time.perf_counter)
    frame_time: float = 0.0

    @property
    def has_left_hand(self) -> bool:
        return self.left_hand is not None

    @property
    def has_right_hand(self) -> bool:
        return self.right_hand is not None


class HandTracker:
    def __init__(self, config: Config):
        self.config = config
        self.is_active = True

        base_options = mp.tasks.BaseOptions(
            model_asset_path=config.tracking.hand_model_path,
            delegate=mp.tasks.BaseOptions.Delegate.CPU
        )

        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            num_hands=2,
            min_hand_detection_confidence=config.tracking.min_hand_detection_confidence,
            min_hand_presence_confidence=config.tracking.min_hand_detection_confidence,
        )

        self._hand_landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)
        log.info("HandTracker initialized")

    def process(self, frame: np.ndarray, frame_time: float = 0.0) -> HandData:
        if not self.is_active:
            return HandData()

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        result = self._hand_landmarker.detect(image)

        hand_data = HandData(frame_time=frame_time)

        if result:
            for hand_landmarks, handedness_list in zip(
                result.hand_landmarks, result.handedness
            ):
                handedness = handedness_list[0] if handedness_list else None
                hand_type = handedness.category_name.lower() if handedness else "right"

                positions = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks], dtype=np.float32)
                confidences = np.array([getattr(lm, 'visibility', 1.0) for lm in hand_landmarks], dtype=np.float32)

                hand = HandLandmarks(
                    positions=positions,
                    confidences=confidences,
                    wrist_pos=positions[WRIST],
                    hand_type=hand_type,
                    timestamp=hand_data.timestamp,
                )

                if hand_type == "left":
                    hand_data.left_hand = hand
                else:
                    hand_data.right_hand = hand

        return hand_data

    def is_grip(self, hand: HandLandmarks) -> bool:
        """Check if hand is making a fist."""
        positions = hand.positions
        for mcp_idx, tip_idx in zip(
            [INDEX_FINGER_MCP, MIDDLE_FINGER_MCP, RING_FINGER_MCP, PINKY_MCP],
            [INDEX_FINGER_TIP, MIDDLE_FINGER_TIP, RING_FINGER_TIP, PINKY_TIP]
        ):
            if positions[tip_idx][1] <= positions[mcp_idx][1]:
                return False
        return True

    def trigger_value(self, hand: HandLandmarks) -> float:
        """Get trigger value from index finger curl."""
        positions = hand.positions
        delta_y = positions[INDEX_FINGER_TIP][1] - positions[INDEX_FINGER_MCP][1]
        return float(max(0.0, min(1.0, delta_y / 0.08)))

    def get_orientation(self, hand: HandLandmarks) -> np.ndarray:
        """Get hand orientation as quaternion."""
        positions = hand.positions
        forward = positions[MIDDLE_FINGER_TIP] - positions[WRIST]
        forward /= np.linalg.norm(forward) + 1e-6
        right = positions[PINKY_MCP] - positions[INDEX_FINGER_MCP]
        right /= np.linalg.norm(right) + 1e-6
        up = np.cross(right, forward)
        up /= np.linalg.norm(up) + 1e-6
        rot_matrix = np.column_stack([right, up, forward])
        rot = R.from_matrix(rot_matrix)
        quat = rot.as_quat()
        return np.array([quat[3], quat[0], quat[1], quat[2]])

    def close(self):
        self.is_active = False
        self._hand_landmarker.close()
