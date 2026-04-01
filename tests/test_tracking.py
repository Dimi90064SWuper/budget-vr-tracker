"""
Tests for tracking modules.
"""

import numpy as np
import pytest
from tracker.coordinate_fusion import fix_rotation_matrix


def test_fix_rotation_matrix_positive_det():
    """Test that fixed matrix has positive determinant."""
    R = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    R_fixed = fix_rotation_matrix(R)
    assert np.linalg.det(R_fixed) > 0


def test_fix_rotation_matrix_negative_det():
    """Test fixing matrix with negative determinant."""
    R = np.array([[1, 0, 0], [0, 1, 0], [0, 0, -1]])  # det = -1
    R_fixed = fix_rotation_matrix(R)
    assert np.linalg.det(R_fixed) > 0


def test_fix_rotation_matrix_orthogonal():
    """Test that fixed matrix is orthogonal."""
    R = np.array([[1, 0, 0], [0, 0.8, -0.6], [0, 0.6, 0.8]])
    R_fixed = fix_rotation_matrix(R)
    # R @ R.T should be identity
    identity = R_fixed @ R_fixed.T
    np.testing.assert_array_almost_equal(identity, np.eye(3), decimal=5)
