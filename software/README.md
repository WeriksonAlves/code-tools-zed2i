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

### Optional Open3D Environment

For Open3D-based processing, it is recommended to use a virtual environment
with access to system ROS 2 packages:

```bash
cd ~/ufv/GitHub/code-tools-zed2i

python3 -m venv .venv --system-site-packages
source .venv/bin/activate
export PYTHONNOUSERSITE=1

python3 -m pip install -r software/requirements-open3d.txt
```

Recommended activation order:
```bash
cd ~/ufv/GitHub/code-tools-zed2i/software

source /opt/ros/humble/setup.bash
source ../.venv/bin/activate
export PYTHONNOUSERSITE=1
source install/setup.bash
```

The file `requirements-open3d.txt` pins compatible versions of NumPy, SciPy, scikit-learn, setuptools, and Open3D to avoid conflicts with ROS 2 Humble and `colcon-core`.

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

## Frame Conversion Utilities

The package provides optional conversion utilities for image-based streams.

These utilities are intentionally not executed inside the main ROS 2 callbacks,
to keep the relay path lightweight.

Available conversions:

```text
sensor_msgs/msg/Image -> numpy.ndarray
sensor_msgs/msg/Image -> OpenCV-compatible image
stereo_msgs/msg/DisparityImage -> numpy.ndarray
````

Example:

```python
from tools_zed2i.application.snapshot_converter import SnapshotConverter

converter = SnapshotConverter()
converted_snapshot = converter.convert_images_to_bgr(snapshot)

left_image = converted_snapshot.left_image
right_image = converted_snapshot.right_image
disparity = converted_snapshot.disparity
```

Required system packages:

```bash
sudo apt install python3-opencv ros-humble-cv-bridge
```

---

## Open3D Conversion Utilities

The package provides optional Open3D conversion utilities for point cloud
processing.

Open3D is treated as an optional dependency. The base package can be imported
and used without Open3D installed.

Supported conversions:

```text
numpy.ndarray Nx3 -> open3d.geometry.PointCloud
sensor_msgs/msg/PointCloud2 -> open3d.geometry.PointCloud
```

Install optional dependency:
```python
python3 -m pip install open3d
```

Example:
```python
from tools_zed2i.infrastructure.converters.open3d_converter import Open3DConverter

converter = Open3DConverter()
open3d_cloud = converter.xyz_array_to_open3d(xyz_points)
```

Snapshot conversion example:
```python
converted_snapshot = snapshot_converter.convert_all_available(
    snapshot,
    include_open3d=True,
)

open3d_cloud = converted_snapshot.point_cloud_open3d
```

---

## Point Cloud Processing Utilities

The package provides basic Open3D-based point cloud processing utilities.

Available operations:

```text
voxel downsampling
statistical outlier removal
radius outlier removal
plane segmentation with RANSAC
basic preprocessing for mapping
```

Example:

```python
from tools_zed2i.application.pointcloud_processor import Open3DPointCloudProcessor

processor = Open3DPointCloudProcessor()

filtered_cloud = processor.preprocess_for_mapping(
    point_cloud=open3d_cloud,
    voxel_size=0.05,
    nb_neighbors=30,
    std_ratio=2.0,
)

plane_result = processor.segment_plane(
    filtered_cloud,
    distance_threshold=0.05,
    ransac_n=3,
    num_iterations=1000,
)

ground_plane = plane_result.inlier_cloud
remaining_cloud = plane_result.outlier_cloud
```

These utilities are intended for experimental 3D mapping pipelines and should
be tuned according to sensor resolution, scene scale, and terrain structure.

---

## Mapping Preprocessing Pipeline

The package provides a reusable preprocessing pipeline for 3D mapping
experiments.

The pipeline combines:

```text
SensorSnapshot
PointCloud2 conversion
Open3D point cloud conversion
voxel downsampling
statistical outlier removal
optional RANSAC plane segmentation
```

Example:

```python
from tools_zed2i.application.mapping_pipeline import (
    MappingPreprocessingConfig,
    MappingPreprocessingPipeline,
)

pipeline = MappingPreprocessingPipeline()

result = pipeline.run_from_snapshot(
    snapshot=snapshot,
    config=MappingPreprocessingConfig(
        voxel_size=0.05,
        nb_neighbors=30,
        std_ratio=2.0,
        enable_plane_segmentation=True,
        plane_distance_threshold=0.05,
        plane_ransac_n=3,
        plane_num_iterations=1000,
    ),
)

preprocessed_cloud = result.preprocessed_cloud

if result.has_plane_segmentation():
    ground_candidate = result.plane_segmentation.inlier_cloud
    remaining_cloud = result.plane_segmentation.outlier_cloud
```

This pipeline is intended as a lightweight experimental entry point for
terrain mapping, planar segmentation, and future temporal tracking routines.

---

## Dataset Recording API

The package provides a simple dataset recording API for saving available sensor
snapshot streams to disk.

Supported outputs:

```text
left image    -> PNG
right image   -> PNG
disparity     -> NPY
point cloud   -> NPY
metadata      -> JSON
```

Default layout:

```text
dataset_root/
└── sequence_name/
    ├── images/
    │   ├── left/
    │   └── right/
    ├── disparity/
    ├── pointclouds/
    └── metadata/
