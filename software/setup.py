"""Package setup configuration for tools_zed2i."""

from __future__ import annotations

from glob import glob
from pathlib import Path

from setuptools import find_packages, setup


PACKAGE_NAME = "tools_zed2i"
PACKAGE_VERSION = "0.13.0"


def get_data_files() -> list[tuple[str, list[str]]]:
    """Return package data files installed by ament_python."""
    return [
        (
            "share/ament_index/resource_index/packages",
            [f"resource/{PACKAGE_NAME}"],
        ),
        (
            f"share/{PACKAGE_NAME}",
            ["package.xml"],
        ),
        (
            f"share/{PACKAGE_NAME}/launch",
            glob("launch/*.launch.py"),
        ),
        (
            f"share/{PACKAGE_NAME}/config",
            glob("config/*.yaml"),
        ),
    ]


def get_long_description() -> str:
    """Return the package long description from README when available."""
    readme_path = Path("README.md")

    if not readme_path.exists():
        return "Modular ROS 2 Python package for ZED2i camera integration."

    return readme_path.read_text(encoding="utf-8")


setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    packages=find_packages(exclude=["test", "test.*"]),
    data_files=get_data_files(),
    install_requires=[
        "setuptools",
        "PyYAML",
        "numpy",
    ],
    extras_require={
        "open3d": [
            "open3d==0.19.0",
        ],
    },
    zip_safe=True,
    maintainer="Werikson Alves",
    maintainer_email="werikson.alves@ufv.br",
    description=(
        "Modular ROS 2 Python package for ZED2i camera integration, "
        "stream diagnostics, point cloud preprocessing, and dataset tools."
    ),
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    license="MIT",
    entry_points={
        "console_scripts": [
            "zed2i_node = tools_zed2i.infrastructure.ros2.zed2i_node:main",
            (
                "zed2i_dataset_recorder_node = "
                "tools_zed2i.infrastructure.ros2.dataset_recorder_node:main"
            ),
            "inspect_zed2i_dataset = tools_zed2i.scripts.inspect_dataset:main",
            "export_zed2i_dataset = tools_zed2i.scripts.export_dataset:main",
        ],
    },
)
