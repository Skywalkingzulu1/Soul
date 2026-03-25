import time
import subprocess
from soul.agentic.act import ActionExecutor

def control_main_browser():
    print("Initializing World-Class Desktop Controls...")
    executor = ActionExecutor()
    executor._init()
    
    print("\n1. Opening main browser to Twitter...")
    # Open the default web browser to the Twitter login page
    # This relies on the OS default browser configuration
    subprocess.Popen(['cmd', '/c', 'start', 'https://twitter.com/login'])
    
    # Wait for the browser and page to load
    print("Waiting for browser to load (10 seconds)...")
    time.sleep(10)
    
    print("\n2. Entering Username...")
    # Assuming the cursor is focused on the username field after load, or we press Tab to reach it
    # We will try typing directly first, if that fails, a manual click might be needed in a real robust setup
    executor.type_text("ever mlaudzi", base_interval=0.08)
    time.sleep(1.5)
    
    # Press Enter to proceed to password
    executor.press('enter')
    
    print("Waiting for password field (3 seconds)...")
    time.sleep(3)
    
    print("\n[NOTE] Not entering password to maintain security. Simulating human pause...")
    time.sleep(3)
    
    # Normally we would type password here and press enter
    
    print("\n3. Scrolling around to simulate reading...")
    # Move mouse to the center of the screen to ensure scroll works on the page
    executor.move(960, 540) # Approximate center of a 1080p screen
    time.sleep(1)
    
    print("Scrolling down...")
    executor.scroll(-800)
    time.sleep(2)
    
    print("Scrolling down more...")
    executor.scroll(-1200)
    time.sleep(3)
    
    print("Scrolling up...")
    executor.scroll(600)
    
    print("\nTest complete! Browser left open.")

if __name__ == "__main__":
    control_main_browser()