```

Example:

```python
from pathlib import Path

from from tools_zed2i.application.dataset.models.dataset_config import DatasetRecordingConfig
from tools_zed2i.application.dataset.snapshot_recorder import SnapshotDatasetRecorder

config = DatasetRecordingConfig(
    dataset_root=Path("datasets"),
    sequence_name="sequence_test",
)

recorder = SnapshotDatasetRecorder(config=config)

saved_paths = recorder.record_snapshot(snapshot)
```

The first version records the available data in a `SensorSnapshot`. It does not
perform temporal synchronization across topics yet.

---

## Dataset Recorder ROS 2 Node

The package provides a ROS 2 node for periodically recording available ZED2i
sensor snapshots to disk.

Executable:

```text
zed2i_dataset_recorder_node
```

Example:

```bash
cd ~/ufv/GitHub/code-tools-zed2i/software

source /opt/ros/humble/setup.bash
source ../.venv/bin/activate
export PYTHONNOUSERSITE=1
source install/setup.bash

ros2 run tools_zed2i zed2i_dataset_recorder_node --ros-args \
  -p config_path:=$(pwd)/config/zed2i.yaml \
  -p dataset_root:=$(pwd)/datasets \
  -p sequence_name:=test_sequence \
  -p recording_period_sec:=1.0
```

The node internally runs the ZED2i stream reader and periodically records the
latest available `SensorSnapshot`.

Initial behavior:

```text
ZED2i streams -> SensorSnapshot -> DatasetRecordingAPI -> dataset folder
```

This first node version records periodically. It does not yet provide start/stop
services.

---

### Dataset Recorder Services

The dataset recorder node provides ROS 2 services for controlling recording at
runtime.

Available services:

```text
/tools_zed2i_dataset_recorder_node/start_recording
/tools_zed2i_dataset_recorder_node/stop_recording
/tools_zed2i_dataset_recorder_node/record_once
```

Service type:

```text
std_srvs/srv/Trigger
```

Start periodic recording:

```bash
ros2 service call \
  /tools_zed2i_dataset_recorder_node/start_recording \
  std_srvs/srv/Trigger
```

Stop periodic recording:

```bash
ros2 service call \
  /tools_zed2i_dataset_recorder_node/stop_recording \
  std_srvs/srv/Trigger
```

Record a single snapshot:

```bash
ros2 service call \
  /tools_zed2i_dataset_recorder_node/record_once \
  std_srvs/srv/Trigger
```

To start the node with periodic recording disabled:

```bash
ros2 run tools_zed2i zed2i_dataset_recorder_node --ros-args \
  -p config_path:=$(pwd)/config/zed2i.yaml \
  -p dataset_root:=$(pwd)/datasets \
  -p sequence_name:=manual_recording_test \
  -p recording_period_sec:=1.0 \
  -p recording_enabled:=false
```

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

## Dataset Inspection Tools

The package provides a command-line tool for inspecting datasets recorded with
the ZED2i dataset recorder.

Executable:

```text
inspect_zed2i_dataset
```

Example:

```bash
inspect_zed2i_dataset datasets/zed2i_real_service_test
```

Generated reports:

```text
datasets/zed2i_real_service_test/inspection/inspection_summary.json
datasets/zed2i_real_service_test/inspection/inspection_report.md
```

The inspection tool checks:

```text
sample count
missing files
left/right image shape
disparity shape
point cloud shape
point count
metadata validity
```

Example output:

```text
Dataset path: datasets/zed2i_real_service_test
Total samples: 18
Complete samples: 18
Incomplete samples: 0
Total point count: ...
Average point count: ...
```

---

## Dataset Manifest

Recorded datasets include a `manifest.json` file at the sequence root.

Example:

```text
dataset_root/
└── sequence_name/
    ├── manifest.json
    ├── images/
    ├── disparity/
    ├── pointclouds/
    ├── metadata/
    └── inspection/
```

The manifest stores:

manifest version
sequence name
creation timestamp
recording configuration
enabled streams
expected dataset layout
inspection summary, when available

When inspect_zed2i_dataset is executed, the manifest is updated with a compact
inspection summary if manifest.json exists.


---

## Dataset Export Tools

The package provides a command-line tool for exporting consolidated dataset
metadata and reports.

Executable:

```text
export_zed2i_dataset
```

Example:
```
ros2 run tools_zed2i export_zed2i_dataset datasets/zed2i_sequence
```

Generated files:
```
datasets/zed2i_sequence/exports/
├── samples.csv
├── summary.json
├── summary.md
└── manifest_snapshot.json
```

The export tool consolidates:
```
sample IDs
sample completeness
image shapes
disparity shapes
point cloud shapes
point counts
missing files
inspection errors
manifest snapshot, when available
```

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