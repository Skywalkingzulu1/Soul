import cv2
import sys
import os

# Add root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from soul.vision.ocr import OCRReader

def debug_screenshot(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    ocr = OCRReader()
    img = cv2.imread(path)
    if img is None:
        print(f"Failed to read image: {path}")
        return

    print(f"--- OCR RESULTS FOR {path} ---")
    text = ocr.read_text(img)
    print(text)
    
    print("\n--- BOXES ---")
    boxes = ocr.read_with_boxes(img)
    for box in boxes:
        print(f"[{box['conf']:.1f}] {box['text']} at ({box['x']}, {box['y']}, {box['w']}, {box['h']})")

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "screenshots/gmx_iteration_v3_state.png"
    debug_screenshot(path)
