import asyncio
import subprocess
import os
import socket
import shutil
from pathlib import Path
from soul.core.logger import setup_logger

logger = setup_logger(__name__)


class ResiliencyEngine:
    """The 'Immune System' of the Soul."""

    @staticmethod
    async def check_network() -> bool:
        """Verify internet connectivity via pinging 1.1.1.1."""
        try:
            # Connect to Cloudflare DNS
            socket.create_connection(("1.1.1.1", 53), timeout=3)
            return True
        except OSError:
            logger.warning("Network partition detected. System pausing...")
            return False

    @staticmethod
    async def check_ollama() -> bool:
        """Check if Ollama service is responsive."""
        try:
            import requests

            resp = requests.get("http://localhost:11434/api/tags", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    @staticmethod
    async def monitor_ollama() -> bool:
        """Ensure Ollama service is responsive. Restart if needed."""
        # Simple check: can we reach the API?
        if await ResiliencyEngine.check_ollama():
            return True

        logger.warning("Ollama service unreachable. Attempting restart...")

        # Try to find and kill existing Ollama processes
        try:
            # On Windows
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/F", "/IM", "ollama.exe"],
                    capture_output=True,
                    timeout=5,
                )
            else:
                # On Unix-like systems
                subprocess.run(
                    ["pkill", "-f", "ollama"], capture_output=True, timeout=5
                )
        except Exception as e:
            logger.debug(f"Could not kill existing Ollama: {e}")

        # Wait a moment for process to terminate
        await asyncio.sleep(2)

        # Start Ollama in background
        try:
            # Start without waiting (background process)
            if os.name == "nt":
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                )
            else:
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

            # Wait for startup
            for i in range(10):
                await asyncio.sleep(2)
                if await ResiliencyEngine.check_ollama():
                    logger.info("Ollama restarted successfully")
                    return True

            logger.error("Failed to restart Ollama after 20 seconds")
            return False

        except Exception as e:
            logger.error(f"Failed to start Ollama: {e}")
            return False

    @staticmethod
    def kill_zombie_browsers():
        """Kill orphaned Chromium/Playwright processes to save RAM."""
        count = 0
        try:
            import psutil

            for proc in psutil.process_iter(["name"]):
                if proc.info["name"] and any(
                    x in proc.info["name"].lower()
                    for x in ["chrome", "chromium", "playwright"]
                ):
                    try:
                        proc.terminate()
                        count += 1
                    except:
                        pass
        except ImportError:
            # Fallback for Windows if psutil not available
            try:
                if os.name == "nt":
                    subprocess.run(
                        ["taskkill", "/F", "/IM", "chrome.exe"],
                        capture_output=True,
                        timeout=5,
                    )
                    subprocess.run(
                        ["taskkill", "/F", "/IM", "msedge.exe"],
                        capture_output=True,
                        timeout=5,
                    )
            except:
                pass

        if count > 0:
            logger.info(f"Killed {count} orphaned browser processes.")
        return count

    @staticmethod
    async def self_heal_script(self, script_path: str, error_trace: str) -> bool:
        """Use the brain to fix a broken script. SAFELY - with backup and validation."""
        from soul.ollama_client import generate

        script_path = Path(script_path)

        if not script_path.exists():
            logger.error(f"Script not found: {script_path}")
            return False

        logger.warning(f"Self-healing triggered for: {script_path}")

        # Step 1: Create backup before any modifications
        backup_path = script_path.with_suffix(script_path.suffix + ".backup")
        try:
            shutil.copy2(script_path, backup_path)
            logger.info(f"Created backup at: {backup_path}")
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False

        # Step 2: Generate fix
        prompt = (
            f"The following Python script at {script_path} failed with this error:\n{error_trace}\n"
            "Please provide the corrected code for the entire file. "
            "Respond ONLY with valid Python code. "
            "Do NOT include any explanations or markdown."
        )

        try:
            response = generate(prompt=prompt)
            new_code = response.get("response", "")
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return False

        if not new_code:
            logger.error("LLM returned empty response")
            return False

        # Step 3: Validate the generated code before writing
        validation_errors = ResiliencyEngine._validate_python_code(new_code)
        if validation_errors:
            logger.error(f"Generated code validation failed: {validation_errors}")
            logger.info("Restoring backup...")
            try:
                shutil.copy2(backup_path, script_path)
            except:
                pass
            return False

        # Step 4: Write the fixed code
        try:
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(new_code)
            logger.info(f"Self-healed {script_path} successfully.")

            # Keep backup for a day
            return True
        except Exception as e:
            logger.error(f"Failed to write fixed code: {e}")
            # Restore backup
            try:
                shutil.copy2(backup_path, script_path)
            except:
                pass
            return False

    @staticmethod
    def _validate_python_code(code: str) -> str:
        """Basic validation of generated Python code."""
        import ast

        if not code:
            return "Empty code"

        # Must start with import or def/class
        code_stripped = code.strip()
        if not (
            code_stripped.startswith("import")
            or code_stripped.startswith("from")
            or code_stripped.startswith("def ")
            or code_stripped.startswith("class ")
        ):
            return "Code does not start with import, def, or class"

        # Try to parse as valid Python
        try:
            ast.parse(code)
        except SyntaxError as e:
            return f"Syntax error: {e}"

        return None  # No errors

    @staticmethod
    def get_system_health() -> dict:
        """Get current system health status."""
        return {
            "network": asyncio.run(ResiliencyEngine.check_network()),
            "ollama": asyncio.run(ResiliencyEngine.check_ollama()),
            "zombies_killed": ResiliencyEngine.kill_zombie_browsers(),
        }
