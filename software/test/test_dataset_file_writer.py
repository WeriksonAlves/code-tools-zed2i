from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from tools_zed2i.application.dataset.dataset_writer import DatasetFileWriter


def test_dataset_file_writer_saves_image(tmp_path: Path) -> None:
    writer = DatasetFileWriter()
    image = np.zeros((4, 4, 3), dtype=np.uint8)

    output_path = tmp_path / "image.png"

    writer.save_image(image=image, path=output_path)

    assert output_path.exists()


def test_dataset_file_writer_saves_array(tmp_path: Path) -> None:
    writer = DatasetFileWriter()
    array = np.ones((3, 3), dtype=np.float32)

    output_path = tmp_path / "array.npy"

    writer.save_array(array=array, path=output_path)

    assert output_path.exists()

    loaded_array = np.load(output_path)

    np.testing.assert_array_equal(loaded_array, array)


def test_dataset_file_writer_saves_metadata(tmp_path: Path) -> None:
    writer = DatasetFileWriter()

    metadata = {
        "sample_id": "sample_001",
        "available_streams": ["left_image", "point_cloud"],
    }

    output_path = tmp_path / "metadata.json"

    writer.save_metadata(metadata=metadata, path=output_path)

    assert output_path.exists()

    with output_path.open("r", encoding="utf-8") as file:
        loaded_metadata = json.load(file)

    assert loaded_metadata == metadata
