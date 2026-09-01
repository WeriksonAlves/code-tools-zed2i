"""ROS image conversion adapters for ZED2i streams.

This module contains infrastructure-level converters that transform ROS image
messages into NumPy/OpenCV-compatible arrays.
"""

from __future__ import annotations

import numpy as np
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
from stereo_msgs.msg import DisparityImage

BGR_ENCODING = "bgr8"
RGB_ENCODING = "rgb8"
MONO_ENCODING = "mono8"
PASSTHROUGH_ENCODING = "passthrough"


class ImageConversionError(RuntimeError):
    """Raised when a ROS image message cannot be converted."""


class RosImageConverter:
    """Converter for ROS image messages.

    This adapter wraps ``cv_bridge`` and exposes conversion methods used by the
    application layer. It is intentionally located in infrastructure because it
    depends on ROS message types and OpenCV-compatible conversions.
    """

    def __init__(self, bridge: CvBridge | None = None) -> None:
        """Initialize the converter.

        Args:
            bridge: Optional ``CvBridge`` instance, mainly useful for tests.
        """
        self._bridge = bridge or CvBridge()

    def image_to_cv2(
        self,
        image_message: Image,
        desired_encoding: str = PASSTHROUGH_ENCODING,
    ) -> np.ndarray:
        """Convert a ROS image message to an OpenCV-compatible array.

        Args:
            image_message: ROS ``sensor_msgs/Image`` message.
            desired_encoding: Target image encoding.

        Returns:
            Converted image as a NumPy array.

        Raises:
            ImageConversionError: If ``cv_bridge`` cannot convert the message.
        """
        try:
            converted_image = self._bridge.imgmsg_to_cv2(
                image_message,
                desired_encoding=desired_encoding,
            )
            return np.asarray(converted_image)
        except (CvBridgeError, TypeError, ValueError) as exception:
            raise ImageConversionError(
                f"Failed to convert ROS Image message: {exception}"
            ) from exception

    def left_image_to_bgr(self, image_message: Image) -> np.ndarray:
        """Convert a left image message to BGR format."""
        return self.image_to_cv2(
            image_message=image_message,
            desired_encoding=BGR_ENCODING,
        )

    def right_image_to_bgr(self, image_message: Image) -> np.ndarray:
        """Convert a right image message to BGR format."""
        return self.image_to_cv2(
            image_message=image_message,
            desired_encoding=BGR_ENCODING,
        )

    def image_to_rgb(self, image_message: Image) -> np.ndarray:
        """Convert an image message to RGB format."""
        return self.image_to_cv2(
            image_message=image_message,
            desired_encoding=RGB_ENCODING,
        )

    def image_to_mono(self, image_message: Image) -> np.ndarray:
        """Convert an image message to mono8 format."""
        return self.image_to_cv2(
            image_message=image_message,
            desired_encoding=MONO_ENCODING,
        )

    def disparity_to_array(
        self,
        disparity_message: DisparityImage,
    ) -> np.ndarray:
        """Convert a ROS disparity image message to a NumPy array.

        Args:
            disparity_message: ROS ``stereo_msgs/DisparityImage`` message.

        Returns:
            Disparity image as a NumPy array.

        Raises:
            ImageConversionError: If the disparity image cannot be converted.
        """
        try:
            disparity_array = self._bridge.imgmsg_to_cv2(
                disparity_message.image,
                desired_encoding=PASSTHROUGH_ENCODING,
            )
            return np.asarray(disparity_array)
        except (CvBridgeError, TypeError, ValueError) as exception:
            raise ImageConversionError(
                f"Failed to convert ROS DisparityImage message: {exception}"
            ) from exception
