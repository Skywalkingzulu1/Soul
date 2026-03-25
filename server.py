import subprocess
import sys
import time
import requests
import logging

logging.basicConfig(level=logging.INFO, format="[SERVER] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434"
REQUIRED_MODELS = ["gpt-oss:120b-cloud", "nomic-embed-text"]


def is_ollama_running():
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def wait_for_server(timeout=120):
    logger.info("Waiting for ollama server...")
    start = time.time()
    while time.time() - start < timeout:
        if is_ollama_running():
            logger.info("Ollama server is ready.")
            return True
        time.sleep(2)
    logger.error(f"Ollama server did not start within {timeout}s")
    return False


def pull_models():
    for model in REQUIRED_MODELS:
        logger.info(f"Checking model: {model}")
        try:
            r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=10)
            tags = r.json().get("models", [])
            if any(m["name"].startswith(model.split(":")[0]) for m in tags):
                logger.info(f"  {model} already installed.")
                continue
        except Exception:
            pass

        logger.info(f"  Pulling {model}...")
        try:
            result = subprocess.run(
                ["ollama", "pull", model],
                capture_output=True,
                text=True,
                timeout=600,
            )
            if result.returncode == 0:
                logger.info(f"  {model} pulled successfully.")
            else:
                logger.error(f"  Failed to pull {model}: {result.stderr}")
        except subprocess.TimeoutExpired:
            logger.error(f"  Timeout pulling {model}")
        except FileNotFoundError:
            logger.error(
                "  'ollama' command not found. Install from https://ollama.com"
            )
            sys.exit(1)


def start_ollama():
    if is_ollama_running():
        logger.info("Ollama already running.")
    else:
        logger.info("Starting ollama serve...")
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if not wait_for_server():
            logger.error("Failed to start ollama server.")
            sys.exit(1)

    pull_models()
    logger.info("Ollama server ready with all models.")


if __name__ == "__main__":
    start_ollama()
