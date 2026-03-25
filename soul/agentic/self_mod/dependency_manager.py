"""Dependency manager - handles package updates and compatibility."""

import subprocess
import logging
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

UPGRADE_MAPPINGS = {
    "ddgs": "duckduckgo-search",
    "requests": "httpx",
    "opencv-python": "opencv-python-headless",
}

RECOMMENDED_ADDITIONS = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "python-dotenv>=1.0.0",
    "pydantic-settings>=2.0.0",
    "tenacity>=8.0.0",
]


@dataclass
class DependencyUpdate:
    package: str
    current_version: Optional[str]
    new_version: Optional[str]
    action: str
    success: bool
    error: Optional[str] = None


class DependencyManager:
    """Manages package dependencies and updates."""

    def __init__(self, requirements_path: str = "requirements.txt"):
        self.requirements_path = Path(requirements_path)
        self.current_deps = {}
        self.updates: list[DependencyUpdate] = []

    def load_dependencies(self) -> dict:
        """Load current dependencies from requirements.txt."""
        if not self.requirements_path.exists():
            logger.warning(f"No requirements.txt found at {self.requirements_path}")
            return {}

        deps = {}
        with open(self.requirements_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    match = re.match(r"([a-zA-Z0-9_-]+)(>=|<=|==|>|<)?(.+)?", line)
                    if match:
                        pkg, op, ver = match.groups()
                        deps[pkg] = {"op": op or ">=", "version": ver or "latest"}

        self.current_deps = deps
        logger.info(f"Loaded {len(deps)} dependencies")
        return deps

    def check_updates(self) -> list[DependencyUpdate]:
        """Check for available updates."""
        logger.info("Checking for package updates...")
        updates = []

        for pkg in self.current_deps:
            try:
                result = subprocess.run(
                    ["pip", "index", "versions", pkg],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    latest = self._parse_latest_version(result.stdout)
                    current = self.current_deps[pkg].get("version")

                    if latest and latest != current:
                        updates.append(
                            DependencyUpdate(
                                package=pkg,
                                current_version=current,
                                new_version=latest,
                                action="upgrade",
                                success=True,
                            )
                        )
            except Exception as e:
                logger.debug(f"Could not check {pkg}: {e}")

        self.updates = updates
        return updates

    def _parse_latest_version(self, output: str) -> Optional[str]:
        """Parse latest version from pip index output."""
        lines = output.split("\n")
        for line in lines:
            if "Available versions:" in line or "LATEST:" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.replace(".", "").isdigit():
                        return part.strip(",")
        return None

    def apply_upgrades(self, dry_run: bool = False) -> list[DependencyUpdate]:
        """Apply available upgrades."""
        if not self.updates:
            self.check_updates()

        results = []

        for update in self.updates:
            if dry_run:
                logger.info(
                    f"[DRY RUN] Would upgrade {update.package}: {update.current_version} -> {update.new_version}"
                )
                results.append(update)
                continue

            try:
                result = subprocess.run(
                    [
                        "pip",
                        "install",
                        "--upgrade",
                        f"{update.package}>={update.new_version}",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

                if result.returncode == 0:
                    update.success = True
                    logger.info(f"Upgraded {update.package} to {update.new_version}")
                else:
                    update.success = False
                    update.error = result.stderr[:200]
                    logger.error(f"Failed to upgrade {update.package}: {update.error}")

                results.append(update)

            except Exception as e:
                update.success = False
                update.error = str(e)
                results.append(update)

        return results

    def add_recommended(self, dry_run: bool = False) -> list[DependencyUpdate]:
        """Add recommended missing packages."""
        results = []

        for pkg in RECOMMENDED_ADDITIONS:
            name = pkg.split(">=")[0]
            version = pkg.split(">=")[1] if ">=" in pkg else "latest"

            if name in self.current_deps:
                continue

            update = DependencyUpdate(
                package=name,
                current_version=None,
                new_version=version,
                action="add",
                success=True,
            )

            if not dry_run:
                try:
                    subprocess.run(
                        ["pip", "install", pkg], capture_output=True, timeout=60
                    )
                except Exception as e:
                    update.success = False
                    update.error = str(e)

            results.append(update)

        if not dry_run:
            self._update_requirements_file(results)

        return results

    def _update_requirements_file(self, updates: list[DependencyUpdate]):
        """Update requirements.txt with new packages."""
        lines = []

        for pkg, info in self.current_deps.items():
            if pkg in [u.package for u in updates if u.action == "add"]:
                continue

            version = info.get("version", "")
            op = info.get("op", ">=")
            lines.append(f"{pkg}{op}{version}" if version else pkg)

        for update in updates:
            if update.action == "add" and update.success:
                lines.append(f"{update.package}>={update.new_version}")

        with open(self.requirements_path, "w") as f:
            f.write("\n".join(lines) + "\n")

        logger.info(f"Updated {self.requirements_path}")

    def get_recommendations(self) -> dict:
        """Get recommendations for improvements."""
        recs = {
            "replace": [],
            "add": [],
            "upgrade": [],
        }

        for pkg, mapping in UPGRADE_MAPPINGS.items():
            if pkg in self.current_deps:
                recs["replace"].append({"from": pkg, "to": mapping})

        for pkg in RECOMMENDED_ADDITIONS:
            name = pkg.split(">=")[0]
            if name not in self.current_deps:
                recs["add"].append(pkg)

        for update in self.updates:
            recs["upgrade"].append(
                {
                    "package": update.package,
                    "from": update.current_version,
                    "to": update.new_version,
                }
            )

        return recs

    def apply_replacements(self, dry_run: bool = False) -> list[DependencyUpdate]:
        """Apply recommended package replacements."""
        results = []

        for pkg, new_pkg in UPGRADE_MAPPINGS.items():
            if pkg not in self.current_deps:
                continue

            if dry_run:
                logger.info(f"[DRY RUN] Would replace {pkg} with {new_pkg}")
                results.append(
                    DependencyUpdate(
                        package=pkg,
                        current_version=self.current_deps[pkg].get("version"),
                        new_version=new_pkg,
                        action="replace",
                        success=True,
                    )
                )
                continue

            try:
                subprocess.run(
                    ["pip", "install", new_pkg], capture_output=True, timeout=60
                )
                results.append(
                    DependencyUpdate(
                        package=pkg,
                        current_version=self.current_deps[pkg].get("version"),
                        new_version=new_pkg,
                        action="replace",
                        success=True,
                    )
                )
                logger.info(f"Replaced {pkg} with {new_pkg}")
            except Exception as e:
                results.append(
                    DependencyUpdate(
                        package=pkg,
                        current_version=self.current_deps[pkg].get("version"),
                        new_version=new_pkg,
                        action="replace",
                        success=False,
                        error=str(e),
                    )
                )

        return results
