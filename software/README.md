# tools_zed2i

Reusable ROS 2 Python package for ZED2i camera integration.

## Current Features

- ROS 2 Humble support
- YAML-based configuration
- Left image relay
- Right image relay
- Disparity image relay
- IMU relay
- Registered point cloud relay
- Basic stream diagnostics
- Unit tests for configuration and state classes

## Requirements

- Ubuntu 22.04
- ROS 2 Humble
- ZED SDK
- ZED ROS 2 Wrapper
- Python 3.10+

## Build

```bash
cd ~/ufv/GitHub/code-tools-zed2i/software

source /opt/ros/humble/setup.bash
colcon build --symlink-install

source install/setup.bash
````

## Run without ZED data

```bash
ros2 run tools_zed2i zed2i_node --ros-args \
  -p config_path:=$(pwd)/config/zed2i.yaml
```

Expected behavior:

```text
ZED2i diagnostics: left_image=NO_DATA, count=0 | right_image=NO_DATA, count=0 | disparity=NO_DATA, count=0 | imu=NO_DATA, count=0 | point_cloud=NO_DATA, count=0
```

## Run with ZED Wrapper

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

Expected behavior:

```text
left_image=OK
right_image=OK
disparity=OK
imu=OK
point_cloud=OK
```

## Check Topics

```bash
ros2 topic list | grep tools_zed2i
```

Expected topics:

```text
/tools_zed2i/left/image_rect_color
/tools_zed2i/right/image_rect_color
/tools_zed2i/disparity/disparity_image
/tools_zed2i/imu/data
/tools_zed2i/point_cloud/cloud_registered
```

## Tests

```bash
ruff check tools_zed2i test
python3 -m pytest test
python3 -m compileall tools_zed2i
```

## Current Scope

This version only relays and monitors ZED2i streams. It does not perform image conversion, dataset recording, point cloud conversion, calibration, synchronization, or ZED-Livox fusion yet.
