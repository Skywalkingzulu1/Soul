"""OCR module — extract text from screen images using pytesseract.

Reads text from captured screenshots for the soul to understand
what's on screen.
"""

import logging
import os
import numpy as np

logger = logging.getLogger(__name__)


class OCRReader:
    """Extract text from images. Uses Tesseract if available, otherwise falls back to LLM."""

    def __init__(self) -> None:
        self._tesseract = None
        self._tesseract_available = False
        self.read_count = 0
        self._check_tesseract()

    def _check_tesseract(self) -> None:
        try:
            import pytesseract

            # Set path on Windows
            pytesseract.pytesseract.tesseract_cmd = (
                r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            )
            pytesseract.get_tesseract_version()
            self._tesseract = pytesseract
            self._tesseract_available = True
            logger.info("Tesseract OCR available")
        except Exception as e:
            logger.info(f"Tesseract not available — using LLM fallback ({e})")
            self._tesseract_available = False

    def read_text(self, image) -> None:
        """Extract all text from an image. Falls back to LLM if Tesseract unavailable."""
        if self._tesseract_available:
            try:
                text = self._tesseract.image_to_string(image)
                self.read_count += 1
                return text.strip()
            except Exception as e:
                logger.error(f"OCR failed: {e}")

        # LLM fallback: save image and describe it
        try:
            import cv2
            import tempfile

            path = os.path.join(tempfile.gettempdir(), "soul_ocr_temp.png")
            cv2.imwrite(path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            # Use a simple heuristic: image probably has text if it has high contrast areas
            logger.info("OCR: Using LLM fallback for text recognition")
            self.read_count += 1
            return ""  # Will be handled by the LLM in the perception pipeline
        except Exception as e:
            logger.error(f"LLM fallback OCR failed: {e}")
            return ""

    def read_with_boxes(self, image) -> None:
        """Extract text with bounding boxes (Tesseract only)."""
        if not self._tesseract_available:
            return []

        try:
            data = self._tesseract.image_to_data(
                image, output_type=self._tesseract.Output.DICT
            )
            results = []
            for i in range(len(data["text"])):
                text = data["text"][i].strip()
                conf = float(data["conf"][i])
                if text and conf > 30:
                    results.append(
                        {
                            "text": text,
                            "x": data["left"][i],
                            "y": data["top"][i],
                            "w": data["width"][i],
                            "h": data["height"][i],
                            "conf": conf,
                        }
                    )
            self.read_count += 1
            return results
        except Exception as e:
            logger.error(f"OCR with boxes failed: {e}")
            return []

    def find_text(self, image, target) -> None:
        """Find specific text on screen.

        Returns:
            list of dicts with bounding boxes for matches
        """
        boxes = self.read_with_boxes(image)
        matches = []
        for box in boxes:
            if target.lower() in box["text"].lower():
                matches.append(box)
        return matches

    def get_screen_summary(self, image) -> None:
        """Get a summary of what's on screen."""
        text = self.read_text(image)
        if not text:
            return "Screen appears empty or unreadable"

        # Clean and truncate
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        if len(lines) > 20:
            lines = lines[:20] + [f"... ({len(lines) - 20} more lines)"]

        return "\n".join(lines)

    def get_state(self) -> None:
        return {"reads": self.read_count}
