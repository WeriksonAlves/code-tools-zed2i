# tools_zed2i

Reusable ROS 2 Python package for ZED2i camera integration.

This package provides a configurable and extensible interface for receiving,
monitoring, and relaying ZED2i sensor streams in ROS 2 Humble.

The current implementation is designed as a reusable software module for future
robotics and 3D mapping projects within the NERo ecosystem.

---

## Current Version Scope

The current version provides:

- ROS 2 Humble Python package
- YAML-based configuration
- Configurable stream presets
- Left image relay
- Right image relay
- Disparity image relay
- IMU relay
- Registered point cloud relay
- Text-based stream diagnostics
- Structured ROS 2 diagnostics using `diagnostic_msgs/msg/DiagnosticArray`
- Internal sensor snapshot API
- Unit tests for configuration, state, snapshot, and service layers

This version does not yet provide:

- OpenCV image conversion
- NumPy/Open3D point cloud conversion
- Dataset recording
- Temporal synchronization
- Calibration routines
- ZED-Livox fusion
- GUI or visualization interface

---

## Repository Context

This package is located inside the `software/` folder because the repository
follows the NERo robotics project template.

Recommended repository name:

```text
code-tools-zed2i
```

ROS 2 package name:

```text
tools_zed2i
```

Main executable:

```text
zed2i_node
```

---

## Requirements

* Ubuntu 22.04
* ROS 2 Humble
* Python 3.10+
* ZED SDK
* ZED ROS 2 Wrapper
* `rclpy`
* `sensor_msgs`
* `stereo_msgs`
* `diagnostic_msgs`
* `PyYAML`

---

## Build

From the `software/` directory:

```bash
cd ~/ufv/GitHub/code-tools-zed2i/software

source /opt/ros/humble/setup.bash
colcon build --symlink-install

source install/setup.bash
```

Check whether the package is visible:

```bash
ros2 pkg list | grep tools_zed2i
```

Check the executable:

```bash
ros2 pkg executables tools_zed2i
```

Expected result:

```text
tools_zed2i zed2i_node
```

---

## Configuration

The main configuration file is:

```text
config/zed2i.yaml
```

The active preset is selected through:

```yaml
active_preset: "mapping"
```

Available presets:

```yaml
minimal:
  left_image: true
  right_image: false
  disparity: false
  imu: true
  point_cloud: false

stereo:
  left_image: true
  right_image: true
  disparity: true
  imu: false
  point_cloud: false

mapping:
  left_image: true
  right_image: true
  disparity: true
  imu: true
  point_cloud: true

pointcloud_only:
  left_image: false
  right_image: false
  disparity: false
  imu: true
  point_cloud: true

full:
  left_image: true
  right_image: true
  disparity: true
  imu: true
  point_cloud: true
```

For 3D mapping experiments, the recommended preset is:

```yaml
active_preset: "mapping"
```

---

## Run Without Active ZED Streams

This test validates whether the node loads the YAML file and creates the
configured subscribers, publishers, and diagnostics.

```bash
cd ~/ufv/GitHub/code-tools-zed2i/software

source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run tools_zed2i zed2i_node --ros-args \
  -p config_path:=$(pwd)/config/zed2i.yaml
```

Expected diagnostic behavior:

```text
left_image=NO_DATA
right_image=NO_DATA
disparity=NO_DATA
imu=NO_DATA
point_cloud=NO_DATA
```

This is expected when the ZED ROS 2 wrapper is not running.

---

## Run With ZED ROS 2 Wrapper

Terminal 1:

```bash
source /opt/ros/humble/setup.bash
source ~/zed_ws/install/setup.bash

ros2 launch zed_wrapper zed_camera.launch.py camera_model:=zed2i
```

Terminal 2:

```bash
cd ~/ufv/GitHub/code-tools-zed2i/software

source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run tools_zed2i zed2i_node --ros-args \
  -p config_path:=$(pwd)/config/zed2i.yaml
```

Expected diagnostic behavior:

```text
left_image=OK
right_image=OK
disparity=OK
imu=OK
point_cloud=OK
```

---

## Output Topics

With the default `mapping` preset, the node relays the following topics:

```text
/tools_zed2i/left/image_rect_color
/tools_zed2i/right/image_rect_color
/tools_zed2i/disparity/disparity_image
/tools_zed2i/imu/data
/tools_zed2i/point_cloud/cloud_registered
/tools_zed2i/diagnostics
```

Check them with:

```bash
ros2 topic list | grep tools_zed2i
```

---

## Diagnostics

The node publishes structured diagnostics to:

```text
/tools_zed2i/diagnostics
```

Message type:

```text
diagnostic_msgs/msg/DiagnosticArray
```

Check one diagnostic message:

```bash
ros2 topic echo /tools_zed2i/diagnostics --once
```

Each stream reports:

* stream name
* status
* message count
* estimated frequency in Hz
* message age in seconds

Diagnostic state mapping:

```text
OK      -> DiagnosticStatus.OK
STALE   -> DiagnosticStatus.WARN
NO_DATA -> DiagnosticStatus.ERROR
```

---

## Sensor Snapshot API

The package provides an internal immutable snapshot object:

```python
from tools_zed2i.domain.snapshot import SensorSnapshot
```

The snapshot stores the latest available messages:

```python
snapshot.left_image
snapshot.right_image
snapshot.disparity
snapshot.imu
snapshot.point_cloud
```

It also provides helper methods:

```python
snapshot.has_left_image()
snapshot.has_right_image()
snapshot.has_disparity()
snapshot.has_imu()
snapshot.has_point_cloud()
snapshot.is_complete()
snapshot.available_streams()
```

This API is intended for future modules that will consume ZED2i data directly
without accessing the internal ROS 2 node cache.

---

## Tests

Run from the `software/` directory:

```bash
cd ~/ufv/GitHub/code-tools-zed2i/software

source /opt/ros/humble/setup.bash
source install/setup.bash

ruff check tools_zed2i test
python3 -m pytest test
python3 -m compileall tools_zed2i
```

Expected result:

```text
All checks passed
```

and all unit tests passing.

---

## Current Validation Summary

The package has been validated with a real ZED2i camera and the ZED ROS 2 wrapper.

Observed approximate stream rates:

```text
left_image   ≈ 10 Hz
right_image  ≈ 10–11 Hz
disparity    ≈ 10–11 Hz
imu          ≈ 100 Hz
point_cloud  ≈ 6–8 Hz
```

The point cloud frequency may vary depending on:

* ZED SDK configuration
* depth mode
* resolution
* point cloud generation cost
* host machine performance
* QoS behavior
* system load

---

## Development Notes

Generated ROS 2 build folders must not be committed:

```text
build/
install/
log/
```

The repository should only track source code, configuration files,
documentation, tests, launch files, and package metadata.

---

## Recommended Next Features

Suggested future branches:

```text
feature/frame-conversion-utils
feature/dataset-recording
feature/topic-synchronization
feature/zed-configuration-presets
feature/pointcloud-conversion-api
feature/zed-livox-fusion-preparation
```