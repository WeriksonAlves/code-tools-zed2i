from setuptools import find_packages, setup
import os
from glob import glob
from os.path import join

package_name = "tools_zed2i"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["tests"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (
            os.path.join("share", package_name, "launch"),
            glob("launch/*.launch.py"),
        ),
        (
            os.path.join("share", package_name, "config"),
            glob("config/*.yaml"),
        ),
    ],
    install_requires=[
        "setuptools",
        "PyYAML",
        "numpy",
    ],
    zip_safe=True,
    maintainer="Werikson Alves",
    maintainer_email="werikson.alves@ufv.br",
    description="Reusable ROS 2 Python module for ZED2i camera integration.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "zed2i_node = tools_zed2i.infrastructure.ros2.zed2i_node:main",
            "zed2i_dataset_recorder_node = tools_zed2i.infrastructure.ros2.dataset_recorder_node:main",
            "inspect_zed2i_dataset = tools_zed2i.scripts.inspect_dataset:main",
            "export_zed2i_dataset = tools_zed2i.scripts.export_dataset:main",
        ],
    },
)
