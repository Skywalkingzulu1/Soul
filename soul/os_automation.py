import logging
import asyncio
import os

logger = logging.getLogger(__name__)

class OSAutomation:
    """Controls the operating system GUI (mouse, keyboard, screen) autonomously using world-class human simulation."""

    def __init__(self) -> None:
        try:
            from soul.agentic.act import ActionExecutor
            import pyautogui
            # Failsafe: moving mouse to corner of screen aborts the script
            pyautogui.FAILSAFE = True
            self.pg = pyautogui
            self.executor = ActionExecutor()
        except ImportError:
            self.pg = None
            self.executor = None
            logger.warning("pyautogui not installed. OS Automation disabled.")

    def execute(self, action, **kwargs) -> None:
        if not self.executor:
            return "Error: OS Automation is disabled. Install pyautogui."
        
        try:
            if action == "type":
                text = kwargs.get("text", "")
                interval = kwargs.get("interval", 0.05)
                self.executor.type_text(text, base_interval=interval)
                return f"Typed: '{text}' (Human-like)"
            
            elif action == "press":
                key = kwargs.get("key", "enter")
                self.executor.press(key)
                return f"Pressed key: '{key}' (Human-like)"
            
            elif action == "hotkey":
                keys = kwargs.get("keys", [])
                self.executor.hotkey(*keys)
                return f"Executed hotkey: {'+'.join(keys)} (Human-like)"
            
            elif action == "click":
                x = kwargs.get("x")
                y = kwargs.get("y")
                button = kwargs.get("button", "left")
                clicks = kwargs.get("clicks", 1)
                
                if clicks == 2:
                    self.executor.double_click(x=x, y=y)
                    return f"Double-clicked {button} at ({x}, {y}) (Human-like)"
                else:
                    for _ in range(clicks):
                        self.executor.click(x=x, y=y, button=button)
                    return f"Clicked {button} at ({x}, {y}) {clicks} time(s) (Human-like)."
            
            elif action == "move":
                x = kwargs.get("x", 0)
                y = kwargs.get("y", 0)
                duration = kwargs.get("duration", None)
                self.executor.move(x, y, duration=duration)
                return f"Moved mouse to ({x}, {y}) (Human-like Easing)."
            
            elif action == "screenshot":
                path = kwargs.get("path", "os_screenshot.png")
                self.pg.screenshot(path)
                return f"Screenshot saved to {path}."
            
            elif action == "screen_size":
                width, height = self.pg.size()
                return f"Screen resolution: {width}x{height}"
            
            else:
                return f"Unknown OS action: {action}"
                
        except Exception as e:
            logger.error(f"OS Automation error: {e}")
            return f"Failed to execute OS action '{action}': {str(e)}"
