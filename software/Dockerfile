# Development container for tools_zed2i.
#
# This Dockerfile provides a minimal ROS 2 Humble environment for static checks,
# package builds, and unit tests. Hardware access to the ZED2i camera and ZED SDK
# integration may require additional host-specific configuration.

FROM ros:humble-ros-base-jammy

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    python3-opencv \
    python3-yaml \
    ros-humble-cv-bridge \
    ros-humble-diagnostic-msgs \
    ros-humble-sensor-msgs \
    ros-humble-stereo-msgs \
    ros-humble-std-srvs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/code-tools-zed2i/software

COPY . /workspace/code-tools-zed2i/software

RUN python3 -m pip install --no-cache-dir \
    pytest \
    ruff \
    numpy==1.26.4 \
    PyYAML

SHELL ["/bin/bash", "-c"]

CMD source /opt/ros/humble/setup.bash && \
    colcon build --symlink-install && \
    source install/setup.bash && \
    ruff check tools_zed2i test && \
    python3 -m pytest test
