"""tools_zed2i package.

A modular Python/ROS 2 package for using the Stereolabs ZED2i camera in
robotics and 3D mapping experiments.

The package provides:

- configurable ROS 2 stream acquisition;
- stream health diagnostics;
- sensor snapshot access;
- image, disparity, PointCloud2, and Open3D conversion utilities;
- point cloud preprocessing utilities;
- dataset recording, inspection, manifest, and export tools.

The internal architecture follows a layered organization:

- ``domain`` contains technology-independent models and ports;
- ``application`` contains use-case services and processing workflows;
- ``infrastructure`` contains concrete adapters for ROS 2, OpenCV, Open3D,
  NumPy, and file-system I/O;
- ``scripts`` contains command-line entry points.
"""

__all__: list[str] = []
