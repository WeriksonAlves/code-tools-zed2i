# Basic ZED2i Node Validation

## Date

2026-08-10

## Environment

- Ubuntu 22.04
- ROS 2 Humble
- ZED2i camera
- ZED ROS 2 Wrapper
- Package: tools_zed2i

## Test Objective

Validate that the `tools_zed2i_node` can subscribe to the ZED2i ROS 2 wrapper streams and relay the configured topics.

## Tested Streams

- Left image
- Right image
- Disparity image
- IMU
- Registered point cloud

## Result

The node successfully initialized all configured subscribers and relay publishers.

The diagnostics changed from `NO_DATA` to `OK` for all configured streams when the ZED wrapper was running.

## Status

Passed.
