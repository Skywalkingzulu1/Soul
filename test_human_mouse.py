import time
from soul.agentic.act import ActionExecutor

def test_world_class_desktop():
    print("Initializing World-Class Desktop Controls...")
    executor = ActionExecutor()
    executor._init()
    
    print("1. Moving mouse with human-like easing (Fitts's Law)...")
    executor.move(200, 200)
    time.sleep(0.5)
    executor.move(800, 600)
    time.sleep(0.5)
    executor.move(400, 300)
    
    print("\n2. Typing with natural cadence...")
    # Moving to center roughly to type
    executor.type_text("Hello! I am now typing like a real human being.", base_interval=0.03)
    
    print("\n3. Natural click and double-click...")
    executor.click(button="left")
    time.sleep(0.5)
    executor.double_click()
    
    print("\n4. Chunked, natural scrolling...")
    executor.scroll(-500)
    
    print("\nTest complete!")

if __name__ == "__main__":
    test_world_class_desktop()
