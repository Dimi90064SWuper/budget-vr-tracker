"""
Coordinate fusion for Budget VR Tracker.
Converts MediaPipe coordinates to SteamVR space.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import yaml
from scipy.spatial.transform import Rotation as R

from .config import Config
from .hand_tracker import HandData, HandLandmarks
from .pose_tracker import PoseData, FootData

log = logging.getLogger(__name__)


@dataclass
class DevicePose:
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    rotation: np.ndarray = field(default_factory=lambda: np.array([1.0, 0.0, 0.0, 0.0]))
    grip: bool = False
    trigger: float = 0.0
    timestamp: float = field(default_factory=time.perf_counter)


@dataclass
class VRFrameData:
    left_ctrl: DevicePose = field(default_factory=DevicePose)
    right_ctrl: DevicePose = field(default_factory=DevicePose)
    left_foot: DevicePose = field(default_factory=DevicePose)
    right_foot: DevicePose = field(default_factory=DevicePose)
    timestamp: float = field(default_factory=time.perf_counter)

    def to_dict(self) -> dict:
        return {
            "ts": time.time(),
            "devices": {
                "left_ctrl": {
                    "pos": self.left_ctrl.position.tolist(),
                    "rot": self.left_ctrl.rotation.tolist(),
                    "buttons": {"grip": self.left_ctrl.grip, "trigger": self.left_ctrl.trigger},
                },
                "right_ctrl": {
                    "pos": self.right_ctrl.position.tolist(),
                    "rot": self.right_ctrl.rotation.tolist(),
                    "buttons": {"grip": self.right_ctrl.grip, "trigger": self.right_ctrl.trigger},
                },
                "left_foot": {
                    "pos": self.left_foot.position.tolist(),
                    "rot": self.left_foot.rotation.tolist(),
                },
                "right_foot": {
                    "pos": self.right_foot.position.tolist(),
                    "rot": self.right_foot.rotation.tolist(),
                },
            },
        }


def fix_rotation_matrix(R_mat: np.ndarray) -> np.ndarray:
    """Fix rotation matrix with non-positive determinant."""
    det = np.linalg.det(R_mat)
    if det < 0:
        R_mat = R_mat.copy()
        R_mat[:, 2] = -R_mat[:, 2]
    U, _, Vt = np.linalg.svd(R_mat)
    R_fixed = U @ Vt
    if np.linalg.det(R_fixed) < 0:
        U = U.copy()
        U[:, -1] *= -1
        R_fixed = U @ Vt
    return R_fixed


class CoordinateFusion:
    def __init__(self, config: Config):
        self.config = config
        self.calibration_scale = 1.0

    def mp_to_steamvr(self, pos: np.ndarray) -> np.ndarray:
        """Convert MediaPipe coords to SteamVR: Y-down → Y-up, Z-to-camera → Z-to-user."""
        return np.array([pos[0], -pos[1], -pos[2]], dtype=np.float32)

    def transform(self, hand_data: HandData, pose_data: PoseData) -> VRFrameData:
        vr_frame = VRFrameData(timestamp=time.perf_counter())

        if hand_data.has_left_hand:
            vr_frame.left_ctrl = self._hand_to_pose(hand_data.left_hand)
        if hand_data.has_right_hand:
            vr_frame.right_ctrl = self._hand_to_pose(hand_data.right_hand)
        if pose_data.has_left_foot:
            vr_frame.left_foot = self._foot_to_pose(pose_data.left_foot)
        if pose_data.has_right_foot:
            vr_frame.right_foot = self._foot_to_pose(pose_data.right_foot)

        return vr_frame

    def _hand_to_pose(self, hand: HandLandmarks) -> DevicePose:
        pos = self.mp_to_steamvr(hand.wrist_pos) * self.calibration_scale
        rot = self._compute_hand_orientation(hand)
        return DevicePose(position=pos, rotation=rot, grip=False, trigger=0.0)

    def _foot_to_pose(self, foot: FootData) -> DevicePose:
        if foot.position is None or foot.rotation is None:
            return DevicePose()
        pos = self.mp_to_steamvr(foot.position) * self.calibration_scale
        return DevicePose(position=pos, rotation=foot.rotation.copy())

    def _compute_hand_orientation(self, hand: HandLandmarks) -> np.ndarray:
        positions = hand.positions
        forward = positions[12] - positions[0]
        forward /= np.linalg.norm(forward) + 1e-6
        right = positions[17] - positions[5]
        right /= np.linalg.norm(right) + 1e-6
        up = np.cross(right, forward)
        up /= np.linalg.norm(up) + 1e-6
        rot_matrix = np.column_stack([right, up, forward])
        rot_matrix = fix_rotation_matrix(rot_matrix)
        rot = R.from_matrix(rot_matrix)
        quat = rot.as_quat()
        return np.array([quat[3], quat[0], quat[1], quat[2]])
