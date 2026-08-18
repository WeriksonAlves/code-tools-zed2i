# v0.1 ZED2i Basic Validation

## Objective

Validate the first functional version of the `tools_zed2i` ROS 2 Python package.

The validation checks whether the package can:

- Load the YAML configuration
- Select stream presets
- Subscribe to ZED2i streams
- Relay configured topics
- Publish text diagnostics
- Publish structured ROS 2 diagnostics
- Provide an internal sensor snapshot API
- Pass unit tests and static checks

---

## Environment

- Operating system: Ubuntu 22.04
- ROS version: ROS 2 Humble
- Camera: ZED2i
- ZED ROS 2 wrapper: enabled
- Package: `tools_zed2i`
- Repository: `code-tools-zed2i`

---

## Validated Streams

The following streams were validated using the `mapping` preset:

- Left image
- Right image
- Disparity image
- IMU
- Registered point cloud

---

## Validation Commands

### Build

```bash
cd ~/ufv/GitHub/code-tools-zed2i/software

source /opt/ros/humble/setup.bash
colcon build --symlink-install

source install/setup.bash
```

### Static checks and tests

```bash
ruff check tools_zed2i test
python3 -m pytest test
python3 -m compileall tools_zed2i
```

### Runtime test

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

### Diagnostics topic

```bash
ros2 topic echo /tools_zed2i/diagnostics --once
```

---

## Expected Behavior

When the ZED ROS 2 wrapper is not running, all configured streams should report:

```text
NO_DATA
```

When the ZED ROS 2 wrapper is running, all configured streams should report:

```text
OK
```

---

## Observed Runtime Behavior

The node successfully received and monitored all configured streams.

Observed approximate stream rates:

```text
left_image   ≈ 10 Hz
right_image  ≈ 10–11 Hz
disparity    ≈ 10–11 Hz
imu          ≈ 100 Hz
point_cloud  ≈ 6–8 Hz
```

The registered point cloud stream showed a lower rate than the image and IMU
streams, which is expected due to the higher computational cost of point cloud
generation and publication.

---

## Test Result

The package passed:

* ROS 2 package build
* Ruff static checks
* Unit tests
* Python compile check
* Runtime test without active ZED streams
* Runtime test with active ZED streams
* Structured diagnostics topic validation

---

## Status

Passed.
