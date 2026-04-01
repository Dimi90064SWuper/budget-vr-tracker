#!/bin/bash
# Initialize OpenVR SDK

set -e

LIBRARIES_DIR="$(dirname "$0")/driver/libraries"

echo "=== Initializing OpenVR SDK ==="

mkdir -p "$LIBRARIES_DIR"
cd "$LIBRARIES_DIR"

if [ -d "openvr/.git" ]; then
    echo "OpenVR SDK already initialized"
    git submodule update --init openvr
else
    echo "Cloning OpenVR SDK..."
    git clone --depth 1 https://github.com/ValveSoftware/openvr.git
fi

echo "✓ OpenVR SDK ready"
