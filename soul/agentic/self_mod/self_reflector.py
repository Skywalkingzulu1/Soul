"""Self-reflector - analyzes own code for modernization opportunities."""

import ast
import os
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

PROTECTED_FILES = {"brain.py", "memory.py", "identity.py", "main.py", "__init__.py"}

PROTECTED_DIRS = {
    "philosophy",
    "vital_core",
    "vision_core",
    "knowledge_core",
}

PROTECTED_AGENTIC_FILES = {"loop.py", "perceive.py", "act.py"}

ISSUES = {
    "no_type_hints": {
        "severity": "medium",
        "description": "Missing type hints",
        "pattern": r"def \w+\([^)]*\):",
    },
    "bare_except": {
        "severity": "high",
        "description": "Bare except clause - swallows errors",
        "pattern": r"except\s*:",
    },
    "hardcoded_config": {
        "severity": "medium",
        "description": "Hardcoded configuration values",
        "pattern": r'(?<!")(?<!\w)(timeout|limit|max|min)\s*=\s*\d+',
    },
    "f_string_complex": {
        "severity": "low",
        "description": "Complex f-string could use helper",
        "pattern": r'f".*\{.*\{',
    },
    "missing_docstring": {
        "severity": "low",
        "description": "Missing function/class docstring",
        "pattern": r"(class|def) \w+\([^)]*\):\s*\n(?!\s+\"\"\")",
    },
}


@dataclass
class CodeIssue:
    file_path: str
    line: int
    issue_type: str
    severity: str
    description: str
    code_snippet: str


@dataclass
class AnalysisReport:
    files_scanned: int = 0
    total_lines: int = 0
    issues_by_severity: dict = field(default_factory=dict)
    issues: list = field(default_factory=list)
    modernization_score: float = 0.0

    def summary(self) -> str:
        return (
            f"Scanned {self.files_scanned} files, {self.total_lines} lines. "
            f"Issues: {sum(self.issues_by_severity.values())} "
            f"(H:{self.issues_by_severity.get('high', 0)}, "
            f"M:{self.issues_by_severity.get('medium', 0)}, "
            f"L:{self.issues_by_severity.get('low', 0)}). "
            f"Score: {self.modernization_score:.1f}%"
        )


