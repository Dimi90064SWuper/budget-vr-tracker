"""
Pose tracking with MediaPipe Pose (Tasks API).
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

# Pose landmark indices
LEFT_HIP = 23
RIGHT_HIP = 24
LEFT_KNEE = 25
RIGHT_KNEE = 26
LEFT_ANKLE = 27
RIGHT_ANKLE = 28
LEFT_HEEL = 29
RIGHT_HEEL = 30
LEFT_FOOT_INDEX = 31
RIGHT_FOOT_INDEX = 32


@dataclass
class FootData:
    position: Optional[np.ndarray] = None
    rotation: Optional[np.ndarray] = None
    confidence: float = 0.0
    timestamp: float = 0.0

    @property
    def is_valid(self) -> bool:
        return self.position is not None and self.rotation is not None


@dataclass
class PoseData:
    left_foot: FootData = field(default_factory=FootData)
    right_foot: FootData = field(default_factory=FootData)
    timestamp: float = field(default_factory=time.perf_counter)
    frame_time: float = 0.0

    @property
    def has_left_foot(self) -> bool:
        return self.left_foot.is_valid

    @property
    def has_right_foot(self) -> bool:
        return self.right_foot.is_valid


class PoseTracker:
    def __init__(self, config: Config):
        self.config = config
        self.is_active = True

        base_options = mp.tasks.BaseOptions(
            model_asset_path=config.tracking.pose_model_path,
            delegate=mp.tasks.BaseOptions.Delegate.CPU
        )

        options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            num_poses=1,
            min_pose_detection_confidence=config.tracking.min_pose_detection_confidence,
        )

        self._pose_landmarker = mp.tasks.vision.PoseLandmarker.create_from_options(options)
        log.info("PoseTracker initialized")

    def process(self, frame: np.ndarray, frame_time: float = 0.0) -> PoseData:
        if not self.is_active:
            return PoseData()

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        result = self._pose_landmarker.detect(image)

        pose_data = PoseData(frame_time=frame_time)

        if result and result.pose_world_landmarks:
            landmarks = np.array([[lm.x, lm.y, lm.z] for lm in result.pose_world_landmarks[0]], dtype=np.float32)

            pose_data.left_foot = self._process_foot(landmarks, LEFT_HEEL, LEFT_FOOT_INDEX, LEFT_ANKLE)
            pose_data.right_foot = self._process_foot(landmarks, RIGHT_HEEL, RIGHT_FOOT_INDEX, RIGHT_ANKLE)

        return pose_data

    def _process_foot(self, landmarks, heel_idx, toe_idx, ankle_idx) -> FootData:
        heel = landmarks[heel_idx]
        toe = landmarks[toe_idx]
        ankle = landmarks[ankle_idx]

        foot_center = (heel + toe) / 2
        rotation = self._foot_quaternion(heel, toe)

        return FootData(
            position=foot_center,
            rotation=rotation,
            confidence=0.9,
            timestamp=time.perf_counter(),
        )

    def _foot_quaternion(self, heel: np.ndarray, toe: np.ndarray) -> np.ndarray:
        direction = toe - heel
        direction /= np.linalg.norm(direction) + 1e-6
        up = np.array([0.0, 1.0, 0.0])
        right = np.cross(up, direction)
        right_norm = np.linalg.norm(right)
        if right_norm < 1e-6:
            return np.array([1.0, 0.0, 0.0, 0.0])
        right /= right_norm
        up_corrected = np.cross(direction, right)
        rot_matrix = np.column_stack([right, up_corrected, direction])
        rot = R.from_matrix(rot_matrix)
        quat = rot.as_quat()
        return np.array([quat[3], quat[0], quat[1], quat[2]])

    def close(self):
        self.is_active = False
        self._pose_landmarker.close()
