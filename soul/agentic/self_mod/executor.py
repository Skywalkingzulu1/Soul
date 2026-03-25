"""Agentic executor - autonomous self-modification loop."""

import logging
import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

from .self_reflector import SelfReflector
from .refactor_engine import RefactorEngine
from .dependency_manager import DependencyManager
from .test_generator import TestGenerator
from .safety_gate import SafetyGate


MODES = {
    "analyze": "Run code analysis only",
    "refactor": "Apply code refactoring",
    "dependencies": "Update dependencies",
    "full": "Full self-improvement cycle",
}


@dataclass
class ExecutorResult:
    mode: str
    success: bool
    changes_made: int
    tests_passed: bool
    reverted: bool
    message: str
    details: dict = field(default_factory=dict)


class AgenticExecutor:
    """Autonomous self-modification executor."""

    def __init__(self, root_path: str = "."):
        self.root = Path(root_path).resolve()
        self.frozen = False

        self.reflector = SelfReflector(str(self.root / "soul"))
        self.refactor_engine = RefactorEngine(str(self.root / "soul"))
        self.dep_manager = DependencyManager(str(self.root / "requirements.txt"))
        self.test_gen = TestGenerator(str(self.root))
        self.safety = SafetyGate(str(self.root))

        self.last_plan = None
        self.last_result = None

    def run(self, mode: str = "full", dry_run: bool = False) -> ExecutorResult:
        """Run autonomous self-modification."""
        if self.frozen:
            return ExecutorResult(
                mode=mode,
                success=False,
                changes_made=0,
                tests_passed=False,
                reverted=False,
                message="Self-modification is frozen",
            )

        logger.info(f"Starting agentic executor in {mode} mode (dry_run={dry_run})")

        if mode == "analyze":
            return self._run_analysis()
        elif mode == "refactor":
            return self._run_refactor(dry_run)
        elif mode == "dependencies":
            return self._run_dependencies(dry_run)
        elif mode == "full":
            return self._run_full_cycle(dry_run)
        else:
            return ExecutorResult(
                mode=mode,
                success=False,
                changes_made=0,
                tests_passed=False,
                reverted=False,
                message=f"Unknown mode: {mode}",
            )

    def _run_analysis(self) -> ExecutorResult:
        """Run self-analysis."""
        logger.info("Running self-analysis...")

        plan = self.reflector.get_fix_plan()
        self.last_plan = plan

        message = f"Analysis complete. Score: {plan['score']:.1f}%, Issues: {plan['total_issues']}"

        logger.info(message)

        return ExecutorResult(
            mode="analyze",
            success=True,
            changes_made=0,
            tests_passed=True,
            reverted=False,
            message=message,
            details=plan,
        )

    def _run_refactor(self, dry_run: bool) -> ExecutorResult:
        """Run refactoring."""
        logger.info("Running refactoring...")

        plan = self.reflector.get_fix_plan()

        if not plan["top_fixes"]:
            return ExecutorResult(
                mode="refactor",
                success=True,
                changes_made=0,
                tests_passed=True,
                reverted=False,
                message="No refactoring needed",
            )

        results = []

        if not dry_run:
            results.extend(self.refactor_engine.apply_refactor("bare_except"))
            results.extend(self.refactor_engine.apply_refactor("type_hints"))

        changes = sum(r.changes_made for r in results if r.success)

        if dry_run:
            return ExecutorResult(
                mode="refactor",
                success=True,
                changes_made=changes,
                tests_passed=True,
                reverted=False,
                message=f"[DRY RUN] Would make {changes} changes",
            )

        safety_result = self.safety.verify()

        if not safety_result.passed:
            logger.warning("Safety checks failed, reverting...")
            self.safety.revert()
            return ExecutorResult(
                mode="refactor",
                success=False,
                changes_made=changes,
                tests_passed=False,
                reverted=True,
                message=f"Reverted due to failed checks: {safety_result.error}",
            )

        return ExecutorResult(
            mode="refactor",
            success=True,
            changes_made=changes,
            tests_passed=True,
            reverted=False,
            message=f"Refactoring complete. {changes} changes applied",
            details={"results": [str(r) for r in results]},
        )

    def _run_dependencies(self, dry_run: bool) -> ExecutorResult:
        """Run dependency updates."""
        logger.info("Running dependency management...")

        self.dep_manager.load_dependencies()
        recs = self.dep_manager.get_recommendations()

        if dry_run:
            return ExecutorResult(
                mode="dependencies",
                success=True,
                changes_made=0,
                tests_passed=True,
                reverted=False,
                message=f"[DRY RUN] Recommendations: {recs}",
            )

        results = []

        if recs["add"]:
            results.extend(self.dep_manager.add_recommended())

        if recs["replace"]:
            results.extend(self.dep_manager.apply_replacements())

        changes = len([r for r in results if r.success])

        return ExecutorResult(
            mode="dependencies",
            success=True,
            changes_made=changes,
            tests_passed=True,
            reverted=False,
            message=f"Dependency updates complete. {changes} changes",
            details={"recommendations": recs},
        )

    def _run_full_cycle(self, dry_run: bool) -> ExecutorResult:
        """Run full self-improvement cycle."""
        logger.info("Running full self-improvement cycle...")

        steps = []

        step1 = self._run_analysis()
        steps.append(("analyze", step1.success, step1.message))

        if not step1.success:
            return ExecutorResult(
                mode="full",
                success=False,
                changes_made=0,
                tests_passed=False,
                reverted=False,
                message="Analysis failed",
            )

        step2 = self._run_refactor(dry_run)
        steps.append(("refactor", step2.success, step2.message))

        if dry_run:
            return ExecutorResult(
                mode="full",
                success=True,
                changes_made=step2.changes_made,
                tests_passed=True,
                reverted=False,
                message=f"[DRY RUN] Full cycle would make {step2.changes_made} changes",
                details={"steps": steps},
            )

        if not step2.success:
            return ExecutorResult(
                mode="full",
                success=False,
                changes_made=step2.changes_made,
                tests_passed=False,
                reverted=step2.reverted,
                message=f"Refactor failed: {step2.message}",
                details={"steps": steps},
            )

        step3 = self._run_dependencies(dry_run=False)
        steps.append(("dependencies", step3.success, step3.message))

        self.last_result = ExecutorResult(
            mode="full",
            success=True,
            changes_made=step2.changes_made + step3.changes_made,
            tests_passed=True,
            reverted=False,
            message=f"Full cycle complete. {step2.changes_made + step3.changes_made} changes",
            details={"steps": steps},
        )

        return self.last_result

    def freeze(self):
        """Freeze self-modification."""
        self.frozen = True
        logger.info("Self-modification frozen")

    def unfreeze(self):
        """Unfreeze self-modification."""
        self.frozen = False
        logger.info("Self-modification unfrozen")

    def get_status(self) -> dict:
        """Get executor status."""
        return {
            "frozen": self.frozen,
            "last_plan": self.last_plan,
            "last_result": self.last_result,
            "safety_status": self.safety.check_status(),
        }

    def get_plan(self) -> dict:
        """Get current improvement plan."""
        if not self.last_plan:
            self._run_analysis()
        return self.last_plan
