import pytest
from pathlib import Path
from benchmarks.evaluator import TaskEvaluator

def test_evaluator_check_imports_safe():
    evaluator = TaskEvaluator(Path("."))

    # 1. Valid built-in / standard imports should pass
    code_ok = "import os\nimport sys\nfrom collections import defaultdict\n"
    assert evaluator._check_imports(code_ok) is True

    # 2. Missing/invalid imports should fail
    code_bad = "import non_existent_garbage_module_xyz\n"
    assert evaluator._check_imports(code_bad) is False
