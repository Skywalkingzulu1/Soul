"""Visual perception pipeline — combines screen capture + OCR + analysis.

The soul's eyes: captures screen, reads text, understands what's happening.
"""

import logging
import time
import numpy as np

logger = logging.getLogger(__name__)


class Eyes:
    """Visual perception pipeline. Sees and understands the screen."""

    def __init__(self) -> None:
        self.screen = None
        self.ocr = None
        self.vision_log = []
        self._initialized = False

    def _init(self) -> None:
        if self._initialized:
            return
        try:
            from soul.vision.screen import ScreenCapture
            from soul.vision.ocr import OCRReader

            self.screen = ScreenCapture()
            self.ocr = OCRReader()
            self._initialized = True
            logger.info("Visual perception initialized")
        except Exception as e:
            logger.warning(f"Vision init failed: {e}")
            self._initialized = False

    def see(self) -> None:
        """Capture and analyze current screen.

        Returns:
            dict with: image, text, summary, timestamp
        """
        self._init()
        if not self._initialized:
            return {"error": "Vision not available", "text": "", "summary": ""}

        result = {
            "timestamp": time.time(),
            "image": None,
            "text": "",
            "summary": "",
            "text_boxes": [],
            "screen_size": None,
        }

        # Capture screen
        img = self.screen.capture()
        if img is None:
            result["error"] = "Screen capture failed"
            return result

        result["image"] = img
        result["screen_size"] = img.shape[:2][::-1]  # (width, height)

        # Read text
        try:
            result["text"] = self.ocr.read_text(img)
            result["summary"] = self.ocr.get_screen_summary(img)
            result["text_boxes"] = self.ocr.read_with_boxes(img)
        except Exception as e:
            result["error"] = f"OCR failed: {e}"

        # Log
        self.vision_log.append(
            {
                "timestamp": result["timestamp"],
                "summary": result["summary"][:100],
                "text_length": len(result["text"]),
            }
        )
        if len(self.vision_log) > 100:
            self.vision_log = self.vision_log[-50:]

        return result

    def find(self, text) -> None:
        """Find text on current screen."""
        self._init()
        if not self._initialized:
            return []

        img = self.screen.capture()
        if img is None:
            return []

        return self.ocr.find_text(img, text)

    def describe(self) -> None:
        """Get a text description of what's on screen."""
        vision = self.see()
        if "error" in vision:
            return f"Vision error: {vision['error']}"

        text = vision["text"]
        if not text:
            return "The screen appears to be empty or locked."

        lines = [l.strip() for l in text.split("\n") if l.strip()]
        return f"Screen shows {len(lines)} lines of text:\n" + "\n".join(lines[:10])

    def save_screenshot(self, path="screenshots/eyes_capture.png") -> None:
        """Save current screen to file."""
        self._init()
        if not self._initialized:
            return None
        return self.screen.capture_to_file(path)

    def get_state(self) -> None:
        self._init()
        state = {
            "initialized": self._initialized,
            "vision_log_entries": len(self.vision_log),
        }
        if self.screen:
            state.update(self.screen.get_state())
        if self.ocr:
            state.update(self.ocr.get_state())
        return state
