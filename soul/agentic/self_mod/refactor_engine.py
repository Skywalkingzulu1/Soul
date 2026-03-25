"""Refactor engine - applies modernization patterns to code."""

import ast
import re
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

PROTECTED_FILES = {"brain.py", "memory.py", "identity.py", "main.py"}
PROTECTED_DIRS = {
    "philosophy",
    "vital_core",
    "vision_core",
    "knowledge_core",
}
PROTECTED_AGENTIC_FILES = {"loop.py", "perceive.py", "act.py"}

REFACTOR_TYPES = {
    "type_hints": "Add type hints to functions",
    "bare_except": "Replace bare except with specific exceptions",
    "dataclass": "Convert classes to dataclasses",
    "docstrings": "Add missing docstrings",
}


@dataclass
class RefactorResult:
    file_path: str
    refactor_type: str
    changes_made: int
    success: bool
    error: Optional[str] = None


class RefactorEngine:
    """Applies modernization patterns to code."""

    def __init__(self, root_path: Optional[str] = None):
        if root_path:
            p = Path(root_path)
            if p.is_absolute():
                self.root = p
            else:
                self.root = (Path(__file__).parent.parent.parent.parent / p).resolve()
        else:
            self.root = Path(__file__).parent.parent.parent.parent.resolve()
        self.results: list[RefactorResult] = []

    def apply_refactor(
        self, refactor_type: str, target: Optional[str] = None
    ) -> list[RefactorResult]:
        """Apply a specific refactor type to target."""
        logger.info(f"Applying refactor: {refactor_type} to {target or 'all files'}")

        target_path = Path(target) if target else self.root
        results = []

        if refactor_type == "type_hints":
            results = self._add_type_hints(target_path)
        elif refactor_type == "bare_except":
            results = self._fix_bare_except(target_path)
        elif refactor_type == "dataclass":
            results = self._convert_to_dataclass(target_path)
        elif refactor_type == "docstrings":
            results = self._add_docstrings(target_path)
        else:
            logger.warning(f"Unknown refactor type: {refactor_type}")

        self.results.extend(results)
        return results

    def _add_type_hints(self, target_path: Path) -> list[RefactorResult]:
        """Add type hints to functions."""
        results = []

        for py_file in target_path.rglob("*.py"):
            if self._is_protected(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                modified_content = self._add_type_hints_to_content(content)

                if modified_content != content:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(modified_content)

                    results.append(
                        RefactorResult(
                            file_path=str(py_file),
                            refactor_type="type_hints",
                            changes_made=modified_content.count("-> "),
                            success=True,
                        )
                    )
                    logger.info(f"Added type hints to {py_file}")

            except Exception as e:
                results.append(
                    RefactorResult(
                        file_path=str(py_file),
                        refactor_type="type_hints",
                        changes_made=0,
                        success=False,
                        error=str(e),
                    )
                )

        return results

    def _add_type_hints_to_content(self, content: str) -> str:
        """Add basic type hints to content."""
        modified = content

        patterns = [
            (r"def (\w+)\(([^)]*)\):", r"def \1(\2) -> None:"),
            (r"async def (\w+)\(([^)]*)\):", r"async def \1(\2) -> None:"),
        ]

        for pattern, replacement in patterns:
            if "->" not in modified:
                modified = re.sub(pattern, replacement, modified)

        return modified

    def _fix_bare_except(self, target_path: Path) -> list[RefactorResult]:
        """Replace bare except with Exception."""
        results = []

        for py_file in target_path.rglob("*.py"):
            if self._is_protected(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                modified_content = content.replace("except Exception:", "except Exception:")

                if modified_content != content:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(modified_content)

                    count = content.count("except Exception:") - modified_content.count("except Exception:")
                    results.append(
                        RefactorResult(
                            file_path=str(py_file),
                            refactor_type="bare_except",
                            changes_made=count,
                            success=True,
                        )
                    )
                    logger.info(f"Fixed bare except in {py_file}")

            except Exception as e:
                results.append(
                    RefactorResult(
                        file_path=str(py_file),
                        refactor_type="bare_except",
                        changes_made=0,
                        success=False,
                        error=str(e),
                    )
                )

        return results

    def _convert_to_dataclass(self, target_path: Path) -> list[RefactorResult]:
        """Convert simple classes to dataclasses."""
        results = []

        for py_file in target_path.rglob("*.py"):
            if self._is_protected(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                modified_content = self._convert_classes_to_dataclass(content)

                if modified_content != content:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(modified_content)

                    count = modified_content.count("@dataclass") - content.count(
                        "@dataclass"
                    )
                    if count > 0:
                        results.append(
                            RefactorResult(
                                file_path=str(py_file),
                                refactor_type="dataclass",
                                changes_made=count,
                                success=True,
                            )
                        )
                        logger.info(
                            f"Converted {count} classes to dataclass in {py_file}"
                        )

            except Exception as e:
                results.append(
                    RefactorResult(
                        file_path=str(py_file),
                        refactor_type="dataclass",
                        changes_made=0,
                        success=False,
                        error=str(e),
                    )
                )

        return results

    def _convert_classes_to_dataclass(self, content: str) -> str:
        """Convert eligible classes to dataclasses."""
        modified = content

        if (
            "from dataclasses import dataclass" not in modified
            and "@dataclass" not in modified
        ):
            lines = modified.split("\n")
            import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    import_idx = i

            lines.insert(import_idx + 1, "from dataclasses import dataclass, field")
            modified = "\n".join(lines)

        class_pattern = r"class (\w+)\([^)]*\):"
        classes = re.findall(class_pattern, modified)

        for class_name in classes[:5]:
            pattern = rf"(class {class_name}\([^)]*\):\s*\n)(\s+)"
            if re.search(pattern, modified):
                modified = re.sub(pattern, r"\1@dataclass\n\2", modified)

        return modified

    def _add_docstrings(self, target_path: Path) -> list[RefactorResult]:
        """Add missing docstrings to classes and functions."""
        results = []

        for py_file in target_path.rglob("*.py"):
            if self._is_protected(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                modified_content = self._add_docstrings_to_content(content)

                if modified_content != content:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(modified_content)

                    count = (
                        modified_content.count('"""') // 2 - content.count('"""') // 2
                    )
                    if count > 0:
                        results.append(
                            RefactorResult(
                                file_path=str(py_file),
                                refactor_type="docstrings",
                                changes_made=count,
                                success=True,
                            )
                        )

            except Exception as e:
                results.append(
                    RefactorResult(
                        file_path=str(py_file),
                        refactor_type="docstrings",
                        changes_made=0,
                        success=False,
                        error=str(e),
                    )
                )

        return results

    def _add_docstrings_to_content(self, content: str) -> str:
        """Add basic docstrings to classes and functions."""
        lines = content.split("\n")
        modified_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            if (
                line.strip().startswith("class ")
                and '"""' not in line
                and '"""' not in (lines[i + 1] if i + 1 < len(lines) else "")
            ):
                class_name = line.strip().split("class ")[1].split("(")[0].rstrip(":")
                modified_lines.append(line)
                modified_lines.append(f'    """{class_name} class."""')
                modified_lines.append("")
                i += 1
                continue

            if (
                line.strip().startswith("def ") or line.strip().startswith("async def ")
            ) and '"""' not in line:
                modified_lines.append(line)
                modified_lines.append('    """TODO: Add docstring."""')
                i += 1
                continue

            modified_lines.append(line)
            i += 1

        return "\n".join(modified_lines)

    def _is_protected(self, file_path: Path) -> bool:
        """Check if file is protected."""
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

    def get_refactor_summary(self) -> dict:
        """Get summary of all refactors applied."""
        if not self.results:
            return {"total": 0, "successful": 0, "failed": 0}

        return {
            "total": len(self.results),
            "successful": len([r for r in self.results if r.success]),
            "failed": len([r for r in self.results if not r.success]),
            "changes": sum(r.changes_made for r in self.results if r.success),
        }
