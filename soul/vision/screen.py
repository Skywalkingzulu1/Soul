"""Screen capture module — captures the user's screen via mss.

Lightweight, fast, no webcam needed. Captures screen as numpy arrays
for OCR and visual analysis.
"""

import logging
import time
import numpy as np

logger = logging.getLogger(__name__)


class ScreenCapture:
    """Capture screen frames for visual perception."""

    def __init__(self) -> None:
        self._mss = None
        self._monitor = None
        self._last_capture = None
        self._last_capture_time = 0
        self.capture_count = 0

    def _init_mss(self) -> None:
        if self._mss is None:
            try:
                import mss

                self._mss = mss.mss()
                self._monitor = self._mss.monitors[1]  # Primary monitor
                logger.info(
                    f"Screen capture initialized: {self._monitor['width']}x{self._monitor['height']}"
                )
            except ImportError:
                raise ImportError("mss not installed. Run: pip install mss")
            except Exception as e:
                raise RuntimeError(f"Screen capture init failed: {e}")

    def capture(self, region=None) -> None:
        """Capture current screen as numpy array.

        Args:
            region: Optional (x, y, width, height) tuple for partial capture

        Returns:
            numpy array (height, width, 3) in BGR format (OpenCV compatible)
        """
        self._init_mss()

        try:
            if region:
                monitor = {
                    "left": region[0],
                    "top": region[1],
                    "width": region[2],
                    "height": region[3],
                }
            else:
                monitor = self._monitor

            screenshot = self._mss.grab(monitor)
            img = np.array(screenshot)  # BGRA
            img = img[:, :, :3]  # Drop alpha channel → BGR
            img = img[:, :, ::-1]  # BGR → RGB

            self._last_capture = img
            self._last_capture_time = time.time()
            self.capture_count += 1

            return img

        except Exception as e:
            logger.error(f"Screen capture failed: {e}")
            return None

    def capture_to_file(self, path="screenshots/screen_capture.png") -> None:
        """Capture and save to file."""
        import cv2

        img = self.capture()
        if img is not None:
            import os

            os.makedirs(os.path.dirname(path), exist_ok=True)
            cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            return path
        return None

    def get_screen_size(self) -> None:
        """Get screen dimensions."""
        self._init_mss()
        return self._monitor["width"], self._monitor["height"]

    def get_state(self) -> None:
        return {
            "screen_size": self.get_screen_size() if self._mss else None,
            "captures": self.capture_count,
            "last_capture_age": time.time() - self._last_capture_time
            if self._last_capture_time
            else None,
        }
