"""Plane segmentation models and services for mapping pipelines.

This module currently exposes the plane segmentation result model used by the
Open3D point cloud processor. Future versions should move dedicated plane
segmentation services to this module, including multi-plane extraction,
temporal association, and semantic plane attributes.
"""

from tools_zed2i.application.pointcloud.pointcloud_processor import (
    PlaneSegmentationResult,
)

__all__ = ["PlaneSegmentationResult"]