class SelfReflector:
    """Analyzes codebase for modernization opportunities."""

    def __init__(self, root_path: Optional[str] = None):
        if root_path:
            p = Path(root_path)
            if p.is_absolute():
                self.root = p
            else:
                self.root = (Path(__file__).parent.parent.parent.parent / p).resolve()
        else:
            self.root = Path(__file__).parent.parent.parent.parent.resolve()
        self.issues: list[CodeIssue] = []

    def analyze(self, target_dir: Optional[str] = None) -> AnalysisReport:
        """Run full analysis on target directory."""
        target = Path(target_dir) if target_dir else self.root

        logger.info(f"Analyzing {target} for modernization opportunities...")

        report = AnalysisReport()

        for py_file in target.rglob("*.py"):
            if self._is_protected(py_file):
                logger.debug(f"Skipping protected: {py_file}")
                continue

            file_issues = self._analyze_file(py_file)
            self.issues.extend(file_issues)
            report.files_scanned += 1

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    report.total_lines += len(lines)
            except Exception:
                pass

        for issue in self.issues:
            severity = issue.severity
            report.issues_by_severity[severity] = (
                report.issues_by_severity.get(severity, 0) + 1
            )

        report.issues = self.issues
        report.modernization_score = self._calculate_score(report)

        logger.info(report.summary())
        return report

    def _is_protected(self, file_path: Path) -> bool:
        """Check if file is protected from modification."""
        try:
            rel_path = file_path.relative_to(self.root)
        except ValueError:
            return True

        rel_str = str(rel_path)

        if "agentic" in rel_str:
            if "self_mod" in rel_str:
                return False
            if file_path.name in PROTECTED_AGENTIC_FILES:
                return True

        for protected_dir in PROTECTED_DIRS:
            if protected_dir in rel_str:
                return True

        return file_path.name in PROTECTED_FILES

    def _analyze_file(self, file_path: Path) -> list[CodeIssue]:
        """Analyze single file for issues."""
        issues = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"Cannot read {file_path}: {e}")
            return issues

        lines = content.split("\n")

        try:
            tree = ast.parse(content)
        except SyntaxError:
            logger.warning(f"Cannot parse {file_path}")
            return issues

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not ast.get_docstring(node):
                    if node.col_offset == 0:
                        issues.append(
                            CodeIssue(
                                file_path=str(file_path),
                                line=node.lineno,
                                issue_type="missing_docstring",
                                severity="low",
                                description="Function missing docstring",
                                code_snippet=lines[node.lineno - 1].strip()
                                if node.lineno <= len(lines)
                                else "",
                            )
                        )

                if not node.returns:
                    has_annotations = False
                    if node.args.args:
                        for arg in node.args.args:
                            if arg.annotation:
                                has_annotations = True
                                break
                    if not has_annotations:
                        if node.col_offset == 0:
                            issues.append(
                                CodeIssue(
                                    file_path=str(file_path),
                                    line=node.lineno,
                                    issue_type="no_type_hints",
                                    severity="medium",
                                    description="Function missing type hints",
                                    code_snippet=lines[node.lineno - 1].strip()
                                    if node.lineno <= len(lines)
                                    else "",
                                )
                            )

            elif isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    issues.append(
                        CodeIssue(
                            file_path=str(file_path),
                            line=node.lineno,
                            issue_type="bare_except",
                            severity="high",
                            description="Bare except clause - use specific exception",
                            code_snippet=lines[node.lineno - 1].strip()
                            if node.lineno <= len(lines)
                            else "",
                        )
                    )

        for i, line in enumerate(lines, 1):
            if "=" in line and not line.strip().startswith("#"):
                for pattern_name, info in ISSUES.items():
                    if pattern_name == "hardcoded_config" and "=" in line:
                        if (
                            any(kw in line for kw in ["timeout", "limit", "max", "min"])
                            and not "#" in line.split("=")[0]
                        ):
                            if any(c.isdigit() for c in line.split("=")[1][:10]):
                                issues.append(
                                    CodeIssue(
                                        file_path=str(file_path),
                                        line=i,
                                        issue_type="hardcoded_config",
                                        severity="medium",
                                        description=f"Hardcoded config: {line.strip()[:50]}",
                                        code_snippet=line.strip()[:80],
                                    )
                                )
                                break

        return issues

    def _calculate_score(self, report: AnalysisReport) -> float:
        """Calculate modernization score (0-100)."""
        total_issues = len(report.issues)
        if total_issues == 0:
            return 100.0

        severity_weights = {"high": 10, "medium": 5, "low": 1}
        weighted_issues = sum(
            severity_weights.get(i.severity, 1) for i in report.issues
        )

        max_score = 100
        penalty = min(weighted_issues * 2, max_score)

        return max(0, max_score - penalty)

    def get_top_issues(
        self, limit: int = 10, min_severity: str = "medium"
    ) -> list[CodeIssue]:
        """Get top issues to fix."""
        severity_order = {"high": 0, "medium": 1, "low": 2}
        min_level = severity_order.get(min_severity, 2)

        filtered = [
            i for i in self.issues if severity_order.get(i.severity, 2) <= min_level
        ]

        return sorted(filtered, key=lambda x: severity_order.get(x.severity, 2))[:limit]

    def get_fix_plan(self) -> dict:
        """Generate a fix plan from analysis."""
        report = self.analyze()
        top_issues = self.get_top_issues(limit=20)

        plan = {
            "score": report.modernization_score,
            "total_issues": len(self.issues),
            "high_priority": len([i for i in self.issues if i.severity == "high"]),
            "medium_priority": len([i for i in self.issues if i.severity == "medium"]),
            "top_fixes": [
                {
                    "file": issue.file_path,
                    "line": issue.line,
                    "type": issue.issue_type,
                    "severity": issue.severity,
                    "description": issue.description,
                }
                for issue in top_issues
            ],
        }

        return plan
