"""Agentic action execution — perform actions based on visual perception.

Executes: click, type, scroll, hotkey, and other mouse/keyboard actions.
Upgraded to World-Class human-like simulation.
"""

import logging
import time
import random
import math

logger = logging.getLogger(__name__)


class ActionExecutor:
    """Execute mouse and keyboard actions with world-class human-like simulation."""

    def __init__(self):
        self._pyautogui = None
        self.action_count = 0
        self.last_action = None

    def _init(self):
        if self._pyautogui is None:
            try:
                import pyautogui

                pyautogui.FAILSAFE = True  # Move mouse to corner to abort
                pyautogui.PAUSE = 0.1  # Reduced base pause for smoother fluid chaining
                self._pyautogui = pyautogui
                logger.info("Action executor initialized (pyautogui with human-like features)")
            except ImportError:
                raise ImportError("pyautogui not installed. Run: pip install pyautogui")

    def _human_delay(self, min_time=0.03, max_time=0.1):
        """Introduce a slight human-like delay."""
        time.sleep(random.uniform(min_time, max_time))

    def _calculate_duration(self, current_pos, target_x, target_y):
        """Calculate dynamic duration based on distance (Fitts's Law approximation)."""
        dist = math.hypot(target_x - current_pos[0], target_y - current_pos[1])
        base_speed = random.uniform(800, 1400)  # pixels per second (variable human speed)
        return min(max(dist / base_speed, 0.2), 1.5)  # clamp between 0.2s and 1.5s

    def click(self, x=None, y=None, button="left"):
        """Click at position with human-like mechanics."""
        self._init()
        try:
            if x is not None and y is not None:
                self.move(x, y)
                self._human_delay(0.05, 0.1)
                
            self._pyautogui.mouseDown(button=button)
            self._human_delay(0.02, 0.08)  # Hold duration naturally varies
            self._pyautogui.mouseUp(button=button)
            
            self._log("click", f"({x},{y}) {button}")
            return True
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return False

    def double_click(self, x=None, y=None):
        """Double-click at position with natural timing."""
        self._init()
        try:
            if x is not None and y is not None:
                self.move(x, y)
                self._human_delay(0.05, 0.1)
                
            self.click(button="left")
            self._human_delay(0.04, 0.09)  # Gap between first and second click
            self.click(button="left")
            
            self._log("double_click", f"({x},{y})")
            return True
        except Exception as e:
            logger.error(f"Double-click failed: {e}")
            return False

    def type_text(self, text, base_interval=0.05):
        """Type text with varying, human-like keystroke intervals."""
        self._init()
        try:
            for char in text:
                # Add random variation to typing speed to simulate bursts and pauses
                variation = random.uniform(-0.02, 0.05)
                interval = max(0.01, base_interval + variation)
                
                if char.isascii():
                    self._pyautogui.typewrite(char)
                else:
                    self._pyautogui.write(char)
                    
                time.sleep(interval)
                
            self._log("type", f"'{text[:30]}...'" if len(text) > 30 else f"'{text}'")
            return True
        except Exception as e:
            logger.error(f"Type failed: {e}")
            return False

    def press(self, key):
        """Press a single key naturally."""
        self._init()
        try:
            self._pyautogui.keyDown(key)
            self._human_delay(0.03, 0.08)
            self._pyautogui.keyUp(key)
            self._log("press", key)
            return True
        except Exception as e:
            logger.error(f"Press failed: {e}")
            return False

    def hotkey(self, *keys):
        """Press a key combination naturally."""
        self._init()
        try:
            # Press down in sequence
            for key in keys:
                self._pyautogui.keyDown(key)
                self._human_delay(0.02, 0.06)
            
            self._human_delay(0.05, 0.1)
            
            # Release in reverse sequence
            for key in reversed(keys):
                self._pyautogui.keyUp(key)
                self._human_delay(0.02, 0.06)
                
            self._log("hotkey", "+".join(keys))
            return True
        except Exception as e:
            logger.error(f"Hotkey failed: {e}")
            return False

    def scroll(self, clicks, x=None, y=None):
        """Scroll at position naturally in chunked bursts."""
        self._init()
        try:
            if x is not None and y is not None:
                self.move(x, y)
                self._human_delay(0.1, 0.2)
                
            # Break scroll into smaller, uneven chunks for realism
            steps = abs(clicks)
            direction = 1 if clicks > 0 else -1
            
            while steps > 0:
                chunk = min(random.randint(1, max(3, steps // 2)), steps)
                self._pyautogui.scroll(chunk * direction)
                steps -= chunk
                self._human_delay(0.02, 0.08)
                
            self._log("scroll", f"{clicks} clicks")
            return True
        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return False

    def move(self, x, y, duration=None):
        """Move mouse to position with ease-in-out and dynamic duration."""
        self._init()
        try:
            current_pos = self.get_mouse_position()
            
            # Add slight target jitter to avoid perfect mathematical pixel targeting
            target_x = int(x + random.randint(-2, 2))
            target_y = int(y + random.randint(-2, 2))
            
            if duration is None:
                duration = self._calculate_duration(current_pos, target_x, target_y)
                
            # Easing function for natural acceleration and deceleration
            self._pyautogui.moveTo(
                target_x, 
                target_y, 
                duration=duration, 
                tween=self._pyautogui.easeInOutQuad
            )
            
            self._log("move", f"({x},{y})")
            return True
        except Exception as e:
            logger.error(f"Move failed: {e}")
            return False

    def get_mouse_position(self):
        """Get current mouse position."""
        self._init()
        return self._pyautogui.position()

    def _log(self, action_type, detail):
        self.action_count += 1
        self.last_action = {
            "type": action_type,
            "detail": detail,
            "time": time.time(),
        }

    def get_state(self):
        return {
            "actions": self.action_count,
            "last_action": self.last_action,
        }
