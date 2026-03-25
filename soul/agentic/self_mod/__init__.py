"""Self-modification capabilities for autonomous code improvement."""

from .self_reflector import SelfReflector
from .refactor_engine import RefactorEngine
from .dependency_manager import DependencyManager
from .test_generator import TestGenerator
from .safety_gate import SafetyGate
from .executor import AgenticExecutor

__all__ = [
    "SelfReflector",
    "RefactorEngine",
    "DependencyManager",
    "TestGenerator",
    "SafetyGate",
    "AgenticExecutor",
]
