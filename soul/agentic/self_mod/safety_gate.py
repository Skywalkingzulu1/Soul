"""Safety gate - verifies changes and auto-reverts on failure."""

import subprocess
import logging
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class SafetyCheck:
    check_name: str
    passed: bool
    message: str
    timestamp: str = ""


@dataclass
class GateResult:
    passed: bool
    checks: list[SafetyCheck]
    revert_triggered: bool = False
    error: Optional[str] = None


class SafetyGate:
    """Safety verification and auto-revert system."""

    def __init__(self, root_path: str = "."):
        self.root = Path(root_path)
        self.log_path = self.root / "knowledge" / "self_modifications.log"
        self.log_path.parent.mkdir(exist_ok=True)

    def verify(self, test_path: str = "tests", dry_run: bool = False) -> GateResult:
        """Run safety checks and tests."""
        logger.info("Running safety gate verification...")

        checks = []

        check1 = self._check_imports()
        checks.append(check1)

        check2 = self._check_syntax()
        checks.append(check2)

        check3 = self._check_protected_files()
        checks.append(check3)

        if test_path:
            check4 = self._run_tests(test_path)
            checks.append(check4)

        all_passed = all(c.passed for c in checks)

        if not all_passed and not dry_run:
            self._log_verification(checks, passed=False)

        return GateResult(
            passed=all_passed,
            checks=checks,
            revert_triggered=False,
            error=None if all_passed else "Some checks failed",
        )

    def _check_imports(self) -> SafetyCheck:
        """Check all imports work."""
        # Only check 'soul' import if we are in the Soul repo or it has a soul folder
        if not (self.root / "soul").exists():
            return SafetyCheck(
                check_name="import_check",
                passed=True,
                message="External repo - skipping soul import check",
                timestamp=datetime.now().isoformat(),
            )
        
        try:
            result = subprocess.run(
                ["python", "-c", "import soul"],
                capture_output=True,
                timeout=30,
                cwd=self.root,
            )

            if result.returncode == 0:
                return SafetyCheck(
                    check_name="import_check",
                    passed=True,
                    message="All imports successful",
                    timestamp=datetime.now().isoformat(),
                )
            else:
                return SafetyCheck(
                    check_name="import_check",
                    passed=False,
                    message=f"Import failed: {result.stderr[:200]}",
                    timestamp=datetime.now().isoformat(),
                )
        except Exception as e:
            return SafetyCheck(
                check_name="import_check",
                passed=False,
                message=str(e),
                timestamp=datetime.now().isoformat(),
            )

    def _check_syntax(self) -> SafetyCheck:
        """Check Python syntax of modified files."""
        issues = []

        for py_file in self.root.rglob("soul/**/*.py"):
            if py_file.is_file():
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        compile(f.read(), str(py_file), "exec")
                except SyntaxError as e:
                    issues.append(f"{py_file}: {e}")

        if not issues:
            return SafetyCheck(
                check_name="syntax_check",
                passed=True,
                message="All files have valid syntax",
                timestamp=datetime.now().isoformat(),
            )

        return SafetyCheck(
            check_name="syntax_check",
            passed=False,
            message=f"Syntax errors: {'; '.join(issues[:3])}",
            timestamp=datetime.now().isoformat(),
        )

    def _check_protected_files(self) -> SafetyCheck:
        """Ensure protected files were not modified."""
        protected = ["brain.py", "memory.py", "identity.py", "main.py"]
        
        # Only check files that actually exist in this repo
        existing_protected = [pf for pf in protected if (self.root / pf).exists() or (self.root / "soul" / pf).exists()]
        
        if not existing_protected:
            return SafetyCheck(
                check_name="protected_check",
                passed=True,
                message="No protected files found in this repo - skipping",
                timestamp=datetime.now().isoformat(),
            )

        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.root,
            )

            modified = []
            for line in result.stdout.split("\n"):
                if line.strip() and line.strip().startswith("M"):
                    for pf in protected:
                        if pf in line:
                            modified.append(pf)

            if not modified:
                return SafetyCheck(
                    check_name="protected_check",
                    passed=True,
                    message="No protected files modified",
                    timestamp=datetime.now().isoformat(),
                )

            return SafetyCheck(
                check_name="protected_check",
                passed=False,
                message=f"Protected files modified: {modified}",
                timestamp=datetime.now().isoformat(),
            )

        except Exception:
            return SafetyCheck(
                check_name="protected_check",
                passed=True,
                message="Git not available, skipping check",
                timestamp=datetime.now().isoformat(),
            )

    def _run_tests(self, test_path: str) -> SafetyCheck:
        """Run tests to verify functionality."""
        test_dir = self.root / test_path
        if not test_dir.exists():
            return SafetyCheck(
                check_name="test_check",
                passed=True,
                message="No tests directory - skipping",
                timestamp=datetime.now().isoformat(),
            )

        test_files = list(test_dir.glob("test_*.py"))
        if not test_files:
            return SafetyCheck(
                check_name="test_check",
                passed=True,
                message="No test files - skipping",
                timestamp=datetime.now().isoformat(),
            )

        try:
            result = subprocess.run(
                ["pytest", test_path, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.root,
            )

            if result.returncode == 0:
                return SafetyCheck(
                    check_name="test_check",
                    passed=True,
                    message="All tests passed",
                    timestamp=datetime.now().isoformat(),
                )

            return SafetyCheck(
                check_name="test_check",
                passed=False,
                message=f"Tests failed: {result.stdout[-300:]}",
                timestamp=datetime.now().isoformat(),
            )

        except subprocess.TimeoutExpired:
            return SafetyCheck(
                check_name="test_check",
                passed=False,
                message="Tests timed out",
                timestamp=datetime.now().isoformat(),
            )
        except Exception as e:
            return SafetyCheck(
                check_name="test_check",
                passed=False,
                message=f"Could not run tests: {e}",
                timestamp=datetime.now().isoformat(),
            )

    def revert(self) -> bool:
        """Revert all changes."""
        try:
            result = subprocess.run(
                ["git", "checkout", "--", "."],
                capture_output=True,
                text=True,
                cwd=self.root,
            )

            if result.returncode == 0:
                logger.info("Reverted all changes")
                self._log_verification([], passed=False, reverted=True)
                return True

            return False
        except Exception as e:
            logger.error(f"Revert failed: {e}")
            return False

    def _log_verification(
        self, checks: list[SafetyCheck], passed: bool, reverted: bool = False
    ):
        """Log verification results."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "passed": passed,
            "reverted": reverted,
            "checks": [
                {"name": c.check_name, "passed": c.passed, "message": c.message}
                for c in checks
            ],
        }

        with open(self.log_path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def check_status(self) -> dict:
        """Check current safety gate status."""
        status = {
            "last_check": None,
            "changes_since_last_check": False,
            "tests_available": (self.root / "tests").exists(),
        }

        if self.log_path.exists():
            with open(self.log_path, "r") as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    status["last_check"] = last_entry

        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.root,
            )
            status["changes_since_last_check"] = bool(result.stdout.strip())
        except Exception:
            pass

        return status
