"""System awareness — the soul knows its own capabilities and limitations."""

import platform
import sys
import os


class SystemInfo:
    """Self-awareness of hardware, software, capabilities, and limitations."""

    def __init__(self) -> None:
        self.model = "gpt-oss:120b-cloud"
        self.model_params = "116.8 billion"
        self.embedding_model = "nomic-embed-text"
        self.hardware = self._detect_hardware()
        self.capabilities = self._list_capabilities()
        self.limitations = self._list_limitations()

    def _detect_hardware(self) -> None:
        info = {
            "platform": platform.system(),
            "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "arch": platform.machine(),
        }
        try:
            import psutil

            info["ram_gb"] = round(psutil.virtual_memory().total / (1024**3), 1)
            info["cpu_cores"] = psutil.cpu_count(logical=False)
            info["cpu_threads"] = psutil.cpu_count(logical=True)
        except ImportError:
            info["ram_gb"] = "unknown"
            info["cpu_cores"] = "unknown"
            info["cpu_threads"] = "unknown"

        # Check for GPU
        try:
            import subprocess

            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                info["gpu"] = result.stdout.strip()
            else:
                info["gpu"] = "none (CPU only)"
        except Exception:
            info["gpu"] = "none (CPU only)"

        return info

    def _list_capabilities(self) -> None:
        return {
            "reasoning": "Chain-of-thought, debate, task decomposition (120B model)",
            "memory": "Persistent SQLite + ChromaDB semantic search (BGE-M3 embeddings)",
            "web_search": "DuckDuckGo search",
            "code_execution": "Sandboxed Python subprocess",
            "browser": "AI browser automation (browser-use + 120B model)",
            "email_send": "Gmail SMTP for sending emails",
            "email_create": "mail.tm disposable email creation for signups",
            "email_verify": "Auto-poll inbox, extract verification codes and links",
            "captcha": "CAPTCHA detection, pause for manual solve, auto-continue",
            "form_filling": "Smart form analysis and filling with human-like typing",
            "session_mgmt": "Save/load browser sessions (cookies, localStorage)",
            "signup_flow": "Autonomous website signup (email + form + verification + session)",
            "reflection": "Self-critique and meta-reflection",
            "identity": "Digital twin of Andile Sizophila Mchunu",
            "time_awareness": "Knows current time, session duration, time of day",
            "codebase_tools": "glob, grep, read_file, write_file, ls - like Gemini CLI",
            "plan_mode": "/plan command shows execution plan without running",
            "yolo_mode": "ANDILE_YOLO=1 env var auto-approves all actions",
            "mcp_support": "Connect to MCP servers for extended tools",
        }

    def _list_limitations(self) -> None:
        return {
            "model_size": "116.8B parameters — large model with strong reasoning",
            "inference": "Remote GPU inference via Ollama — fast responses",
            "context_window": "128K context window — can hold long conversations",
            "no_training": "Cannot learn new facts permanently (memory is session-based recall)",
            "no_real_time": "Cannot access real-time data without web search",
            "hallucination": "May occasionally generate incorrect information, verify important facts",
        }

    def get_context(self) -> None:
        """Return system awareness context for prompts."""
        lines = ["SYSTEM AWARENESS:"]
        lines.append(f"  Model: {self.model} ({self.model_params} parameters)")
        lines.append(
            f"  Hardware: CPU inference on {self.hardware.get('platform', 'unknown')}"
        )
        lines.append(f"  GPU: {self.hardware.get('gpu', 'unknown')}")
        lines.append("")
        lines.append("  You know the following about yourself:")
        for cap, desc in self.capabilities.items():
            lines.append(f"    - {cap}: {desc}")
        lines.append("")
        lines.append("  Your limitations:")
        for lim, desc in self.limitations.items():
            lines.append(f"    - {lim}: {desc}")
        lines.append("")
        lines.append(
            "  When you don't know something, SEARCH THE WEB rather than guessing."
        )
        lines.append("  When a task is too complex, DECOMPOSE it into smaller steps.")
        return "\n".join(lines)

    def get_tools_list(self, tools_registry=None) -> None:
        """Return available tools for prompts."""
        lines = ["AVAILABLE TOOLS:"]
        lines.append(
            "  - search: DuckDuckGo web search. Use when you need current information or don't know something."
        )
        lines.append(
            "  - code: Execute Python code. Use for calculations, data processing, or verification."
        )
        lines.append(
            "  - browser: AI-powered web browsing. Use for complex web research."
        )
        lines.append("  - think: Chain-of-thought reasoning. Use for complex analysis.")
        lines.append(
            "  - debate: Multi-agent debate. Use for controversial or multi-perspective questions."
        )
        return "\n".join(lines)

    def summary(self) -> None:
        return (
            f"Model: {self.model} | Hardware: CPU | "
            f"GPU: {self.hardware.get('gpu', 'unknown')} | "
            f"RAM: {self.hardware.get('ram_gb', '?')}GB"
        )
