from setuptools import find_packages, setup
from glob import glob
from os.path import join

package_name = "tools_zed2i"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["tests"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (join("share", package_name, "config"), glob("config/*.yaml")),
        (join("share", package_name, "launch"), glob("launch/*.py")),
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
        ],
    },
)