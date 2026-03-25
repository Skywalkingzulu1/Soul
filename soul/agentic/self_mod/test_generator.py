"""Test generator - auto-creates tests for refactored code."""

import ast
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class TestFile:
    module_path: str
    test_path: str
    functions_generated: int
    success: bool


class TestGenerator:
    """Generates pytest tests for Python modules."""

    def __init__(self, root_path: Optional[str] = None, test_dir: str = "tests"):
        self.root = Path(root_path or ".")
        self.test_dir = Path(test_dir)
        self.test_dir.mkdir(exist_ok=True)

    def generate_tests_for_module(self, module_path: str) -> TestFile:
        """Generate tests for a single module."""
        module_file = self.root / module_path

        if not module_file.exists():
            return TestFile(
                module_path=module_path,
                test_path="",
                functions_generated=0,
                success=False,
            )

        test_file = self._create_test_file(module_path)

        try:
            with open(module_file, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            test_content = self._generate_test_content(module_path, tree)

            test_file_path = (
                self.test_dir
                / f"test_{module_path.replace('/', '_').replace('.py', '')}.py"
            )

            with open(test_file_path, "w", encoding="utf-8") as f:
                f.write(test_content)

            return TestFile(
                module_path=module_path,
                test_path=str(test_file_path),
                functions_generated=content.count("def "),
                success=True,
            )

        except Exception as e:
            logger.error(f"Failed to generate tests for {module_path}: {e}")
            return TestFile(
                module_path=module_path,
                test_path="",
                functions_generated=0,
                success=False,
            )

    def _create_test_file(self, module_path: str) -> Path:
        """Create test directory and file."""
        module_name = module_path.replace("/", ".").replace(".py", "")
        test_file = self.test_dir / f"test_{module_name.split('.')[-1]}.py"
        return test_file

    def _generate_test_content(self, module_path: str, tree: ast.AST) -> str:
        """Generate test content from AST."""
        module_name = module_path.replace("/", ".").replace(".py", "")

        imports = [
            "import pytest",
            f"from {module_name} import *",
            "",
        ]

        classes = []
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                if not class_name.startswith("_"):
                    tests = self._generate_class_tests(class_name, node)
                    classes.append(tests)

            elif isinstance(node, ast.FunctionDef):
                func_name = node.name
                if not func_name.startswith("_") and not func_name.startswith("test_"):
                    test_func = self._generate_function_test(func_name, node)
                    functions.append(test_func)

        content = "\n".join(imports)
        content += "\n\n".join(classes + functions)

        return content

    def _generate_class_tests(self, class_name: str, node: ast.ClassDef) -> str:
        """Generate tests for a class."""
        lines = [
            f"class Test{class_name}:",
            f'    """Tests for {class_name}."""',
            "",
        ]

        init_method = None
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                init_method = item
                break

        lines.append("    @pytest.fixture")
        lines.append(f"    def {class_name.lower()}(self) -> {class_name}:")

        if init_method:
            params = [arg.arg for arg in init_method.args.args if arg.arg != "self"]
            if params:
                lines.append(
                    f"        return {class_name}({', '.join(f'{p}=None' for p in params)})"
                )
            else:
                lines.append(f"        return {class_name}()")
        else:
            lines.append(f"        return {class_name}()")

        lines.append("")

        for item in node.body:
            if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                method_name = item.name
                lines.append(f"    def test_{method_name}(self, {class_name.lower()}):")
                lines.append(f'        """Test {method_name}."""')
                lines.append(f"        result = {class_name.lower()}.{method_name}()")
                lines.append("        assert result is not None")
                lines.append("")

        return "\n".join(lines)

    def _generate_function_test(self, func_name: str, node: ast.FunctionDef) -> str:
        """Generate test for a function."""
        args = [arg.arg for arg in node.args.args if arg.arg != "self"]

        lines = [
            f"def test_{func_name}():",
            f'    """Test {func_name}."""',
        ]

        if args:
            lines.append(f"    result = {func_name}({', '.join(['None'] * len(args))})")
        else:
            lines.append(f"    result = {func_name}()")

        lines.append("    assert result is not None")

        return "\n".join(lines)

    def generate_conftest(self) -> bool:
        """Generate conftest.py for shared fixtures."""
        conftest_path = self.test_dir / "conftest.py"

        if conftest_path.exists():
            return False

        content = '''"""Pytest configuration and shared fixtures."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_soul():
    """Mock Soul instance for testing."""
    from soul.brain import Soul
    return Soul(name="Test")


@pytest.fixture
def mock_memory():
    """Mock memory for testing."""
    from soul.memory import Memory
    return Memory()
'''

        with open(conftest_path, "w") as f:
            f.write(content)

        logger.info(f"Created {conftest_path}")
        return True

    def generate_pytest_ini(self) -> bool:
        """Generate pytest.ini configuration."""
        ini_path = self.root / "pytest.ini"

        if ini_path.exists():
            return False

        content = """[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = -v --tb=short
"""

        with open(ini_path, "w") as f:
            f.write(content)

        logger.info(f"Created {ini_path}")
        return True

    def run_tests(self, test_path: Optional[str] = None) -> dict:
        """Run generated tests."""
        import subprocess

        test_args = ["pytest", str(self.test_dir)]
        if test_path:
            test_args = ["pytest", test_path]

        try:
            result = subprocess.run(
                test_args, capture_output=True, text=True, timeout=60
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "errors": str(e),
            }
