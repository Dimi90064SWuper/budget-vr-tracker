#!/bin/bash
# Download MediaPipe models

set -e

TRACKER_DIR="$(dirname "$0")/tracker"

echo "Downloading MediaPipe models..."

# Hand landmarker
if [ ! -f "$TRACKER_DIR/hand_landmarker.task" ]; then
    wget -q -O "$TRACKER_DIR/hand_landmarker.task" \
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    echo "✓ hand_landmarker.task downloaded"
else
    echo "✓ hand_landmarker.task exists"
fi

# Pose landmarker
if [ ! -f "$TRACKER_DIR/pose_landmarker_full.task" ]; then
    wget -q -O "$TRACKER_DIR/pose_landmarker_full.task" \
        "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/1/pose_landmarker_full.task"
    echo "✓ pose_landmarker_full.task downloaded"
else
    echo "✓ pose_landmarker_full.task exists"
fi

echo "Done!"
